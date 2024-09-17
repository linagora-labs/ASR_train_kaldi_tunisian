from lang_trans.arabic import buckwalter
import unicodedata

ACCENT_TO_CODE = {
    '́': 'a', # acute accent
    '̀': 'g', # grave accent
    '̂': 'h', # hat
    '̈': 'd', # double dot
    '̧': 'c', # cedilla
    'ğ': 'g',  # Transliterate 'ğ' to 'g'
}

CODE_TO_ACCENT = dict((v, k) for k, v in ACCENT_TO_CODE.items())

def augmented_bw_transliterate(text, to_lower_case=False, allow_punctuation=False, separate_symbols=False):
    bw_text = buckwalter.transliterate(text)
    # if "*" in bw_text:
    #     bw_text = bw_text.replace('*','V')
    assert len(text) == len(bw_text)
    bw_text_augmented = []
    for x, y in zip(text, bw_text):
        if not allow_punctuation and not x.isalnum() and not x in ["'", "-", " "]:
            continue
        if x != y:
            assert x.lower() == x
            kind = "A"
        else:
            if to_lower_case:
                y = y.lower()
            chars = unicodedata.normalize('NFKD', y)
            assert len(chars) in [1, 2], f"Invalid character '{y}'"
            if len(chars) == 2:
                assert chars[1] in ACCENT_TO_CODE, f"Invalid character '{y}' -> {chars}"
                y = chars[0]
                kind = ACCENT_TO_CODE[chars[1]]
            elif y == " ":
                kind = ""
            else:
                kind = "L"
        assert (ord(y) >= 36 and ord(y) <= 126) or ord(y) == 32, f"Invalid character '{x}' -> '{y}'"
        if kind:
            assert (ord(kind) >= 36 and ord(kind) <= 126), f"Invalid character '{y}' -> '{kind}{y}'"
        if separate_symbols and len(bw_text_augmented):
            bw_text_augmented.append(" ")
        bw_text_augmented.append(f"{kind}{y}")
    return "".join(bw_text_augmented)


def augmented_bw_untransliterate(bw_text, separate_symbols=False):
    text = []
    i = 0
    while i < len(bw_text):
        kind = bw_text[i]
        c = bw_text[i+1] if i < len(bw_text) - 1 else ""
        if kind == " ":
            step = 1
            if not separate_symbols:
                text.append(" ")
        else:
            step = 2
            assert c.strip()
            if kind == "L":
                text.append(c)
            elif kind == "A":
                text.append(buckwalter.untransliterate(c))
            elif kind in CODE_TO_ACCENT:
                text.append(unicodedata.normalize('NFC', "".join([c, CODE_TO_ACCENT[kind]])))
            else:
                raise ValueError(f"Input text does not seem to be augmented buckwalter (invalid character {bw_text[i]} at position {i})")
        i += step
    return "".join(text)
        
if __name__ == "__main__":
    import argparse
    import os
    
    parser = argparse.ArgumentParser(description='Transliterator Latin to Arabic characters',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('input_file', help='File containing words to transliterate (Latin or Arabic)', type=str)
    parser.add_argument('output_path', help='Output lexicon path', type=str)

    args = parser.parse_args()

    input_file = args.input_file
    output_path = args.output_path

    unique_words = set()  # To keep track of unique words

    with open(input_file, "r", encoding='utf-8') as inp_f:
        for line in inp_f:
            words = line.strip().split()
            for w in words:
                if w not in unique_words:  # Check for duplicates
                    unique_words.add(w)
                    
    # Sort the lexicon
    sorted_lexicon = sorted(unique_words)
    print(len(sorted_lexicon))

    # Write sorted lexicon to a separate file if needed
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, "lexicon.txt")
    

    with open(output_file, 'w', encoding='utf-8') as sorted_out_f:
        for word in sorted_lexicon:
            bw_text = augmented_bw_transliterate(word, separate_symbols=True)
            sorted_out_f.write(f'{word}   {bw_text}\n')

    
    