from lang_trans.arabic import buckwalter
import unicodedata

ACCENT_TO_CODE = {
    '́': 'a', # acute accent
    '̀': 'g', # grave accent
    '̂': 'h', # hat
    '̈': 'd', # double dot
    '̧': 'c', # cedilla
}

CODE_TO_ACCENT = dict((v, k) for k, v in ACCENT_TO_CODE.items())

def augmented_bw_transliterate(text, to_lower_case=False, allow_punctuation=False):
    bw_text = buckwalter.transliterate(text)
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
        bw_text_augmented.append(f"{kind}{y}")
    return "".join(bw_text_augmented)


def augmented_bw_untransliterate(bw_text):
    text = []
    i = 0
    while i < len(bw_text):
        kind = bw_text[i]
        c = bw_text[i+1] if i < len(bw_text) - 1 else ""
        if kind == " ":
            step = 1
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
    parser = argparse.ArgumentParser(description='Transliterator augmentation bw (solve latin word problem)',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('input_file', help='File containing words to transliterate / untranslate', type=str)
    parser.add_argument('output_file', help='Output file', type=str)
    parser.add_argument('--ignore_ids', help="use it to ignore ids of text", default=False, action='store_true')
    parser.add_argument('-u', help='use it to translate',default=False, action="store_true")
    args = parser.parse_args()

    
    with open(args.input_file, "r", encoding="utf-8") as input_f, open(args.output_file, "w", encoding="utf-8") as output_f:
        for line in input_f:
            ids = ""
            line = line.strip()
            
            if args.ignore_ids:
                ids,line = line.split(' ', 1)
                ids+=" "
            if args.u:
                text = augmented_bw_untransliterate(line)
            else:
                text = augmented_bw_transliterate(line)    

            output_f.write(f'{ids}{text}\n')