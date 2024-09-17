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

def collapse_whitespace(text):
    #_whitespace_re = re.compile(r'\s+')
    _whitespace_re = re.compile(r'[^\S\r\n]+') # All whitespace except new line
    return re.sub(_whitespace_re, ' ', text).strip()

def text_parser(text):
    text = ' '+text+' '

    text = re.sub('{{event:noise}}',r' <noise> ', text)
    text = re.sub('{{comment:[^}]*}}',' <comment> ', text)
    text = re.sub('{{background:[^}]*}}',' <background> ', text)
    
    text = collapse_whitespace(text)
    for reg, replacement in _corrections_caracteres_speciaux_fr:
        text = re.sub(reg, replacement, text)
    
    text = ' '+text+' '
    text = re.sub(" \+ "," <noise> ", text)
    text = re.sub(" ///"," <background> ", text)
    text = re.sub("¤+[A-Za-z0-9]*¤+"," <noise> ", text)
    text = re.sub("¤+","", text)
    text = re.sub(" < "," <noise> ", text)
    text = re.sub(" > "," <noise> ", text)


    hesitations=re.findall("/[^/]*,[^/]*/",text)
    for hesitation in hesitations:
        #print('1:',hesitation)
        text = re.sub(re.sub("\*", "\*", hesitation)," <unk> ", text)

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
    #text = re.sub("'","' ", text)
    #text = re.sub('"',' " ', text)
    #text = re.sub("' '", "''", text)
    #text = re.sub(":", " : ", text)
    #text = re.sub(";", " ; ", text)
    text = re.sub(',|¸',',', text)
    #text = re.sub(", ", " , ", text)
    #text = re.sub("\!", " ! ", text)
    #text = re.sub("\?", " ? ", text)
    text = re.sub("^ *-+", "", text)
    text = re.sub("\^+","", text)
    text = re.sub(" +(- +)+", " ", text)
    text = re.sub("([,;:\!\?\.]) -([a-zàâäçèéêëîïôùûü]+)", r"\1 \2", text)
    text = re.sub("([a-zàâäçèéêëîïôùûü]{3,})' ", r"\1 ", text)
    text = re.sub("([a-zàâäçèéêëîïôùûü]{2,})' *[,;:\!\?\.]", r"\1 ", text)
    text = re.sub('\.{2,}',' ', text)
    text = re.sub('\. *$',' . ', text)
    text = re.sub('(\d)\. ',r'\1 . ', text)

    text = re.sub('\([^\(]*\)',' ', text)
    text = re.sub('\[[^\[]*\]',' ', text)
    text = re.sub('\{[^\{]*\}',' ', text)
    text = re.sub('\([^\}]*\}',' ', text)
    
    #text = re.sub(" '", " ", text)
    text = re.sub('--+',' ', text)
    text = re.sub('_',' ', text)
    text = re.sub('–',' ', text)
    text = re.sub('—+',' ', text)
    text = re.sub('…','...', text)
    text = re.sub('\*+', ' ', text)
    text = re.sub('«','"', text)
    text = re.sub('»','"', text)
    text = re.sub('“','"', text)
    text = re.sub('”','"', text)
    text = re.sub('/',' ', text)
    text = re.sub("&"," et ", text)
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

    text=re.sub("jeunesse@rfi.fr","jeunesse arobase rfi point fr", text)
    text=re.sub("aval98.asso.com","aval 98 point asso point com",text)
    text=re.sub(" mohamed "," mohammed ",text)
    text=re.sub(" mohammed +(<[^<]*> *)* *vi "," mohammed six ",text)
    text=re.sub(" mohammed +(<[^<]*> *)* *v "," mohammed cinq ",text)
    text=re.sub(" henri +(<[^<]*> *)* *iv "," henri quatre ",text)
    text=re.sub(" paul +(<[^<]*> *)* *vi "," paul six ",text)
    text=re.sub(" gustave +(<[^<]*> *)* *vi "," gustave six ",text)
    text=re.sub(" abdellah +(<[^<]*> *)* *ii ", " abdellah deux ",text)
    text=re.sub(" jean-paul +(<[^<]*> *)* *ii ", " jean-paul deux ",text)
    text=re.sub(" pierre +(<[^<]*> *)* *ii ", " pierre deux ",text)
    text=re.sub(" henri +(<[^<]*> *)* *ii ", " henri deux ",text)
    text=re.sub(" paris +(<[^<]*> *)* *ii ", " paris deux ",text)
    text=re.sub(" louis +(<[^<]*> *)* *ii ", " louis deux ",text)
    text=re.sub(" canal (<[^<]*> *)* *\+ "," canal plus ",text)


    _corrections=[]
    ordinaux=re.findall("[^ ]*ème|\d+ère|\d+re|\d+er?| [xiv]{2,}e ",text)
    for chiffre in ordinaux:
        chiffre = chiffre.strip()
        romain = chiffre.split('ème')[0]
        romain = re.sub('[^xievr\d]',' ',romain)
        #if ' ' not in romain and romain != "vie" and romain != "vive":
        #    print('2:',chiffre, chiffre in _chiffre_ordinaux_fr_in)
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
        #print(h)
        split_h=h.split('h')
        text_rep=re.sub('^0+','',split_h[0])+' heures '+re.sub('^0+','',split_h[1])
        #text_rep=split_h[0]+' heures '+split_h[1]
        text=text.replace(h, text_rep)


    text=re.sub(" (\d+),(\d+) ",r" \1 virgule \2 ",text)
    chiffres = re.findall(" [^ ]*\d+[^ ]* ",text)
    chiffres = list(map(lambda s: s.strip(), chiffres))
    chiffres = list(set(chiffres))
    for chiffre in chiffres:
        try:
            word = num2words(float(chiffre), lang='fr')
            text = re.sub(' '+str(chiffre)+' ', ' '+word.encode('utf8')+' ',text)
        except:
            #print('3:',chiffre)
            newChiffre = re.sub('^(\d+)h',r'\1heures', chiffre)
            newChiffre = re.sub('\-','', newChiffre)
            newChiffre = re.sub('([^\d]*)(\d+\.?\d*)([^\d]*)',r'\1 \2 \3', newChiffre)
            newChiffre = newChiffre.split(' ')
            word = num2words(float(newChiffre[1]), lang='fr')
            newWord = " ".join(newChiffre[0])
            newWord = newWord+' '+word.encode('utf8')
            if len(newChiffre)==3:
                newWord = newWord+' '+newChiffre[2]
            text = re.sub(' '+str(chiffre)+' ', ' '+newWord+' ',text)


    for reg, replacement in _corrections_number_fr:
        text = re.sub(reg, replacement, text)

    text = re.sub(r',|;|:|\!|\?|\.|"|\{|\}|\(|\)|\[|\]|=',' ',text)
    text = re.sub(' -',r' ', text)
    text = re.sub(' < ', '', text)
    text = re.sub(' > ', '', text)
    text = re.sub('\++', ' <noise> ', text)
    text = collapse_whitespace(text)
    verif = re.sub('<[^<]*>', '', text)
    verif = collapse_whitespace(verif)
    if verif == '':
        return ''

    # Remove special words
    text = re.sub(r"<\w+>","", text)
    return collapse_whitespace(text)

def parseXML(file):
    file = list(map(lambda s: s.strip(), file))
    file = list(map(lambda s: re.sub('<Sync(.*)/>',r'<Sync\1>',s), file))
    file = list(map(lambda s: re.sub('<Sync','</Sync><Sync',s), file))
    file = list(map(lambda s: re.sub('</Turn>','</Sync></Turn>',s), file))
    file = list(map(lambda s: re.sub('<Event.*type="([^"]*)".*/>',r'{{event:\1}}',s), file))
    file = list(map(lambda s: re.sub('<Comment.*desc="([^"]*)".*/>',r'{{comment:\1}}',s), file))
    file = list(map(lambda s: re.sub('<Background.*type="([^"]*)".*/>',r'{{background:\1}}',s), file))
    file = ' '.join(file)
    file = re.sub('<Turn([^<]*)> </Sync>',r'<Turn\1>',file)
    
    #file = re.sub('<Event *desc="sampa *: *[^"]*" type="pronounce" extent="begin"/>([^<]*)<Event[^>]*type="pronounce" extent="end"/>',r'@@@@@@\1@@@@',file)
    #file = re.sub('<Event desc="([^"]*)" type="pronounce" extent="begin"/>[^<]*<Event[^>]*type="pronounce" extent="end"/>',r'\1',file)
    #file = re.sub('<Event[^>]*type="([^"]*)"[^>]*/>',r'{{event:\1}}',file)
    #file = re.sub('<Comment[^>]*desc="([^"]*)"[^>]*/>',r'{{comment:\1}}',file)
    #file = re.sub('<Background[^>]*type="([^"]*)"[^>]*/>',r'{{background:\1}}',file)
    
    #file = re.sub('<Turn([^<]*)startTime="([^<]*)"([^<]*)> *<(?!\bSync\b)([^<]*)>',r'<Turn\1startTime="\2"\3><Sync time="\2"><\4>',file)
    file = re.sub('<Turn([^<]*)startTime="([^<"]*)"([^<]*)> *(?!\b<Sync\b)([^<]+)',r'<Turn\1startTime="\2"\3><Sync time="\2">\4',file)
    return file
    
if __name__ == '__main__':
    trsPath=sys.argv[1]
    wavPath=sys.argv[2]
    outdir=sys.argv[3]
    
    basename=os.path.basename(os.path.splitext(trsPath)[0])
    basename=basename.lower()
    
    # Handle spaces in filenames
    basename= basename.replace(" ","_")
    if " " in wavPath:
        wavPath = "'"+wavPath+"'"

    changeSpk=False
    if len(sys.argv) == 5:
        changeSpk=True
        cspkId = basename[0:len(basename)-2]
        cspkGender = cspkId[-1]

    with open(trsPath) as f:
        file = f.readlines()

    file = parseXML(file)
    dict = xmltodict.parse(file)

    # prepare the list of speakers
    newSpkId = 1
    speaker_id=[]
    speaker_gender=[]
    speaker_name=[]
    speaker_scope=[]
    alldata=[]
    
    if "Speakers" in dict["Trans"] and dict["Trans"]["Speakers"] is not None:
            speakers = dict["Trans"]["Speakers"]["Speaker"]
            if '@id' in dict["Trans"]["Speakers"]["Speaker"]:
                speakers = [dict["Trans"]["Speakers"]["Speaker"]]
            for spk in speakers:
                speaker_id.append(spk["@id"])
                speaker_gender.append(spk["@type"].lower()) if '@type' in spk else speaker_gender.append("unknown")
                speaker_name.append(spk["@name"].lower()) if '@name' in spk else speaker_name.append("unknown")
                speaker_scope.append(spk["@scope"].lower()) if '@scope' in spk else speaker_scope.append("unknown")
            
            speaker_gender = list(map(lambda s: re.sub('^m.*','m',s), speaker_gender))
            speaker_gender = list(map(lambda s: re.sub('^f.*','f',s), speaker_gender))

    
    sections = dict["Trans"]["Episode"]["Section"]
    if '@startTime' in dict["Trans"]["Episode"]["Section"] or '@type' in dict["Trans"]["Episode"]["Section"] or '@endTime' in dict["Trans"]["Episode"]["Section"]:
        sections = [dict["Trans"]["Episode"]["Section"]]
    # print("Length sections: ",len(sections))
    for i in range(len(sections)):
        turns = sections[i]["Turn"]
        if '@startTime' in sections[i]["Turn"]:
            turns = [sections[i]["Turn"]]
        
        section_topic = sections[i]["@topic"] if "@topic" in sections[i] else "None"
        section_topic = "None" if section_topic == "" else section_topic
        
        # print("Length turns: ",len(turns))
        for j in range(len(turns)):
            syncs = turns[j]["Sync"]
            if '@time' in turns[j]["Sync"]:
                syncs = [turns[j]["Sync"]]
            # print("Length syncs: ",len(turns))

            turn_start = turns[j]["@startTime"] if "@startTime" in turns[j] else ""
            turn_end = turns[j]["@endTime"] if "@endTime" in turns[j] else ""
            if "@speaker" in turns[j]:
                turn_speaker_id = turns[j]["@speaker"]
            else:
                turn_speaker_id = "newSpkGen"+str(newSpkId)
                speaker_id.append(turn_speaker_id)
                speaker_gender.append("unknown")
            
            if turn_speaker_id in speaker_id:
                turn_speaker_gender = speaker_gender[speaker_id.index(turn_speaker_id)]
            else:
                turn_speaker_gender = ""
            if turn_speaker_id == "":
                nbr_spk = 0
                turn_speaker_id = "-1"
            else:
                nbr_spk = len(turn_speaker_id.split(' '))

            
            turn_fidelity = turns[j]["@fidelity"] if "@fidelity" in turns[j] else "" #(high|medium|low)
            
            data = []
            for k in range(len(syncs)):
                sync_text = syncs[k]["#text"] if "#text" in syncs[k] else ""
                sync_stime = syncs[k]["@time"] if "@time" in syncs[k] else ""
                sync_text2 = sync_text.encode('utf-8')
                sync_text = text_parser(sync_text2)
                # if sync_text != sync_text2:
                #     print(sync_text2)
                #     print(">>> " + sync_text)
                
                seg_id = str(basename) + '_%s-%03d_Section%02d_Topic-%s_Turn-%03d_seg-%07d' % (
                    str(re.sub('\d+','',turn_speaker_id)),int(re.sub('[a-zA-Z ]','',turn_speaker_id)),i+1,str(section_topic),j+1,k)

                spkr_id = str(basename)+'_%s-%03d' % (str(re.sub('\d+','',turn_speaker_id)),int(re.sub('[a-zA-Z ]','',turn_speaker_id)))
                
                current = {
                    "id":seg_id,
                    "spkId":spkr_id,
                    "spk":turn_speaker_id,
                    "gender":turn_speaker_gender,
                    "text":sync_text,
                    "rawtext":sync_text2,
                    "nbrSpk":nbr_spk,
                    "sTime":sync_stime,
                    "eTime":None
                }
                
                data.append(current)
            data[-1]["eTime"] = turn_end
            for d in range(len(data)-1):
                data[d]["eTime"] = data[d+1]["sTime"]
            
            alldata.append(data)
            
    alldata = [item for sublist in alldata for item in sublist]
    
    #Save the data
    # Output File needed for kaldi input
    segments_file = open(outdir + '/segments', 'a')
    utt2spk_file = open(outdir + '/utt2spk', 'a')
    text_file = open(outdir + '/text', 'a')
    rawtext_file = open(outdir + '/text_raw', 'a')
    wav_scp = open(outdir + '/wav.scp', 'a')
    spk2gender= open(outdir + '/spk2gender', 'a')
    
    final_list_of_speakers=[]
    for data in alldata:
        if data["nbrSpk"] == 1 and data["text"] != "":
            final_list_of_speakers.append(data["spk"])
            segments_file.write(data["id"]+" "+basename+" "+data["sTime"]+" "+data["eTime"]+"\n")
            if changeSpk:
                utt2spk_file.write(data["id"]+" "+cspkId+"\n")
            else:
                utt2spk_file.write(data["id"]+" "+data["spkId"]+"\n")
            text_file.write(data["id"]+" "+data["text"]+"\n")
            rawtext_file.write(data["id"]+" "+data["rawtext"]+"\n")

    if changeSpk:
        spk2gender.write(cspkId+" "+cspkGender+"\n")
    else:
        final_list_of_speakers = list(set(final_list_of_speakers))
        for id in final_list_of_speakers:
            spk_id = str(basename)+'_%s-%03d' % (str(re.sub('\d+','',id)),int(re.sub('[a-zA-Z ]','',id)))
            spk2gender.write(spk_id+" "+re.sub('^[^mf].*','m',speaker_gender[speaker_id.index(id)])+"\n")

    wav_scp.write(basename+" sox "+ wavPath +" -t wav -r 16k -b 16 -c 1 - |\n")
    segments_file.close()
    utt2spk_file.close()
    text_file.close()
    wav_scp.close()
    spk2gender.close()
