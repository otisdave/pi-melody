import os
import random
import subprocess
import threading
import time
import json

# Get the directory of the script
script_dir = os.path.dirname(__file__)

# Read configuration from JSON file
config_path = os.path.join(script_dir, 'config.json')
with open(config_path) as config_file:
    config = json.load(config_file)

# Total duration of the music in minutes
total_duration_minutes = config.get('total_duration_minutes', 20)

# Path to the folder containing the music files
music_folder = os.path.join(script_dir, 'melodies')

# Verify if the folder exists
if not os.path.exists(music_folder):
    print("The specified folder does not exist.")
    exit()

# Get the list of audio files in the folder
music_files = [f for f in os.listdir(music_folder)]

# Verify if audio files are available
if not music_files:
    print("No audio files found in the specified folder.")
    exit()

# Function to play music with MPV
def play_music():
    mpv_options = ['mpv', '--no-video']
    if config.get('quiet_mpv', False):
        mpv_options.append('--really-quiet')
    
    initial_volume = config.get('volume', 100)
    mpv_options.extend(['--volume=' + str(initial_volume)])

    if config.get('shuffle', False):
        mpv_options.append('--shuffle')

    while time.time() - start_time < total_duration_minutes * 60:
        # Randomly choose an audio file from the folder
        music_file = random.choice(music_files)
        music_path = os.path.join(music_folder, music_file)
        try:
            # Launch MPV to play the audio file
            subprocess.run(mpv_options + [music_path])
        except Exception as e:
            print(f"Error while playing the file {music_file}: {e}")
            continue

# Function to stop MPV and execute a custom command
def stop_script():
    time.sleep(total_duration_minutes * 60)
    os.system('pkill mpv')  # Stop all MPV processes
    end_script_command = config.get('end_script_command')
    if end_script_command is not None and end_script_command.strip() != '':
        os.system(end_script_command)  # Execute the custom command

# Start time counter
start_time = time.time()

# Start playing music in a separate thread
music_thread = threading.Thread(target=play_music)
music_thread.start()

# Start the thread to stop the music and execute the custom command after the total duration
stop_thread = threading.Thread(target=stop_script)
stop_thread.start()

# Wait for the music thread to finish
music_thread.join()

# Wait for the stop thread to finish (which should not happen if everything goes well)
stop_thread.join()
