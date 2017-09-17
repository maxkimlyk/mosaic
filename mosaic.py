""" Mosaic. Generates mosaic from images. """

import os
import math
import argparse
from PIL import Image

DEFAULT_SEGMENTS_SIZE = 32
DEFAULT_OUT_IMAGE_NAME = "out.png"

class MosaicSegment:
    """ Implements small mosaic segment """
    def __init__(self, image, color):
        self.image = image
        self.color = color

def list_of_files_in_dir(path):
    """ Returns list of files in directory """
    entities_in_dir = os.listdir(path)
    files_in_dir = [f for f in entities_in_dir if os.path.isfile(os.path.join(path, f))]
    return files_in_dir

def color_combine(color1, color2):
    return ((color1[0] + color2[0]) // 2, (color1[1] + color2[1]) // 2, (color1[2] + color2[2]) // 2)

def add_image_halfframe(image, frame_color):
    """ Adds halfpixel frame to image """
    for j in range(image.width):
        color = image.getpixel((j, 0))
        new_color = color_combine(color, frame_color)
        image.putpixel((j, 0), new_color)

        color = image.getpixel((j, image.height - 1))
        new_color = color_combine(color, frame_color)
        image.putpixel((j, image.height - 1), new_color)

    for i in range(1, image.height-1):
        color = image.getpixel((0, i))
        new_color = color_combine(color, frame_color)
        image.putpixel((0, i), new_color)

        color = image.getpixel((image.width - 1, i))
        new_color = color_combine(color, frame_color)
        image.putpixel((image.width - 1, i), new_color)

def generate_segments_from_dir(src_dir, size, allow_frames):
    """ Generates thumbnails and saves to certain directory """
    files_in_dir = list_of_files_in_dir(src_dir)

    segments = []

    for filename in files_in_dir:
        image = Image.open(os.path.join(src_dir, filename))
        image.thumbnail(size, Image.ANTIALIAS)
        if (image.width != image.height):
            image = image.resize(size)
        mid_color = mean_color(image)

        if (allow_frames):
            add_image_halfframe(image, (0, 0, 0))

        segments.append(MosaicSegment(image, mid_color))

    return segments

def image_add_transform(image, color_vector):
    """ Transform y = x + a for entire image """
    pixels = list(image.getdata())
    for i,color in enumerate(pixels):
        pixels[i] = (
            max(min(color[0] + color_vector[0], 255), 0),
            max(min(color[1] + color_vector[1], 255), 0),
            max(min(color[2] + color_vector[2], 255), 0))

    newimage = Image.new(image.mode, image.size)
    newimage.putdata(pixels)

    return newimage

def color_sub(color1, color2):
    """ Vector subtraction """
    return (color1[0] - color2[0], color1[1] - color2[1], color1[2] - color2[2])

def color_difference(color1, color2):
    """ Color difference """
    return abs(color1[0] - color2[0]) + abs(color1[1] - color2[1]) + abs(color1[2] - color2[2])

def mean_color(image):
    """ Finds mean color in image """
    summ_color = (0, 0, 0)
    for y in range(image.height):
        for x in range(image.width):
            color = image.getpixel((x, y))
            summ_color_r = color[0] + summ_color[0]
            summ_color_g = color[1] + summ_color[1]
            summ_color_b = color[2] + summ_color[2]
            summ_color = (summ_color_r, summ_color_g, summ_color_b)
    number = image.height * image.width
    return (summ_color[0] // number, summ_color[1] // number, summ_color[2] // number)

def make_mosaic(image_name, segments, save_name):
    """ Builds mosaic """
    raw_width = segments[0].image.width
    raw_height = segments[0].image.height

    sample_image = Image.open(image_name)
    width = sample_image.width * raw_width
    height = sample_image.height * raw_height

    mosaic = Image.new("RGB", (width, height))

    for i in range(sample_image.height):

        print_progress_bar(i, sample_image.height)

        for j in range(sample_image.width):
            wanted_color = sample_image.getpixel((j, i))
            wanted_color = (wanted_color[0], wanted_color[1], wanted_color[2])

            best_match = []
            best_diff = math.inf
            for segment in segments:
                diff = color_difference(wanted_color, segment.color)
                if (diff < best_diff):
                    best_diff = diff
                    best_match = segment

            color_correction = color_sub(wanted_color, best_match.color)
            new_image = image_add_transform(best_match.image, color_correction)
            mosaic.paste(new_image, (raw_width * j, raw_height * i))

    mosaic.save(save_name)
    print_progress_bar(1, 1)

def print_progress_bar(iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """ Call in a loop to create terminal progress bar """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')

    if iteration == total:
        print()

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("source_file", help="source file for the mosaic")
    arg_parser.add_argument("segments_dir", help="directory containing raw segments (images may be any size)")
    arg_parser.add_argument("-o", "--out", type=str, help="output file (by default {})".format(DEFAULT_OUT_IMAGE_NAME))
    arg_parser.add_argument("-s", "--size", type=int, help="size of mosaic segment (by default {})".format(DEFAULT_SEGMENTS_SIZE))
    arg_parser.add_argument("-f", "--frames", help="allow rendering frames of segments", action="store_true")
    args = arg_parser.parse_args()

    if (args.out is None):
        args.out = DEFAULT_OUT_IMAGE_NAME

    if (args.size is None):
        args.size = DEFAULT_SEGMENTS_SIZE
    segment_size = (args.size, args.size)

    segments = generate_segments_from_dir(args.segments_dir, segment_size, args.frames)
    make_mosaic(args.source_file, segments, args.out)
