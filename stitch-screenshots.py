#!/usr/bin/env python3
import os, argparse, subprocess, sys, math
import re
# python3 -m pip install --upgrade Pillow
from PIL import Image
from enum import Enum

class Mode(Enum):
  RGB = "RGB"
  RGBA = "RGBA"

outfile = "stitched"
modeChoices = [Mode.RGB.value, Mode.RGBA.value]
mode = Mode.RGB
modeExt = {
  Mode.RGB: ".jpg",
  Mode.RGBA: ".png"
}
modeBG = {
  Mode.RGB: 0,
  Mode.RGBA: 0
}
spacing = 1
quality = 95

class Resize(Enum):
  MIN = "min"
  MAX = "max"
  NONE = "none"

resize = Resize.NONE
resizeChoices = [Resize.MIN.value, Resize.MAX.value]

parser = argparse.ArgumentParser(description="Horizontally stitch some images together", formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-o", dest="output", type=str, help=f"Output file (default: ~/Pictures/{outfile}.jpg)\n\tNote: if the path is not specified, it uses the path of the first input file\n\tNote: if the extension is not specified, it uses one approrpriate for the selected mode", default=outfile)
parser.add_argument("-s", dest="spacing", type=int, help=f"Horizontal spacing between images in pixels (default: {spacing})", default=spacing)
parser.add_argument("-O", dest="shouldOpen", type=bool, help="Whether or not to open the destination folder when finished", default=True)
parser.add_argument("-m", dest="mode", type=str, help=f"Output file format (default: {mode.value})", choices=modeChoices, default=mode.value)
parser.add_argument("-q", dest="quality", type=int, help=f"Output jpeg quality - valid for mode=RGB only - (default: {quality})", default=quality)
parser.add_argument("-r", dest="resize", type=str, help=f"Output file format (default: {resize.value})", choices=resizeChoices, default=resize.value)
parser.add_argument("input", metavar="FILES", type=str, nargs='+', help="The list of image files to stitch together, leave empty to be prompted")

args = parser.parse_args()

# loads the image and prints it out
def loadImage(infile, mode=mode):
  try:
    im = Image.open(infile)
    if im.mode != mode.value:
      im = im.convert(mode=mode.value)
    print("* ", infile, im.format, im.size, im.mode)
    return im
  except OSError:
    print("Could not find file: "+infile)
    return None

# unescapes the input path string
def unescapePath(inpath):
  return inpath.replace(r'\ ', ' ')

# Saves the image based on mode
def saveImage(mode, img, out):
  switcher = {
    Mode.RGB: lambda i,o: i.save(o, quality=quality), # https://github.com/python-pillow/Pillow/blob/master/src/PIL/JpegPresets.py
    Mode.RGBA: lambda i,o: i.save(o)
  }
  switcher.get(mode)(img, out)

mode = Mode(args.mode)
quality = args.quality

# Output Filepath
outfile = args.output
# if input isn't whitespace
if outfile and not outfile.isspace():
  # if it doesn't include a file extension
  if "." not in outfile:
    outfile = outfile + modeExt.get(mode)

# Parse Input Files
infiles = args.input
if not infiles:
  print("Enter Image Files to stitch (paste a list or leave empty to finish)")
  while True:
    inp = input("-> ")
    if not inp:
      break
    # Breaks paths based on non-escaped spaces (if you copied a list of files from Finder and pasted it into terminal, that's how it works)
    paths = re.split(r'(?<!\\)\ ', inp)
    if len(paths) > 1:
      for path in paths:
        infiles.append(path)
      break
    else:
      infiles.append(inp)

if not infiles:
  print("No Input files entered, exiting...")
  exit()

unescaped = map(unescapePath, infiles)
inpaths = list(map(os.path.expanduser, unescaped))

if not inpaths:
  print("No Fully-qualified input paths, exiting...")
  exit()

if "/" not in outfile:
  firstPath = os.path.dirname(inpaths[0])
  if firstPath and not firstPath.isspace():
    outfile = firstPath + "/" + outfile
  else:
    outfile = "~/Pictures/" + outfile

outpath = os.path.expanduser(outfile)

maybeImages = map(loadImage, inpaths)
origImages = list(filter(None, maybeImages))

if not origImages:
  print("No Images to Process, exiting..")
  exit()

spacing = args.spacing
resize = Resize(args.resize)

# canvas height
height = sys.maxsize if resize == Resize.MIN else 0

# Get Max or Min Canvas height
for image in origImages:
  if resize == Resize.MIN:
    height = min(height, image.size[1])
  else:
    height = max(height, image.size[1])

# Optionally resize
def resizeImage(image):
  # print("Old", image.size)
  h = height
  w = math.ceil(h * image.size[0] / image.size[1])
  # print("New", (w,h))
  return image.resize((w, h))

images = origImages if resize == Resize.NONE else list(map(resizeImage, origImages))

height += spacing * 2 # top and bottom margin

# Determine canvas width
width = spacing # left margin
for image in images:
  width += image.size[0] + spacing

print("Height", height, "Width", width)
canvas = Image.new(mode=mode.value, size=(width,height), color=modeBG.get(mode))

print("<- ", outpath, canvas.format, canvas.size, canvas.mode)

x = spacing
y = spacing

for image in images:
  print("Pasting", image, image.size, "to", (x, y))
  canvas.paste(image, (x, y))
  x += image.size[0] + spacing
  # image.close()

saveImage(mode, canvas, outpath)
# canvas.close()

if args.shouldOpen:
  subprocess.Popen(["open", os.path.dirname(outpath)])
