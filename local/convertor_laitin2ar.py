import argparse
import json
import os
import re

char_dict={
    "a": "آآ",
    "b": "ببب",
    "c": "سسس",
    "d": "ددد",
    "e": "إإإ",
    "f": "ففف",
    "g": "ججج",
    "h": "ههش",
    "i": "إإي",
    "j": "ججي",
    "k": "ككك",
    "l": "لللل",
    "m": "آام",
    "n": "ننن",
    "o": "آووو",
    "p": "بببي",
    "q": "ققق",
    "r": "ررر",
    "s": "صصصص",
    "t": "تتت",
    "u": "يووو",
    "v": "فففف",
    "w": "دبليو",
    "x": "إكس",
    "y": "إغراغ",
    "z": "ززز",
    "á": "آآآ",
    "à": "آآآآآ",
    "é": "إإإإإ",
    "è": "إإإإإإ",
    "í": "إاإي",
    "ì": "إإإي",
    "ó": "آآوووو",
    "ò": "آآوووآو",
    "ú": "ييو",
    "ù": "يوو",
    "û": "ييوو",
    "â": "آهآآآ",
    "ê": "آيآآآ",
    "î": "إيإيإإ",
    "ô": "آوآ",
    "ç": "صصي",
    "'": "تقسم"
}
def find_key_by_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None 

def check_file_exists(file_path):
    return os.path.exists(file_path)

# def contains_latin_characters(word):
#     latin_pattern = re.compile(r"[a-zA-ZçáàéèíìóòúùâêîôûäëïöüÁÀÉÈÍÌÓÒÚÙÂÊÎÔÛÄËÏÖÜ']")
#     return bool(latin_pattern.search(word))

def extaract_latin_words(text):
    latin_pattern = re.compile(r"\b[a-zA-ZçáàéèíìóòúùâêîôûäëïöüÁÀÉÈÍÌÓÒÚÙÂÊÎÔÛÄËÏÖÜ']+\b")
    latin_words = latin_pattern.findall(text)
    return latin_words

def transliterate_word(word, char_dict):
    arabic_word = ""
    for char in word:
        for k, v in char_dict.items():
            if char in k:
                arabic_word += v
    return arabic_word

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transliterator Latin to Arabic characters',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('input_file', help='File containing words to transliterate (Latin or Arabic)', type=str)
    parser.add_argument('output_file', help='Output file (JSON format, {Latin_word:Arabic_word})', type=str)
    parser.add_argument('--dict_l2a', help="path to of dictionary that has the latin words and there transilitration on Arabic",default="~/Train_ASR_Kaldi/data/Dictionary_l2ar.json", type=str)
    parser.add_argument('--ignore_ids', help="use it to ignore ids of text", default=False, action='store_true')
    parser.add_argument('--reverse', help="Whether to convert Arabic words to Latin (default: Arabic to Latin)",default=False, action='store_true')
    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    reverse = args.reverse
    dict_l2a=args.dict_l2a
    transliteration_dict = {}
    latin_words=[]
    
    if not check_file_exists(input_file):
        print(f"Input file '{input_file}' does not exist.")
        exit()
        
    if check_file_exists(output_file):
        print(f"Output file '{output_file}' Already exist.")
        exit()
        
   
    
    with open(input_file, 'r', encoding='utf-8') as input_file,open(output_file, 'w', encoding='utf-8') as output_file :
        ids=""
        if not reverse:
            for line in input_file:
                if args.ignore_ids:
                    ids, line = line.split(' ', 1)
                    ids+=" "
                words = line.strip().split()
                sentence = ""
                with open(dict_l2a, 'w', encoding='utf-8') as dict_l2ar:
                    latin_words.extend(extaract_latin_words(line.lower())) 
                    trans_words = [transliterate_word(word,char_dict) for word in latin_words]
                    for k,v in zip(latin_words,trans_words):
                        transliteration_dict[k] = v
                    sorted_transliteration_dict = sorted(transliteration_dict.items())
                    for word in words:
                        if word in transliteration_dict.keys():
                            sentence += transliteration_dict[word] +" "
                        else:
                            sentence += word + " "
                    output_file.write(f"{ids}{sentence}\n")
                    output_file.flush()
                    json.dump(sorted_transliteration_dict, dict_l2ar, ensure_ascii=False, indent=4)
            print(len(sorted_transliteration_dict),":WORD LATIN FOUND")
        elif reverse:
            if not check_file_exists(dict_l2a):
                print(f"Dictionary file '{dict_l2a}' does not exist.")
                exit()  
                    
            with open(dict_l2a, 'r', encoding='utf-8') as dict_l2ar:
                dict_Latin2AR = json.load(dict_l2ar)
                dictionary_data = {pair[0]: pair[1] for pair in dict_Latin2AR}
                
            for line in input_file:
                if args.ignore_ids:
                    ids, line = line.split(' ', 1)
                    ids+=" "
                words = line.strip().split()
                sentence = ""
                for word in words:
                    latin_word = find_key_by_value(dictionary_data, word)
                    if latin_word is not None:
                        sentence += latin_word +" "
                    else:
                        sentence += word + " "
                    
                output_file.write(f"{ids}{sentence}\n")
                output_file.flush()