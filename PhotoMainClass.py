from PIL import Image, ImageFilter
import numpy as np
import sqlite3

conn = sqlite3.connect('actions.db')
cur = conn.cursor()
def add_to_db(action):
    db = cur.execute("""INSERT INTO actions (action)
    VALUES
    (?)
    ;""", (action,))

def save_image(filter_name, image):
    add_to_db(f'cash_image/{filter_name}.png photo')
    image.save(f'cash_image/{filter_name}.png')
    image = image.resize((130, 130))
    image.save(f'cash_image/min_{filter_name}.png')


def curve(pixel):
    r, g, b = pixel
    brightness = r + g + b
    if brightness < 60:
        k = 60 / brightness if brightness != 0 else 1
        return min(255, int(r * k ** 2)), min(255, int(g * k ** 2)), min(255, int(b * k ** 2))
    else:
        return r, g, b


class Photo:
    def __init__(self, name_file=None):
        if name_file is not None:
            add_to_db(f'{name_file} photo')
            self.image_pil = Image.open(name_file)
            self.image_array = np.array(self.image_pil)
            self.save_all_in_cash()

    def save_all_in_cash(self):
        self.negative_photo()
        save_image('real', self.image_pil)
        self.warm_photo()
        self.gray_photo()
        self.cold_photo()
        self.change_chanels()

    def change_chanels(self):
        im = self.image_pil
        pixels = im.load()  # список с пикселями
        x, y = im.size

        for i in range(x):
            for j in range(y):
                pixels[i, j] = curve(pixels[i, j])

        save_image('change_chanels', im)

    def negative_photo(self):
        picture = self.image_array[:]
        picture[:, :, 0] = 255 - picture[:, :, 0]
        picture[:, :, 1] = 255 - picture[:, :, 1]
        picture[:, :, 2] = 255 - picture[:, :, 2]
        image = Image.fromarray(picture)
        save_image('negative', image)

    def gray_photo(self):
        picture = self.image_array[:]
        summa = picture[:, :, 0] + picture[:, :, 1] + picture[:, :, 2]
        picture[:, :, 0] = summa // 3
        picture[:, :, 1] = summa // 3
        picture[:, :, 2] = summa // 3
        image = Image.fromarray(picture)
        save_image('gray', image)

    def warm_photo(self):
        picture = self.image_array[:]
        picture[:, :, 0] = 255
        picture[:, :, 2] = 200
        image = Image.fromarray(picture)
        save_image('warm', image)

    def cold_photo(self):
        picture = self.image_array[:]
        picture[:, :, 2] = 255
        image = Image.fromarray(picture)
        save_image('cold', image)

    def change_turbidity(self, radius):
        im2 = self.image_pil.filter(ImageFilter.GaussianBlur(radius=radius))
        im2.save('data_change/NEW.png')

    def gray_photo_with_koeff(self, koeff):
        picture = self.image_array[:]
        summa = picture[:, :, 0] + picture[:, :, 1] + picture[:, :, 2]
        picture[:, :, 0] = summa // koeff
        picture[:, :, 1] = summa // koeff
        picture[:, :, 2] = summa // koeff
        image = Image.fromarray(picture)
        image.save('data_change/NEW.png')

    def quantize(self, koeff):
        im = self.image_pil.quantize(koeff)
        im.save('data_change/NEW.png')

    def flip_90(self):
        im = self.image_pil
        im2 = im.transpose(Image.ROTATE_90)
        im2.save('data_change/NEW.png')

    def flip_to_bottom(self):
        im = self.image_pil
        im2 = im.transpose(Image.FLIP_LEFT_RIGHT)
        im2.save('data_change/NEW.png')
