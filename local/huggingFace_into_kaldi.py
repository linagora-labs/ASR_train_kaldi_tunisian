#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import soundfile
from tqdm import tqdm
from datasets import load_dataset
from kaldi_dataset import KaldiDataset              
                
def write_dataset(huggingface_dataset, kaldi_dir="kaldi", wavs_path="wavs", language=None, subset=None, trust_remote_code=False, set_name=None):
    subset = language if language is not None else subset
    if set_name is not None and set_name in ["train", "test", "validation", "dev"]:
        data = load_dataset(huggingface_dataset, name=subset, split=set_name, trust_remote_code=trust_remote_code, streaming=True)
        write_split(data, set_name, kaldi_dir, wavs_path, subset)
    else:
        splits = load_dataset(huggingface_dataset, trust_remote_code=trust_remote_code, name=subset, streaming=True)
        for split in splits:
            data = load_dataset(huggingface_dataset, trust_remote_code=trust_remote_code, name=subset, split=split, streaming=True)
            write_split(data, split, kaldi_dir, wavs_path, subset)

def write_split(split_data, split_name, kaldi_dir, wavs_path, subset=None):
    dataset = KaldiDataset()
    
    if subset is not None:
        wavs_path = os.path.join(wavs_path, subset)
        kaldi_dir = os.path.join(kaldi_dir, subset)
                
    if split_name is not None:
        kaldi_dir = os.path.join(kaldi_dir, split_name)
        
    for i, row in tqdm(enumerate(split_data), desc="Creating dataset"):
        id_ct = 0
        speaker = row['audio_id']
        sampling_rate = row['audio']['sampling_rate']
        
        if 'speaker_id' in row.keys():
            speaker = row['speaker_id'] 
          
        if subset is not None:
            speaker = f'{subset}_{speaker}'
            
        audio_id = row['audio_id']
        if wavs_path is not None:     
            # Check if the path exist in audio row if yes it take the name of the audio else it will get the audio id as audio name
            if row['audio']['path'] is not None:
                audio_name = os.path.basename(row['audio']['path'])
            else:
                audio_name = f"{audio_id}.wav"
                
            # get the wavs_path and create it if is not exist     
            audio_path = os.path.join(f'{wavs_path}/waves', split_name)
            os.makedirs(audio_path, exist_ok=True)
            
            audio_full_path = os.path.join(audio_path, audio_name)
            audio_array = row['audio']['array']
            
            if os.path.isdir(audio_path):
                soundfile.write(audio_full_path, audio_array, sampling_rate)
        else:
            raise ValueError(f"You have to put the Waves path!") 
        
        for seg in row['segments']:
            text = seg['transcript'].strip()
            if len(text)>1:
                kaldi_row = {
                    "id": f"{audio_id}_{id_ct}",
                    "speaker": speaker,
                    "audio_id": audio_id,
                    "audio_path": audio_full_path,
                    "text": text,
                    "start": seg['start'],
                    "end": seg['end']
                }
                dataset.append(kaldi_row)
                id_ct += 1
    dataset.save(kaldi_dir)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Download and convert a dataset HuggingFace to Kaldi")
    parser.add_argument("--dataset", type=str, default="linagora/SUMM-RE",help="Dataset name")
    parser.add_argument("--kaldi_path", type=str, default="SUMM-RE",help="Path to new Kaldi directory")
    parser.add_argument("--wavs_path", type=str, default=None,help="Path to store the audio files")
    parser.add_argument("--language", type=str, default=None,help="Language of the dataset if applicable")
    parser.add_argument("--subset", type=str, default=None,help="Language of the dataset if applicable")
    parser.add_argument("--trust_remote_code", action="store_true", default=False, help="Trust the remote code to run code locally. Default is False.")
    parser.add_argument("--split", type=str, default=None, help="Name of the set to convert (train, test, validation). If None, all sets are converted.")
    args = parser.parse_args()
    
    write_dataset(huggingface_dataset=args.dataset, kaldi_dir=args.kaldi_path, wavs_path=args.wavs_path, language=args.language, 
                  subset=args.subset, trust_remote_code=args.trust_remote_code, set_name=args.split)