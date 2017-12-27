#!/usr/bin/env python3

# Command line for conversion: png2ass.py M10_scaled.png --start-time 0:00:10.00 --with-ass-header --text-prefix "{\fad(500,500)}" > PM-M10.ass

import argparse
from datetime import timedelta
import re

import png

ASS_HEADER = """
[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H0000FFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def is_same_color(color1, color2):
    assert len(color1) == len(color2) == 4
    if color1[3] == 0:
        # Fully transparent, RGB doesn't matter
        return color2[3] == 0

    return color1 == color2


def from_ass_time(ass_time):
    parts_str = re.match(r"^(\d+):(\d\d):(\d\d)\.(\d\d)$", ass_time).groups()
    parts = [int(x) for x in parts_str]
    return timedelta(
        hours=parts[0],
        minutes=parts[1],
        seconds=parts[2],
        milliseconds=parts[3] * 10,
    )


def to_ass_time(value):
    m, s = divmod(value.seconds, 60)
    h, m = divmod(m, 60)
    h += value.days * 24

    cs = round(value.microseconds / 10000)

    return "{}:{:02d}:{:02d}.{:02d}".format(h, m, s, cs)


def prepare_ass_data(file, pos):
    reader = png.Reader(file)
    width, height, pixels, metadata = reader.asRGBA8()
    org_x, org_y = [int(x) for x in pos.split(",")]

    for row in range(height):
        raw_pixels = next(pixels)
        assert len(raw_pixels) == width * 4
        blocks = []
        cur_block_start = -1
        block_color = (0, 0, 0, 0)
        origin_column = 0

        for col in range(width):
            pixel_color = tuple(raw_pixels[col*4:col*4+4])
            if is_same_color(pixel_color, block_color):
                continue

            if cur_block_start > -1:
                blocks.append((col - cur_block_start, block_color))
            else:
                origin_column = col

            cur_block_start = col
            block_color = pixel_color

        if block_color[3] != 0:
            blocks.append((col - cur_block_start, block_color))

        if blocks:
            yield (org_x + origin_column, org_y + row), blocks


def output_ass(ass_data, layer, start_time, end_time, pos,
               text_prefix, text_suffix,):
    for (row_x, row_y), blocks in ass_data:
        row_pos = "{},{}".format(row_x, row_y)
        print((
            r"Dialogue: {layer},{start_time},{end_time},Default,,"
            r"0000,0000,0000,,{text_prefix}{{\an7\bord0\shad0\fnArial\fs20"
            r"\pos({row_pos})}}"
        ).format(**locals()), end="")
        for block_width, block_color in blocks:
            args = list(block_color + (block_width,))
            # Convert regular alpha to ASS alpha (actually transparency)
            args[3] = 0xff - args[3]
            print((
                r"{{\1c&H{2:02X}{1:02X}{0:02X}\alpha&H{3:X}\p1}}"
                r"m 0 0 l 0 1 {4} 1 {4} 0{{\p0}}"
            ).format(*args), end="")

        print(text_suffix)


def png_to_ass(name,
               layer=0,
               start_time=timedelta(),
               end_time=timedelta(hours=1),
               pos="0,0",
               text_prefix="",
               text_suffix="",
               with_ass_header=False,
              ):
    if with_ass_header:
        print(ASS_HEADER.strip())

    ass_data = prepare_ass_data(name, pos)

    start_time_ass = to_ass_time(start_time)
    end_time_ass = to_ass_time(end_time)
    output_ass(
        ass_data, layer, start_time_ass, end_time_ass, pos,
        text_prefix, text_suffix,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name")
    parser.add_argument("--layer", type=int, default=0)
    parser.add_argument("--start-time",
                        type=from_ass_time, default="0:00:00.00")
    parser.add_argument("--end-time",
                        type=from_ass_time, default="1:00:00.00")
    parser.add_argument("--pos", default="0,0")
    parser.add_argument("--text-prefix", default="")
    parser.add_argument("--text-suffix", default="")
    parser.add_argument("--with-ass-header", action="store_true")
    png_to_ass(**vars(parser.parse_args()))

if __name__ == "__main__":
    main()
