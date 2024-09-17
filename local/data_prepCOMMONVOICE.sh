#!/bin/bash

# Copyright (C) 2019, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

# This script is used to prepare MAILABS corpus and to generate KALDI data files
# It uses "local/parseMAILABS.py" for corpus parsing and normalization

nj=12

. utils/parse_options.sh || exit 1;
. path.sh || exit 1


if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <src-dir> <wav-dir> <dst-dir>"
    echo "e.g: $0 /media/nas/CORPUS_FINAL/Corpus_audio/common-voice-fr_v2 clips ASR_MONTREAL/COMMONVOICE"
    exit 1
fi

src=$1
dst=$2
split=$3

# all utterances are Wav compressed, we use sox for reading signal in binary format
if ! which sox >&/dev/null; then
    echo "Please install 'sox' on All worker nodes"
    echo "apt-get install sox"
    #exit 1
fi

echo "=== Starting initial $dst Data preparation ..."

mkdir -p $dst || exit 1;

[ ! -d $src ] && echo "$0: no such directory $src" && exit  1;
[ ! -d $src/clips ] && [ ! -d $src/$split ] && echo "$O: no such directory $src/clips" && exit 1;

python3 local/parseCOMMONVOICE.py $src $dst $split || exit 1;

sed -i "s:' ' :' :g" $dst/text
sed -i "s:' $::g" $dst/text

utils/fix_data_dir.sh $dst
#utils/data/get_utt2dur.sh --nj $nj $dst 1>&2 #|| exit 1
utils/validate_data_dir.sh --no-feats $dst #|| exit 1;
echo "=== Successfully prepared data $dst.."
