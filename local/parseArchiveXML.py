#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (C) 2020, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

import xmltodict, json
import re
import sys
import os
from num2words import num2words

_corrections_caracteres_speciaux_fr = [(re.compile('%s' % x[0], re.IGNORECASE), '%s' % x[1])
                  for x in [
                    ("â","â"),
                    ("à","à"),
                    ("á","á"),
                    ("ã","à"),
                    ("ê","ê"),
                    ("é","é"),
                    ("è","è"),
                    ("ô","ô"),
                    ("û","û"),
                    ("î","î"),
                    ("Ã","à"),
                    ('À','à'),
                    ('É','é'),
                    ('È','è'),
                    ('Â','â'),
                    ('Ê','ê'),
                    ('Ç','ç'),
                    ('Ù','ù'),
                    ('Û','û'),
                    ('Î','î'),
                    ("œ","oe"),
                    ("æ","ae")
                ]]

def collapse_whitespace(text):
    _whitespace_re = re.compile(r'\s+')
    return re.sub(_whitespace_re, ' ', text).strip()

def text_parser(text):
    text = text.lower()
    text = ' '+text+' '

    text = collapse_whitespace(text)
    for reg, replacement in _corrections_caracteres_speciaux_fr:
        text = re.sub(reg, replacement, text)
    

    text = re.sub('\[[^\[]*:([^\[]*):[^\[]*\]',r' <\1> ',text) # replace non-speech marks in ESLO-orleans
    text = re.sub('\(rires?[^\(]*\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(bruits?[^\(]*\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\([^\(]*pause\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\([^\(]*tousse\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(locuteur très ému\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(inspiration\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(souffle\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(problème d\'enregistrement[^\(]*\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(murmure\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(incompréhensible\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(toussotements?\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(hésitation?\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(grincement de porte?\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(l\'enquêtrice[^\(]*\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(toux\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(éternuement\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\([^\(]*inaudible\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\([^\(]*rit\)',' <noise> ',text) # replace non-speech marks in PFC
    text = re.sub('\(xx+\)',' <unk> ',text) # replace non-speech marks in PFC
    text = re.sub('\(davayet\)',' <unk> ',text) # replace non-speech marks in PFC
#
    return text

if __name__ == '__main__':
    xmlPath=sys.argv[1]
    wavPath=sys.argv[2]
    outdir=sys.argv[3]
    print(xmlPath)
    
    basename=os.path.basename(xmlPath.split('.')[0])
    basename=basename.lower()
    
    changeSpk=False
    if len(sys.argv) == 5:
        changeSpk=True
        cspkId = basename[0:len(basename)-2]
        cspkGender = cspkId[-1]

    with open(xmlPath) as f:
        file = f.readlines()
    file = ' '.join(file)
    dict = xmltodict.parse(file)


    # prepare the list of speakers
    alldata=[]
    

    if '@xml:lang' in dict['TEXT'] and dict['TEXT']['@xml:lang'].lower() != "fr":
        print('"@xml:lang" is not fr!!')
    else:
        if "S" in dict["TEXT"] and dict["TEXT"]["S"] is not None:
            segments = dict["TEXT"]["S"]
            for seg in segments:
                id=None
                spk=None
                sTime=None
                eTime=None
                text=None
                if '@id' in seg and seg['@id'] != "":
                    id=seg['@id'].lower().encode('utf-8')
                if '@who' in seg and seg['@who'] != "":
                    spk=seg['@who'].encode('utf-8')
                    spk=re.sub(' ','',spk)
                    spk=spk+'_'+basename
                if 'AUDIO' in seg and '@start' in seg['AUDIO'] and '@end' in seg['AUDIO']:
                    sTime = seg['AUDIO']['@start'].encode('utf-8')
                    eTime = seg['AUDIO']['@end'].encode('utf-8')
                if 'FORM' in seg:
                    if '#text' in seg['FORM']:
                        text = seg['FORM']['#text'].lower().encode('utf-8')
                    else:
                        text = seg['FORM'].lower().encode('utf-8')
                    text = text_parser(text)
                if id is not None and spk is not None and sTime is not None and eTime is not None and text is not None:
                    seg_id = spk + '_' + str(basename) + '_' + id
                    current = {
                        "id":seg_id,
                        "spkId":spk,
                        "text":text,
                        "sTime":sTime,
                        "eTime":eTime
                    }
                    alldata.append(current)

                else:
                    if spk is None:
                        print('Speaker indentifier is missing!!')
                    else:
                        print('One of the parameters is missing!!')

        else:
            print('No segment is found!!')

    #Save the data
    # Output File needed for kaldi input
    segments_file = open(outdir + '/segments', 'a')
    utt2spk_file = open(outdir + '/utt2spk', 'a')
    text_file = open(outdir + '/text', 'a')
    wav_scp = open(outdir + '/wav.scp', 'a')
    
    if len(alldata) > 0:
        for data in alldata:
            segments_file.write(data["id"]+" "+basename+" "+data["sTime"]+" "+data["eTime"]+"\n")
            utt2spk_file.write(data["id"]+" "+data["spkId"]+"\n")
            text_file.write(data["id"]+" "+data["text"]+"\n")
        wav_scp.write(basename+" sox "+ wavPath +" -t wav -r 16k -b 16 -c 1 - |\n")

    segments_file.close()
    utt2spk_file.close()
    text_file.close()
    wav_scp.close()