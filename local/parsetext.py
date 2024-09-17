#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019, Linagora, Ilyes Rebai
# Email: irebai@linagora.com

# This script is used in "automatic_audio_segmentation_using_asr.sh"
# It normalizes the input text and split it into NJ overlapped files


import sys, re
import argparse
sys.path.insert(1, 'local')
import os
from glob import glob
from num2words import num2words


_chiffres = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf", "vingt", "vingt-et-un", "vingt-deux", "vingt-trois", "vingt-quatre", "vingt-cinq", "vingt-six", "vingt-sept", "vingt-huit", "vingt-neuf", "trente", "trente-et-un", "trente-deux", "trente-trois", "trente-quatre", "trente-cinq", "trente-six", "trente-sept", "trente-huit", "trente-neuf", "quarante", "quarante-et-un", "quarante-deux", "quarante-trois", "quarante-quatre", "quarante-cinq", "quarante-six", "quarante-sept", "quarante-huit", "quarante-neuf", "cinquante", "cinquante-et-un", "cinquante-deux", "cinquante-trois", "cinquante-quatre", "cinquante-cinq", "cinquante-six", "cinquante-sept", "cinquante-huit", "cinquante-neuf", "soixante", "soixante-et-un", "soixante-deux", "soixante-trois", "soixante-quatre", "soixante-cinq", "soixante-six", "soixante-sept", "soixante-huit", "soixante-neuf", "soixante-dix", "soixante-et-onze", "soixante-douze", "soixante-treize", "soixante-quatorze", "soixante-quinze", "soixante-seize", "soixante-dix-sept", "soixante-dix-huit", "soixante-dix-neuf", "quatre-vingts", "quatre-vingt-un", "quatre-vingt-deux", "quatre-vingt-trois", "quatre-vingt-quatre", "quatre-vingt-cinq", "quatre-vingt-six", "quatre-vingt-sept", "quatre-vingt-huit", "quatre-vingt-neuf", "quatre-vingt-dix", "quatre-vingt-onze", "quatre-vingt-douze", "quatre-vingt-treize", "quatre-vingt-quatorze", "quatre-vingt-quinze", "quatre-vingt-seize", "quatre-vingt-dix-sept", "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf", "cent", "mille"]
_chiffres_ordinaux = ["premier", "première", "onzième", "vingt et unième", "trente et unième", "deuxième", "douzième", "vingt-deuxième", "quarantième", "troisième", "treizième", "vingt-troisième", "cinquantième", "quatrième", "quatorzième", "vingt-quatrième", "soixantième", "cinquième", "quinzième", "vingt-cinquième", "soixante-dixième", "sixième", "seizième", "vingt-sixième", "quatre-vingtième", "septième", "dix-septième", "vingt-septième", "quatre-vingt-dixième", "huitième", "dix-huitième", "vingt-huitième", "centième", "neuvième", "dix-neuvième", "vingt-neuvième", "millième", "dixième", "vingtième", "trentième", "millionième"]
_abbreviations = ["monsieur", "monseigneur", "maître", "mademoiselle", "messieurs", "madame", "nom", "notez bien", "néologisme", "numéro", "ouvrage cité", "masculin", "maximum", "maximal", "jésus-christ", "c' est-à-dire", "le même", "la même chose", "iconographie", "centigrade", "figuré", "féminin", "familier", "exemple", "étymologie", "et cetera", "environ", "docteur", "dictionnaire", "curriculum vitae", "boulevard", "avenue", "arrondissement" ]
_ponctuations = ["point", "virgule", "point-virgule", "deux-points", "points d' interrogation", "points d' exclamation", "points de suspension", "entre parenthèses", "fermer la parenthèse", "ouvre la parenthèse", "entre crochets", "entre guillemets", "fermer guillemet", "tiret", "entre tirets"]

_extra_words = _chiffres + _chiffres_ordinaux + _abbreviations + _ponctuations


_corrections_caracteres_speciaux_fr = [(re.compile('%s' % x[0], re.IGNORECASE), '%s' % x[1])
                  for x in [
                    (" ", " "),
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

_chiffre_ordinaux_fr_in=['1ère','1er','1e','1re','ixième','19ème', 'xxème', 'xiième', '16e', '2e', '3e', '8e', '15e', '53e', 'xviie', 'xiiie', 'xixe', 'xxe', 'xviiie', 'xvie', 'xiie', 'xve', 'iiie', 'xive', 'ixe', 'xxie', '20ème', '43e', '38e', '5e']
_chiffre_ordinaux_fr_out=['première','premier','premier','première','neuvième','dix-neuvième', 'vingtième', 'douzième', 'seizième', 'deuxième', 'troisième', 'huitième', 'quinzième', 'cinquante troisième', 'dix-septième', 'treizième', 'dix-neuvième', 'vingtième', 'dix-huitième', 'seizième', 'douzième', 'quinzième', 'troisième', 'quatorzième', 'neuvième', 'vingt-et-unième', 'vingtième', 'quarante-troisième', 'trente-huitième', 'cinquième']

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

    text = re.sub('\{|\}|\(|\)|\[|\]|"|=',' ',text)
    text = re.sub('(\.|\?|\!|,|;|:)-',r'\1 ', text)
    text = collapse_whitespace(text)
    return text




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--parse_only',
        type=int,
        help='parse text only.',
        default=0)
    parser.add_argument(
        '--nj',
        type=int,
        help='Number of Jobs (integer).',
        default=None)
    parser.add_argument(
        '--use_extra',
        type=str,
        help='use extra words (true|false).',
        default=None)
    parser.add_argument(
        '--keep_punc',
        type=str,
        help='keep punctuation characters (true|false).',
        default='false')
    parser.add_argument(
        '--lexicon_path',
        type=str,
        help='used with mailabs v1 parser',
        default='')
    parser.add_argument(
        'file_path',
        type=str)
    parser.add_argument(
        'output_file',
        type=str)
    args = parser.parse_args()

    file_path = args.file_path
    lexicon_path = args.lexicon_path
    output_file = args.output_file
    nj = args.nj
    keep_punc = True if args.keep_punc == 'true' else False
    use_extra = True if args.use_extra == 'true' else False


    #Prepare text file
    with open(file_path) as f: #load lexicon
        file = f.readlines()
    file = list(filter(None, file))


    #Prepare lexicon
    if lexicon_path != "":
        lexicon=[]
        with open(lexicon_path) as f: #load lexicon
            lex = f.readlines()
        for e in lex:
            e = e.replace('\t',' ').split(' ')
            lexicon.append(e[0].strip())
        lexicon = list(set(lexicon)) #remove duplicates from list

    if args.parse_only:
        print("> File path",file_path)
        text_file = open(output_file, 'a')
        for text in file:
            text = text_parser(text)
            if not keep_punc:
                text = re.sub(r',|;|:|\!|\?|\.',' ',text)
            text = collapse_whitespace(text)
            text_file.write(text+'\n')
        text_file.close()
        exit()

    #file = ["des parties similaires de Charles Bonnet, assez hardi pour écrire en 1760 ! L'animal végète comme la plante ? on trouve, dis-je, les rudiments de la belle loi du soi pour soi sur laquelle repose l'unité de compo sition. Il n'y a qu'un animal. Le créateur ne s'est servi que d'un seul et même patron pour tous les êtres organisés. L'animal est un principe qui prend sa forme extérieure, ou, pour parler plus exactement, les différences de sa forme, dans les milieux où il est appelé à se développer. Les Espèces Zoologiques résultent de ces différences. La proclamation et le soutien de ce système, en harmonie d'ailleurs avec les idée s que nous nous faisons de la puissance divine, sera l'éternel honneur de Geoffroi Saint-Hilaire, le vainqueur de Cuvier sur ce point de la haute science, et dont le triomphe a été salué par le dernier article q u'écrivit le grand Goethe."]

    utterances = []
    for text in file:
        #text = french_corpus_cleaners(text, lexicon, _corrections_mailabs_other_fr)
        text = text_parser(text)
        text = re.sub(" ,", ",", text)
        text = re.sub(" :", ":", text)
        text = re.sub(" ;", ";", text)
        text = re.sub(" \.", ".", text)
        text = re.sub(" \!", "!", text)
        text = re.sub(" \?", "?", text)
        text = re.sub("([a-zàâäçèéêëîïôùûü]{3,})(\.|\!|\?) ",r"\1\2 \n", text)
        text = text.splitlines()
        utterances.append(text)

    utterances = [item for sublist in utterances for item in sublist]
    if not keep_punc:
        utterances = list(map(lambda s: re.sub(r',|;|:|\!|\?|\.',' ',s), utterances))



    text = ' '.join(utterances)
    text = collapse_whitespace(text)
    text_file = open(output_file+'_full', 'w')
    text_file.write(text+'\n')
    text_file.close()

    text_file = open(output_file+'_extra', 'w')
    for word in _extra_words:
        text_file.write(word+"\n")
    text_file.close()



    if nj is not None:
        utterances = list(map(lambda s: re.sub(r',|;|:|\!|\?|\.',' ',s), utterances))
        text = ' '.join(utterances)
        text = collapse_whitespace(text)
        text = re.sub("' ","'",text)
        text = text.split(' ')
        text = list(filter(None, text))
        nb = round(len(text)/nj)
        for i in range(nj):
            text_file = open(output_file+'.'+str(i+1), 'w')
            if i == 0:
                _text = ' '.join(text[0:nb+round(nb/2)])
                _text = re.sub("'","' ", _text)
                _text = re.sub(" \*\*\* ","\n", _text)
                text_file.write(_text+'\n')
                if use_extra:
                    for word in _extra_words:
                        text_file.write(word+"\n")
            else:
                _text = ' '.join(text[nb*i-round(nb/2):nb*(i+1)+round(nb/2)])
                _text = re.sub("'","' ", _text)
                _text = re.sub(" \*\*\* ","\n", _text)
                text_file.write(_text+'\n')
                if use_extra:
                    for word in _extra_words:
                        text_file.write(word+"\n")
            text_file.close()
