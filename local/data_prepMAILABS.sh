#!/bin/bash

# Copyright (C) 2019, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

# This script is used to prepare MAILABS corpus and to generate KALDI data files
# It uses "local/parseMAILABS.py" for corpus parsing and normalization

. utils/parse_options.sh || exit 1;
. path.sh || exit 1


if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <src-dir> <dst-dir>"
    echo "e.g: $0 /media/nas/CORPUS_FINAL/Corpus_audio/M-AILABS/librivox-fr/fr_FR data/M-AILABS"
    exit 1
fi

src=$1
dst=$2

echo "=== Starting initial $dst Data preparation ..."

mkdir -p $dst #|| exit 1;
rm -rf $dst/*

[[ ! -d $src/male && ! -d $src/female ]] && echo "$0: no such directory $src/(male|female)" && exit  1;

for csv_file in $(find $src/female/*/*/metadata.csv) $(find $src/male/*/*/metadata.csv); do
    echo $csv_file
    python3 local/parseMAILABS.py $csv_file $dst >> $dst/log.txt
done

utils/utt2spk_to_spk2utt.pl < $dst/utt2spk >$dst/spk2utt || exit 1
utils/data/get_utt2dur.sh --nj 12 $dst 1>&2 #|| exit 1
utils/fix_data_dir.sh $dst || exit 1;
utils/validate_data_dir.sh --no-feats $dst || exit 1;
echo "=== Successfully prepared data $dst.."
