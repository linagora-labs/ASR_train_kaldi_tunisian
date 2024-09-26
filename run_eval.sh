#!/usr/bin/env bash

# Copyright © 2024 LINAGORA 
# Email: hnaouara@linagora.com
# License: AGPL v3

# Input arguments
data=$1                # Path(s) to the data to test (can be a list of paths or a single path)
model_path=$2          # Path to the model directory (should contain: [am / graph / ivector / conf])

# Number of jobs
nj=4

# Check if the required directories and files exist
if [ ! -d "$model_path/am" ] || [ ! -d "$model_path/graph" ] || [ ! -d "$model_path/ivector" ] || [ ! -d "$model_path/conf" ]; then
    echo "Model path or required directories do not exist: $model_path"
    exit 1
fi

# Step 1: Data preparation and validation
############################################################################################################
# 1. Prepare data `check local/huggingFace_into_kaldi.py` or prepare your own dataset                         #
# 2. Combine data `Non need if you used local/huggingFace_into_kaldi.py` else use `utils/combine_data.sh`     #
# 3. Fix and validate with utils/validate_data_dir.sh and utils/fix_data_dir.sh                            #
############################################################################################################

# Set default A.M parameters if not set
[ ! -f $model_path/am/frame_subsampling_factor ] && echo "3" > $model_path/am/frame_subsampling_factor
[ ! -f $model_path/am/cmvn_opts ] && echo "--norm-means=false --norm-vars=false" > $model_path/am/cmvn_opts

# Step 2: Feature extraction
# Determine number of jobs
num_spk=$(wc -l < "$data/spk2utt")
njobs=$(( num_spk >= nj ? nj : num_spk ))

# Compute MFCC features
if [ ! -f "$data/feats.scp" ]; then
    steps/make_mfcc.sh --nj $njobs --mfcc-config $model_path/conf/mfcc.conf $data $data/{log,mfcc}
    utils/fix_data_dir.sh "$data"
fi

# Compute CMVN stats
if [ ! -f $data/cmvn.scp ]; then
    steps/compute_cmvn_stats.sh $data $data/{log,mfcc}
fi

# Compute iVectors
if [ ! -f $data/ivectors/ivector_online.scp ]; then
    steps/online/nnet2/extract_ivectors_online.sh --nj $njobs $data $model_path/ivector $data/ivectors
fi

# Decode the data
data_name=$(basename $data)

if [ ! -f "$model_path/am/$data_name/.done" ]; then
    steps/nnet3/decode.sh \
        --acwt 1.0 --post-decode-acwt 10.0 \
        --extra-left-context 50 \
        --extra-right-context 0 \
        --extra-left-context-initial 0 \
        --extra-right-context-final 0 \
        --frames-per-chunk 150 \
        --nj $nj --num-threads 2 --use-gpu true \
        --online-ivector-dir "$data/ivectors" \
        "$model_path/graph" "$data" "$model_path/am/$data_name"
    
    # Mark as done
    touch "$model_path/am/$data_name/.done"
fi
