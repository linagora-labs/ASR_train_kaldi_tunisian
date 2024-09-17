#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2021, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

import os
import re
import sys


# Create and save tokenizer
punctuations_to_ignore_regex = '[\,\?\.\!]'
chars_to_ignore_regex = '[\;\:\"\“\%\”\�\…\·\ǃ\«\‹\»\›“\”\ʿ\ʾ\„\∞\|\;\:\*\—\–\─\―\_\/\:\ː\;\=\«\»\→]'


def collapse_whitespace(text):
    _whitespace_re = re.compile(r'\s+')
    return re.sub(_whitespace_re, ' ', text).strip()


def parse_text(text):
    text = text.lower().strip()
    text = re.sub("’|´|′|ʼ|‘|ʻ|`", "'", text)
    text = re.sub(chars_to_ignore_regex, ' ', text)
    text = re.sub(punctuations_to_ignore_regex, ' ', text)
    text = ' ' + text + ' '
    text = re.sub(' 7 ',' sept ',text)
    text = re.sub(' 8 ',' huit ',text)
    text = re.sub(' 9 ',' neuf ',text)
    text = re.sub(' 11 ',' onze ',text)
    text = re.sub(' 13 ',' treize ',text)
    text = re.sub(' 18 ',' dix-huit ',text)
    text = re.sub(' 20 ',' vingt ',text)
    text = re.sub(' 44 ',' quarante-quatre ',text)
    text = re.sub(' 1898 ',' mille huit cent quatre-vingt-dix-huit ',text)
    text = re.sub(' 1911 ',' mille neuf cent onze ',text)
    # put space after '
    text = re.sub(r"\'","\' ",text)
    text = collapse_whitespace(text)
    return text


if __name__ == '__main__':
    src=sys.argv[1]
    dest=sys.argv[2]
    txt=sys.argv[3]
    spk=sys.argv[4]


    #Save the data
    # Output File needed for kaldi input
    utt2spk_file = open(dest + '/utt2spk', 'a')
    text_file = open(dest + '/text', 'a')
    rawtext_file = open(dest + '/text_raw', 'a')
    wav_scp = open(dest + '/wav.scp', 'a')


    for x in open(txt, encoding='utf-8'):
        id=x.split(' ')[0]
        text=x.split(' ')[1:]
        rawtext = ' '.join(text).strip()
        text=parse_text(rawtext)
        utt_id=spk + "_" + id
        wav_path=os.path.join(src, 'wav', id+'.wav')

        if os.path.exists(wav_path):
            utt2spk_file.write(utt_id+" "+spk+"\n")
            text_file.write(utt_id+" "+text+"\n")
            rawtext_file.write(utt_id+" "+rawtext+"\n")
            wav_scp.write(utt_id+" sox "+ wav_path +" -t wav -r 16k -b 16 -c 1 - |\n")


    utt2spk_file.close()
    text_file.close()
    rawtext_file.close()
    wav_scp.close()
