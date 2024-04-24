import subprocess
import cv2
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip

def extract_frames_with_audio(video_path, output_dir):
    # Separate audio and video using ffmpeg
    audio_path = output_dir + "/audio.wav"
    video_path_no_audio = output_dir + "/final/video_no_audio.mp4"
    command = ["ffmpeg", "-i", video_path, "-vn", audio_path, "-an", video_path_no_audio]
    subprocess.run(command)

    # Open video capture for frame extraction
    cap = cv2.VideoCapture(video_path_no_audio)
    frame_rate = cap.get(cv2.CAP_PROP_FPS)
    print(f"{frame_rate} frames per second")

    if not frame_rate:
        raise ValueError("Failed to get frame rate from video.")

    frame_count = 0

    # Define output video details
    output_video_path = output_dir + "/final/stitched_video.mp4"
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = frame_rate
    input_file_list = output_dir + "/input_files.txt"

    audio_video_filenames = []
    while frame_count < 50:
        ret, frame = cap.read()

        if not ret:
            break

        # Calculate audio duration for current frame
        audio_duration = frame_count / frame_rate

        # Create output filename with frame number and timestamp in audio duration format (HH:MM:SS.sss)
        output_filename = f"{output_dir}/frame_{frame_count:04d}_{audio_duration:.3f}.mp4"
        audio_video_filenames.append(output_filename)

        command = ["ffmpeg", "-i", video_path_no_audio, "-ss", f"{audio_duration:.3f}", "-t", 
                   "0.001", "-c:v", "mpeg4", "-an", "-i", audio_path, 
                   "-ss", f"{audio_duration:.3f}", "-t", "0.001", "-c:a", "copy", output_filename]
        subprocess.run(command)

        # # Load the video and audio files
        # video = VideoFileClip(video_path_no_audio)
        # audio = AudioFileClip(audio_path)
        # # Set the audio of the video clip to the new audio file
        # final_clip = video.set_audio(audio)
        # final_clip.write_videofile(output_filename)
        
        frame_count += 1

    cap.release()

    # Create final stitched video using ffmpeg (combining all audio-video combinations)
    mp4_files = [file for file in os.listdir(output_dir) if file.endswith('.mp4')]
    
    # Create a list of VideoFileClip objects    
    os.chdir(output_dir)
    clips = [VideoFileClip(file) for file in mp4_files]

    # Concatenate the clips
    final_clip = concatenate_videoclips(clips)
    
    os.chdir('../')
    print('Guru - ' + os.getcwd())
    final_clip.write_videofile(output_video_path)

# Example usage
video_path = "video.mp4"
output_dir = "output"
extract_frames_with_audio(video_path, output_dir)
print("Frames and audio-video combinations extracted successfully!")
