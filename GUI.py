import cv2
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

html_color = lambda color : '%02x%02x%02x' % (color.red(),color.green(),color.blue())

class Window(QWidget):
    K = 5
    palette_button = []
    Source_image = ''
    image_label = ''
    cv2Image = []
    current_palette = 0
    palette_color = ['ff0000','00ff00','0000ff', \
                     'ff00ff','ffff00','00ffff','ffffff']
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pallete Based Photo Recoloring')
        self.UiComponents()
        self.show()

    def pixmap_img(self):
        self.cv2Image = cv2.imread(self.Source_image, cv2.IMREAD_COLOR)
        height, width, channel = self.cv2Image.shape
        qImage = QImage(self.cv2Image.data, width, height, 3 * width, \
                        QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap(qImage)
        return pixmap

    def clicked(self, N):
        self.current_palette = N
        print('current palette:', self.current_palette)
        color = QColorDialog.getColor(#initial=current, 
            options=QColorDialog.DontUseNativeDialog)
        print('#'+html_color(color))
        self.palette_color[self.current_palette] = html_color(color)
        self.set_palette_color()

    def set_palette_color(self):
        for i in range(self.K):
            attr = 'background-color:#' + self.palette_color[i]
            self.palette_button[i].setStyleSheet(attr)
    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self,"QFileDialog.getOpenFileName()", "", \
            "Images (*.jpg *.JPG *jpeg *.png *.webp *.tiff *.tif *.bmp *.dib);;All Files (*)", options=options)
        self.Source_image = file_name
        self.image_label.setPixmap(self.pixmap_img())
    def save_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self,"QFileDialog.getOpenFileName()", "", \
            "PNG (*.png);;JPG (*.jpg);;Images (*.jpg *.JPG *jpeg *.png *.webp *.tiff *.tif *.bmp *.dib);;All Files (*)", options=options)
        print('Saving to',file_name)
        if file_name.find('.') == -1:
            file_name += '.png'
        cv2.imwrite(file_name,self.cv2Image)
        print('Saved to',file_name)
    def set_number_of_palettes(self, text):
        self.K = int(text)
        self.Palette = QWidget()
        self.palette_layout = QHBoxLayout()
        for i in range(self.K):
            self.palette_button.append(QPushButton())
            self.palette_button[i].clicked.connect(
                lambda state,x=i: self.clicked(x))
            self.palette_layout.addWidget(self.palette_button[i])
        self.set_palette_color()
        self.Palette.setLayout(self.palette_layout)

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
        Image_section.setLayout(image_section_layout)
        self.main_layout.addWidget(Image_section)

        self.Palette = QWidget()
        self.palette_layout = QHBoxLayout()
        for i in range(self.K):
            self.palette_button.append(QPushButton())
            self.palette_button[i].clicked.connect(
                lambda state,x=i: self.clicked(x))
            self.palette_layout.addWidget(self.palette_button[i])
        self.set_palette_color()
        self.Palette.setLayout(self.palette_layout)
        self.main_layout.addWidget(self.Palette)

        Image_button = QWidget()
        image_button_layout = QHBoxLayout()
        combo_box = QComboBox()
        for i in range(3,8):
            combo_box.addItem(str(i))
        combo_box.activated[str].connect(self.set_number_of_palettes)
        image_button_layout.addWidget(combo_box)
        combo_box.setCurrentText(str(self.K))
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


