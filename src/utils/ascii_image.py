from PIL import Image


class AsciiConverter:
    @classmethod
    def get_character(cls, pixel, ascii_characters):
        return ascii_characters[int(pixel / 255 * (len(ascii_characters) - 1))]

    @classmethod
    def convert_to_ascii(cls, image, ascii_characters, width):
        pixels = image.getdata()
        characters = [cls.get_character(pixel, ascii_characters) for pixel in pixels]

        rows = ["".join(characters[i:i + width]) for i in range(0, len(characters), width)]

        return "\n".join(rows)


class AsciiImage(AsciiConverter):

    def __init__(self, path, width: int = 100, ascii_characters: list[str] = None):
        self.path = path
        self.width = width

        if ascii_characters is None:
            self.ascii_characters = ["@", "#", "S", "%", "?", "*", "+", ";", ":", ",", "."]

    def load_image(self):
        image = Image.open(self.path)
        aspect_ratio = image.width / image.height
        image = image.resize((self.width, int(self.width / aspect_ratio)))

        return image

    def __str__(self):
        image = self.load_image()
        return self.convert_to_ascii(image, self.ascii_characters, self.width)