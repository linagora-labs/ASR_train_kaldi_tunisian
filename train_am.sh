#!/usr/bin/env bash

# Set default values for variables
sys= # Path to the repository
stage=0
train=true  # set to false to disable the training-related scripts
decode=false  # set to false to disable the decoding-related scripts
nj=9  # Number of parallel jobs
kaldi_data_path=$1

architectur="tdnn13" # should be tdnn13 or tdnn17 or tdnn_attention

data_train=data/data_train # add train dataset
# data_test="data/YTB_SORTS_V1_AUG"  # Uncomment and set this if you have test data
lang=data/lang
exp=exp

# Parse optional arguments
. ./cmd.sh  # Adjust this file to suit your system's job scheduler
. utils/parse_options.sh  # Parse options


# Function to extract features
extract_features_for_data() {
    local data_dir="$1"
    echo "Feature Extraction for $data_dir"

    if [[ $(wc -l < $data_dir/spk2utt) -ge "$nj" ]]; then
        njobs="$nj"
    else
        njobs=$(wc -l < $data_dir/spk2utt)
    fi

    if [ ! -f $data_dir/feats.scp ]; then
        rm -rf $data_dir/log $data_dir/mfcc
        steps/make_mfcc.sh --nj $njobs --cmd "$train_cmd" $data_dir $data_dir/log $data_dir/mfcc
    fi

    if [ ! -f "$data_dir/cmvn.scp" ]; then
        steps/compute_cmvn_stats.sh $data_dir $data_dir/log $data_dir/mfcc
    fi

    if [ ! -f $data_dir/.valid.done ]; then
        utils/fix_data_dir.sh $data_dir
        utils/validate_data_dir.sh $data_dir
        touch $data_dir/.valid.done
    fi
}

# copy the train dataset into data folder
cp -r $kaldi_data_path $sys/ASR_train_kaldi_tunisian/data/data_train

# Feature extraction for training data
extract_features_for_data $data_train

# Optional: Feature extraction for test data
# extract_features_for_data $data_test

# Count the number of rows in the dataset
num_rows=$(wc -l < $data_train/text)
# Calculate half of the rows
half_rows=$((num_rows / 2))
# Use the subset_data_dir.sh with half the dataset
utils/subset_data_dir.sh --first $data_train $half_rows ${data_train}_half || exit 1

# Stage 1: Monophone training and decoding
if [ $stage -le 1 ]; then
    if $train; then
        steps/train_mono.sh --boost-silence 1.25 --nj $nj --cmd "$train_cmd" ${data_train}_half $lang $exp/mono || exit 1
    fi

    if $decode; then
        utils/mkgraph.sh $lang $exp/mono $exp/mono/graph
        steps/decode.sh --nj $nj --cmd "$decode_cmd" $exp/mono/graph $data_test $exp/mono/decode_${_test_filename} || exit 1
    fi
fi

# Stage 2: Triphone (delta + delta-delta) training and decoding
if [ $stage -le 2 ]; then
    if $train; then
        steps/align_si.sh --boost-silence 1.25 --nj $nj --cmd "$train_cmd" $data_train $lang $exp/mono $exp/mono_ali || exit 1
        steps/train_deltas.sh --boost-silence 1.25 --cmd "$train_cmd" 8000 15000 $data_train $lang $exp/mono_ali $exp/tri1 || exit 1
    fi

    if $decode; then
        utils/mkgraph.sh $lang $exp/tri1 $exp/tri1/graph || exit 1
        steps/decode.sh --nj $nj --cmd "$decode_cmd" $exp/tri1/graph $data_test $exp/tri1/decode_${_test_filename} || exit 1
    fi
fi

# Stage 3: LDA+MLLT training and decoding
if [ $stage -le 3 ]; then
    if $train; then
        steps/align_si.sh --nj $nj --cmd "$train_cmd" $data_train $lang $exp/tri1 $exp/tri1_ali || exit 1
        steps/train_lda_mllt.sh --cmd "$train_cmd" --splice-opts "--left-context=3 --right-context=3" 8000 15000 $data_train $lang $exp/tri1_ali $exp/tri2 || exit 1
    fi

    if $decode; then
        utils/mkgraph.sh $lang $exp/tri2 $exp/tri2/graph || exit 1
        steps/decode.sh --nj $nj --cmd "$decode_cmd" $exp/tri2/graph $data_test $exp/tri2/decode_${_test_filename} || exit 1
        # steps/decode_biglm.sh --nj $nj --cmd "$decode_cmd" $exp/tri2/graph $lang/G.fst $data_test $exp/tri2/decode_${_test_filename}_biglm
    fi
fi

# Stage 4: LDA+MLLT+SAT training and decoding
if [ $stage -le 4 ]; then
    if $train; then
        steps/align_si.sh --nj $nj --cmd "$train_cmd" $data_train $lang $exp/tri2 $exp/tri2_ali || exit 1
        steps/train_sat.sh --cmd "$train_cmd" 10000 20000 $data_train $lang $exp/tri2_ali $exp/tri3 || exit 1
    fi

    if $decode; then
        utils/mkgraph.sh $lang $exp/tri3 $exp/tri3/graph || exit 1
        steps/decode_fmllr.sh --nj $nj --cmd "$decode_cmd" $exp/tri3/graph $data_test $exp/tri3/decode_${_test_filename} || exit 1
    fi
fi

# Stage 6: Additional SAT training and decoding
if [ $stage -le 6 ]; then
    if $train; then
        steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" $data_train $lang $exp/tri3 $exp/tri3_ali || exit 1
        steps/train_sat.sh --cmd "$train_cmd" 15000 25000 $data_train $lang $exp/tri3_ali $exp/tri4 || exit 1
    fi

    if $decode; then
        utils/mkgraph.sh $lang $exp/tri4 $exp/tri4/graph || exit 1
        steps/decode_fmllr.sh --nj $nj --cmd "$decode_cmd" $exp/tri4/graph $data_test $exp/tri4/decode_${_test_filename} || exit 1
    fi
fi

local/nnet3/run_tdnn.sh $architectur