import cv2
from moviepy.editor import VideoFileClip, ImageSequenceClip, AudioFileClip, CompositeAudioClip
import os
import shutil
import random

# 1. Input video file
video_file = "video.mp4"

# 2. Get frame rate of the video
video = VideoFileClip(video_file)
frame_rate = video.fps
print(f"Frame rate: {frame_rate} frames per second")

# 3. Separate audio and video
video_clip = video.without_audio()
audio_clip = video.audio

# 4. Extract each frame of the video along with audio
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

categories = ['batting', 'bowling', 'fielding', 'others']
for category in categories:
    category_dir = os.path.join(output_dir, category)
    os.makedirs(category_dir, exist_ok=True)

count = 0
for frame in video_clip.iter_frames():
    # 2. Generate a random number from 0 to 3
    random_category = random.randint(0, 3)
    category = categories[random_category]

    category_dir = os.path.join(output_dir, category)

    # Save frame and audio
    frame_file = os.path.join(category_dir, f"frame_{count}.png")
    cv2.imwrite(frame_file, frame)

    start_time = count / frame_rate
    end_time = (count + 1) / frame_rate
    audio_clip_segment = audio_clip.subclip(start_time, end_time)
    audio_file = os.path.join(category_dir, f"audio_{count}.mp3")
    audio_clip_segment.write_audiofile(audio_file)

    count += 1

print(f"Extracted {count} frames to {output_dir}")

# 5. Stitch video and audio clips in each category folder
for category in categories:
    category_dir = os.path.join(output_dir, category)

    # Get a list of frame files in the category directory
    frame_files = [os.path.join(category_dir, f) for f in os.listdir(category_dir) if f.endswith('.png')]
    frame_files.sort()  # Sort the list of frame files

    video_clip = ImageSequenceClip(frame_files, fps=frame_rate)

    audio_files = [os.path.join(category_dir, f) for f in os.listdir(category_dir) if f.endswith('.mp3') and not f.startswith('audio_')]
    audio_files.sort()  # Sort the list of audio files
    audio_clips = [AudioFileClip(audio_file) for audio_file in audio_files]

    # Check if audio_clips list is not empty
    if audio_clips:
        combined_audio = CompositeAudioClip(audio_clips)
        final_clip = video_clip.set_audio(combined_audio)
        combined_audio.close()
    else:
        final_clip = video_clip

    output_video = os.path.join(category_dir, f"{category}_video.mp4")
    final_clip.write_videofile(output_video)

    print(f"Final video saved as: {output_video}")

    # Close the audio clips
    for audio_clip in audio_clips:
        audio_clip.close()

# Close the video and audio clips
video.close()
audio_clip.close()