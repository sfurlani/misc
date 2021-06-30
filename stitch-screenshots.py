import os, argparse, subprocess
import re
from PIL import Image

mode = "RGB"
spacing = 1

# loads the image and prints it out
def loadImage(infile):
  try:
    im = Image.open(infile)
    if im.mode != mode:
      im = im.convert(mode=mode)
    print("* ", infile, im.format, im.size, im.mode)
    return im
  except OSError:
    print("Could not find file: "+infile)
    return None

# unescapes the input path string
def unescapePath(inpath):
  return inpath.replace(r'\ ', ' ')

outfile = "~/Pictures/stitched.jpg"
inp = input("Enter output file name: ")

# if input isn't whitespace
if inp and not inp.isspace():
  # if it doesn't include a file extension
  if "." not in inp:
    inp = inp + ".jpg"
  outfile = inp

infiles = []

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
images = list(filter(None, maybeImages))

if not images:
  print("No Images to Process, exiting..")
  exit()

width = spacing
height = 0

for image in images:
  height = max(height, image.size[1])
  width += image.size[0] + spacing

canvas = Image.new(mode=mode, size=(width,height))

print("<- ", outpath, canvas.format, canvas.size, canvas.mode)

x = spacing
y = 0

for image in images:
  canvas.paste(image, (x, y))
  x += image.size[0] + spacing
  # image.close()

# https://github.com/python-pillow/Pillow/blob/master/src/PIL/JpegPresets.py
canvas.save(outpath, quality='web_high')
# canvas.close()

subprocess.Popen(["open", os.path.dirname(outpath)])
