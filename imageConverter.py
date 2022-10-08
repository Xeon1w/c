from PIL import Image
import numpy as np
from colorthief import ColorThief
import glob
from os import path, mkdir

filenameConvert = "imagesProcessed"


class imageMani:
    def change_contrast(path):
        npImage = np.array(Image.open(path).convert("L"))
        min = np.min(npImage)
        max = np.max(npImage)
        LUT = np.zeros(256, dtype=np.uint8)
        LUT[min:max+1] = np.linspace(start=0, stop=255, num=(max-min)+1, endpoint=True, dtype=np.uint8)
        Image.fromarray(LUT[npImage]).save(f'{filenameConvert}/contrastResult.png')

    def resizeDouble(path):
        im = Image.open(path)
        resized_im = im.resize((round(im.size[0]*3), round(im.size[1]*3)), Image.NEAREST)
        resized_im.save(f"{filenameConvert}/resized.png")

    def domColour(path):
        color_thief = ColorThief(path)
        palette = color_thief.get_palette(color_count=2, quality=1)
        for r, g, b in palette[1:-1]:
            colour = r, g, b
            return colour

    def removegb(path, outputpath, sensitivity: int = 60):
        r = 0
        g = 0
        b = 0
        img = Image.open(path).convert('RGBA')
        width = img.size[0]
        height = img.size[1]

        for i in range(0, width):
            for j in range(0, height):
                data = img.getpixel((i, j))
                d = sensitivity  # ? Blacks sensitivity
                if (data[0] in range(r-d, r+d) and data[1] in range(g-d, g+d) and data[2] in range(b-d, b+d)):
                    img.putpixel((i, j), (0, 0, 0))

        for i in range(0, width):
            for j in range(0, height):
                data = img.getpixel((i, j))
                if (data[0] != 0 and data[1] != 0 and data[2] != 0):
                    img.putpixel((i, j), (255, 255, 255))

        img.save(outputpath)


def process(path, output, sensitivity):
    try:
        mkdir(filenameConvert)
    except Exception:
        pass
    imageMani.resizeDouble(path)
    imageMani.change_contrast(f"{filenameConvert}/resized.png")
    imageMani.removegb(f"{filenameConvert}/contrastResult.png", output)


def convert_all(pat, output="convertedset"):
    try:
        mkdir(output)
    except Exception:
        pass
    for filename in glob.glob(f'{pat}/*.png'):
        file = filename.replace(f"{pat}/", "").replace(f"{pat}\\", "")
        if not path.exists(f"{output}/{file}"):
            pathname = f"{output}/{file}"
            process(filename, pathname, 60)


if __name__ == "__main__":
    convert_all("dataset", "capt")
