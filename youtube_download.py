import os
import sys
import re

import lyricsgenius
from pytube import YouTube, Playlist
import requests
from moviepy.editor import AudioFileClip
import eyed3
from getpass import getpass

from pytube.exceptions import RegexMatchError


def update_metadata(path, title=None, author=None, thumbnail_url=None, lyrics=None):
    audio = eyed3.load(path)
    if audio.tag is None:
        audio.initTag()

    thumbnail_url = thumbnail_url
    thumbnail_response = requests.get(thumbnail_url)
    thumbnail_data = thumbnail_response.content

    audio.tag.title = title
    if author:
        audio.tag.artist = author
    if thumbnail_data:
        audio.tag.images.set(3, thumbnail_data, 'image/jpeg', u"Front cover")
    if lyrics:
        audio.tag.lyrics.set(lyrics)

    audio.tag.save()


def convert_to_mp3(title, path, folder="songs"):
    new_path = folder + "/" + title + '.mp3'

    # Convert the audio to MP3 format using moviepy
    audio_clip = AudioFileClip(path)
    audio_clip.write_audiofile(new_path, codec='mp3', verbose=False)
    audio_clip.close()

    os.remove(path)  # Remove the original file
    return new_path


def get_video(video_url, folder_path):
    yt = YouTube(video_url)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    formatted_title = re.sub('[^A-Za-z0-9 ]+', '', yt.title).replace(" ", "_")

    return yt, formatted_title


def download_video(video_url, folder="songs", overwrite=False, genius_object=None):
    folder_path = os.path.join(os.getcwd(), folder)

    try:
        yt, formatted_title = get_video(video_url, folder_path)

        if formatted_title + ".mp3" in os.listdir(folder_path):
            if overwrite:
                os.remove(os.path.join(folder_path, formatted_title + ".mp3"))
            else:
                print("Already downloaded ", yt.title, "\n")
                return

        audio_stream = yt.streams.filter(only_audio=True).first()
        raw_file = audio_stream.download(output_path=folder_path, filename=formatted_title)
        mp3_file = convert_to_mp3(formatted_title, raw_file, folder)

        lyrics = None
        if genius_object and yt.title:
            if yt.author:
                song = genius_object.search_song(yt.title, yt.author)
            else:
                song = genius_object.search_song(yt.title)

            lyrics = song.lyrics

        update_metadata(mp3_file, yt.title, yt.author, yt.thumbnail_url, lyrics)

        print("Finished saving ", yt.title, "\n")

    except (ConnectionError, OSError) as e:
        print(f"Error - couldn't download: {video_url}", e)
    except KeyboardInterrupt:
        yt, formatted_title = get_video(video_url, folder_path)
        print("\nPossibly corrupted file: ", os.path.join(formatted_title + ".mp3"))
        raise KeyboardInterrupt


def download_playlist(playlist_url, folder="songs", overwrite=False, genius_object=None):
    try:
        playlist = Playlist(playlist_url)
        folder_path = os.path.join(os.getcwd(), folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        for video_url in playlist.video_urls:
            download_video(video_url, folder, overwrite, genius_object)

    except ConnectionError as e:
        print("Error:", e)


def main():
    try:
        if len(sys.argv) < 2 or len(sys.argv) > 4 or "-h" in sys.argv:
            print("Usage: youtube_download.py [-g] [-u] <video_url>\n")
            return

        genius = None
        overwrite = False
        if "-g" in sys.argv:
            token = getpass("Genius API access token: \n")
            genius = lyricsgenius.Genius(token)
        if "-u" in sys.argv:
            overwrite = True

        url = sys.argv[-1]
        if "youtube.com/playlist" in url:
            download_playlist(url, "songs", overwrite, genius)
        else:
            download_video(url, "songs", overwrite, genius)
    except KeyboardInterrupt:
        print("\nExiting...")
    except RegexMatchError:
        print("Usage: youtube_download.py [-g] [-u] <video_url>\n")


if __name__ == "__main__":
    main()
