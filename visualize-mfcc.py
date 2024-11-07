import numpy as np
import matplotlib.pyplot as plt
import librosa.display
import pandas as pd

def visualize_mfcc(mfcc_file_path):
    # Load the MFCC features from the .csv file
    mfcc_df = pd.read_csv(mfcc_file_path)

    # Convert DataFrame to NumPy array
    mfcc = mfcc_df.to_numpy()
    
    # Plot the MFCC features
    plt.figure(figsize=(10, 6))
    librosa.display.specshow(mfcc, x_axis='time')
    plt.colorbar(format='%+2.0f dB')
    plt.title('MFCC')
    plt.xlabel('Time (s)')
    plt.ylabel('MFCC Coefficients')
    plt.tight_layout()
    plt.show()

    # plt.figure(figsize=(10, 4))
    # librosa.display.specshow(mfcc, x_axis='time')
    # plt.colorbar(label='Amplitude (dB)')
    # plt.title('MFCC')
    # plt.xlabel('Time')
    # plt.ylabel('MFCC Coefficients')
    # plt.tight_layout()
    # plt.show()

mfcc_file = "test_cleaned_audio_features/Scottish/A BIG Discovery in Scotland’s Sma Glen_segment_0.csv"
visualize_mfcc(mfcc_file)
