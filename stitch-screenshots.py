import os, sys
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

outfile = "~/Pictures/stitched.jpg"
inp = input("Enter output file name (default: \"" + outfile + "\"): ")
if inp and not inp.isspace():
  outfile = inp

outpath = os.path.expanduser(outfile)

infiles = []

print("Enter Image Files to stitch (leave empty to finish)")
while True:
  inp = input("-> ")
  if not inp:
    break
  infiles.append(inp)

if not infiles:
  print("No Input files entered, exiting...")
  exit()

inpaths = map(os.path.expanduser, infiles)

maybeImages = map(loadImage, inpaths)
images = list(filter(None, maybeImages))

width = 0
height = 0

for image in images:
  height = max(height, image.size[1])
  width += image.size[0] + spacing

canvas = Image.new(mode=mode, size=(width,height))

print("<- ", outpath, canvas.format, canvas.size, canvas.mode)

x = 0
y = 0

for image in images:
  canvas.paste(image, (x, y))
  x += image.size[0] + spacing
  # image.close()

canvas.save(outpath)
# canvas.close()
