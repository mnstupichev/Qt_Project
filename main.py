import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, \
    QFileDialog, QInputDialog, QErrorMessage
from grafix import Ui_MainWindow
# from PhotoMainClass import Photo
import sqlite3
from PIL import Image, ImageFilter
import numpy as np

class Data:
    def __init__(self):
        self.conn = sqlite3.connect('actions.db')


class Photo():
    def __init__(self, db, name_file=None):
        self.db = db
        self.cur = self.db.conn.cursor()
        if name_file is not None:
            self.add_to_db(f'{name_file} photo')
            self.image_pil = Image.open(name_file)
            self.image_array = np.array(self.image_pil)
            self.save_all_in_cash()

    def add_to_db(self, action):
        self.cur.execute("""INSERT INTO actions (action)
        VALUES
        (?)
        ;""", (action,))

    def save_image(self, filter_name, image):
        self.add_to_db(f'cash_image/{filter_name}.png photo')
        image.save(f'cash_image/{filter_name}.png')
        image = image.resize((130, 130))
        image.save(f'cash_image/min_{filter_name}.png')

    def curve(self, pixel):
        r, g, b = pixel
        brightness = r + g + b
        if brightness < 60:
            k = 60 / brightness if brightness != 0 else 1
            return min(255, int(r * k ** 2)), min(255, int(g * k ** 2)), min(255, int(b * k ** 2))
        else:
            return r, g, b
    def save_all_in_cash(self):
        self.negative_photo()
        self.save_image('real', self.image_pil)
        self.warm_photo()
        self.gray_photo()
        self.cold_photo()
        self.change_chanels()

    def change_chanels(self):
        im = self.image_pil
        pixels = im.load()
        x, y = im.size

        for i in range(x):
            for j in range(y):
                pixels[i, j] = self.curve(pixels[i, j])

        self.save_image('change_chanels', im)

    def negative_photo(self):
        picture = self.image_array[:]
        picture[:, :, 0] = 255 - picture[:, :, 0]
        picture[:, :, 1] = 255 - picture[:, :, 1]
        picture[:, :, 2] = 255 - picture[:, :, 2]
        image = Image.fromarray(picture)
        self.save_image('negative', image)

    def gray_photo(self):
        picture = self.image_array[:]
        summa = picture[:, :, 0] + picture[:, :, 1] + picture[:, :, 2]
        picture[:, :, 0] = summa // 3
        picture[:, :, 1] = summa // 3
        picture[:, :, 2] = summa // 3
        image = Image.fromarray(picture)
        self.save_image('gray', image)

    def warm_photo(self):
        picture = self.image_array[:]
        picture[:, :, 0] = 255
        picture[:, :, 2] = 200
        image = Image.fromarray(picture)
        self.save_image('warm', image)

    def cold_photo(self):
        picture = self.image_array[:]
        picture[:, :, 2] = 255
        image = Image.fromarray(picture)
        self.save_image('cold', image)

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

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.cur = self.db.conn.cursor()
        self.first = False
        self.koeffs_arr = {'turbidity': [0, 0, 10],
                           'hightlight': [0, 3, 5],
                           'brillance': [100, 3, 100]}
        self.selected_filter = None
        self.setupUi(self)
        self.count_main_change = 0
        self.errorwidget = QErrorMessage(self)
        self.centralwidget.setLayout(self.verticalLayout_3)
        self.filters_name = ['negative', 'gray', 'warm', 'cold', 'real', 'change_chanels']
        self.objectsnames = []
        self.undofiles = []
        self.FILENAME = 'data_change/NEW.png'
        self.main_photo = Photo(db= db)
        self.hide_objects = {self.verticalLayout: [self.turbidity, self.brillance,
                                                   self.hightlight],
                             self.verticalLayout_4: [self.mirror, self.rotate_90],
                             self.verticalLayout_2: [self.label_1, self.label_2,
                                                     self.label_3, self.label_4,
                                                     self.label_5, self.label_6]}
        [obj.hide() for obj in self.hide_objects[self.verticalLayout_4]]
        [obj.hide() for obj in self.hide_objects[self.verticalLayout_2]]
        self.connect_widgets()
        self.style_sheet()
        self.filter_photo()
        self.open()

    def add_to_db(self, action):
        self.cur.execute("""INSERT INTO actions (action)
        VALUES
        (?)
        ;""", (action,))

    def style_sheet(self):
        [obj.clicked.connect(self.value_for_edditor) for obj in self.hide_objects[self.verticalLayout]]
        [obj.setAlignment(Qt.AlignCenter) for obj in self.hide_objects[self.verticalLayout_2]]
        self.setStyleSheet("background-color: rgb(61, 43, 33);")
        self.imageplace.setStyleSheet("background-color: rgb(155, 120, 80)")
        self.menubar.setStyleSheet("background-color: rgb(55, 55, 55)")
        for objs in self.hide_objects.items():
            for obj in objs[1]:
                obj.setAlignment(Qt.AlignCenter)

    def connect_widgets(self):
        self.openphotoact.changed.connect(self.open)
        self.closephotoact.changed.connect(self.close)
        self.renamephotoact.changed.connect(self.rename)
        self.savephotoact.changed.connect(self.save)
        self.reverse.clicked.connect(self.reverse_image)
        self.edits.clicked.connect(self.change_color_of_image)
        self.filters.clicked.connect(self.filter_photo)
        self.valuegforeditor.valueChanged.connect(self.re_edit_photo)
        self.rotate_90.clicked.connect(self.flip_90)
        self.mirror.clicked.connect(self.flip_to_bottom)

    def flip_90(self):
        self.main_photo.flip_90()
        self.update_main_photo('data_change/NEW.png', True)

    def flip_to_bottom(self):
        self.main_photo.flip_to_bottom()
        self.update_main_photo('data_change/NEW.png', True)

    def filter_photo(self):
        [obj.hide() for obj in self.hide_objects[self.verticalLayout_4]]
        [obj.hide() for obj in self.hide_objects[self.verticalLayout]]
        [obj.show() for obj in self.hide_objects[self.verticalLayout_2]]

    def update_photo_filter(self):
        for i, name_filter in enumerate(self.filters_name):
            name_file = f'cash_image/min_{name_filter}'
            exec(f'self.label_{i + 1}.setPixmap(QPixmap(name_file))')
            exec(f'self.label_{i + 1}.clicked.connect(self.photo_selected)')
            self.add_to_db(f'{name_file} up to date')

    def photo_selected(self):
        name_filter = self.filters_name[int(self.sender().objectName()[-1]) - 1]
        name_file = f'cash_image/{name_filter}'
        self.add_to_db(f'{name_file} photo_selected')
        self.update_main_photo(name_file)

    def change_color_of_image(self):
        [obj.hide() for obj in self.hide_objects[self.verticalLayout_4]]
        [obj.hide() for obj in self.hide_objects[self.verticalLayout_2]]
        [obj.show() for obj in self.hide_objects[self.verticalLayout]]

    def reverse_image(self):
        [obj.hide() for obj in self.hide_objects[self.verticalLayout]]
        [obj.hide() for obj in self.hide_objects[self.verticalLayout_2]]
        [obj.show() for obj in self.hide_objects[self.verticalLayout_4]]

    def save(self):
        self.add_to_db(f'{self.FILENAME} {self.undofiles[-1]}')
        QPixmap(self.FILENAME).save(self.undofiles[-1])

    def rename(self):
        endsfiles = ['.png', '.jpg', '.bmp', '.jpeg']
        name, ok_pressed = QInputDialog.getText(self, "Ввод нового имени файла",
                                                "Введите новое имя файла")
        while ok_pressed and not any([name.endswith(endfile) for endfile in endsfiles]):
            name, ok_pressed = QInputDialog.getText(self, "Ввод нового имени файла",
                                                    "Введите новое имя файла(вместе с его расширением)")
        if ok_pressed:
            QPixmap(self.undofiles[-1]).save('data_change/' + name)
            self.undofiles[-1] = self.undofiles[-1][:self.undofiles[-1].rfind('/') + 1] + name

    def open(self):
        new_filename = QFileDialog.getOpenFileName(
                self, 'Выбрать картинку', '',
                '*.png;*.jpg;*.bmp;*.jpeg')[0]
        if new_filename != '':
            file_name_for_main = new_filename[new_filename.rfind('/') + 1:]
            self.undofiles.append(new_filename)
            QPixmap(new_filename).save('data_change/' + file_name_for_main)
            self.update_main_photo(new_filename, True)
            self.count_main_change += 1

    def update_main_photo(self, new_filename, update=False):
        pixmap = QPixmap(new_filename)
        pixmap.save(self.FILENAME)
        x, y = pixmap.size().width(), pixmap.size().height()
        procent = min((100 * 800) / x, (100 * 800) / y) / 100
        self.imageplace.setPixmap(pixmap.scaled(int(procent * x), int(procent * y)))
        self.main_photo = Photo(self.db, self.FILENAME) if update else self.main_photo
        self.update_photo_filter()

    def value_for_edditor(self):
        self.selected_filter = self.sender().objectName()
        self.add_to_db(f'{self.koeffs_arr[self.selected_filter]}')
        self.valuegforeditor.setMinimum(self.koeffs_arr[self.selected_filter][1])
        self.valuegforeditor.setMaximum(self.koeffs_arr[self.selected_filter][2])
        self.valuegforeditor.setValue(self.koeffs_arr[self.selected_filter][0])
        self.first = False

    def re_edit_photo(self):
        if self.selected_filter is not None and self.first:
            koeff = self.valuegforeditor.value()
            self.add_to_db(f'{koeff}')
            self.add_to_db(f'{self.selected_filter} re edit')
            if self.selected_filter == 'turbidity':
                self.main_photo.change_turbidity(koeff)
            elif self.selected_filter == 'hightlight':
                self.main_photo.gray_photo_with_koeff(koeff)
            elif self.selected_filter == 'brillance':
                self.main_photo.quantize(koeff)
            self.update_main_photo('data_change/NEW.png', True)
        elif not self.first:
            self.first = True

    def except_hook(self, cls, exception, traceback):
        self.errorwidget.showMessage(str(exception))
        sys.__excepthook__(cls, exception, traceback)


db = Data()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow(db)
    ex.showMaximized()
    sys.excepthook = ex.except_hook
    sys.exit(app.exec())

result = db.conn.cursor().execute("""SELECT * FROM actions""").fetchall()
for line in result:
    print(*line)
db.conn.cursor().execute("""DELETE FROM actions""")