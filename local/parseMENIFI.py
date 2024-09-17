#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright (C) 2020, Linagora, Ilyes Rebai, Sami Benhamiche
# Email: irebai@linagora.com

import xmltodict
import sys
import re
import os
import string
from num2words import num2words
import hashlib

_chiffre_ordinaux_fr_in = ['1ère', '1er', '1e', '1re', '2e', '3e', '4e', '5ème', '7e' '21e', '21ème']
_chiffre_ordinaux_fr_out = ['première', 'premier', 'premier', 'deuxième',
                            'première', 'troisième', 'quatrième', 'cinquième', 'septième', 'vingt-et-unième', 'vingt-et-unième']


_chiffre_romain_fr_in=['ii','iii','iv','vii','viii','ix','xi','xii','xiii','xiv','xv','xvi','xvii','xviii','xix','xx','xxi']
_chiffre_romain_fr_out=['deux','trois','quatre','sept','huit','neuf','onze','douze','treize','quatorze','quinze','seize','dix-sept','dix-huit','dix-neuf','vingt','vingt-et-unième']

def undigit(str, to="cardinal"):
    str = re.sub(" ","", str)
    if to == "denominator":
        if str == "2": return "demi"
        if str == "3": return "tiers"
        if str == "4": return "quart"
        to = "ordinal"
    return num2words(float(str), lang='fr', to=to).encode('utf-8')


def parse_text(word):
    NOCOMMIT = word

    problem = False

    word = word.encode('utf-8').strip()
    word = word.lower()
    word = re.sub("\.+$", "", word)

    # TODO: Complet the text normalization
    # EG: remove the punctuation, convert number to letters, convert symbols (e.g. %) to letters, add whitespace after quote, ...
    # 1,5 => un virgule cinq
    # 4.000 => 4000 => (num2words) => quatre milles
    # 5.600 => 5600

    if re.search("\d+(\.\d{3})+", word): # chiffre
        #print("chiffre: "+word)
        word = re.sub("\.","",word)
        #print("chiffre: "+word)

    if re.search("(\d+),(\d+)",word): # virgule
        #print("virgule: "+word)
        word = word.split(',')
        num1 = num2words(float(word[0]), lang='fr')
        num2 = num2words(float(word[1]), lang='fr')
        word = num1 + " virgule " + num2
        word = word.encode('utf-8')
        #print("virgule: "+word)  
        
    if re.search("\d(\.\d)+",word): # version
        print("version: "+word)
        new = ""
        for i in word.split('.'):
            new += num2words(float(i), lang='fr')
            new += " point "
        word = re.sub(' point $','',new)
        word = word.encode('utf-8')
        print("version: "+word)

    # if re.search("^\d+ème$|^\d+ère$|^\d+re$|^\d+er?$|^[xiv]{2,}e$", word) and word not in ["vie", "vive", "viver", "vivier"]: #  ordinaux
    #     #print("ordinaux: "+word)
    #     if word in _chiffre_ordinaux_fr_in:
    #         word = _chiffre_ordinaux_fr_out[_chiffre_ordinaux_fr_in.index(word)]
    #         #print("ordinaux: "+word)
    #     else:
    #         print("ordinaux (not found): "+word)

    chiffres = re.findall(r"\b1(?:ère|ere|er|re|r)|2(?:nd|nde)|\d+(?:ème|eme|e)\b", word)
    chiffres = sorted(list(set(chiffres)), reverse=True, key=len)    
    for chiffre in chiffres:
        if chiffre in ["1ère","1ere"]:
            word = "première"
        elif chiffre in ["2nd"]:
            word = "second"
        elif chiffre in ["2nde"]:
            word = "seconde"
        else:
            word = undigit(re.findall(r"\d+", chiffre)[0], to= "ordinal")
            word = re.sub(r'\b'+str(chiffre)+r'\b', word, word)

    chiffres = re.findall(r"\b\d[ /\d]*\b",word)
    chiffres = list(map(lambda s: s.strip(r"[/ ]"), chiffres))
    chiffres = sorted(list(set(chiffres)), reverse=True, key=len)    
    for chiffre in chiffres:
        numslash = len(re.findall("/", chiffre))
        if numslash == 0:
            word = undigit(chiffre)
        elif numslash == 1:
            i = chiffre.index("/")
            first = undigit(chiffre[:i])
            second = undigit(chiffre[i+1:], to="denominator")
            word = first + " " + second
        else:
            word = "/".join([undigit(s) for s in chiffre.split('/')])
        word = re.sub(r'\b'+str(chiffre)+r'\b', word, word)

    if re.search("^[ixv]{2,}$",word): # romains
        #print("romains: "+word)
        if word in _chiffre_romain_fr_in:
            word = _chiffre_romain_fr_out[_chiffre_romain_fr_in.index(word)]
            #print("romains: "+word)
        # else:
        #     problem = True
        #     print("romains (not found): "+word)

    if re.search("\d+h\d*", word): # time
        #print("heures: "+word+" < "+NOCOMMIT)
        if word.startswith("jt"):
            prefix = "j t "
            word = word[2:]
        else:
            prefix = "j t "
        numbers = word.split('h')
        hn = float(numbers[0])
        h = num2words(hn, lang='fr')
        m = num2words(float(numbers[1]), lang='fr') if numbers[1] != '' else ""
        word = prefix + h + " heure" + ("s" if hn > 1 else "") + " " + m
        word = word.encode('utf-8')
        #print("heures: "+word)

    if re.search('%',word): # pourcentage
        word = re.sub('%','pour cent',word)
        #print("pourcent: "+word)

    if re.search("\d+",word): # numbers & accronyms
        try:
            word = num2words(float(word), lang='fr') 
            word = word.encode('utf-8')
        except:
            #print('ERROR: '+word)
            word = re.sub('bac\+5','bac plus cinq',word)
            word = re.sub('bac\+2','bac plus deux',word)
            word = re.sub('co2','c o deux',word)
            word = re.sub('cac40','cac quarante',word)
            word = re.sub('cop21','cop vingt-et-un',word)
            word = re.sub('50/50','cinquante sur cinquante',word)

            word = re.sub('(\d+)',r' \1 ',word)
            chiffre = re.findall(' \d+ ',word)
            for i in chiffre:
                num = num2words(float(i), lang='fr')
                num = num.encode('utf-8')
                word = re.sub(i," "+num+" ",word)

    if re.search('\.',word): # abbreviations
        #print('abbreviations: ',word)
        word = re.sub('\.',' ',word)
        #problem = True
        #print('abbreviations: ',word)

    word = word.strip(",")

    return (problem, word)


def convert_utterance_to_data(utterance, turn_id, default_spk):
    text = ""
    words = [row["#text"] for row in utterance]
    word_tot_number = len(words)
    pbs = False
    for word in words:
        pb, w = parse_text(word)
        if re.match("["+string.punctuation+"]\Z", w): # Remove punctuations
            continue
        text += " " + w
        pbs = pbs or pb
    text = text.strip()
    if pbs:
        print(" ".join(words).encode("utf-8"))
        print(text)
        print()

    stime = round(float(utterance[0]["@timestamp"]), 2) \
        if "@timestamp" in utterance[0] else None
    etime = round(float(utterance[len(utterance) - 1]["@timestamp"]), 2) + round(float(utterance[len(utterance) - 1]["@timedur"]), 2) \
        if "@timestamp" in utterance[len(utterance) - 1] and "@timedur" in utterance[len(utterance) - 1] else None
    dur = round(float(etime)-float(stime), 2) \
        if stime is not None and etime is not None else None

    seg_id = str(utterance[0]["@speakerid"]) + '-' + str(basename) + '_seg-' + str(turn_id)

    spkr_id = str(utterance[0]["@speakerid"])
    if not spkr_id:
        spkr_id = default_spk

    spkr_gender = str(utterance[0]["@gender"])
    if not spkr_gender:
        spkr_gender = "u"

    return {
        "id": seg_id,
        "spkId": spkr_id,
        "gender": spkr_gender,
        "text": text,
        "rawtext": " ".join(words).encode("utf-8").replace(" .", ".").replace(" ?", "?").replace(" !", "!").replace(" ,", ","),
        "sTime": str(stime),
        "eTime": str(etime),
        "dur": str(dur)
    }, word_tot_number


def find_audio_file(xml_file, ext = "mp3"):
    dirname, basename = os.path.split(xml_file)
    if basename == "20120614_Defi_climat_2_copie_wmv_0_fre_minefi.xml":
        print("This file is known to be empty!")
        return None
    filenames = os.listdir(dirname)
    pattern_end = "." + ext
    for w in reversed(list(re.finditer("[\._]", basename))):
        i = w.span()[0]
        if i==0: break
        pattern_start = basename[:i]
        result = [x for x in filenames if x.startswith(pattern_start) and x.endswith(pattern_end)]
        if len(result) > 1:
            #print("WARNING: Several candidate files for %s (%s):\n%s" % (pattern_start, xml_file, ", ".join(result)))
            return None
        elif len(result) == 1:
            return os.path.join(dirname, result[0])
    return None # raise RuntimeError("Could not find audio file for %s", xml_file)

def commonprefix(m):
    "Given a list of pathnames, returns the longest common leading component"
    if not m: return ''
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1

if __name__ == '__main__':
    if len(sys.argv) != 3:
        raise Exception("Error: python2 parseXmlJSON.py <xmlPath> <output-dir>")

    xmlPath = sys.argv[1]
    wavPath = find_audio_file(xmlPath)
    if wavPath is None:
        print("WARNING: Could not find audio file for %s" % xmlPath)
        sys.exit()
    outdir = sys.argv[2]

    max_time_between_utterance = 0.5

    basename = commonprefix([os.path.basename(xmlPath), os.path.basename(wavPath)]).strip("_")
    default_spk = hashlib.sha1(basename.encode('utf-8')).hexdigest()[:10]

    with open(xmlPath) as f:
        file = f.readlines()
    file = ' '.join(file)
    dict = xmltodict.parse(file)

    if "root" in dict:
        speaker_id = []
        speaker_gender = []
        turns = []

        # Verifications
        rows = len(dict["root"]["row"])
        words = len(dict["root"]["text"].split(' ')) if "text" in dict["root"] and dict["root"]["text"] is not None else -1
        # if rows != words and words != -1:
        #     print(xmlPath, " word number check: ", rows == words)

        # Since we don't have xml shema, we print the xml keys to have a vew of the data
        #print(dict["root"].keys())
        #if dict["root"]["speakers"] != None:
        #    print(dict["root"]["speakers"])

        # Get separate turns from the full text based on speakerID
        # Concat the words of the same speaker by turn
        # Get speaker information (create speaker_id list and speaker_gender list)
        turn = []
        speaker_test = []
        for row in dict["root"]["row"]:
            if not row["@speakerid"]:
                row["@speakerid"] = default_spk
            if not row["@gender"]:
                row["@gender"] = "u"
            speaker_test.append(row["@speakerid"])
            if len(turn) > 0 and row["@speakerid"] == turn[0]["@speakerid"]:
                turn.append(row)
            else:
                turns.append(turn)
                turn = [row]
                if row["@speakerid"] not in speaker_id:
                    speaker_id.append(row["@speakerid"])
                    speaker_gender.append(row["@gender"].lower())

        speaker_gender = list(
            map(lambda s: re.sub('^m.*', 'm', s), speaker_gender))
        speaker_gender = list(
            map(lambda s: re.sub('^f.*', 'f', s), speaker_gender))

        # Append the last turn to the list of turns
        if len(turn) > 0:
            turns.append(turn)

        # Do some verifications about speakers
        if len(speaker_id) != len(list(set(speaker_test))):
            print(len(speaker_id))
            print(len(list(set(speaker_test))))
            print("Error: number of speakers mismatch ", xmlPath)

        # Get separate utterances from the list of turns
        # Use the punctuation marks for segmentation
        # Here we convert the turns to sentences to have short speech segments for training
        utterances = []
        last_start = 0
        for turn in turns:
            utterance = []
            for row in turn:
                punctuation = re.findall("\. ?$|\? ?$|! ?$", row["#text"])
                coma = re.findall(", ?$", row["#text"])
                start = float(row["@timestamp"])
                if len(punctuation) != 0:
                    utterance.append(row)
                    utterances.append(utterance)
                    utterance = []
                elif len(coma) > 0:
                    if len(utterance) == 0 and len(utterances) > 0:
                        utterances[-1].append(row)
                    else:
                        utterance.append(row)
                else:
                    if start > last_start + max_time_between_utterance and len(utterance) > 0:
                        utterances.append(utterance)
                        utterance = []
                    utterance.append(row)
                last_start = start + float(row["@timedur"])

        # Append the last utterance to the list of utterances
        if len(utterance) > 0:
            utterances.append(utterance)

        # Get all data information by utterance in order to create the final outputs (kaldi based files)
        # Resegment long utterances (dur > 20 seconds) to have a more short segments
        # The word "et" is used as a separation symbol if it exists
        alldata = []
        turn_id = 1
        word_tot_number = 0
        for utterance in utterances:
            # Get timestamps of the current utterance: start-time, end-time, as well as duration
            # The duration will be used to filter the segments
            # Long segments will be more processed
            stime = round(float(utterance[0]["@timestamp"]), 2) \
                if "@timestamp" in utterance[0] else None
            etime = round(float(utterance[len(utterance) - 1]["@timestamp"]), 2) + round(float(utterance[len(utterance) - 1]["@timedur"]), 2) \
                if "@timestamp" in utterance[len(utterance) - 1] and "@timedur" in utterance[len(utterance) - 1] else None

            if stime == None or etime == None:
                print("error")
                continue

            dur = round(float(etime)-float(stime), 2) \
                if stime is not None and etime is not None else None

            if dur < 20:  # check the duration < 20 seconds
                # Get data from utterance
                current, word_tot_number_ = convert_utterance_to_data(utterance, turn_id, default_spk)
                alldata.append(current)
                word_tot_number += word_tot_number_
                turn_id += 1
            else:
                # Process long utterance
                utterances_ = []
                new_utterance = []
                count = 0
                # Create the new utterances based on the word "et" and the number of words
                for row_ in utterance:
                    if row_["#text"].lower().strip() == "et" and count > 20 and count < 30:
                        utterances_.append(new_utterance)
                        new_utterance = [row_]
                        count = 0
                    elif count > 30:
                        utterances_.append(new_utterance)
                        new_utterance = [row_]
                        count = 0
                    else:
                        new_utterance.append(row_)
                    count += 1

                if len(new_utterance) > 0:
                    # Check if the last new utterance is helpfull or not (we fix a threshold of number of words "> 5")
                    if len(new_utterance) > 5 or len(utterances_) == 0:
                        utterances_.append(new_utterance)
                    else:
                        # if the last segment has few number of words, we add it to the last new utterance
                        for new_utterance_ in new_utterance:
                            utterances_[len(utterances_) -1].append(new_utterance_)

                for utterance_ in utterances_:
                    # Get data from the new utterances
                    current, word_tot_number_ = convert_utterance_to_data(utterance_, turn_id, default_spk)
                    alldata.append(current)
                    word_tot_number += word_tot_number_
                    turn_id += 1

        # Check if the number of words of the created utterances is equal to
        # the number of words of the rows in the xml and the number of words of the text in the xml too
        # This double check helps as to make sure that the code the data process is correct
        if rows != word_tot_number:
            print(xmlPath, " word number check: (row vs text) ", rows ==
                  words, " (row vs utterances) ", rows == word_tot_number)

        # Output File needed for kaldi input
        segments_file = open(outdir + '/segments', 'a')
        utt2spk_file = open(outdir + '/utt2spk', 'a')
        utt2dur_file = open(outdir + '/utt2dur', 'a')
        text_file = open(outdir + '/text', 'a')
        rawtext_file = open(outdir + '/text_raw', 'a')
        wav_scp = open(outdir + '/wav.scp', 'a')
        spk2gender = open(outdir + '/spk2gender', 'a')

        # Save the data to files
        wrong_dur = 0
        wrong_tot_dur = 0
        for data in alldata:
            if data["text"] != "":
                segments_file.write(
                    data["id"]+" "+basename+" "+data["sTime"]+" "+data["eTime"]+"\n")
                utt2spk_file.write(data["id"]+" "+data["spkId"]+"\n")
                utt2dur_file.write(data["id"]+" "+data["dur"]+"\n")
                text_file.write(data["id"]+" "+data["text"]+"\n")
                rawtext_file.write(data["id"]+" "+data["rawtext"]+"\n")

            if float(data["dur"]) > 30:
                wrong_dur += 1
                wrong_tot_dur += float(data["dur"])

        # check if we don't have anymore long segments
        #if wrong_dur > 0:
        #    print("number of segments (>30s): "+str(wrong_dur)+" with total duration: "+str(wrong_tot_dur))

        for id in speaker_id:
            spk_id = str(id)
            spk2gender.write(
                spk_id+" "+re.sub('^[^mf].*', 'm', speaker_gender[speaker_id.index(id)])+"\n")

        wav_scp.write(basename+" sox " + wavPath +
                      " -t wav -r 16k -b 16 -c 1 - |\n")

        segments_file.close()
        utt2spk_file.close()
        utt2dur_file.close()
        text_file.close()
        wav_scp.close()
        spk2gender.close()

    else:
        print("Error: no root found in ", xmlPath)
