#!/bin/bash

# Copyright (C) 2020, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

corpus= # this options can be used if there are different Transcriber parser
audio=wav
changeSpk= # this option is reserved for BREF corpus since the speaker information is not correct
per_file=0
. ./path.sh
. ./utils/parse_options.sh


if [ "$#" -lt 2 ]; then
    echo "Usage: $0 [<options1>] <src-dir> <dst-dir> [<options2>]"
    echo "e.g: $0 /baie/corpus/ESTER/DGA/Phase1/data data/Phase1"
    echo "options1:"
    echo "--per_file 1: to generate one output per file"
    echo "options2: see parseTranscriber.py"
    exit 1
fi

src=$1
shift
dst=$1
shift
opts=$*

echo "=== Starting initial $dst Data preparation ..."

[ ! -d $src ] && echo "$0: no such directory $src" #&& exit  1;

mkdir -p $dst #|| exit 1;
rm -f $dst/*

if [ "$corpus" == "TCOF" ]; then
    echo "$0: you are using TCOF parser!!"
    parser=local/parseTranscriber-TCOF.py
elif [ "$corpus" == "CFPP2000" ]; then
    echo "$0: you are using CFPP2000 parser!!"
    parser=local/parseTranscriber-CFPP2000.py
else
    echo "$0: you are using Transcriber parser!!"
    parser=local/parseTranscriber.py
fi

for trs_file in $(find $src -type f -name "*.trs" | sort); do
    wav_file=$(echo $trs_file | sed "s/.trs/.${audio}/g")
    audio2=$(echo $audio | tr [a-z] [A-Z])
    wav2_file=$(echo $trs_file | sed "s/.trs/.${audio2}/g")
    echo $trs_file
    if [[ ! -f $wav_file && ! -f $wav2_file ]]; then
        echo " Missing $wav_file file "
        exit 1
    fi
    if [ ! -f $wav_file ]; then
        wav_file=$wav2_file
    fi
    python2 $parser $trs_file $wav_file $dst $changeSpk $opts || exit 1 # >> $dst/log.txt 2>&1
    if [ $per_file -gt 0 ];then
        dst2=$dst.`basename $trs_file`
        mkdir -p $dst2 #|| exit 1;
        rm -f $dst2/*
        python2 $parser $trs_file $wav_file $dst2 $changeSpk $opts || exit 1 # >> $dst/log.txt 2>&1
    fi
done

utils/utt2spk_to_spk2utt.pl < $dst/utt2spk >$dst/spk2utt || exit $?
utils/data/get_utt2dur.sh --nj 12 $dst 1>&2 || exit $?
utils/fix_data_dir.sh $dst || exit $?;
utils/validate_data_dir.sh --no-feats $dst || exit $?;
rm -Rf $dst/.backup
echo "=== Successfully prepared data $dst.."
