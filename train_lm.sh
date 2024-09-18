#!/usr/bin/env bash

# Copyright © 2024  LINAGORA
# Email: hnaouara@linagora.com
# License: AGPL v3

# Description: This script automatically generates a language model (LM) based on your inputs.

. ./path.sh

# Set up paths (replace 'sys' with the actual repository path)
sys= # Path to the repository
data_dir="$sys/ASR_train_kaldi_tunisian/data"
lang_dir="$data_dir/lang"
dict_dir="$data_dir/dict"
db="$data_dir/db"
local_dir="$sys/ASR_train_kaldi_tunisian/local"

# Define variables with default values
input_text_file=
ignore_ids=false
arpa_basemodel=
language="ar"
order_lm=4
ngram_count="ngram-count"
arpa2fst="arpa2fst"

display_help() {
    echo "Usage: $0 [OPTIONS]"
    echo "  --input_text_file    Path to the input text file"
    echo "  --ignore_ids         Optional flag to ignore IDs in the input text (use this if using a text file from a Kaldi dataset)"
    echo "  --arpa_basemodel     Optional path to the ARPA language model"
    echo "  --language           Optional flag to specify the language (default: ar)"
    echo "  --order_lm           Optional flag to specify the LM order (default: 4)"
    echo "  -h, --help           Show this help message"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --input_text_file)
            input_text_file="$2"
            shift 2
            ;;
        --ignore_ids)
            ignore_ids=true
            shift
            ;;
        --arpa_basemodel)
            arpa_basemodel="$2"
            shift 2
            ;;
        --language)
            language="$2"
            shift 2
            ;;
        --order_lm)
            order_lm="$2"
            shift 2
            ;;
        -h|--help)
            display_help
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

echo "ignor_ids = $ignore_ids"

set -euo pipefail

# Check if the necessary tools are available
command -v "$ngram_count" >/dev/null 2>&1 || { echo "Error: $ngram_count is not installed." >&2; exit 1; }
command -v "$arpa2fst" >/dev/null 2>&1 || { echo "Error: $arpa2fst is not installed." >&2; exit 1; }

# Create directories if they don't exist
mkdir -p "$db" "$dict_dir" "$lang_dir"

# Process input text
if [ "$ignore_ids" == true ]; then 
    cut -d' ' -f2- "$input_text_file" > "$db/extra.txt" || exit 1
else
    cp "$input_text_file" "$db/extra.txt" || exit 1
fi

# Prepare the lexicon and language model
if [ ! -f "$dict_dir/.done_dict" ]; then
    sort -u "$db/extra.txt" > "$db/extra_undup.txt"
    python3 "$local_dir/prepare_lexicon.py" "$db/extra_undup.txt" "$dict_dir"
    cut -d' ' -f2- "$dict_dir/lexicon.txt" | sed 's/SIL//g' | tr ' ' '\n' | sort -u | sed '/^$/d' > "$dict_dir/nonsilence_phones.txt"
    sed -i '1i<unk> SIL' "$dict_dir/lexicon.txt"
    echo '<sil> SIL' >> "$dict_dir/lexicon.txt"
    echo 'SIL' > "$dict_dir/optional_silence.txt"
    echo 'SIL' > "$dict_dir/silence_phones.txt"
    touch "$dict_dir/extra_questions.txt"
    echo "Dictionary prepared successfully."
    touch "$dict_dir/.done_dict"
fi

# Generate language model
if [ ! -f "$data_dir/extra.arpa" ]; then
    echo "Generating extra.arpa"
    $ngram_count -wbdiscount -order "$order_lm" -text "$db/extra_undup.txt" -interpolate -lm "$data_dir/extra.arpa"
fi

if [ -n "$arpa_basemodel" ]; then
    echo "Base model detected. Mixing and pruning."
    
    echo "Generating $language-mix.arpa"
    ngram -order "$order_lm" -lm "$arpa_basemodel" -mix-lm "$data_dir/extra.arpa" -lambda 0.3 -write-lm "$data_dir/$language-mix.arpa"
    
    echo "Generating $language-mixp.arpa"
    ngram -order "$order_lm" -lm "$data_dir/$language-mix.arpa" -prune 1e-9 -write-lm "$data_dir/$language-mixp.arpa"
    
    echo "Removing $language-mix.arpa & extra.arpa"
    rm -f "$data_dir/$language-mix.arpa" "$data_dir/extra.arpa"
else
    echo "No base model provided. Using extra.arpa as the final language model."
fi

# Prepare language-related files
if [ ! -f "$lang_dir/L.fst" ]; then
    utils/prepare_lang.sh "$dict_dir" "<unk>" "$data_dir/lang_local" "$lang_dir"
    rm -r "$data_dir/lang_local"
fi

if [ ! -f "$lang_dir/G.fst" ]; then
    if [ -f "$data_dir/$language-mixp.arpa" ]; then
        arpamodel="$data_dir/$language-mixp.arpa"
    elif [ -f "$data_dir/extra.arpa" ]; then
        arpamodel="$data_dir/extra.arpa"
    else
        echo "Error: No ARPA model found." >&2
        exit 1
    fi
    
    $arpa2fst --disambig-symbol="#0" --read-symbol-table="$lang_dir/words.txt" "$arpamodel" "$lang_dir/G.fst"
fi
