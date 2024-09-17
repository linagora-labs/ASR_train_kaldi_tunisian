#!/bin/bash

# Copyright (C) 2020, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

LC_CTYPE=en_US.utf8

. ./path.sh
. ./utils/parse_options.sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <src-dir> <dst-dir>"
    echo "e.g: $0 /media/nas/CORPUS_FINAL/Corpus_audio/VoxForge_FR_40H data/VOXFORG"
    exit 1
fi

src=$1
dst=$2

echo "=== Starting initial $dst Data preparation ..."

[ ! -d $src ] && echo "$0: no such directory $src" #&& exit  1;

mkdir -p $dst #|| exit 1;
rm -fr $dst/*

for folder in $(find $src -maxdepth 1 -type d | sort); do
    spk=$(basename $folder)
    [ -f $folder/etc/prompts-original ] && python3 local/parseVoxforge.py $folder $dst $folder/etc/prompts-original $spk
done

utils/utt2spk_to_spk2utt.pl < $dst/utt2spk >$dst/spk2utt || exit 1
utils/data/get_utt2dur.sh --nj 12 $dst 1>&2 #|| exit 1
utils/fix_data_dir.sh $dst || exit 1;
utils/validate_data_dir.sh --no-feats $dst || exit 1;
echo "=== Successfully prepared data $dst.."
