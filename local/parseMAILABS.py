#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

# A text normalization for M-AILABS and for any text

import re
import os
from glob import glob
from num2words import num2words
import sys


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

_chiffre_romain_fr_in=['ii','iii','iv','vii','viii','ix','xi','xii','xiii','xiv','xv','xvi','xvii','xviii','xix','xx']
_chiffre_romain_fr_out=['deux','trois','quatre','sept','huit','neuf','onze','douze','treize','quatorze','quinze','seize','dix-sept','dix-huit','dix-neuf','vingt']

_chiffre_ordinaux_fr_in=['1ère','1er','1e','1re','ixième','19ème', 'xxème', 'xiième', '16e', '2e', '3e', '8e', '15e', '53e', 'xviie', 'xiiie']
_chiffre_ordinaux_fr_out=['première','premier','premier','première','neuvième','dix-neuvième', 'vingtième', 'douzième', 'seizième', 'deuxième', 'troisième', 'huitième', 'quinzième', 'cinquante troisième', 'dix-septième', 'treizième']

def collapse_whitespace(text):
    _whitespace_re = re.compile(r'\s+')
    return re.sub(_whitespace_re, ' ', text).strip()

def text_parser(text):
    text = text.lower()
    text = ' '+text+' '
    
    text = collapse_whitespace(text)
    for reg, replacement in _corrections_caracteres_speciaux_fr:
        text = re.sub(reg, replacement, text)

    #test=0
    #romains=re.findall("\d+,\d+|\d+\.\d+",text)
    #for chiffre in romains:
    #    test=1
    #    print('1:',chiffre)

    text=re.sub(' 3,129',' 3129 ',text)
    text=re.sub(' 186o',' 1860 ', text)
    text=re.sub('1802-1804',' 18 100 2 18 100 4 ',text)
    text=re.sub(' 1866-67',' 1866 67 ',text)
    numbers=re.findall("\d+,000",text)
    for n in numbers:
        text = re.sub(n,re.sub(",","",n), text)


    # Abbréviations
    text = re.sub(" m\. "," monsieur ",text)
    text = re.sub(" mme\.? ", " madame ",text)
    text = re.sub(" mlle\.? ", " mademoiselle ",text)


    text = re.sub("’","'", text)
    text = re.sub("‘","'", text)
    text = re.sub("'","' ", text)
    text = re.sub('"',' " ', text)
    text = re.sub("' '", "''", text)
    text = re.sub(":", " : ", text)
    text = re.sub(";", " ; ", text)
    text = re.sub(',|¸',',', text)
    text = re.sub(", ", " , ", text)
    text = re.sub("\!", " ! ", text)
    text = re.sub("\?", " ? ", text)
    text = re.sub("^ *-+", "", text)
    text = re.sub("\^+","", text)
    text = re.sub(" +(- +)+", " ", text)
    text = re.sub("- ", "-", text)
    text = re.sub("([a-zàâäçèéêëîïôùûü]+)- +", r"\1-", text)
    text = re.sub(" -([a-zàâäçèéêëîïôùûü]+)", r"-\1", text)
    text = re.sub("([,;:\!\?\.]) -([a-zàâäçèéêëîïôùûü]+)", r"\1 \2", text)
    text = re.sub("([a-zàâäçèéêëîïôùûü]{3,})' ", r"\1 ", text)
    text = re.sub("([a-zàâäçèéêëîïôùûü]{2,})' *[,;:\!\?\.]", r"\1 ", text)
    text = re.sub('\.{2,}',' ', text)
    text = re.sub('\. *$',' . ', text)
    text = re.sub('(\d)\. ',r'\1 . ', text)
    
    #text = re.sub('\([^\(]*\)',' ', text)
    #text = re.sub('\[[^\[]*\]',' ', text)
    #text = re.sub('\{[^\{]*\}',' ', text)
    #text = re.sub('\([^\}]*\}',' ', text)

    text=re.sub('\{',' { ',text)
    text=re.sub('\}',' } ',text)
    text=re.sub('\(',' ( ',text)
    text=re.sub('\)',' ) ',text)
    text=re.sub('\[',' [ ',text)
    text=re.sub('\]',' ] ',text)

    text = re.sub(" '", " ", text)
    text = re.sub('--+',' ', text)
    text = re.sub('_',' ', text)
    text = re.sub('–',' ', text)
    text = re.sub('—+',' ', text)
    text = re.sub('…',' ', text)
    text = re.sub('\*+', ' ', text)
    text = re.sub('«',' ', text)
    text = re.sub('»',' ', text)
    text = re.sub('“',' ', text)
    text = re.sub('”',' ', text)
    text = re.sub('/',' ', text)
    text = re.sub("&","et", text)
    text = re.sub('#+',' ', text)
    text = re.sub('%', ' pour cent ', text)
    text = re.sub('€', ' euro ', text)
    text = re.sub('\$', ' dollar ', text)
    text = re.sub(' 00 ', ' 0 0 ', text)
    text = re.sub(' 0(\d) ',r' 0 \1 ', text)
    text = re.sub(" "," ",text)
    text = re.sub(' ', '  ',text)
    text = ' '+text+' '

    for reg, replacement in _corrections_regex_fr:
        text = re.sub(reg, replacement, text)

    text=re.sub(" henri +iv "," henri quatre ",text)
    text=re.sub(" paul +vi "," paul six ",text)
    text=re.sub(" gustave +vi "," gustave six ",text)
    text=re.sub(" abdellah +ii ", " abdellah deux ",text)
    text=re.sub(" jean-paul +ii ", " jean-paul deux ",text)
    text=re.sub(" pierre +ii ", " pierre deux ",text)
    text=re.sub(" henri +ii ", " henri deux ",text)
    text=re.sub(" paris +ii ", " paris deux ",text)
    text=re.sub(" louis +ii ", " louis deux ",text)
    text=re.sub(" charles +x ", " charles cinq ",text)
    text=re.sub(" mahomet +ii ", " mahomet deux ",text)
    text=re.sub(" catherine +ii ", " catherine deux ",text)
    text=re.sub(" napoléon +ii ", " napoléon deux ",text)
    text=re.sub(" article +ii", " article deux ",text)

    #text=re.sub(" ii ", " il ", text)
    #text=re.sub('(\d+)\.(\d{1,2})',r'\1 virgule \2',text)

    _corrections=[]
    ordinaux=re.findall("[^ ]*ème|\d+ère|\d+re|\d+er?| [xiv]{2,}e ",text)
    for chiffre in ordinaux:
        chiffre = chiffre.strip()
        romain = chiffre.split('ème')[0]
        romain = re.sub('[^xievr\d]',' ',romain)
        if ' ' not in romain and romain != "vie" and romain != "vive":
            print('2:',chiffre, chiffre in _chiffre_ordinaux_fr_in)
        if chiffre in _chiffre_ordinaux_fr_in:
            _corrections.append((' '+chiffre+' ',' '+_chiffre_ordinaux_fr_out[_chiffre_ordinaux_fr_in.index(chiffre)]+' '))

    romains=re.findall(" [ixv]{2,} ",text)
    for chiffre in romains:
        chiffre = chiffre.strip()
        if chiffre != "vi":
            if chiffre in _chiffre_romain_fr_in:
                _corrections.append((' '+chiffre+' ',' '+_chiffre_romain_fr_out[_chiffre_romain_fr_in.index(chiffre)]+' '))
        #else:
        #print(text)
        #print(chiffre)

    for reg, replacement in _corrections:
        text = re.sub(reg, replacement, text)

    heures=re.findall("\d+ *h *\d+",text)
    for h in heures:
        print(h)
        split_h=h.split('h')
        text_rep=re.sub('^0+','',split_h[0])+' heures '+re.sub('^0+','',split_h[1])
        #text_rep=split_h[0]+' heures '+split_h[1]
        text=text.replace(h, text_rep)

    text=re.sub("(\d+)''",r"\1 secondes ",text)
    text=re.sub("(\d+)'",r"\1 minutes ",text)
    text=re.sub("(\d+)°",r"\1 degrés ",text)
    text=re.sub(" (\d+),(\d+) ",r" \1 virgule \2 ",text)

    chiffres = re.findall(" [^ ]*\d+[^ ]* ",text)
    chiffres = list(map(lambda s: s.strip(), chiffres))
    chiffres = list(set(chiffres))
    for chiffre in chiffres:
        try:
            word = num2words(float(chiffre), lang='fr')
            text = re.sub(' '+str(chiffre)+' ', ' '+word+' ',text)
        except:
            print('3:',chiffre)
            newChiffre = re.sub('\-','', chiffre)
            newChiffre = re.sub('([^\d]*)(\d+\.?\d*)([^\d]*)',r'\1 \2 \3', newChiffre)
            newChiffre = newChiffre.split(' ')
            word = num2words(float(newChiffre[1]), lang='fr')
            newWord = " ".join(newChiffre[0])
            newWord = newWord+' '+word
            if len(newChiffre)==3:
                newWord = newWord+' '+newChiffre[2]
            text = re.sub(' '+str(chiffre)+' ', ' '+newWord+' ',text)
            #print(text)


    for reg, replacement in _corrections_number_fr:
        text = re.sub(reg, replacement, text)

    text = re.sub(r',|;|:|\!|\?|\.|"|\{|\}|\(|\)|\[|\]|=',' ',text)
    text = re.sub(' -',r' ', text)
    text = collapse_whitespace(text)
    return text


if __name__ == '__main__':
    csvPath=sys.argv[1]
    outdir=sys.argv[2]
    print(csvPath)

    basename=os.path.basename(csvPath.split('.')[0])
    folder = os.path.dirname(csvPath)

    # determine speaker based on folder structure...
    regex = re.compile("[^/]+/(male|female)/(?P<speaker_name>[^/]+)/(.*)/")
    regex_match = regex.search(csvPath)
    if regex_match is None:
        print("> File %s is not correct!"%(csvPath))
        exit()
    speaker = regex_match.group("speaker_name")
    speaker = speaker.lower()
    if regex_match.group(1) == 'male':
        gender = 'm'
    else:  gender = 'f'

    alldata = []
    with open(csvPath, 'r') as ttf:
        for line in ttf:
            cols = line.split('|')
            id = speaker+'_'+cols[0]
            wav_file = os.path.join(folder, 'wavs', cols[0] + '.wav')
            if os.path.isfile(wav_file):
                text = cols[1].strip()
                text = text_parser(text)
                current = {
                    "id": id,
                    "text": text,
                    "wav": wav_file
                }
                alldata.append(current)
            else:
                print("WRNG: wav file %s is not exist! Skip!!"%(wav_file))

    # Output File needed for kaldi input
    text_file = open(outdir + '/text', 'a')
    wav_scp = open(outdir + '/wav.scp', 'a')
    utt2spk_file = open(outdir + '/utt2spk', 'a')
    spk2gender= open(outdir + '/spk2gender', 'a')

    for data in alldata:
        if data["text"] != "":
            utt2spk_file.write(data["id"]+" "+speaker+"\n")
            wav_scp.write(data["id"]+" "+data["wav"]+"\n")
            text_file.write(data["id"]+" "+data["text"]+"\n")
    spk2gender.write(speaker+" "+gender+"\n")

    utt2spk_file.close()
    text_file.close()
    wav_scp.close()
    spk2gender.close()
