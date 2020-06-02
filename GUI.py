from PIL import Image, ImageEnhance
from PIL.ImageQt import ImageQt, toqpixmap
from palette import *
from util import *
#from test import *
from transfer import *
import numpy as np
import cv2
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

html_color = lambda color : '%02x%02x%02x' % (color[0],color[1],color[2])
color_np = lambda color : np.array([color.red(),color.green(),color.blue()])

class Window(QWidget):
    K = 0 
    palette_button = []
    Source = ''
    image_label = ''
    cv2Image = []
    img = []
    palette_color = (np.zeros((7,3)) + 239).astype(int) #initial grey
    #palette_color = ['ff0000','00ff00','0000ff', \
    #                 'ff00ff','ffff00','00ffff','ffffff']
    sample_level = 16
    sample_colors = sample_RGB_color(sample_level)
    sample_weight_map = []
    means = []
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pallete Based Photo Recoloring')
        self.UiComponents()
        self.show()

    def pixmap_open_img(self):
        # load image
        self.img = Image.open(self.Source)
        print(self.Source, self.img.format, self.img.size, self.img.mode)
        # transfer to lab
        lab = rgb2lab(self.img)
        # get palettes
        self.K = 5
        colors = lab.getcolors(self.img.width * self.img.height)
        bins = {}
        for count, pixel in colors:
            bins[pixel] = count
        bins = sample_bins(bins)
        self.means = k_means(bins, k=5, init_mean=True)
        print(self.means)
        means_rgb = cv2.cvtColor(
            self.means.astype(np.ubyte)[None,:,:],cv2.COLOR_Lab2RGB)
        print(means_rgb[0])
        self.palette_color = means_rgb[0]
        self.set_palette_color()
        pixmap = toqpixmap(self.img)
        return pixmap
    def clicked(self, N):
        if N >= self.K:
            print('invalid palette')
            return
        print('change palette', N, 'to', end='\t')
        # choose new color
        curr_clr = self.palette_color[N]
        current = QColor(curr_clr[0],curr_clr[1],curr_clr[2])
        color = QColorDialog.getColor(initial=current, 
            options=QColorDialog.DontUseNativeDialog)
        print(color_np(color))
        self.palette_color[N] = color_np(color)
        self.set_palette_color()
        # modify image
        palette_color_lab = cv2.cvtColor(
            self.palette_color[None,:,:],cv2.COLOR_RGB2Lab)[0]
        self.img = img_color_transfer(
            self.img, self.means, palette_color_lab, self.sample_weight_map, self.sample_colors, self.sample_level)
        #self.img.save('tmp.png')
        #tmp = cv2.imread('tmp.png')
        #tmp = cv2.cvtColor(tmp, cv2.COLOR_Lab2BGR)
        #height, width, channel = tmp.shape
        #qImage = QImage(tmp.data, width, height, 3 * width, \
        #                QImage.Format_RGB888).rgbSwapped()
        #pixmap = QPixmap(qImage)
        ## for testing
        #enhancer = ImageEnhance.Brightness(self.img)
        #self.img = enhancer.enhance(1.1)
        # show image
        #self.image_label.setPixmap(pixmap)
        self.image_label.setPixmap(toqpixmap(self.img))
    def init_palette_color(self):
        for i in range(7):
            attr = 'background-color:#'+html_color(
                self.palette_color[i])+';border:0px'
            self.palette_button[i].setStyleSheet(attr)
    def set_palette_color(self):
        for i in range(self.K):
            attr = 'background-color:#'+html_color(
                self.palette_color[i])+';border:0px'
            self.palette_button[i].setStyleSheet(attr)
    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,"QFileDialog.getOpenFileName()", "", \
            "Images (*.jpg *.JPG *jpeg *.png *.webp *.tiff *.tif *.bmp *.dib);;All Files (*)", options=options)
        self.Source = file_name
        self.image_label.setPixmap(self.pixmap_open_img())
        # rbf weights
        self.sample_weight_map = rbf_weights(self.means, self.sample_colors)
    def save_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,"QFileDialog.getOpenFileName()", "", \
            "PNG (*.png);;JPG (*.jpg);;Images (*.jpg *.JPG *jpeg *.png *.webp *.tiff *.tif *.bmp *.dib);;All Files (*)", options=options)
        print('Saving to',file_name)
        if file_name.find('.') == -1:
            file_name += '.png'
        self.img.save(file_name)
        #cv2.imwrite(file_name,self.cv2Image)
        print('Saved to',file_name)
    def set_number_of_palettes(self, text):
        self.K = int(text)
        self.set_palette_color()
        for i in range(self.K, 7):
            attr = 'background-color:#EFEFEF;border:0px'
            self.palette_button[i].setStyleSheet(attr)
    def UiComponents(self):
        self.main_layout = QVBoxLayout()

        Image_section = QWidget()
        image_section_layout = QHBoxLayout()
        self.image_label = QLabel()
        #label.setPixmap(self.pixmap_img())
        image_section_layout.addWidget(self.image_label)
        Color_wheel = QWidget()
        color_wheel_layout = QVBoxLayout()
        Color_wheel.setLayout(color_wheel_layout)
        image_section_layout.addWidget(Color_wheel)

        self.Palette = QWidget()
        #self.palette_layout = QHBoxLayout()
        self.palette_layout = QVBoxLayout()
        for i in range(7):
            self.palette_button.append(QPushButton())
            self.palette_button[i].clicked.connect(
                lambda state,x=i: self.clicked(x))
            self.palette_layout.addWidget(self.palette_button[i])
        self.init_palette_color()
        self.Palette.setLayout(self.palette_layout)
        image_section_layout.addWidget(self.Palette)
        #self.main_layout.addWidget(self.Palette)

        Image_section.setLayout(image_section_layout)
        self.main_layout.addWidget(Image_section)

        Image_button = QWidget()
        image_button_layout = QHBoxLayout()
        combo_box = QComboBox()
        for i in range(3,8):
            combo_box.addItem(str(i))
        combo_box.activated[str].connect(self.set_number_of_palettes)
        image_button_layout.addWidget(combo_box)
        #combo_box.setCurrentText(str(self.K))
        combo_box.setCurrentText('5')
        open_image = QPushButton('Open')
        reset_image = QPushButton('Reset')
        save_image = QPushButton('Save')
        open_image.clicked.connect(self.open_file)
        save_image.clicked.connect(self.save_file)
        image_button_layout.addWidget(open_image)
        image_button_layout.addWidget(reset_image)
        image_button_layout.addWidget(save_image)
        Image_button.setLayout(image_button_layout)
        self.main_layout.addWidget(Image_button)

        self.setLayout(self.main_layout)

app = QApplication([])
window = Window()
app.exec_()
