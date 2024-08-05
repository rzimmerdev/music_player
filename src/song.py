import os
import urllib.request

from PIL import Image, ImageEnhance, ImageFilter
from difflib import SequenceMatcher


class Song:
    def __init__(self, title, author, url, thumbnail_url, thumbnail=None, window=None, stream=None):
        self.title = title
        self.author = author
        self.url = url
        self._thumbnail = thumbnail
        self._thumbnail_url = thumbnail_url
        self.window = window
        self.stream = stream

    def __str__(self):
        return f"{self.title} - {self.author}"

    @property
    def thumbnail(self):
        # test if self.thumbnail is local or remote
        if self._thumbnail is None:
            # download the thumbnail
            title = format_title(self.title) + "_" + format_title(self.author)
            urllib.request.urlretrieve(self._thumbnail_url, f"thumb/{title}.jpg")
            self._thumbnail = f"thumb/{title}.jpg"
        return self._thumbnail

    @property
    def thumb_ascii(self):
        image = Image.open(self.thumbnail)
        screen_size = [dim // 1.4 for dim in self.window.size]
        # 0 if dim 0 (height) is smaller, 1 if dim 1 (width) is smaller
        if screen_size[0] < screen_size[1]:
            new_height = screen_size[0]
            new_width = new_height * 2
        else:
            new_width = screen_size[1]
            new_height = new_width // 2

        image = image.resize((int(new_width), int(new_height))).convert('L')
        # normalize the image between 0 and 1

        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))

        ascii_str = ""
        chars = list(" .:-=+*#%@")

        for y in range(image.height):
            for x in range(image.width):
                pixel = image.getpixel((x, y))
                ascii_str += chars[int(pixel / 255 * (len(chars) - 1))]
            ascii_str += "\n"

        return ascii_str

    def save(self):
        """Save to .zfy file"""
        with open(self.url + ".zfy", "w") as file:
            file.write(f"{self.title}\n"
                       f"{self.author}\n"
                       f"{self.url}\n"
                       f"{self._thumbnail_url}"
                       f"\n{self._thumbnail}"
                       f"\n")

    @classmethod
    def load(cls, file_path, window=None):
        with open(file_path, "r") as file:
            title = file.readline().strip()
            author = file.readline().strip()
            url = file.readline().strip()
            thumbnail_url = file.readline().strip()
            thumbnail = file.readline().strip()
        return cls(title, author, url, thumbnail_url, thumbnail, window)


def load_all() -> list[Song]:
    songs = []
    for file in os.listdir("songs"):
        if file.endswith(".zfy"):
            songs.append(Song.load(os.path.join("songs", file)))
    return songs


def search(songs, query, n=5):
    # get the best n matches
    matches = []

    for song in songs:
        title_ratio = SequenceMatcher(None, song.title, query).ratio()
        author_ratio = SequenceMatcher(None, song.author, query).ratio()
        matches.append((title_ratio + author_ratio, song))

    matches.sort(reverse=True)
    return [song for _, song in matches[:n]]


def format_title(title):
    return title.replace(" ", "_").replace(":", "").replace("?", "").replace("!", "").replace("'", "")
