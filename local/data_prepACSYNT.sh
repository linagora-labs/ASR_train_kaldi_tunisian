#!/bin/bash
#
# Copyright 2017 Sonia BADENE @Linagora
# Modified by Ilyes Rebai @2021

source path.sh

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 <src-dir> <dst-dir>"
	echo "e.g: $0 /home/lingora/Documents/Linagora/Data/Tcof/tcof/3/Corpus/train data/train"
	#exit 1
fi

src=$1
dst=$2

# all utterances are Wav compressed, we use sox for reading signal in binary format
if ! which sox >&/dev/null; then
	echo "Please install 'sox' on All worker nodes"
	echo "apt-get install sox"
fi

mkdir -p $dst #|| exit 1;
[ ! -d $src ] && echo "$0: no such directory $src" #&& exit  1;

wav_scp=$dst/wav.scp; [[ -f "$wav_scp" ]] && rm $wav_scp
trans=$dst/text; [[ -f "$trans" ]] && rm $trans
utt2spk=$dst/utt2spk; [[ -f "$utt2spk" ]] && rm $utt2spk
utt2dur=$dst/utt2dur; [[ -f "$utt2dur" ]] && rm $utt2dur
segments=$dst/segments; [[ -f "$segments" ]] && rm $segments

# For each meeting
for meeting_dir in $(find $src -mindepth 1 -maxdepth 1 -type d | sort); do
	for meeting_part_TextGrid in $(find $meeting_dir/* | grep ".TextGrid"); do
		wav_file=`echo $meeting_part_TextGrid | sed "s/TextGrid/wav/"`
		txt_file=`echo $meeting_part_TextGrid | sed "s/TextGrid/txt/"`
		[ ! -f $wav_file ] && echo " Missing $wav_file file " && exit 1
		[ ! -f $txt_file ] && echo " Missing $txt_file file " && exit 1
		python local/parseACSYNT.py $meeting_part_TextGrid $txt_file $dst
	done
done

# convert utt2spk to spk2utt
spk2utt=$dst/spk2utt
utils/utt2spk_to_spk2utt.pl <$utt2spk >$spk2utt #|| exit 1

# compute segment's duration
utils/data/get_utt2dur.sh $dst 1>&2 #|| exit 1
# fix errors
utils/fix_data_dir.sh $dst
# Validate Kladi Inputs
utils/validate_data_dir.sh --no-feats $dst #|| exit 1;

echo "Successfully prepared data in $dst"

#exit 0
