#!/bin/bash

# Copyright (C) 2019, Linagora, Ilyes Rebai
# Email: irebai@linagora.com


boost=false
spk=""
nj=12
wer=0.0
extract_oov=false
extract_wav_segments=false
output_tts=tmp

. ./path.sh
. ./utils/parse_options.sh


if [ $# != 3 ]; then
  echo "ERROR"
  echo "Usage: $0 [options] <corpus> <output-folder> <asr-decoder>"
  echo " local/data_prepAutomaticSeg.sh /media/nas/CORPUS_FINAL/Corpus_audio/Sami-corpus/l_allemagne ASR_OUTPUT/Sami-corpus ../stt-worker-standalone"
  exit 1;
fi


corpus=$1
output=$2
asr_online=$3


pwd=$(pwd)

if $extract_wav_segments; then
  mkdir -p $output_tts/wavs
  rm -f $output_tts/metadata.csv
fi

mkdir -p $output
rm -f $output/log.txt

# Check the OOV words and fix them before data preparation
if $extract_oov; then
  for wav in $(ls $corpus/*.wav); do
    name=$(basename $wav | sed 's:.wav$::g')
    text=$corpus/$name
    python3 local/parsetext.py --parse_only 1 $text "Nothing" >> $output/log.txt
  done
fi
#exit

for wav in $(ls $corpus/*.wav); do
  echo
  echo "-------------------------------------------"
  echo $wav
  # if [ $wav == /media/nas/CORPUS_FINAL/Corpus_audio/Corpus_FR/LIBRIVOX/librivox_fr_sami/bernard/alombredesjeunesfillesenfleurs/alombredesjeunesfillesenfleurs_1_01_proust_64kb.wav ];then
  #   continue
  # fi

  name=$(basename $wav | sed 's:.wav$::g')
  text=$corpus/$name

  if [ ! -f $text ]; then
    echo "ERROR: text file \"$name\" not found! Audio file will not processed!!!"
  else
    echo "Start processing the audio file \"$name\""
    mkdir -p $output/$name
    local/audio_segmentation_using_asr.sh --nj $nj --wer $wer --spk \"$spk\" --improve-annotation $boost --extract-wav-segments $extract_wav_segments \
                                          $wav $text $output/$name $asr_online || exit 1
    
    # if [ -f $output/$name/error.txt ]; then

    #   local/audio_segmentation_using_asr.sh --nj 8 --wer $wer --spk \"$spk\" --improve-annotation $boost --extract-wav-segments $extract_wav_segments \
    #                                       $wav $text $output/$name $asr_online || exit 1
    # fi
    # if [ -f $output/$name/error.txt ]; then
    #     local/audio_segmentation_using_asr.sh --nj 6 --wer $wer --spk \"$spk\" --improve-annotation $boost --extract-wav-segments $extract_wav_segments \
    #                                       $wav $text $output/$name $asr_online || exit 1
    # fi
    # if [ -f $output/$name/error.txt ]; then
    #   exit 1
    # fi

    # local/audio_segmentation_using_asr2.sh $text $wav $asr_online \
    #   $asr_online/ivector_extractor $asr_online/LM_gen/dict \
    #   /home/jlouradour/models/RecoFR/decoding_graph_fr-FR_Big_v2.2.0 \
    #   $output/$name \
    #   --g2p-model=$asr_online/LM_gen/g2p/model || exit 1

    if $extract_wav_segments; then
      if [ ! -z $output_tts ]; then
        mv $output/$name/data_tts/tmp/*.wav $output_tts/wavs
        cat $output/$name/data_tts/tmp/metadata.csv >> $output_tts/metadata.csv
      fi
    fi
  fi
done

echo "Data preparation is done successfully"
