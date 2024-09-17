#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import requests
import json
import time
import tempfile
import subprocess
import contextlib
import wave

# Read sample rate of an audio file
def get_sample_rate(file):
    with contextlib.closing(wave.open(file,'r')) as f:
        rate = f.getframerate()
        return rate


# Convert audio file to wave file
def open_wav(file, freq):
    if not os.path.isfile(file):
        raise RuntimeError("Could not find file %s" % file)
    if file.endswith(".wav") and get_sample_rate(file) == freq:
        fname = file
    else:
        fname = tempfile.mktemp(suffix = ".wav")
        out = subprocess.run(["sox", file, "-t", "wav", "-r", str(freq), "-b", "16", "-c", "1", fname], stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        if out.returncode != 0:
            raise RuntimeError("Could not convert input file to wav. Make sure you have sox and libsox-fmt-mp3 installed")
    res = open(fname, 'rb').read()
    if fname != file:
        os.remove(fname)
    return res

def main(args):
    INGRESS_API = "{}/transcribe".format(args.transcription_server)
    JOB_API = "{}/job/".format(args.transcription_server)
    RESULT_API = "{}/results/".format(args.transcription_server)
    start_time = time.time()

    audio = open_wav(args.audio_file, args.freq)

    # Initial request
    try:
        response = requests.post(INGRESS_API, 
                                 headers={"accept":"application/json"},
                                 files = {"file": audio}
                                )
    except Exception as e:
        print(str(e))
        print("Failed to establish connexion at {}".format(INGRESS_API))
        exit(-1)

    if response.status_code != 200:
        print("Failed to join API at {} ({}: {}, {})".format(INGRESS_API, response.status_code, response.reason, response.text))
        exit(-1)
    
    result = json.loads(response.text)["text"]
    print("Process time = {:.2f}s".format(time.time() - start_time))
    if args.output_file is not None:
        try:
            with open(args.output_file, "w") as f:
                f.write(result)
            print(f"Result written at {args.output_file}")
        except Exception as e:
            print("Failed to write {}: {}".format(args.output_file, str(e)))
    else:
        print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Transcription request test')
    parser.add_argument('transcription_server', help="Transcription service API", type=str)
    parser.add_argument('audio_file', help="File to transcript", type=str)
    parser.add_argument('output_file', help="Write result in a file", default=None, nargs='?', type=str)
    parser.add_argument('--freq', help="reference frame rate", default=8000, type=int)
    
    args = parser.parse_args()

    main(args)