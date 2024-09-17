# Introduction

This folder contains two scripts to run the transcription.
* One is a standalone python executable that loads the STT model each time it runs, and decode a file or a list of files
* One is a python executable that decode by doing a http request to a server that has been previously setup using https://github.com/linto-ai/linto-platform-stt

In a nutshell, what is needed can be installed with:
```
apt-get install python3 sox libsox-fmt-mp3
pip3 install vosk numpy wavio
```


## Standalone executable

Use `decoding/stt_standalone.py`, making sure that the paths to the trained model are the right ones (options `--am_path` and `--lm_path`).
If not either change the script to point to the right ones, or launch with non-default option values.

```
$decoding/stt_standalone.py -h

usage: stt_standalone.py [-h] [--output_file OUTPUT_FILE] [--am_path AM_PATH] [--lm_path LM_PATH] [--use_filename] input_file [input_file ...]

Standalone Speech-To-Text: Decode the text in one or several audio files

positional arguments:
  input_file            One or several input audio files

optional arguments:
  -h, --help            show this help message and exit
  --output_file OUTPUT_FILE
                        Output filename (if not specified, the results will be printed in stdout) (default: None)
  --am_path AM_PATH     Path to the accoustic model (default: /local_scratch/sbdc7b8n/models_trained/AcousticModel/ReleaseV2)
  --lm_path LM_PATH     Path to the language model (default: /local_scratch/sbdc7b8n/models_trained/LanguageModel/lm/graph)
  --use_filename        Whether to include the filename in the output (before each text transcription) (default: False)
```

## With HTTP server

### On a server where you have docker privilege

First launch the HTTP server, following the instructions of https://github.com/linto-ai/linto-platform-stt.
Basically:
```
docker pull lintoai/linto-platform-stt

cp .envdefault .env

docker run --rm \
-p 8080:80 \
-v /raid/sbdc7b8n/models_trained/AcousticModel/ReleaseV2:/opt/AM \
-v /raid/sbdc7b8n/models_trained/LanguageModel/lm/graph:/opt/LM \
--env-file .env \
--name lintoai_platform
linto-platform-stt:latest
```

Then either access `http://localhost:8080/docs` in a browser on the machine (or `http://<IP ADRESS>:8080/docs` on a remote machine), click "Try it out", upload a file and click on "Execute" to see the automatic transcription.
Or run on the command line:
```
decoding/stt_request.py http://localhost:8080 audio.mp3
```
(replacing localhost by the IP of the machine on a remote machine) where `audio.mp3` is the file you want to transcribe.
