# ASR_train_kaldi_tunisian

## Training Acoustic Models with Kaldi

This script facilitates the training of a TDNN-based chain model for speech recognition from scratch using the Kaldi toolkit. It streamlines the process of building various components essential for a complete ASR system.

## Key Features

- **Language Model (LM) Training:** Build an ARPA language model from scratch.
- **Dictionary Creation:** Generate a pronunciation dictionary required for the LM.
- **Acoustic Model (AM) Training:** Train an acoustic model for recognizing speech.
- **IVector Extraction:** Create IVector features for speaker adaptation.

## Prerequisites

Before using this script, ensure you have a Kaldi environment set up. You have two options:

1. **Prepare a Kaldi Container:** If you're using a containerized environment, make sure it has Kaldi pre-installed.
2. **Install Kaldi Locally:** If you're setting up Kaldi in your local workspace, follow the installation instructions provided in the Kaldi documentation.

   - **Kaldi ASR Toolkit:** [Kaldi Documentation](https://kaldi-asr.org/doc/)

   This documentation will guide you through the installation process, including dependencies and configuration.

## Model

You can find our public ASR model on Hugging Face: [linagora/linto-asr-ar-tn-0.1](https://huggingface.co/linagora/linto-asr-ar-tn-0.1)

## Language Model (LM)

A Language Model (LM) is a statistical model or neural network that predicts the likelihood of a sequence of words or tokens. It helps in understanding the structure and meaning of text by learning patterns and relationships within the language. In our case, we chose to work with statistical N-Gram Models, as Kaldi requires them for its operations.

**Statistical N-Gram Models:**  
These models predict the probability of a word based on the previous \(N-1\) words. For example, a bigram model considers the previous word, while a trigram model considers the previous two words. These models are simple but can be limited by their fixed context window.


## Acoustic Model (AM)

The Acoustic Model (AM) is a crucial component of an Automatic Speech Recognition (ASR) system, designed to model the relationship between audio signals and phonetic units (such as phonemes or subword units). It plays a vital role in converting spoken language into text by recognizing and transcribing audio input.

1. **Purpose:**
    - The AM’s primary function is to convert acoustic signals (audio features) into phonetic representations. This is achieved by learning the statistical relationship between audio features and phonetic units from a training dataset.

2. **Types of Models:**

    - Acoustic models can be based on various techniques, including:
        * Hidden Markov Models (HMMs)
        * Deep Neural Networks (DNNs)
        * Convolutional Neural Networks (CNNs)
        * Recurrent Neural Networks (RNNs)
        * Time Delay Neural Networks (TDNNs)
        * More recently, Transformer-based architectures

    - In the Tunisian model, we initially chose Gaussian Mixture Models (GMMs) because they are fundamental for building a model from scratch. We started with a monophone model and progressed to a triphone model. To enhance performance, we applied Linear Discriminant Analysis (LDA) and Maximum Likelihood Linear Transform (MLLT) techniques, followed by Speaker Adaptive Training (SAT) to improve robustness and accuracy across different speakers. Finally, we fine-tuned the model using a Time Delay Neural Network (TDNN)-based chain model to leverage its advanced capabilities for improved performance.
    
    - **Time Delay Neural Networks (TDNNs):** TDNNs are widely used in speech recognition due to their ability to model temporal dependencies in speech. TDNN-based chain models, a specific neural network architecture in the Kaldi speech recognition toolkit, combine TDNNs with chain training techniques. These models are effective in building robust speech recognition systems by learning discriminative features from large amounts of speech data and are particularly useful for handling large vocabulary speech recognition tasks.
    
    - **Overview of TDNN-based Chain Models:** TDNN-based chain models integrate TDNNs with chain training techniques. They are designed to learn discriminative features from speech data, making them well-suited for large vocabulary tasks. This approach improves the model's ability to handle diverse speech data and noisy environments.

3. **Architectures Used in Training:**
    - To produce the Tunisian model, we experimented with two architectures mentioned in the `run_tdnn.sh` script:
    
        * **TDNN13:** A TDNN architecture with 13 TDNN layers. It provides a balance between model complexity and performance, often used for baseline systems.
        
        * **TDNN17:** An extension of TDNN13 with additional layers (17 in total). This architecture captures more complex temporal patterns and can achieve better performance, especially in noisy environments or with diverse speech data.
        
        * **TDNN with Attention:** Incorporates attention mechanisms to focus on relevant parts of the input sequence, improving the model’s ability to handle long-term dependencies and varying input lengths.

    > **Conclusion:** We chose the TDNN13 model because it provided the best performance in terms of Word Error Rate (WER).

    - **Advantages of TDNN Architecture:**

        * **Temporal Context:** TDNNs can capture long-range temporal dependencies, which is beneficial for recognizing speech patterns over time.
        
        * **Discriminative Training:** Chain training allows for the modeling of discriminative features, improving the accuracy of phoneme or subword recognition.
        
        * **Flexibility:** TDNN-based chain models can be adapted to various languages and dialects, making them versatile for different speech recognition applications.

## Initialization and Configuration

### 1. Clone the Repository

First, clone the repository containing the script and necessary resources:

```bash
git clone https://github.com/linagora-labs/ASR_train_kaldi_tunisian.git
cd ASR_train_kaldi_tunisian

```

## How to Use

1) **Prepare Your Data:**
    - You can find our public datasets in HuggingFace: [linagora/linto-dataset-audio-ar-tn-0.1](https://huggingface.co/datasets/linagora/linto-dataset-audio-ar-tn-0.1) & [linagora/linto-dataset-audio-ar-tn-augmented-0.1](https://huggingface.co/datasets/linagora/linto-dataset-audio-ar-tn-augmented-0.1)
    - You can just follow this code to download all the data:
    ```bash 
    cd ASR_train_kaldi_tunisian

    python3 local/huggingFace_into_kaldi.py --dataset linagora/linto-dataset-audio-ar-tn-0.1 --kaldi <PATH/TO/SAVE/KALDI/DATA> --wavs_path <PATH/TO/SAVE/AUDIOS>

    python3 local/huggingFace_into_kaldi.py --dataset linagora/linto-dataset-audio-ar-tn-augmented-0.1 --kaldi <PATH/TO/SAVE/KALDI/DATA> --wavs_path <PATH/TO/SAVE/AUDIOS>    
    ```
    - You can use utils/combine_data.sh to combine all datasets at once.

    - If you want to use your own dataset, ensure it's in Kaldi format (e.g., text, wav.scp, segments, utt2dur, spk2utt, utt2spk). For more info, check this [link](https://kaldi-asr.org/doc/data_prep.html#data_prep_data_yourself).

  

2) **Build the Language Model:**
    - **To build a Language model from scratch you have to use the `train_lm.sh` script:**
        * **Set Up the Path:**
            
            - Edit the `sys` variable in the script to point to the parent directory of the **ASR_train_kaldi_tunisian** repository. This ensures that the script can locate the necessary tools and data.

        * **Understand the Options:**
            
            - Review the available command-line options in the script to customize its behavior. You can view the options by running the script with the -h or --help flag. Here are some key options:
                
                - `--input_text_file`: Specify the path to your input text file.
                -  `--ignore_ids`: Use this flag if your text file contains IDs that should be ignored.
                - `--arpa_basemodel`: Provide the path to an optional ARPA language model base for mixing.
                - `--language`: Set the language for the model (default is "ar" for Arabic).
                - `--order_lm`: Define the order of the language model (default is 4).
        
        * **Run the Script:**
            - Execute the script with your desired options to generate the language model. The script will handle:
                - Preparing the lexicon and dictionary.
                - Generating ARPA language models.
                - Mixing and pruning models if a base model is provided.
                - Converting the ARPA model to FST format.
    
    - **Example Usage**
    
    ```bash 
    cd /path/to/ASR_train_kaldi_tunisian
    ```

    * Using a base ARPA model: 
        
        ```bash 
        ./train_lm.sh --input_text_file /path/to/input.txt --arpa_basemodel /path/to/base_model.arpa --language 'YOUR-LANGUAGE'--order_lm 4
        ```

    * Training a model without a base ARPA model:

        ```bash 
        ./train_lm.sh --input_text_file /path/to/input.txt --language 'YOUR-LANGUAGE' --order_lm 4
        ```


3) **Train the Acoustic Model:**
    - **To build an Acoustic Model from scratch, use the `train_am.sh` script:**

        * **Set Up the Path & Parameters:**

            * Edit the sys variable in the script to point to the parent directory of the Kaldi scripts repository. This ensures that the script can locate the necessary tools and data.

            * Configure the number of jobs and other parameters as needed. Review the script and adjust the parameters according to your requirements.

            * Choose the architecture by modifying the architectur variable by selecting one from "tdnn13", "tdnn17", or "tdnn_attention" based on your performance needs.

    - **Example Usage:**
        
        ```bash 
        cd /path/to/ASR_train_kaldi_tunisian
        ```

        * Run the train_am.sh script with your training dataset:
 
            ```bash
            ./train_am.sh  /path/to/your/training-dataset
            ```

3) **Evaluation:**

    * **To evaluate the ASR system you have to use `run_eval.sh` script:**
        * >  **NB:** You have to prepare a model folder contain:
            - am : Acoustic model (exist in: `ASR_train_kaldi_tunisian/exp/chain*/tdnn*`).
            - graph: graph generated after AM training (exist in: `exp/chain*/tree*/graph`).
            - conf: config folder you will find it in the ASR_train_kaldi_tunisian repo.
            - ivector: it's generated during the `TDNN` training (exist in: `exp/nnet3*/extractor`)

    * **Example Usage:**

        ```bash 
        cd /path/to/ASR_train_kaldi_tunisian
        ```
        - Run the evaluation with the following command:
            
            ```bash
            ./run_eval.sh  /path/to/your/test-dataset /path/to/your/model-folder
            ```