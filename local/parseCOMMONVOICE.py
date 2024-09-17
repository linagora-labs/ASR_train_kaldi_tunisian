#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

import os
import re
import sys

_corrections_number_fr = [(re.compile(' %s ' % x[0], re.IGNORECASE), ' %s ' % x[1])
                  for x in [
                    ("pourcent","pour cent"),
                    ("zero","zéro"),
                    ("dix +sept","dix-sept"),
                    ("dix +huit","dix-huit"),
                    ("dix +neuf","dix-neuf"),
                    ("vingt +et +un","vingt-et-un"),
                    ("vingt +et +une","vingt-et-une"),
                    ("vingt +deux","vingt-deux"),
                    ("vingt +trois","vingt-trois"),
                    ("vingt +quatre","vingt-quatre"),
                    ("vingt +cinq","vingt-cinq"),
                    ("vingt +six","vingt-six"),
                    ("vingt +sept","vingt-sept"),
                    ("vingt +huit","vingt-huit"),
                    ("vingt +neuf","vingt-neuf"),
                    ("trente +et +un","trente-et-un"),
                    ("trente +et +une","trente-et-une"),
                    ("trente +deux","trente-deux"),
                    ("trente +trois","trente-trois"),
                    ("trente +quatre","trente-quatre"),
                    ("trente +cinq","trente-cinq"),
                    ("trente +six","trente-six"),
                    ("trente +sept","trente-sept"),
                    ("trente +huit","trente-huit"),
                    ("trente +neuf","trente-neuf"),
                    ("quarante +et +un","quarante-et-un"),
                    ("quarante +et +une","quarante-et-une"),
                    ("quarante +deux","quarante-deux"),
                    ("quarante +trois","quarante-trois"),
                    ("quarante +quatre","quarante-quatre"),
                    ("quarante +cinq","quarante-cinq"),
                    ("quarante +six","quarante-six"),
                    ("quarante +sept","quarante-sept"),
                    ("quarante +huit","quarante-huit"),
                    ("quarante +neuf","quarante-neuf"),
                    ("cinquante +et +un","cinquante-et-un"),
                    ("cinquante +et +une","cinquante-et-une"),
                    ("cinquante +deux","cinquante-deux"),
                    ("cinquante +trois","cinquante-trois"),
                    ("cinquante +quatr","cinquante-quatre"),
                    ("cinquante +cinq","cinquante-cinq"),
                    ("cinquante +six","cinquante-six"),
                    ("cinquante +sept","cinquante-sept"),
                    ("cinquante +huit","cinquante-huit"),
                    ("cinquante +neuf","cinquante-neuf"),
                    ("soixante +et +un","soixante-et-un"),
                    ("soixante +et +une","soixante-et-une"),
                    ("soixante +deux","soixante-deux"),
                    ("soixante +trois","soixante-trois"),
                    ("soixante +quatre","soixante-quatre"),
                    ("soixante +cinq","soixante-cinq"),
                    ("soixante +six","soixante-six"),
                    ("soixante +sept","soixante-sept"),
                    ("soixante +huit","soixante-huit"),
                    ("soixante +neuf","soixante-neuf"),
                    ("soixante +dix","soixante-dix"),
                    ("soixante +et +onze","soixante-et-onze"),
                    ("soixante +douze","soixante-douze"),
                    ("soixante +treize","soixante-treize"),
                    ("soixante +quatorze","soixante-quatorze"),
                    ("soixante +quinze","soixante-quinze"),
                    ("soixante +seize","soixante-seize"),
                    ("soixante +dix +sept","soixante-dix-sept"),
                    ("soixante +dix +huit","soixante-dix-huit"),
                    ("soixante +dix +neuf","soixante-dix-neuf"),
                    ("quatre +vingts","quatre-vingts"),
                    ("quatre +vingt +un","quatre-vingt-un"),
                    ("quatre +vingt +deux","quatre-vingt-deux"),
                    ("quatre +vingt +trois","quatre-vingt-trois"),
                    ("quatre +vingt +quatre","quatre-vingt-quatre"),
                    ("quatre +vingt +cinq","quatre-vingt-cinq"),
                    ("quatre +vingt +six","quatre-vingt-six"),
                    ("quatre +vingt +sept","quatre-vingt-sept"),
                    ("quatre +vingt +huit","quatre-vingt-huit"),
                    ("quatre +vingt +neuf","quatre-vingt-neuf"),
                    ("quatre +vingt +dix","quatre-vingt-dix"),
                    ("quatre +vingt +onze","quatre-vingt-onze"),
                    ("quatre +vingt +douze","quatre-vingt-douze"),
                    ("quatre +vingt +treize","quatre-vingt-treize"),
                    ("quatre +vingt +quatorze","quatre-vingt-quatorze"),
                    ("quatre +vingt +quinze","quatre-vingt-quinze"),
                    ("quatre +vingt +seize","quatre-vingt-seize"),
                    ("quatre +vingt +dix +sept","quatre-vingt-dix-sept"),
                    ("quatre +vingt +dix +huit","quatre-vingt-dix-huit"),
                    ("quatre +vingt +dix +neuf","quatre-vingt-dix-neuf")
                ]]


_corrections_regex_fr = [(re.compile(' %s ' % x[0], re.IGNORECASE), ' %s ' % x[1])
                  for x in [
                    ("nº","numéro"),
                    ("n°","numéro"),
                    ("mp3","m p 3"),
                    ("jus +qu'","jusqu'"),
                    ("pres +qu'","presqu'"),
                    ("lors +qu'","lorsqu'"),
                    ("quel +qu'","quelqu'"),
                    ("puis +qu'","puisqu'"),
                    ("aujour +d'","aujourd'"),
                    ("jusqu","jusqu'"),
                    ("presqu","presqu'"),
                    ("lorsqu","lorsqu'"),
                    ("quelqu","quelqu'"),
                    ("puisqu","puisqu'"),
                    ("aujourd","aujourd'"),
                    ("aujourd' +hui","aujourd'hui"),
                    ("quoiqu","quoiqu'"),
                    ("°", " degrés "),
                ]]


# Create and save tokenizer
punctuations_to_ignore_regex = '[\,\?\.\!]'
chars_to_ignore_regex = '[\;\:\"\“\%\”\�\…\·\ǃ\«\‹\»\›“\”\ʿ\ʾ\„\∞\|\;\:\*\—\–\─\―\_\/\:\ː\;\=\«\»\→]'

def collapse_whitespace(text):
    _whitespace_re = re.compile(r'\s+')
    return re.sub(_whitespace_re, ' ', text).strip()

def normalize_text(
    text,
    punctuation=False
    ):
    text = text.lower().strip()
    text = re.sub(" ", " ",text)
    text = re.sub("â","â",text)
    text = re.sub("à","à",text)
    text = re.sub("á","á",text)
    text = re.sub("ã","à",text)
    text = re.sub('ҫ','ç',text)
    text = re.sub("ê","ê",text)
    text = re.sub("é","é",text)
    text = re.sub("è","è",text)
    text = re.sub("ô","ô",text)
    text = re.sub("û","û",text)
    text = re.sub('ù','ù',text)
    text = re.sub("î","î",text)
    text = re.sub("œ","oe",text)
    text = re.sub("æ","ae",text)
    
    text = re.sub("’|´|′|ʼ|‘|ʻ|`", "'", text)
    text = re.sub("'+ ", " ", text)
    text = re.sub(" '+", " ", text)
    text = re.sub("'$", " ", text)
    text = re.sub("' ", " ", text)

    text = re.sub("−|‐", "-", text)
    text = re.sub(" -", "", text)
    text = re.sub("- ", "", text)
    text = re.sub("--+", " ", text)

    text = re.sub(chars_to_ignore_regex, ' ', text)
    if not punctuation:
        text = re.sub(punctuations_to_ignore_regex, ' ', text)


    for reg, replacement in _corrections_regex_fr:
        text = re.sub(reg, replacement, text)


    text = re.sub(' m\. ', ' monsieur ', text)
    text = re.sub(' mme\. ', ' madame ', text)
    text = re.sub(' mmes\. ', ' mesdames ', text)
    text = re.sub('m\^\{me\}', ' madame ', text)
    text = re.sub('%', ' pourcent ', text)
    text = re.sub(' km ', ' kilomètres ', text)
    text = re.sub('€', ' euro ', text)
    text = re.sub('\$',' dollar ', text)
    text = re.sub('dix nov', 'dix novembre', text)
    text = re.sub('dix déc', 'dix décembre', text)
    text = re.sub('dix fév', 'dix février', text)
    text = re.sub('nº', 'numéro', text)
    text = re.sub('n°', 'numéro', text)
    text = re.sub('onzeº', 'onze degrés', text)
    text = re.sub('α','alpha',text)
    text = re.sub('β','beta',text)
    text = re.sub('γ','gamma',text)
    text = re.sub(' ℰ ',' e ',text)
    text = re.sub(' ℕ ',' n ',text)
    text = re.sub(' ℤ ',' z ',text)
    text = re.sub(' ℝ ',' r ',text)
    text = re.sub('ε','epsilon',text)
    text = re.sub(' ω | Ω ',' oméga ',text)
    text = re.sub(' υ ',' Upsilon ',text)
    text = re.sub(' τ ',' tau ',text)
    text = re.sub('σ|Σ','sigma',text)
    text = re.sub(' π | Π ',' pi ',text)
    text = re.sub(' ν ',' nu ',text)
    text = re.sub(' ζ ',' zeta ',text)
    text = re.sub('δ|Δ|∆',' delta ',text)
    text = re.sub(' ∈ ',' appartient à ',text)
    text = re.sub(' ∅ ',' ',text)
    text = re.sub('☉',' ',text)
    text = re.sub(' ≥ ','supérieur ou égale à',text)
    text = re.sub(' ½ ', ' demi ', text)
    text = re.sub('&', ' et ', text)
    text = re.sub("aujourd' +hui", "aujourd'hui", text)
    text = re.sub(" h' aloutsisme "," haloutsisme ", text)
    text = re.sub(" h' mông ", " hmông ", text)

    for reg, replacement in _corrections_number_fr:
        text = re.sub(reg, replacement, text)

    text = collapse_whitespace(text)
    text = re.sub("'", "' ", text)
    return text

def generate_examples(filepath, path_to_clips):
    """Yields examples."""
    # data_fields =     ["client_id", "path", "sentence", "up_votes", "down_votes", "age", "gender", "accents", "locale", "segment"]
    # data_fields_old = ["client_id", "path", "sentence", "up_votes", "down_votes", "age", "gender", "accent", "locale", "segment"]
    # data_fields_csv = ["filename", "text", "up_votes", "down_votes", "age", "gender", "accent", "duration"]
    is_csv = filepath.endswith(".csv")
    sep = "," if is_csv else "\t"
    

    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
        headline = lines[0]

        column_names = headline.strip().split(sep)
        if "filename" in column_names and "path" not in column_names:
            column_names[column_names.index("filename")] = "path"
        if "accent" in column_names and "accents" not in column_names:
            column_names[column_names.index("accent")] = "accents"
        if "text" in column_names and "sentence" not in column_names:
            column_names[column_names.index("text")] = "sentence"

        assert "path" in column_names, f"No path or filename column found in {filepath}."
        assert "sentence" in column_names, f"No sentence or text column found in {filepath}."
        assert "gender" in column_names, f"No gender column found in {filepath}."
        # assert "client_id" in column_names, f"No client_id column found in {filepath}."
        must_create_client_id = "client_id" not in column_names
        if must_create_client_id:
            column_names.append("client_id")

        path_idx = column_names.index("path")

        checked_files = 0
        for id_, line in enumerate(lines[1:]):
            field_values = line.strip().split(sep)

            # if data is incomplete, fill with empty values
            if len(field_values) < len(column_names):
                field_values += (len(column_names) - len(column_names)) * [None]

            # set an id if not present
            if must_create_client_id:
                field_values.append(field_values[path_idx].replace("/","--"))

            # set absolute path for mp3 audio file
            field_values[path_idx] = os.path.join(path_to_clips, field_values[path_idx])

            if checked_files < 10:
                assert os.path.isfile(field_values[path_idx]), f"Audio file {field_values[path_idx]} does not exist."
                checked_files += 1

            yield {key: value for key, value in zip(column_names, field_values)}



if __name__ == '__main__':
    src=sys.argv[1]
    dest=sys.argv[2]
    split=sys.argv[3]

    vocab  = ['a','e','i','o','u','y','b','c','d','f','g','h','j','k','l','m','n','p','q','r','s','t','v','w','x','z']
    vocab += ['à','â','æ','ç','è','é','ê','ë','î','ï','ô','œ','ù','û','ü','ÿ']
    vocab += [' ',"'",'-']
    
    clips_path = os.path.join(src, 'clips')
    if not os.path.isdir(os.path.join(src, 'clips')):
        clips_path = src
    assert os.path.isdir(clips_path), f"Audio files not found at {os.path.join(src, 'clips')} nor {clips_path}"

    file_path = os.path.join(src, split+'.tsv')
    if not os.path.isfile(file_path):
        file_path = os.path.join(src, split+'.csv')
    assert os.path.isfile(file_path), f"TSV/CSV files not found at {file_path}/.tsv"

    rows = generate_examples(file_path, clips_path)

    #Save the data
    # Output File needed for kaldi input
    utt2spk_file = open(dest + '/utt2spk', 'w')
    text_file = open(dest + '/text', 'w')
    #rawtext_file = open(dest + '/text_raw', 'w')
    wav_scp = open(dest + '/wav.scp', 'w')
    spk2gender= open(dest + '/spk2gender', 'w')

    speakers=[]
    uniq_spks=[]
    for row in rows:
        file_id = os.path.basename(row['path']).split('.')[0]
        spk_id = row['client_id']
        utt_id = spk_id +'_'+ file_id
        if spk_id not in uniq_spks:
            uniq_spks.append(spk_id)
            gender = row['gender'][0] if row['gender'] != '' else 'm'
            if row['gender'] == "other":
                gender = "m"
            if gender not in ["m", "f"]:
                raise RuntimeError("Unexpected gender: "+row['gender'])
            speakers.append({
                'id': spk_id,
                'gender': gender
            })

        rawtext = row["sentence"]
        text = collapse_whitespace(rawtext)
        vocab_regex = f"[{re.escape(''.join(vocab))}]"
        if True: #len(re.sub(vocab_regex, '', text.strip())) == 0 :
            utt2spk_file.write(utt_id+" "+spk_id+"\n")
            text_file.write(utt_id+" "+text+"\n")
            #rawtext_file.write(utt_id+" "+rawtext+"\n")
            wav_scp.write(utt_id+" sox "+ row['path'] +" -t wav -r 16k -b 16 -c 1 - |\n")

    for speaker in speakers:
        spk2gender.write(speaker['id']+" "+speaker['gender']+"\n")

    utt2spk_file.close()
    text_file.close()
    wav_scp.close()
    spk2gender.close()
