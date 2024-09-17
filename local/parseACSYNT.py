#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###########################################
# Copyright 2017 Sonia BADENE @Linagora
# This script normalize the text according
# to the ACSYNT's anotation agreement
###########################################

from textgrid import TextGrid
from sys import argv
from num2words import num2words
import re
import os.path
from xml.sax.saxutils import unescape

def collapse_whitespace(text):
    _whitespace_re = re.compile(r'[^\S\r\n]+') # All whitespace except new line
    return re.sub(_whitespace_re, ' ', text).strip()


def transform_text(text):
    text=text.lower()
    # Delete chevauchements
    text=re.sub(r"< e:"," ",text)
    text=re.sub(r"< l:"," ",text)
    text=re.sub(r"<e:"," ",text)
    text=re.sub(r"<l:"," ",text)
    text=re.sub(r"e:"," ",text)
    text=re.sub(r"l:"," ",text)
    text=re.sub(r"e :"," ",text)
    text=re.sub(r"l :"," ",text)
    text=re.sub(r" e "," ",text)
    text=re.sub(r" l "," ",text)
    #if len(re.findall(r"\<.+\>", text)) > 0:
    text=re.sub(r"\<"," ",text)
    text=re.sub(r"\>"," ",text)
    # supprimer les parenthèses
    text=re.sub(r"[\(,\)]", " ",text)
    # Replace syllabes inaudibles xx to <noise>
    pattern = re.compile('^[x]+$')
    text=' '.join([w if not pattern.match(w) else '<noise>' for w in text.split(' ')])
    # Replace [ noise noise ] to <noise>
    text=re.sub(r"\[.+?\]","<noise> ",text)
    # Delete the only bruit sourd] that remains
    text=re.sub(r"bruit sourd\]"," ",text)
    text=re.sub(r"rires\]","",text)
    text=re.sub(r"aboiements\]"," ",text)
    text=re.sub(r"\]"," ",text)
    # Delete dots
    text=re.sub(r"\."," ",text)
    # Delete \ \\\ \\\\
    text=re.sub(r"\\+"," ",text)
    # put space after '
    text=re.sub(r"\'","\' ",text)
    # Delete les noms propres bruités, Noisy nouns cvcvcv
    pattern = re.compile('^[cv]+$')
    text=' '.join([w if not pattern.match(w) else '<noise>' for w in text.split(' ')])
    # Delete !
    text=re.sub(r"\!"," ",text)
    # Delete the investigator (L'enquêteur) indicated by  E
    text=re.sub(r" e "," ",text)
    # Delete the speaker(locuteur)indicated by L
    text=re.sub(r" l "," ",text)
    # accents
    text=re.sub(r"a\^","â",text)
    text=re.sub(r"u\^","û",text)
    text=re.sub(r"e\^","ê",text)
    text=re.sub(r"c\,","ç",text)
    text=re.sub(r"o\^","ô",text)
    text=re.sub(r"u\`","ù",text)
    text=re.sub(r"i\^","î",text)
    # Delete ?
    text=re.sub(r"\?"," ",text)
    # Delete `
    text=re.sub(r"\`"," ",text)
    # Delete _
    text=re.sub(r"\_"," ",text)
    # replace n succesive spaces with one space
    text=re.sub(r"\s{2,}"," ",text)
    # delete space in the end of utterance
    text=re.sub(r"[\s]+$","",text)
    # num to word
    num_list = re.findall(" \d+| \d+$", text)
    # fix space
    if len(num_list) > 0:
        for num in num_list:
            num_in_word = num2words(int(num), lang='fr')
            text = text.replace(str(num), " " + str(num_in_word) + " ")
    text=collapse_whitespace(re.sub("<noise>", "", text))
    return text.strip()

if __name__=="__main__":
    # Input : file.TEXTGRID and we assume that file.wav are in the same directory
    TEXTGRID_file=argv[1]
    dirname=os.path.dirname(TEXTGRID_file)
    basename=os.path.basename(TEXTGRID_file.split('.')[0])
    WAV_file=dirname+'/'+basename+'.wav'
    # Input : text
    txt_file=argv[2]
    # Output directory
    outdir=argv[3]
    # Output File needed for kaldi input
    segments_file = open(outdir + '/segments', 'a')
    utt2spk_file = open(outdir + '/utt2spk', 'a')
    text_file = open(outdir + '/text', 'a')
    rawtext_file = open(outdir + '/text_raw', 'a')
    wav_scp = open(outdir + '/wav.scp', 'a')

    # Parse TEXTGRID FILE
    TEXTGRID_io=open(TEXTGRID_file,'r')
    TEXTGRID_obj=TextGrid(TEXTGRID_io.read().replace('"""','"'))
    Tier=TEXTGRID_obj.tiers[0]
    # Read text file
    with open(txt_file) as f:
        lines = f.readlines()
    lines = [line for line in lines if line.strip() != '']
    # Create the data
    texts = []
    starts = []
    ends = []
    i=0
    err=0
    rej_text = []
    rej_text_ = []
    rej_start = []
    rej_end = []
    for deb_seg,end_seg,text_seg in Tier.simple_transcript:
        text_seg = text_seg.strip()
        if text_seg == '':
            continue
        text_ = lines[i].strip() if i < len(lines) else ''

#        print(text_seg[:20])
#        print(text_[:20])

        if text_seg[:5] == text_[:5]:
            texts.append(text_)
            starts.append(deb_seg)
            ends.append(end_seg)
        elif text_seg[1:10] == text_[1:10]:
            texts.append(text_)
            starts.append(deb_seg)
            ends.append(end_seg)
        elif re.sub(' *: *',':',text_seg)[:5] == re.sub(' *: *',':',text_)[:5]:
# text_seg.replace(': ',':')[:5] == text_.replace(': ',':')[:5] or text_seg.replace(' *: *',':')[:5] == text_.replace(' *: *',':')[:5]:
            texts.append(text_)
            starts.append(deb_seg)
            ends.append(end_seg)
        else:
            rej_text.append(text_seg)
            rej_text_.append(text_)
            rej_start.append(deb_seg)
            rej_end.append(end_seg)
#            print(text_seg[:20])
#            print(text_[:20])
            err += 1
        i += 1

    if err == 1 or err == 2:
#        print([text[:10] for text in rej_text])
#        print([text[:10] for text in rej_text_])
        for deb_seg, end_seg, text_ in zip(rej_start, rej_end, rej_text_):
            texts.append(text_)
            starts.append(deb_seg)
            ends.append(end_seg)
        err = 0

    if err > 4 and len(texts) > 0:
        del texts[-1]
        del starts[-1]
        del ends[-1]

    if err > 0 and len(texts)>0:
        print(TEXTGRID_file)
        print("number of errors: ",err)

    # Get only first Imte
    count=0
    Spk_that_contribute_to_meeting=[]
    spkr_id=1
    for deb_seg,end_seg,text in zip(starts,ends,texts):
        seg_id=str(basename) + '_spk-%03d_seg-%05d' % (int(count), int(count))
        split_spkr_text=text.split(':')
        if len(split_spkr_text)>1 and len(split_spkr_text[0])==1:
            spk=split_spkr_text[0]
            text=' '.join([w for w in split_spkr_text[1:]])
        else:
            spk="x"
        #print(basename,len(split_spkr_text),len(split_spkr_text[0]),text)
        rawtext = text.strip()
        if rawtext.startswith("L : ") or rawtext.startswith("E : "):
            rawtext = rawtext[4:]
        text=transform_text(text)
        if text == '':
            count=count+1
            continue
        #text=transform_text(text)
        #split_spkr_text=text.split(':')
        if len(split_spkr_text)>=1:
            if not split_spkr_text[0] in Spk_that_contribute_to_meeting:
                Spk_that_contribute_to_meeting.append(split_spkr_text[0])
            spkr=Spk_that_contribute_to_meeting.index(split_spkr_text[0])+1
            spkr_id=str(basename)+'_spk-%03d' % int(spkr)
            #text=split_spkr_text[1]
            seg_id=str(basename) + '_spk-%03d_seg-%05d' % (int(spkr), int(count))
        #print(split_spkr_text)
        segments_file.write(seg_id+" "+basename+" "+str(round(float(deb_seg),3))+" "+str(round(float(end_seg),3))+"\n")
        rawtext_file.write(seg_id+" "+rawtext+"\n")
        text_file.write(seg_id+" "+text+"\n")
        utt2spk_file.write(seg_id+" "+str(spkr_id)+"\n")
        count=count+1
    wav_scp.write(basename+" sox "+WAV_file+" -t wav -r 16000 -c 1 - |\n")
    segments_file.close()
    utt2spk_file.close()
    text_file.close()
    rawtext_file.close()
    wav_scp.close()
