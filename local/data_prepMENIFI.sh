#!/bin/bash

# Copyright (C) 2020, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

corpus= # this options can be used if there are different Transcriber parser
audio=wav
changeSpk= # this option is reserved for BREF corpus since the speaker information is not correct
. ./path.sh
. ./utils/parse_options.sh


if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <src-dir> <dst-dir>"
    echo "e.g: $0 /baie/corpus/ESTER/DGA/Phase1/data data/Phase1"
    exit 1
fi

src=$1
dst=$2

echo "=== Starting initial $dst Data preparation ..."

[ ! -d $src ] && echo "$0: no such directory $src" #&& exit  1;

mkdir -p $dst || exit 1
rm -f $dst/*

for trs_file in $(find $src -type f -name "*.xml" | sort); do
    python2 local/parseMENIFI.py $trs_file $dst $changeSpk || exit 1
done

utils/utt2spk_to_spk2utt.pl < $dst/utt2spk >$dst/spk2utt || exit 1
utils/data/get_utt2dur.sh --nj 12 $dst 1>&2 || exit 1
utils/fix_data_dir.sh $dst || exit 1
utils/validate_data_dir.sh --no-feats $dst || exit 1
echo "=== Successfully prepared data $dst.."
