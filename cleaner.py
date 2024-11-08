from pydub import AudioSegment
from pydub import silence
import noisereduce as nr
import librosa
import soundfile as sf
from scipy.signal import butter, lfilter
import numpy as np
import glob
import os

# What is the point of doing this, the original mp3 file has more sampling rate and therefore the audio quality is much better, also
# the size is smaller. For feature extraction maybe ? ( wav files are more compatible with feature extraction for model, so it's faster
# to process. )
def convert_to_wav(input_file, output_file, sample_rate=16000):
    """
    Converts the mp3 file to wav format.
    
    Parameters:
    - input_file: Path to the input audio file
    - output_file: Path to save the output file
    - sample_rate: Sampling rate of the wav file ( 16Khz by default. )
    """

    # Load the mp3 file
    print(f"Converting {input_file} to {output_file}...")
    audio = AudioSegment.from_file(input_file)

    #print(audio.frame_rate)

    # Set sample rate and convert to mono. Default sr is 44.1Khz, when we reduce it to 16Khz it also reduces the audio file's quality and size.
    # By reducing the number of channels from 2 (stereo) to 1 (mono), it decreases the amount of data to be processed, which increases efficiency.
    # https://cloud.google.com/speech-to-text/docs/best-practices-provide-speech-data
    audio = audio.set_frame_rate(sample_rate).set_channels(1)

    # Export as wav file
    audio.export(output_file, format="wav")
    print(f"Converted {input_file} to {output_file}.")

def normalize_audio(input_file, output_file, target_dBFS=-20.0):
    """
    Normalizes the audio and saves it as output_file in wav format.
    
    Parameters:
    - input_file: Path to the input audio file
    - output_file: Path to save the output file
    """

    print(f"Normalizing {input_file}...")
    audio = AudioSegment.from_file(input_file)

    # Average amplitude is -20 dBFS.
    # https://stackoverflow.com/questions/42492246/how-to-normalize-the-volume-of-an-audio-file-in-python
    change_in_dBFS = target_dBFS - audio.dBFS
    normalized_audio = audio.apply_gain(change_in_dBFS)
    normalized_audio.export(output_file, format="wav")
    print(f"Normalized {input_file} and saved to {output_file}.")

def remove_silence(input_file, output_file, silence_thresh=-55, min_silence_len=1000):
    """
    Removes silence from an audio file and saves it as output_file in wav format.
    
    Parameters:
    - input_file: Path to the input audio file
    - output_file: Path to save the output file
    - silence_thresh: The silence threshold (in dBFS)
    - min_silence_len: Minimum length of silence (in milliseconds) to be considered for trimming
    """

    print(f"Processing {input_file} to remove silence...")
    
    # Load the audio file
    audio = AudioSegment.from_file(input_file)
    
    
    # It looks like the silence threshold is specified in dBFS, or decibels relative to full scale. In other words, 0 dB is the loudest 
    # possible volume for the audio sample, and it goes down from there. Decibels are a logarithmic scale, so -10dB would be equivalent 
    # to 1/10th of full volume, -20dB is 1/100th of full volume, -30 is 1/1000th, and so on.
    # As the value goes up, the parts that will be considered as 'silent' will be much more.

    # Detect non-silent chunks
    nonsilent_chunks = silence.detect_nonsilent(
        audio, 
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh
    )
    
    # If no nonsilent chunks are detected, keep the original audio
    if not nonsilent_chunks:
        print(f"No silence detected in {input_file}. Saving the original audio.")
        audio.export(output_file, format="wav")
        return
    
    # Combine the non-silent chunks
    processed_audio = AudioSegment.empty()
    for start, end in nonsilent_chunks:
        processed_audio += audio[start:end]
    
    # Save the processed audio
    processed_audio.export(output_file, format="wav")
    print(f"Silence removed and audio saved to {output_file}.")

def reduce_noise(input_file, output_file, noise_reduction_strength=1):
    """
    Reduces the noise in an audio file and writes it to output_file.
    
    Parameters:
    - input_file: Path to the input audio file
    - output_file: Path to save the output file
    - noise_reduction_strength: The proportion to reduce the noise by (1.0 = 100%), by default 1.0
    """

    print(f"Reducing noise in {input_file}...")
    audio, sr = librosa.load(input_file, sr=None)

    # Default value for prop_decrease is 1.
    reduced_noise = nr.reduce_noise(y=audio, sr=sr, prop_decrease=noise_reduction_strength)
    sf.write(output_file, reduced_noise, sr)
    print(f"Noise reduced in {input_file} and saved to {output_file}.")

def clean_audio_dataset(input_dir, output_dir):
    """
    Cleans the audio data-set with .mp3 files and saves the files into output_dir.
    
    Parameters:
    - input_dir: Path to the input audio dataset (Only mp3 files.)
    - output_dir: Path to the output audio dataset (Converts it into .wav format)
    """

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Look for .mp3 files
    for file in glob.glob(os.path.join(input_dir, "*.mp3")):  
        base_name = os.path.basename(file)
        
        # Defining the output wav file with the original mp3 file's name.
        wav_file = os.path.join(output_dir, base_name.replace('.mp3', '.wav'))
        
        # Create a temp wav file and save the original mp3 audio to this.
        # Process the temp.wav file.
        # Finally, save the temp.wav as wav_file with the original mp3 file's name.
        temp_file = os.path.join(output_dir, "temp.wav")
        
        # Change to .wav format, resample, remove silence, reduce noise, normalize audio, split the audio into 5 second segments (split-audio.py),
        # MFCC feature extraciton (mfcc-feature-extraction.py)
        # This will do.
        convert_to_wav(file, temp_file)
        remove_silence(temp_file, temp_file)
        reduce_noise(temp_file, temp_file, noise_reduction_strength=0.5)
        normalize_audio(temp_file, wav_file)
        
        # Remove temp file after processing
        os.remove(temp_file)
        print(f"Finished processing {file}.\n")

clean_audio_dataset("audio_files/Australian", "cleaned_audio_files/Australian")