#!/bin/bash

if [ $# -ne 4 ] && [ $# -ne 5 ]; then
  echo "Usage: $0 <output_dir> <text> <arpa-path> <am-path> [<new_lexicon>]"
  echo "e.g.: $0 LanguageModel normalized_text_file ~/models/RecoFR/linSTT_ARPA_fr-FR_Big ~/models/RecoFR/linSTT_AM_fr-FR_v2.2.0"
  exit 1
fi

. ./path.sh || exit 1

output_dir=$1
text=$2
arpa_path=$3
am_path=$4
new_lexicon=$5

. ./utils/parse_options.sh || exit 1

# Acoustic model lexicon
g2p_model=$am_path"/LM_gen/g2p/model"
lexicon=$am_path"/LM_gen/dict/lexicon.txt"

for x in $am_path $g2p_model $lexicon $arpa_path $new_lexicon $text;do
  if [ ! -e $x ];then
    echo "Could not find "$x
    exit 1
  fi
done

# Output folder content
dict=$output_dir/dict
lang=$output_dir/lang
lm=$output_dir/lm
oov=$output_dir/oov
if [ "$new_lexicon" ];then
  newoov=$output_dir/oovplus
else
  newoov=$oov
fi
mkdir -p $dict $lang $lm $oov

if [ ! -f $oov/oov_lexicon ]; then
  #Prepare full vocabulary
  # - add a space to the end
  # - remove empty lines (lines with only spaces)
  # - remove double spaces
  cat $text  | sed "s:$: :g" | sed '/^ *$/d' | \
    sed -e 's:<[^<]*>::g' -e 's:  : :g' | \
    tr -s '[[:space:]]' '\n' | sort | uniq  > $oov/full_vocab
  #Searching for OOV words
  awk 'NR==FNR{words[$1]; next;} !($1 in words)' $lexicon $oov/full_vocab | egrep -v '<.?s>' > $oov/oov_vocab
  #Preparing pronunciations for OOV words
  python2 /opt/kaldi/tools/phonetisaurus-g2p/src/scripts/phonetisaurus-apply --model $g2p_model --word_list $oov/oov_vocab > $oov/oov_lexicon
fi

############ Train the new language model (ARPA)
# Here, we will add the vocabulary directly to the model.
# However, the good practice is to use a text with the domain-specific vocabulary to have the perfect word sequence estimation

# Lexicon
if [ ! -f $newoov/oov_lexicon ];then
  mkdir -p $newoov
  cp $new_lexicon $newoov/full_vocab || exit 1
  awk 'NR==FNR{words[$1]; next;} !($1 in words)' $lexicon $newoov/full_vocab | egrep -v '<.?s>' > $newoov/oov_vocab || exit 1
  python2 /opt/kaldi/tools/phonetisaurus-g2p/src/scripts/phonetisaurus-apply --model $g2p_model --word_list $newoov/oov_vocab > $newoov/oov_lexicon
fi

# Generate new lexicon with the new words oov_vocab
if [ ! -f $dict/lexicon.txt ];then 
  cp -r $am_path/LM_gen/dict/* $dict && rm $dict/lexiconp.txt || exit 1
fi
if [ ! -f $dict/.done ];then
  cat $oov/oov_lexicon $newoov/oov_lexicon $lexicon | sort | uniq > $dict/lexicon.txt || exit 1
  touch $dict/.done
fi

# Generate L.fst
if [ ! -f $lang/L.fst ];then
  tmpdir=/tmp/lang
  utils/prepare_lang.sh $dict "<unk>" $tmpdir $lang || exit 1
  rm -R $tmpdir
fi

if [ ! -f $lm/arpa-3gram.gz ];then
  ngram-count -order 3 -text $text  -prune 0.000000008 -limit-vocab -wbdiscount -interpolate -lm $lm/arpa-3gram.gz || exit 1
fi

# Mix the two ARPAs
if [ ! -f $lm/arpa-mixed.gz ];then
  ngram -order 3 -lm $arpa_path -mix-lm $lm/arpa-3gram.gz -lambda 0.3 -write-lm $lm/arpa-mixed.gz || exit 1
fi

# Generate the grammar graph (G.fst)
if [ ! -f $lang/G.fst ];then
  # Note: this yields a lot of warnings
  gunzip -c $lm/arpa-mixed.gz | arpa2fst --disambig-symbol=#0 \
      --read-symbol-table=$lang/words.txt - $lang/G.fst || exit 1
fi

# Compile HCLG Decoding Graph
if [ ! -f $lm/graph ];then
  utils/mkgraph.sh --self-loop-scale 1.0 $lang $am_path $lm/graph || exit 1
fi
