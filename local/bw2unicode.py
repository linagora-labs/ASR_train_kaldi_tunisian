from lang_trans.arabic import buckwalter as bw

def buckwalter_to_utf8(text):
    # Convert the Buckwalter text to UTF-8 Arabic text
    arabic_text = bw.untransliterate(text)
    return arabic_text

def utf8_to_buckwalter(text):
    # Convert the UTF-8 Arabic text to Buckwalter text
    arabic_text = bw.transliterate(text)
    return arabic_text

if __name__ == '__main__':

    import os
    import argparse
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input_file', help="An input file, or an input string", type=str, nargs="+")
    parser.add_argument('output_file', help="An output file", type=str)
    parser.add_argument('-i',help="To Ignore the ids",default=False,action="store_true", required=False)
    parser.add_argument('-r',help="To reverse translate utf8 into bw",default=False,action="store_true", required=False)
    args = parser.parse_args()

    input = args.input_file
    output = args.output_file

    with open(input[0], "r") as in_f, open(output, 'w') as out_f:
        for line in in_f:
            ids=""
            line = line.strip()
            if args.i:
                ids, line = line.split(' ', 1)
                ids+=" "
            if args.r:
               txt = utf8_to_buckwalter(line)
            else:     
                txt = buckwalter_to_utf8(line)
            out_f.write(f"{ids}{txt}\n")
