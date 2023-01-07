import math
import random

from PIL import Image

"""
Highly inspired by this tutorial : https://rtouti.github.io/graphics/perlin-noise-algorithm
"""


#  Returns a flattened (near 0 and 1) version of an inputted value
def _fade(t: float | int) -> int | float:
    #  Only handle values between 0 and 1
    #  Entering a value < 0.5 will return a value closer to 0
    #  Entering a value > 0.5 will return a value closer to 1
    #  Entering 0.5 will return 0.5
    return ((6 * t - 15) * t + 10) * t * t * t


#  Returns a constant vector from an inputted integer
def _get_constant_vect(value: int) -> tuple[int, int]:
    vect = tuple()
    match value % 4:
        case 0:
            vect = (1.0, 1.0)
        case 1:
            vect = (-1.0, 1.0)
        case 2:
            vect = (-1.0, -1.0)
        case 3:
            vect = (1.0, -1.0)
    return vect


# Returns the dot product of 2 vectors of coordinates (x; y)
def _dot_product_2d(vect1: tuple, vect2: tuple) -> float:
    return vect1[0] * vect2[0] + vect1[1] * vect2[1]


#  Returns a value that lies the 2 inputted ones
def _linear_interpolation(t: float, value1: int | float, value2: int | float) -> float:
    return value1 + t * (value2 - value1)


#  Returns a float value between -1 and 1 for an inputted point of coordinates (x; y)
#  pt : the permutation table
#  border_size : the size of a side of your canvas, assuming it's a square
def _noise_2d(x: int | float, y: int | float, pt: list[int], border_size: int) -> float:
    gX = math.floor(x) % border_size
    gY = math.floor(y) % border_size
    xf = x - math.floor(x)
    yf = y - math.floor(y)

    # 4 corner vector relative to the point (x, y)
    top_left_vect = (xf, yf - 1.0)
    top_right_vect = (xf - 1.0, yf - 1.0)
    bottom_left_vect = (xf, yf)
    bottom_right_vect = (xf - 1.0, yf)

    # pick a value in the permutation table for the 4 corners
    top_left = pt[pt[gX] + gY + 1]
    top_right = pt[pt[gX + 1] + gY + 1]
    bottom_left = pt[pt[gX] + gY]
    bottom_right = pt[pt[gX + 1] + gY]

    # dot product of the corner point value in the permutation table as a constant vector and corner vector
    dot_top_left = _dot_product_2d(_get_constant_vect(top_left), top_left_vect)
    dot_top_right = _dot_product_2d(_get_constant_vect(top_right), top_right_vect)
    dot_bottom_left = _dot_product_2d(_get_constant_vect(bottom_left), bottom_left_vect)
    dot_bottom_right = _dot_product_2d(_get_constant_vect(bottom_right), bottom_right_vect)

    u = _fade(xf)
    v = _fade(yf)

    n = _linear_interpolation(u,
                              _linear_interpolation(v, dot_bottom_left, dot_top_left),
                              _linear_interpolation(v, dot_bottom_right, dot_top_right)
                              )

    return n


class Noise:

    def __init__(self):
        self.width = 100
        self.height = 100
        self.seed = None
        self.register_path = None
        self.image = None
        self.octave = 1

    # Defines the size of the image (width, height) in pixels
    def set_size(self, size: tuple[int, int]):
        self.width, self.height = size

    # Returns the size of the image (width, height) in pixels
    def get_size(self):
        return self.width, self.height

    # Defines the seed of the random used to generate the image (positive integer only)
    def set_seed(self, seed: int):
        self.seed = seed

    # Returns the seed of the random used to generate the image
    def get_seed(self):
        return self.seed

    # Defines the path to the place where to save the generated image (string)
    def set_path(self, path: str):
        self.register_path = path

    # Returns the path to the place where to save the generated image
    def get_path(self):
        return self.register_path

    # Defines the number of octave used to generate the image (Positive integer only)
    def set_octave(self, octave: int):
        self.octave = octave

    # Returns the number of octave used to generate the image (a positive integer)
    def get_octave(self):
        return self.octave

    #  Returns a blank canvas following the inputted width and height
    def create_canvas(self) -> Image:
        self.image = Image.new("RGB", (self.width, self.height), "#FFFFFF")

    #  Returns a permutation table of 2 times the inputted size
    def perm_table(self, size: int) -> list[int]:
        # Seed the randomness if one is specified
        if self.seed is not None:
            random.seed(self.seed)

        array = [i for i in range(size)]
        random.shuffle(array)

        for i in range(size):
            array.append(array[i])

        return array

    #  Changes the color of every pixel of the canvas for a gray shade
    #  octave : higher value increases level of details
    def apply_noise(self) -> Image:
        image = self.image.load()
        #  Assuming the canvas is a square
        border_size: int = self.height
        #  Permutation table
        pt = self.perm_table(size=border_size)

        for y in range(self.height):
            for x in range(self.width):
                coord = (int(x), int(y))

                n: float = 0.0

                frequency: float = 0.025
                motion: float = 1.0

                for _ in range(self.octave):
                    n += motion * _noise_2d(x * frequency, y * frequency, pt=pt, border_size=border_size)
                    motion *= 0.5
                    frequency *= 2

                n += 1
                n *= 0.5
                n = round(n * 255)

                if n < 0.5:
                    color = (0, 0, 2 * n)
                elif n < 0.9:
                    color = (0, n, round(n * 0.5))
                else:
                    color = (n, n, n)

                image[coord] = color

    # Saves the given image as a png following file path and name
    def save_img(self, name: str) -> Image:
        print(type(self.image))
        if self.register_path is not None:
            self.image.save(f"{self.register_path}/{name}.png")
        else:
            raise AttributeError("Not specified path.")

    # Displays the image
    def show_img(self) -> None:
        self.image.show()
