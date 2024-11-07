import librosa
import numpy as np
import pandas as pd
import os

# https://www.kaggle.com/code/super13579/mfcc-feature-extraction
# https://github.com/rctatman/getMFCCs/blob/master/getMFCCs.py
# https://www.youtube.com/watch?v=WJI-17MNpdE

def extract_and_save_mfcc(input_dir, output_base_dir):
    # Iterate through each accent type folder
    for accent_type in os.listdir(input_dir):
        accent_dir = os.path.join(input_dir, accent_type)
        if not os.path.isdir(accent_dir):
            continue
        
        # Create corresponding output directory
        output_dir = os.path.join(output_base_dir, accent_type)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Process each audio file in the accent directory
        for file in os.listdir(accent_dir):
            if file.endswith('.wav'):
                file_path = os.path.join(accent_dir, file)
                print(f"Processing: {file_path}")
                
                # Load the audio file
                y, sr = librosa.load(file_path, sr=None)
                
                # Extract MFCC features
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)

                print(mfcc.shape)
                
                # Convert the MFCC 2D array to a DataFrame
                mfcc_df = pd.DataFrame(mfcc)

                # Save the MFCC features as a .csv file, {file_name.csv}.
                mfcc_file_path = os.path.join(output_dir, f"{os.path.splitext(file)[0]}.csv")
                mfcc_df.to_csv(mfcc_file_path, index=False)
                print(f"Saved MFCC features to: {mfcc_file_path}")

input_directory = "test_cleaned_audio_segments"
output_directory = "test_cleaned_audio_features"
extract_and_save_mfcc(input_directory, output_directory)
