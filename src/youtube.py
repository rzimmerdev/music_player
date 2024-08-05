import re
from dataclasses import dataclass
from typing import List

import requests
from pytube import YouTube

from .song import Song, format_title


@dataclass
class Video:
    idx: int
    title: str
    author: str
    stream: str
    thumb: str

    def to_song(self, window=None) -> Song:
        return Song(self.title, self.author, self.stream, self.thumb, None, window)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Remote(metaclass=Singleton):
    def __init__(self):
        pass

    @staticmethod
    def attributes(video_id) -> Video:
        url = f"https://www.youtube.com/watch?v={video_id}"

        # attributes: title, author, url, thumb
        yt = YouTube(url)
        title = yt.title
        author = yt.author
        url = yt.watch_url
        thumb = yt.thumbnail_url

        return Video(video_id, title, author, url, thumb)

    def search(self, query, n=1) -> List[Video]:
        url = f"https://www.youtube.com/results?search_query={query}"
        response = requests.get(url)
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
        return [self.attributes(video_id) for video_id in video_ids[:n]]

    @classmethod
    def download(cls, video_id, directory="songs"):
        url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(url)
        filename = f"{format_title(yt.title)}.mp3"
        yt.streams.get_audio_only().download(f"{directory}", filename=filename)
        return filename

    @classmethod
    def get_stream(cls, video_id):
        url = f"https://www.youtube.com/watch?v={video_id}"
        yt = YouTube(url)
        return yt.streams.get_audio_only().url
