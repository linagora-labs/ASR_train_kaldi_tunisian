#!/bin/bash

# This script is used to prepare the main folders and files for 
# training the speech recognition models (acoustic model, 
# decoding graph, speaker adaptation model)

nj=24

# configs for 'chain'
train_stage=-6 #-2
get_egs_stage=-10 #0
epc=4
remove_egs=false
xent_regularize=0.1
dropout_schedule='0.5,0.5' #'0,0@0.20,0.5@0.50,0'
common_egs_dir=
frames_per_eg=150,110,100
leaky_hmm_coefficient=0.1
minibatch=64

lr_start=0.00015
lr_final=0.000015
primary_lr_factor=0.25 # The learning-rate factor for transferred layers from source
                       # model. e.g. if 0, it fixed the paramters transferred from source.
                       # The learning-rate factor for new added layers is 1.0.



# Input folders
simulated_rirs="models_data/simulated_rirs_8k"
am_path="models_data/linSTT_AM_fr-FR_v2.2.0_gsm"
am_path0=$am_path #"models_data/linSTT_AM_fr-FR_v2.2.0_gsm"
lm_path="models_trained/LanguageModel"
data_train="data_kaldi/train_corrected"

. ./path.sh || exit 1
. utils/parse_options.sh || exit 1

dict=$lm_path/dict
lang=$lm_path/lang

for x in $simulated_rirs $am_path $am_path0 $lm_path $dict $lang;do
  if [ ! -e $x ];then
    echo "Could not find "$x
    exit 1
  fi
done

# G2P toolkit
g2p_tool=$(cat $am_path/LM_gen/g2p/.tool)
g2p_model=$am_path/LM_gen/g2p/model


train=$data_train/sp_rvb_vol
ivector_train=$train/ivectors
namelat=lat_`echo $am_path | awk -F "/" '{print $NF}'`
lat_train=$train/$namelat
name_expe="lr"$primary_lr_factor"-"$lr_start"-"$lr_final"_drop"`echo $dropout_schedule | awk '{gsub("@","--"); gsub(",","-"); print $0}'`"_hmm"$leaky_hmm_coefficient"_mb"$minibatch
output_dir="models_trained/AcousticModel/nnet_corrected_"$name_expe

if [ -d $output_dir ];then
  if [ -f $output_dir/final.mdl ];then
    echo "Output folder already exists with a trained model"
    exit 0
  fi
  checkpoints=`ls $output_dir/[1-9].mdl 2> /dev/null`" "`ls $output_dir/[0-9][0-9].mdl 2> /dev/null`
  if [ `echo $checkpoints | wc -w` -gt 0 ];then
    train_stage=`echo $checkpoints | awk -F"/" '{gsub(".mdl",""); print $NF}'`
    echo "Restarting from stage "$train_stage
  fi
fi

lang_chain=$lm_path/lang_chain
tree_chain=$output_dir/tree_chain

echo "==========================================="
echo $output_dir
echo "==========================================="

#############################################################################################
##################### DATA AUGMENTATION #####################################################
for data in $data_train; do

  #SPEED
  if [ ! -f $data/sp/text ];then 
    utils/data/perturb_data_dir_speed_3way.sh $data $data/sp || exit 1
  fi

  #REVERB
  rvb_opts=()
  rvb_opts+=(--rir-set-parameters "0.3, $simulated_rirs/smallroom/rir_list")
  rvb_opts+=(--rir-set-parameters "0.3, $simulated_rirs/mediumroom/rir_list")
  rvb_opts+=(--rir-set-parameters "0.3, $simulated_rirs/largeroom/rir_list")
  if [ ! -f $data/sp_rvb/text ];then 
    python3 steps/data/reverberate_data_dir.py \
      "${rvb_opts[@]}" \
      --prefix "rev" \
      --foreground-snrs "20:15:10:5:0" \
      --background-snrs "20:15:10:5:0" \
      --speech-rvb-probability 1 \
      --num-replications 1 \
      --source-sampling-rate 16000 \
      --include-original-data true \
      $data/sp $data/sp_rvb || exit 1
  fi

  if [ ! -f $data/sp_rvb/reco2dur ]; then
    for i in `seq 0 1`; do
      cat $data/sp/reco2dur | sed -e "s/^/rev${i}-/"
    done > $data/sp_rvb/reco2dur
  fi

  #VOLUME
  if [ ! -f $data/sp_rvb_vol/text ];then 
    utils/copy_data_dir.sh $data/sp_rvb $data/sp_rvb_vol || exit 1
  fi
  if [ ! -f $data/sp_rvb_vol/.done ];then
    utils/data/perturb_data_dir_volume.sh --scale-low 0.8 --scale-high 1.2 $data/sp_rvb_vol || exit 1
    touch $data/sp_rvb_vol/.done
  fi

done

#############################################################################################
##################### FEATURE EXTRACTION ####################################################
for data0 in $data_train; do
  for type in "sp_rvb_vol" "sp";do
    data=$data0/$type
    [[ $(wc -l < $data/spk2utt) -ge $nj ]] && njobs=$nj || njobs=$(wc -l < $data/spk2utt)
    #if [ ! -f $data/.wav.done ];then 
    #  nnet2-3/prepare_wav.sh $data || exit 1
    #fi
    if [ ! -f $data/feats.scp ];then
      rm -rf $data/{log,mfcc}
      steps/make_mfcc.sh --nj $nj --mfcc-config $am_path/conf/mfcc.conf $data $data/{log,mfcc} # || exit 1
    fi
    if [ ! -f $data/cmvn.scp ];then
      steps/compute_cmvn_stats.sh $data $data/{log,mfcc} || exit 1
    fi
    if [ ! -f $data/ivectors/ivector_online.scp ];then
      steps/online/nnet2/extract_ivectors_online.sh --nj $njobs $data $am_path/ivector_extractor $data/ivectors || exit 1
    fi
    [ ! -f $data/.valid.done ] && utils/fix_data_dir.sh $data && utils/validate_data_dir.sh $data && touch $data/.valid.done
  done
done

#############################################################################################
##################### LATTICE ALIGN DATA ####################################################

#[ ! -e $am_path/final.ie ] && ln -s $am_path/ivector_extractor/final.ie $am_path
for data in $data_train; do
  data=$data/sp
  [[ $(wc -l < $data/spk2utt) -ge $nj ]] && njobs=$nj || njobs=$(wc -l < $data/spk2utt)
  align_opts="--frames-per-chunk 51 --online-ivector-dir $data/ivectors"
  if [ ! -f $data/$namelat/lat.1.gz ];then 
    steps/nnet3/chain/align_lats.sh --nj $njobs $align_opts $data $lang $am_path $data/$namelat || exit 1
  fi
  if [ ! -f $data/$namelat/ali.1.gz ];then
    echo "$0: generate ali from lats" && run.pl JOB=1:$njobs $data/$namelat/log/generate_alignments.JOB.log \
      lattice-best-path --acoustic-scale=1.0 "ark:gunzip -c $data/$namelat/lat.JOB.gz |" \
          ark:/dev/null "ark:|gzip -c >$data/$namelat/ali.JOB.gz" || exit 1
  fi
done

for data in $data_train; do
  data_sp_ali=$data/sp/$namelat
  data_ali=$data/sp_rvb_vol/$namelat
  mkdir -p $data_ali

  # copy original lattice
  if [ ! -f $data_ali/lats.scp ];then
    lattice-copy "ark:gunzip -c $data_sp_ali/lat.*.gz |" ark,scp:$data_ali/lats.ark,$data_ali/lats.scp || exit 1
  fi

  # adapt the id of original lattice to ids of sp_rvb_vol_gsm
  if [ ! -f $data_ali/lats.final.scp ]; then
    for i in $(seq 0 1); do
      cat $data_ali/lats.scp | sed "s:^:rev${i}-:"
    done > $data_ali/lats.final.scp
  fi
  [ ! -f $data_ali/lat.1.gz ] && run.pl JOB=1:$nj $data_ali/log/lattice_regeneration.JOB.log \
                                 cut -d ' ' -f1 $data_ali/../split$nj/JOB/segments \| \
                                 utils/filter_scp.pl - $data_ali/lats.final.scp \| \
                                 LC_ALL=C sort -u \| \
                                 lattice-copy scp:- "ark:|gzip -c > $data_ali/lat.JOB.gz"
  # copy original alignments
  if [ ! -f $data_ali/alis.txt ];then
    copy-int-vector "ark:gunzip -c $data_sp_ali/ali.*.gz |" ark,t:$data_ali/alis.txt || exit 1
  fi

  # adapt the id of original alignments to ids of sp_rvb_vol_gsm
  if [ ! -f $data_ali/alis.final.txt ]; then
    for i in $(seq 0 1); do
      cat $data_ali/alis.txt | sed "s:^:rev${i}-:"
    done > $data_ali/alis.final.txt
  fi
  [ ! -f $data_ali/ali.1.gz ] && run.pl JOB=1:$nj $data_ali/log/alignment_regeneration.JOB.log \
                                 cut -d ' ' -f1 $data_ali/../split$nj/JOB/segments \| \
                                 utils/filter_scp.pl - $data_ali/alis.final.txt \| \
                                 LC_ALL=C sort -u \| \
                                 copy-int-vector ark,t:- "ark:|gzip -c > $data_ali/ali.JOB.gz"

 
  if [ ! -f $data_ali/final.mdl ];then
    echo $nj > $data_ali/num_jobs
    cp $data_ali/../../sp/$namelat/{cmvn_opts,final.mdl,frame_subsampling_factor,tree,phones.txt} $data_ali || exit 1
  fi
 
done

########################################################################################
###################### prepare lang for chain training #################################
########################################################################################

if [ ! -f $lang_chain/.done ]; then
  cp -r $lang $lang_chain
  silphonelist=$(cat $lang_chain/phones/silence.csl)
  nonsilphonelist=$(cat $lang_chain/phones/nonsilence.csl)
  steps/nnet3/chain/gen_topo.py $nonsilphonelist $silphonelist > $lang_chain/topo
  touch $lang_chain/.done
fi

###################### prepare tree dnn ###################
# use --alignment-subsampling-factor 1 when using a chain model for alignment (LinSTT model)
#if [ ! -f $tree_chain/tree ];then
#  steps/nnet3/chain/build_tree.sh --frame-subsampling-factor 3 --context-opts "--context-width=2 --central-position=1" --cmd "run.pl" --alignment-subsampling-factor 1 \
#    7000 $train $lang_chain $lat_train $tree_chain || exit 1
#fi

#############################################################################################
##################### DNN Transfer Learning #################################################

mkdir -p $output_dir
[ ! -f $output_dir/input.raw ] && run.pl $output_dir/log/generate_input_mdl.log \
   nnet3-am-copy --raw=true --edits="set-learning-rate-factor name=* learning-rate-factor=$primary_lr_factor; set-learning-rate-factor name=output* learning-rate-factor=1.0" \
      $am_path0/final.mdl $output_dir/input.raw

steps/nnet3/chain/train.py --stage $train_stage \
    --cmd="run.pl" \
    --trainer.input-model $output_dir/input.raw \
    --chain.alignment-subsampling-factor=1 \
    --feat.online-ivector-dir $ivector_train \
    --feat.cmvn-opts "--norm-means=false --norm-vars=false" \
    --chain.xent-regularize $xent_regularize \
    --chain.leaky-hmm-coefficient $leaky_hmm_coefficient \
    --chain.l2-regularize 0.0 \
    --chain.apply-deriv-weights false \
    --chain.lm-opts="--num-extra-lm-states=2000" \
    --egs.dir "$common_egs_dir" \
    --egs.stage $get_egs_stage \
    --egs.opts "--frames-overlap-per-eg 0 --constrained false" \
    --egs.chunk-width $frames_per_eg \
    --trainer.dropout-schedule $dropout_schedule \
    --trainer.add-option="--optimization.memory-compression-level=2" \
    --trainer.num-chunk-per-minibatch $minibatch \
    --trainer.frames-per-iter 2500000 \
    --trainer.num-epochs $epc \
    --trainer.optimization.num-jobs-initial 2 \
    --trainer.optimization.num-jobs-final 2 \
    --trainer.optimization.initial-effective-lrate $lr_start \
    --trainer.optimization.final-effective-lrate $lr_final \
    --trainer.max-param-change 2.0 \
    --cleanup.remove-egs $remove_egs \
    --cleanup true \
    --use-gpu true \
    --feat-dir $train \
    --tree-dir $lat_train \
    --lat-dir $lat_train \
    --dir $output_dir || exit 1
