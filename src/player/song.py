from dataclasses import dataclass


@dataclass
class Song:
    title: str
    path: str
    artist: str = None
    album: str = None
    thumbnail_path: str = None

    def __str__(self):
        """Return a string representation of the song."""
        return f"{self.artist} - {self.title} from {self.album}"

    def __eq__(self, other):
        return self.title == other.title and self.artist == other.artist and self.album == other.album

    def __hash__(self):
        return hash(self.title + self.artist + self.album)
