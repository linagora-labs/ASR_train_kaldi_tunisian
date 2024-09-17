#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (C) 2019, Linagora, Ilyes Rebai
# Email: irebai@linagora.com


import sys, re
import argparse

_min_count=3
_min_check_words=6
_interval=[5,10]
_word_overlap=3
_chiffres = ["zéro", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf", "dix", "onze", "douze", "treize", "quatorze", "quinze", "seize", "dix-sept", "dix-huit", "dix-neuf", "vingt", "vingt-et-un", "vingt-deux", "vingt-trois", "vingt-quatre", "vingt-cinq", "vingt-six", "vingt-sept", "vingt-huit", "vingt-neuf", "trente", "trente-et-un", "trente-deux", "trente-trois", "trente-quatre", "trente-cinq", "trente-six", "trente-sept", "trente-huit", "trente-neuf", "quarante", "quarante-et-un", "quarante-deux", "quarante-trois", "quarante-quatre", "quarante-cinq", "quarante-six", "quarante-sept", "quarante-huit", "quarante-neuf", "cinquante", "cinquante-et-un", "cinquante-deux", "cinquante-trois", "cinquante-quatre", "cinquante-cinq", "cinquante-six", "cinquante-sept", "cinquante-huit", "cinquante-neuf", "soixante", "soixante-et-un", "soixante-deux", "soixante-trois", "soixante-quatre", "soixante-cinq", "soixante-six", "soixante-sept", "soixante-huit", "soixante-neuf", "soixante-dix", "soixante-et-onze", "soixante-douze", "soixante-treize", "soixante-quatorze", "soixante-quinze", "soixante-seize", "soixante-dix-sept", "soixante-dix-huit", "soixante-dix-neuf", "quatre-vingts", "quatre-vingt-un", "quatre-vingt-deux", "quatre-vingt-trois", "quatre-vingt-quatre", "quatre-vingt-cinq", "quatre-vingt-six", "quatre-vingt-sept", "quatre-vingt-huit", "quatre-vingt-neuf", "quatre-vingt-dix", "quatre-vingt-onze", "quatre-vingt-douze", "quatre-vingt-treize", "quatre-vingt-quatorze", "quatre-vingt-quinze", "quatre-vingt-seize", "quatre-vingt-dix-sept", "quatre-vingt-dix-huit", "quatre-vingt-dix-neuf", "cent", "mille"]
_chiffres_ordinaux = ["premier", "première", "onzième", "vingt et unième", "trente et unième", "deuxième", "douzième", "vingt-deuxième", "quarantième", "troisième", "treizième", "vingt-troisième", "cinquantième", "quatrième", "quatorzième", "vingt-quatrième", "soixantième", "cinquième", "quinzième", "vingt-cinquième", "soixante-dixième", "sixième", "seizième", "vingt-sixième", "quatre-vingtième", "septième", "dix-septième", "vingt-septième", "quatre-vingt-dixième", "huitième", "dix-huitième", "vingt-huitième", "centième", "neuvième", "dix-neuvième", "vingt-neuvième", "millième", "dixième", "vingtième", "trentième", "millionième"]



def WER(r, h):
    """
    Calculation of WER with Levenshtein distance.

    Works only for iterables up to 254 elements (uint8).
    O(nm) time ans space complexity.

    Parameters
    ----------
    r : list
    h : list

    Returns
    -------
    int

    Examples
    --------
    >>> wer("who is there".split(), "is there".split())
    1
    >>> wer("who is there".split(), "".split())
    3
    >>> wer("".split(), "who is there".split())
    3
    """
    # initialisation
    import numpy
    d = numpy.zeros((len(r)+1)*(len(h)+1), dtype=numpy.uint8)
    d = d.reshape((len(r)+1, len(h)+1))
    for i in range(len(r)+1):
        for j in range(len(h)+1):
            if i == 0:
                d[0][j] = j
            elif j == 0:
                d[i][0] = i

    # computation
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            if r[i-1] == h[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                substitution = d[i-1][j-1] + 1
                insertion    = d[i][j-1] + 1
                deletion     = d[i-1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)

    if d[len(r)][len(h)] == 1 and len(r) == len(h):
        return d[len(r)][len(h)]/len(r), True #1 substitution
    else:
        return d[len(r)][len(h)]/len(r), False #otherwise



def findCount(words,find): # search words in find
    count=0
    _init=0
    __min_check_words = _min_check_words
    _find = ' '.join(find)    
    
    if len(words) < _min_check_words:
        __min_check_words = len(words)
    for i in range(__min_check_words-1,2,-1):
        _words = ' '.join(words[:i+1])
        indices=[m.start() for m in re.finditer(_words, _find)]
        if len(indices) != 0:
            for c in _find[0:indices[len(indices)-1]]:
                if c == ' ':
                    _init += 1
            return _init, _min_check_words


    # for i in range(__min_check_words-2):
    #     _words = ' '.join(words[i:__min_check_words])
    #     indices=[m.start() for m in re.finditer(_words, _find)]
    #     if len(indices) != 0:
    #         for c in _find[0:indices[len(indices)-1]]:
    #             if c == ' ':
    #                 _init += 1
    #         return _init, _min_check_words


    last_idx = -1
    for j in range(__min_check_words-1,-1,-1):
        if words[j] in find:
            idx=[i for i, x in enumerate(find) if x == words[j]]
            if last_idx == -1:
                last_idx = idx[len(idx) - 1]
            else:
                for i in range(len(idx)-1,-1,-1):
                    if idx[i] < last_idx:
                        last_idx = idx[i]
                        break
            count+=1
    if count == 0:
        return -1, count
    _init = last_idx
    
    # indices=[]
    # for j in range(__min_check_words-1,-1,-1):
    #     if words[j] in find:
    #         idx=[i for i, x in enumerate(find) if x == words[j]]
    #         indices.append(idx)
    #         count+=1
    # if count == 0:
    #     return -1, count
    # _init = idx[0]
    # 
    # if len(idx) > 1:
    #     indices = [item for sublist in indices for item in sublist]
    #     indices.sort()
    #     for i in range(len(idx)-1,-1,-1):
    #         if indices.index(idx[i]) == i:
    #             _init=idx[i]
    #             break
    if __min_check_words < _min_count and __min_check_words == count:
        return _init, _min_count
    elif __min_check_words < _min_count and __min_check_words != count:
        return _init, count * 2
    return _init, count


def findCount2(words,find):
    count=0
    _init=-1
    for j in range(_min_check_words-1,-1,-1):
        if words[j] in find:
            _init=find.index(words[j])
            count+=1
    return _init, count

def collapse_whitespace(text):
    _whitespace_re = re.compile(r'\s+')
    return re.sub(_whitespace_re, ' ', text).strip()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--wer',
        type=float,
        help='Word Error Rate.',
        default=0.2)
    parser.add_argument(
        '--nj',
        type=int,
        help='Number of Jobs.',
        default=None)
    parser.add_argument(
        '--restore_punc',
        type=str,
        help='Restore the punctuation (true|false). NB: The text file must includes the puncutations.',
        default='false')
    parser.add_argument(
        '--split_output',
        type=str,
        help='Output folder where to save the split files.',
        default=None)
    parser.add_argument(
        'transcription',
        type=str)
    parser.add_argument(
        'text',
        type=str)
    parser.add_argument(
        'output_file_path',
        type=str)
    args = parser.parse_args()

    output_file = args.output_file_path
    use_punctuation = True if args.restore_punc == 'true' else False

    #Prepare transcription
    with open(args.transcription) as f:
        trans = f.readlines()
    trans = list(map(lambda s: s.strip(), trans))

    #Prepare text
    with open(args.text) as f:
        file = f.readlines()
    text = file[0].split(' ')
    text = list(filter(None, text)) # remove empty elements
    _text = text
    text = list(map(lambda s: re.sub(r',|;|:|\!|\?|\.',' ',s), text))
    text = list(map(lambda s: collapse_whitespace(s), text))


    new_text = []
    new_text_punc = []
    init = 0
    for i in range(len(trans)-1):
        _words=trans[i].split(' ')
        id=_words[0]
        words = _words[1:]
        _words=trans[i+1].split(' ')
        words2 = _words[1:]
        utterance = ''
        test = False
        _start = len(words)-_interval[0]
        _end = len(words)+_interval[1]
        if len(words) < _interval[0]:
            _start = 1
        for t in range(init,init+_start):
            utterance += ' ' + text[t]
        find = text[init+_start:init+_end]
        # print(i, utterance)
        # print(i , ' '.join(words))
        # print(words2[0:_min_check_words])
        # print(' '.join(find))
        _init, count = findCount(words2,find)
        init = t + 1
        # print("words2", words2)
        # print("find", find)
        # print("count", count)
        if count < _min_count:
            # print("utterance", utterance)
            find = utterance.split(' ')
            find = list(filter(None, find))
            # print("find", find)
            _init, count = findCount(words2,find)
            init = init - (len(words) - 5)
            if count < _min_count:
                print('segment not found!!!!')
                print(utterance)
                print(i+1)
                exit()
            utterance = ''
        
        for t in range(init,init+_init):
            utterance += ' ' + text[t]
        init = t + 1
        
        
        utterance = utterance.strip().split(' ')
        newtrans = trans[i+1].split(' ')
        if newtrans[1] == "s'" and utterance[len(utterance) -1] == "c'":
            newtrans[1] = "c'"
            trans[i+1] = ' '.join(newtrans).strip()
            utterance = utterance[:-1]
            init -= 1
        
        utterance.insert(0,id)
        utterance = ' '.join(utterance).strip()
        
        # print(utterance)
        # print(trans[i])
        
        new_text.append(utterance)


        #new_text.append(id+' '+utterance.strip())


        if use_punctuation:
            utterance = utterance.strip().split(' ')
            nbr = len(utterance) - 1
            new_text_punc.append(id+' '+(' '.join(_text[0:nbr])).strip())
            _text = _text[nbr:]
        #print(i, utterance)

    if len(trans) == 1:
        id=trans[0].split(' ')[0]
    else:
        id=trans[i+1].split(' ')[0]

    new_text.append(id+' '+(' '.join(text[init:len(text)])).strip())

    if use_punctuation:
        new_text_punc.append(id+' '+(' '.join(_text)).strip())
    
    
    bad_utterances=[]
    trans_punc=[]
    trans_wer=[]
    for t in range(len(trans)):
        h = trans[t].split(' ')
        r = new_text[t].split(' ')
        h = list(filter(None, h))
        r = list(filter(None, r))
        wer, verif = WER(r,h)
        if verif:
            for i in range(len(trans[t])):
                if h[i] != r[i]:
                    break
            print(trans[t])
            print(new_text[t])
            if h[i] in _chiffres or h[i] in _chiffres_ordinaux:
                print(h[i], r[i])
            else:
                h = r
                wer = 0
        if use_punctuation:
            p = new_text_punc[t].split(' ')
            p[0] = ''
            p = list(map(lambda s: re.sub(r'[^,;:\!\?\.]','',s), p))
            if wer == 0:
                trans_punc.append(new_text_punc[t])
            else:
                #print(new_text_punc[t])
                indice=-1
                for i in range(len(p)):
                    if indice + 1 < len(h) and h[indice + 1] == r[i]:
                        indice += 1
                    elif indice + 2 < len(h) and h[indice + 2]  == r[i]:
                        indice += 2
                    elif indice + 3 < len(h) and h[indice + 3]  == r[i]:
                        indice += 3

                    # if i+2 < len(r) and indice+1 < len(h) and r[i] == "c'" and r[i+1] == "est" and h[indice] == r[i] and h[indice+1] == r[i +2]:
                    #     #print(h[indice], h[indice+1])
                    #     h.insert(indice+1, "est")

                    if p[i] != '':
                        pos = indice+2 if indice+2 < len(h) else len(h)
                        idx=[j+indice for j, x in enumerate(h[indice:pos]) if x == r[i]]
                        if len(idx) == 1:
                            h[idx[0]] += p[i]
                        else:
                            if i == len(r) -1 and h[len(h)-1] == r[i]:
                                h[len(h)-1] += p[i]
                            else:
                                idx=[j+indice for j, x in enumerate(h[indice:]) if x == r[i]]
                                for id in idx:
                                    if id+1 < len(h) and i+1 < len(r) and h[id-1] == r[i-1] and h[id+1] == r[i+1]:
                                        h[id] += p[i]
                                        break
                    if indice+1 == len(h) and r[i]+p[i] == h[indice]:
                        # if(len(r[i+1:len(r)]) != 0):
                        #     strs=r[0]+' '
                        #     strs+=' '.join(r[i+1:len(r)])
                        #     print(strs)
                        break
                #print(' '.join(h))
                trans_punc.append(' '.join(h))
        trans_wer.append(h[0]+' '+str(wer))
        if wer > args.wer:
            bad_utterances.append(t)

    
    # Save the wer of the transcription
    text_file = open(output_file+'/text_wer', 'w')
    for utt in trans_wer:
        text_file.write(utt+'\n')
    text_file.close()
    
    # Save the original text
    text_file = open(output_file+'/text_org', 'w')
    for utt in new_text:
        text_file.write(utt+'\n')
    text_file.close()
 
    if use_punctuation:
        # Save the original text with punctuation
        text_file = open(output_file+'/text_punc', 'w')
        for utt in new_text_punc:
            text_file.write(utt+'\n')
        text_file.close()

    # Save the transcription with WER <= _wer
    text_file = open(output_file+'/text_auto', 'w')
    for i in range(len(trans)):
        if not i in bad_utterances:
            text_file.write(trans[i]+'\n')
    text_file.close()

    if use_punctuation:
        # Save the transcription with punctuation with WER <= _wer
        text_file = open(output_file+'/text_auto-punc', 'w')
        for i in range(len(trans)):
            if not i in bad_utterances:
                text_file.write(trans_punc[i]+'\n')
        text_file.close()

    # Save the bad utterances with WER > _wer
    text_file = open(output_file+'/text_bad', 'w')
    for i in bad_utterances:
        text_file.write(new_text[i]+'\n')
        text_file.write(trans[i]+'\n')
    text_file.close()


    # Save the new utterances into a set of subfiles
    nj = args.nj
    if nj is not None:
        c=1
        for i in range(0,len(new_text),nj):
            text_file = open(args.split_output+'/text.'+str(c), 'w')
            id_file = open(args.split_output+'/id.'+str(c), 'w')
            spk2utt_file = open(args.split_output+'/spk2utt.'+str(c), 'w')
            text = ''
            hyp = ''
            if i != 0:
                h = new_text[i-1].split(' ')
                h = h[1:]
                text += ' '.join(h[-_word_overlap:]) + ' ' if len(h) > _word_overlap else ' '.join(h) + ' '
            if i + nj <= len(new_text) - 1:
                for j in range(nj):
                    h = new_text[i+j].split(' ')
                    r = trans[i+j].split(' ')
                    r = r[1:]
                    hyp += ' '.join(r) + ' '
                    text += ' '.join(h[1:]) + ' '
                    id_file.write(h[0]+'\n')
                    spk2utt_file.write(h[0]+' '+h[0]+'\n')
                if i + j < len(new_text) - 1:
                    h = new_text[i+j+1].split(' ')
                    h = h[1:]
                    text += ' '.join(h[:_word_overlap]) if len(h) > _word_overlap else ' '.join(h)
            else:
                for j in range(i,len(new_text),1):
                    h = new_text[j].split(' ')
                    r = trans[j].split(' ')
                    r = r[1:]
                    hyp += ' '.join(r) + ' '
                    text += ' '.join(h[1:]) + ' '
                    id_file.write(h[0]+'\n')
                    spk2utt_file.write(h[0]+' '+h[0]+'\n')
            
            lst = text.split(' ')
            lst = list(filter(None, lst))
            lst2 = hyp.split(' ')
            lst2 = list(filter(None, lst2))
            extra_words = [x for x in lst2 if x not in lst]
            
            text_file.write(text+'\n')
            text_file.write(hyp+'\n')
            #text_file.write(' '.join(extra_words)+'\n')
            
            c+=1

        text_file.close()
        id_file.close()
        spk2utt_file.close()
