from pydub import AudioSegment
import os
import glob

def split_audio_files(folder_path, accent_type, segment_length_ms=5000, output_dir='cleaned_audio_segments'):
    """
    Splits the audio into segments and saves it to output_base_dir.
    
    Parameters:
    - folder_path: Path to the input audio dataset (Only wav files.)
    - accent_type: Type of accent in the audio dataset
    - segment_length_ms: Segment length for each audio
    - output_dir: Path to the output audio dataset
    """
    try:
        # Get a list of all .wav files in the specified folder
        audio_files = glob.glob(os.path.join(folder_path, "*.wav"))
        
        # Create output directory if it doesn't exist with given accent_type.
        # claned_audio_segments/{accenty_type}
        output_dir = os.path.join(output_dir, accent_type)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for audio_file in audio_files:
            audio = AudioSegment.from_file(audio_file)
            # Get the total_length of the audio file in ms.
            total_length = len(audio)
            segment_count = 0
            
            for i in range(0, total_length, segment_length_ms):
                segment = audio[i:i + segment_length_ms]

                # Create a segment file in the output_dir with the name of the wav input file and replace the first '.' part with
                # _segment_{segment_count} and save the segment into it.
                segment_file = os.path.join(output_dir, f"{os.path.basename(audio_file).split('.')[0]}_segment_{segment_count}.wav")
                segment.export(segment_file, format='wav')
                segment_count += 1
                print(f"Exported: {segment_file}")
        
        print("Audio splitting completed.")
    except Exception as e:
        print(f"Error splitting audio: {e}")

folder_path = "cleaned_audio_files/Australian"
accent_type = "Australian"
split_audio_files(folder_path, accent_type)