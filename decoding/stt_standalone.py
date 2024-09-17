#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

USE_SCIPY = False
if USE_SCIPY:
    from scipy.io import wavfile
else:
    import wave
import numpy as np
from vosk import Model, KaldiRecognizer

import os, shutil
import subprocess, tempfile
import hashlib

# Hash to a string:
def hash256(x):
    return hashlib.sha256(x.encode('utf-8')).hexdigest()

# Convert an audio file to frame rate and bytes:
def file_to_bytes(file_path, force_convert= False):
    tmp_file_path = None
    if force_convert or not file_path.endswith(".wav"):
        tmp_file_path = tempfile.mktemp(suffix = ".wav")
        cmd = ["sox", file_path, "-t", "wav", "-r", "8000", "-b", "16", "-c", "1", tmp_file_path]
        out = subprocess.run(cmd, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        if out.returncode != 0:
            raise RuntimeError("Could not convert input file to wav. Make sure you have sox and libsox-fmt-mp3 installed")
        file_path = tmp_file_path

    if USE_SCIPY:
        try:
            sample_rate, audio = wavfile.read(file_path)
        except:
            if force_convert:
                raise RuntimeError("Could not read wav file")
            return file_to_bytes(file_path, True)
        # Convert stereo to mono:
        if len(audio.shape) == 2 and audio.shape[1] == 2:
            audio = np.mean(audio, axis = 1, dtype = np.int16)

        audio = audio.tobytes()

    else:
        try:
            with wave.open(file_path, "rb") as f:
                sample_rate = f.getframerate()
                audio = f.readframes(-1)
                
                # Convert stereo to mono:
                if f.getnchannels() == 2:
                    dtype = {1: np.int8, 2: np.int16, 4: np.int32 }.get(f.getsampwidth())
                    audio = np.fromstring(audio, dtype = dtype)
                    audio = audio.reshape(audio.shape[0]//2, 2)
                    audio = np.mean(audio, axis = 1, dtype = np.int16)
                    audio = audio.tobytes()
        except wave.Error:
            if force_convert:
                raise RuntimeError("Could not read wav file")
            return file_to_bytes(file_path, True)

    if tmp_file_path:
        os.remove(tmp_file_path)

    return sample_rate, audio

# Read a mp3 file and convert it to wav:
def mp3_to_wav(mp3_path, wav_path):
    os.system("mpg123 -w {} {}".format(wav_path, mp3_path))
    return wav_path

def linagora2vosk(am_path, lm_path):
    conf_path = am_path + "/conf"
    ivector_path = am_path + "/ivector_extractor"

    vosk_path = os.path.join(tempfile.gettempdir(), hash256(str([am_path, lm_path, conf_path, ivector_path])))
    if os.path.isdir(vosk_path):
        shutil.rmtree(vosk_path)
    os.makedirs(vosk_path)
    for path_in, path_out in [
            (am_path, "am"),
            (lm_path, "graph"),
            #(conf_path, "conf"),
            #(ivector_path, "ivector"),
        ]:
        path_out = os.path.join(vosk_path, path_out)
        if os.path.exists(path_out):
            os.remove(path_out)
        os.symlink(path_in, path_out)

    new_ivector_path = os.path.join(vosk_path, "ivector")
    os.makedirs(new_ivector_path)
    for fn in os.listdir(ivector_path):
        os.symlink(os.path.join(ivector_path, fn), os.path.join(new_ivector_path, fn))
    if not os.path.exists(os.path.join(new_ivector_path, "splice.conf")):
        os.symlink(os.path.join(conf_path, "splice.conf"), os.path.join(new_ivector_path, "splice.conf"))

    phones_file = os.path.join(am_path, "phones.txt")
    with open(phones_file, "r") as f:
        silence_indices = []
        for line in f.readlines():
            phoneme, idx = line.strip().split()
            if phoneme.startswith("SIL") or phoneme.startswith("NSN"):
                silence_indices.append(idx)

    new_conf_path = os.path.join(vosk_path, "conf")
    os.makedirs(new_conf_path)
    os.symlink(os.path.join(conf_path, "mfcc.conf"), os.path.join(new_conf_path, "mfcc.conf"))
    with open(os.path.join(new_conf_path, "model.conf"), "w") as f:
        # cf. steps/nnet3/decode.sh
        print("""
    --min-active=200
    --max-active=7000
    --beam=13.0
    --lattice-beam=6.0
    --frames-per-chunk=51
    --acoustic-scale=1.0
    --frame-subsampling-factor=3
    --extra-left-context-initial=1
    --endpoint.silence-phones={}
    --verbose=-1
        """.format(":".join(silence_indices)), file=f)
#--endpoint.silence-phones=1:2:3:4:5:6:7:8:9:10

    return vosk_path

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Standalone Speech-To-Text: Decode the text in one or several audio files',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('input_file', help="One or several input audio files", default= None, nargs='+', type=str)
    parser.add_argument('--output_file', help="Output filename (if not specified, the results will be printed in stdout)", default=None, type=str)
    parser.add_argument('--am_path', help="Path to the accoustic model", type=str, 
        default= "/home/jlouradour/models/RecoFR/EDF_AM_fr-FR" # "/local_scratch/sbdc7b8n/models_trained/AcousticModel/ReleaseV2"
    )
    parser.add_argument('--lm_path', help="Path to the language model", type=str,
        default= "/home/jlouradour/models/RecoFR/decoding_graph_fr-FR_EDF" # "/local_scratch/sbdc7b8n/models_trained/LanguageModel/lm/graph"
    )
    parser.add_argument('--use_filename', help="Whether to include the filename in the output (before each text transcription)", default=False, action="store_true")
    args = parser.parse_args()

    if args.output_file and os.path.exists(args.output_file):
        raise RuntimeError("Output file already exists. Please remove it first.\nrm %s" % args.output_file)
    fout = open(args.output_file, 'w') if args.output_file else None
    for file_path in args.input_file:
        if not os.path.isfile(file_path):
            raise RuntimeError("Missing input file %s" % file_path)

    if not args.am_path and not args.lm_path:
        vosk_path = "/home/jlouradour/.cache/vosk/vosk-model-small-fr-0.22/"
    else:
        vosk_path = linagora2vosk(args.am_path, args.lm_path)
    model = Model(vosk_path)

    rate0 = None
    for i, file_path in enumerate(args.input_file):
        rate, data = file_to_bytes(file_path)
        if rate0 != rate:
            recognizer = KaldiRecognizer(model, rate)
            rate0 = rate
        recognizer.AcceptWaveform(data)
        output = recognizer.FinalResult()
        output = eval(output)["text"]
        if args.use_filename:
            output = "{} {}".format(os.path.splitext(os.path.basename(file_path))[0], output)
        print(output, file = fout)
        if fout is not None:
            fout.flush()

    shutil.rmtree(vosk_path)
