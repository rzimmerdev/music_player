from __future__ import unicode_literals

from pprint import pprint

import yt_dlp


def main():

    urls_file = "playlist_urls"
    file = open(urls_file, 'r')
    song_urls = file.readlines()

    ydl_opts = {
        'outtmpl': 'downloads/%(playlist_index)s.%(title)s.%(ext)s',
        'format': 'bestaudio/best',

        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192'
        }],
        'postprocessor_args': [
            '-ar', '16000'
        ],
        'prefer_ffmpeg': True,
        'keepvideo': False
    }

    ydl = yt_dlp.YoutubeDL(ydl_opts)
    with ydl:
        for url in song_urls:
            url = url.rstrip('\n')
            info = ydl.extract_info(url)


if __name__ == "__main__":
    main()
