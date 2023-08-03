import os
import sys
from pytube import YouTube
import requests
from moviepy.editor import AudioFileClip
import eyed3


def download_video(video_url, folder):
    try:
        yt = YouTube(video_url)

        folder_path = os.path.join(os.getcwd(), folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        print("Downloading:", yt.title)

        audio_stream = yt.streams.filter(only_audio=True).first()

        out = audio_stream.download(output_path=folder_path, filename=yt.title)

        base, ext = os.path.splitext(out)
        audio_file = base + '.mp3'

        # Convert the audio to MP3 format using moviepy
        audio_clip = AudioFileClip(out)
        audio_clip.write_audiofile(audio_file, codec='mp3', verbose=False)
        audio_clip.close()

        os.remove(out)  # Remove the original file

        print("Downloaded:", yt.title)
        print("Saving metadata:", yt.title)

        audio = eyed3.load(audio_file)
        if audio.tag is None:
            audio.initTag()

        audio.tag.title = yt.title
        audio.tag.artist = yt.author

        thumbnail_url = yt.thumbnail_url
        thumbnail_response = requests.get(thumbnail_url)
        thumbnail_data = thumbnail_response.content

        audio.tag.images.set(3, thumbnail_data, 'image/jpeg', u"Front cover")

        audio.tag.save()

        print("Metadata saved:", yt.title)

    except ConnectionError as e:
        print("Error:", e)


def main():
    if len(sys.argv) != 2:
        print("Usage: python youtube_download.py <video_url>")
        return

    video_url = sys.argv[1]
    download_video(video_url, "songs")


if __name__ == "__main__":
    main()
