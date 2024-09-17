#!/bin/bash

# Copyright (C) 2016, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

# Begin configuration section.
sample_rate=16000 # Sample rate of wav file.
path=local
# End configuration section.
. utils/parse_options.sh

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 [option] <src-dir> <dst-dir>"
  echo "e.g.: $0 --apply_adaptation false /french_speech/train /data/train"
  echo "Options:"
  echo " --path 		 # Path to the dataset"
  echo " --apply_adaptation      # Apply text adaptation according to the lexicon. Default=false"
  echo " --sample_rate           # output audio file sample rate"
  exit 1
fi

src=$1
dst=$2

mkdir -p $dst || exit 1;

[ ! -d $src ] && echo "$0: no such directory $src" && exit 1;

rm -f $dst/*

wav_scp=$dst/wav.scp;
trans=$dst/text;
utt2spk=$dst/utt2spk;
spk2utt=$dst/spk2utt;
spk2gender=$dst/spk2gender

for reader_dir in $(find $src -mindepth 1 -maxdepth 1 -type d | sort); do
  reader=$(basename $reader_dir)

  for chapter_dir in $(find -L $reader_dir/ -mindepth 1 -maxdepth 1 -type d | sort); do
    chapter=$(basename $chapter_dir)

    find $chapter_dir/ -iname "*.wav" | sort | xargs -I% basename % .wav | \
      awk -v "dir=$chapter_dir" -v "sr=$sample_rate" '{printf "%s /usr/bin/sox %s/%s.wav -t wav -r %s -c 1 - |\n", $0, dir, $0, sr}' >> $wav_scp|| exit 1

    chapter_trans=$chapter_dir/${reader}-${chapter}.trans.txt
    [ ! -f  $chapter_trans ] && echo "$0: expected file $chapter_trans to exist" && exit 1
    $path/parseLIBVOX.pl $chapter_trans > $dst/text_tmp
    cat $dst/text_tmp | sed -e 's/  / /g' >>$trans

    awk -v "reader=$reader" -v "chapter=$chapter" '{printf "%s %s-%s\n", $1, reader, chapter}' \
      < $chapter_trans >>$utt2spk || exit 1
  done
done

rm $dst/text_tmp

spk2utt=$dst/spk2utt
utils/utt2spk_to_spk2utt.pl <$utt2spk >$spk2utt || exit 1

cat $spk2utt | awk '{print $1" m"}' >$spk2gender

ntrans=$(wc -l <$trans)
nutt2spk=$(wc -l <$utt2spk)
! [ "$ntrans" -eq "$nutt2spk" ] && \
  echo "Inconsistent #transcripts($ntrans) and #utt2spk($nutt2spk)" && exit 1;

utils/data/get_utt2dur.sh --nj 12 $dst

utils/validate_data_dir.sh --no-feats $dst || exit 1;

echo "Successfully prepared data in $dst"

exit 0
