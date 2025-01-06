# coding:utf-8
import os
import sys


from .gallery_interface import GalleryInterface
from ..common.translator import Translator

from PyQt5.QtCore import QPoint, Qt, QStandardPaths
from PyQt5.QtGui import QColor, QImage, QPixmap, QPainter, QWheelEvent, QMouseEvent
from PyQt5.QtWidgets import (QAction, QWidget, QLabel, QVBoxLayout, QFileDialog, QActionGroup, QLabel,
                             QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QGraphicsView,
                             QGraphicsScene, QGraphicsPixmapItem, QFileDialog, QVBoxLayout)
from qfluentwidgets import (RoundMenu, PushButton, Action, CommandBar, Action, TransparentDropDownPushButton,
                            setFont, CommandBarView, Flyout, ImageLabel, FlyoutAnimationType, CheckableMenu,
                            MenuIndicatorType, AvatarWidget, isDarkTheme, BodyLabel, CaptionLabel, HyperlinkButton,
                            ComboBox, PrimaryPushButton, InfoBarIcon, LineEdit)
from qfluentwidgets import FluentIcon as FIF
import cv2


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
# 定义一个名为MaterialInterface的类，继承自GalleryInterface
class MaterialInterface(GalleryInterface):
    """ Material interface """

    # 初始化方法
    def __init__(self, parent=None):
        # 创建一个Translator对象
        t = Translator()
        self.src = None
        self.result = None
        # 调用父类的初始化方法，设置标题和子标题
        super().__init__(
            title=t.material,
            subtitle='遥感原理与图像处理-图像融合',
            parent=parent
        )
        self.imagePathMs = None
        self.imagePathPan  = None
        # 设置对象的名称为'materialInterface'
        self.setObjectName('materialInterface')

        # 浮出命令栏
        self.widget = QWidget(self)
        self.widget.setLayout(QVBoxLayout())  # 设置布局为垂直布局
        self.widget.layout().setContentsMargins(0, 0, 0, 0)  # 设置布局的边距
        self.widget.layout().setSpacing(10)  # 设置布局的间距

        # 创建导入图片按钮A
        self.button_input_A = PushButton(self.tr("导入图片MS多光谱影像"))
        self.button_input_A.setFixedWidth(180)  # 设置按钮大小
        self.h_layout = QHBoxLayout(self.widget)# 创建水平布局
        self.h_layout.setSpacing(10)# 设置水平布局的间距
        self.h_layout.addWidget(self.button_input_A, 0, Qt.AlignLeft)# 将按钮添加到水平布局中
        self.vBoxLayout.addLayout(self.h_layout)# 将水平布局添加到垂直布局中
        self.button_input_A.clicked.connect(self.inputPhoto)  # 连接按钮的点击信号导入图片并显示


        # 创建导入图片按钮B
        self.button_input_B = PushButton(self.tr("导入图片PAN全色图"))
        self.button_input_B.setFixedWidth(150)  # 设置按钮大小
        self.h_layout = QHBoxLayout(self.widget)# 创建水平布局
        self.h_layout.setSpacing(10)# 设置水平布局的间距
        self.h_layout.addWidget(self.button_input_B, 0, Qt.AlignLeft)# 将按钮添加到水平布局中
        self.vBoxLayout.addLayout(self.h_layout)# 将水平布局添加到垂直布局中
        self.button_input_B.clicked.connect(self.inputPhoto_B)  # 连接按钮的点击信号导入图片并显示


        # 创建下拉框
        self.comboBox_filter = ComboBox()  # 创建下拉框
        self.comboBox_filter.setPlaceholderText("请选择图像融合方法")
        items = ['IHSF', 'GIHSF', 'AIHSF', 'IAIHSF']  # 下拉框的选项
        self.comboBox_filter.addItems(items)  # 添加下拉框的选项
        self.comboBox_filter.setCurrentIndex(-1)  # 设置下拉框的默认选项
        self.comboBox_filter.setFixedWidth(100)  # 设置下拉框的宽度
        self.comboBox_filter.setMaximumWidth(180)  # 设置下拉框的最大宽度
        self.h_layout.addWidget(self.comboBox_filter, 0, Qt.AlignLeft)  # 将下拉框添加到水平布局中
        self.comboBox_filter.currentIndexChanged.connect(self.GetcomboBox_value)  # 当下拉框的选项改变时，触发事件

        # 创建导入Apply按钮
        self.button_input_apply = PushButton(self.tr("Apply"))
        self.button_input_apply.setFixedWidth(100)  # 设置按钮大小
        self.button_input_apply.clicked.connect(self.Apply_IMGFusion)  # 连接按钮的点击信号导入图片并显示
        self.h_layout.addWidget(self.button_input_apply, 0, Qt.AlignLeft)  # 将按钮添加到水平布局中

        # 创建保存滤波图像按钮
        self.button_input_save = PrimaryPushButton(self.tr("保存融合图像"))
        self.button_input_save.setFixedWidth(120)  # 设置按钮大小
        self.h_layout.addWidget(self.button_input_save, 0, Qt.AlignLeft)  # 将按钮添加到水平布局中
        self.button_input_save.clicked.connect(self.Filter_saveImage)  # 连接按钮的点击信号导入图片并显示

        # 创建一个标签
        label = QLabel(self.tr('单击图片打开命令栏，图片将在滤波后自动更换！'))
        self.imageLabel = ImageLabel(resource_path('Photos/resource/interface_background/lingsheyinchun.jpg'))# 创建一个ImageLabel对象
        self.imageLabel2 = ImageLabel(resource_path('Photos/resource/interface_background/doupocangqiong.jpg'))# 创建一个ImageLabel对象

        # 设置图片功能
        self.imageLabel.scaledToWidth(500)  # 设置图片的宽度
        self.imageLabel2.scaledToWidth(500)  # 设置图片的宽度
        self.imageLabel.setBorderRadius(8, 8, 8, 8)  # 设置图片的圆角
        self.imageLabel2.setBorderRadius(8, 8, 8, 8)  # 设置图片的圆角
        self.imageLabel.clicked.connect(self.createCommandBarFlyout)  # 连接图片的点击信号，打开命令栏
        self.imageLabel2.clicked.connect(self.createCommandBarFlyout)# 连接图片的点击信号，打开命令栏

        # 创建一个水平布局
        self.h_layout_photos = QHBoxLayout(self.widget)
        self.h_layout_photos.setSpacing(10)# 设置水平布局的间距
        self.h_layout_photos.addWidget(self.imageLabel, 0, Qt.AlignLeft)# 将图片A添加到水平布局中
        self.h_layout_photos.addWidget(self.imageLabel2, 0, Qt.AlignLeft)# 将图片B添加到水平布局中

        self.widget.layout().addWidget(label)  # 将标签添加到布局中
        self.widget.layout().addLayout(self.h_layout_photos)  # 将水平布局添加到布局中

        # 添加一个示例卡片，包含了标签的翻译，标签对象，示例代码的链接，和拉伸值
        self.addExampleCard(
            self.tr('遥感影像'),
            self.widget,
            'https://github.com/',
            stretch=1
        )

    # 当下拉框的选项改变时，触发事件
    def GetcomboBox_value(self):
        # 获取下拉框的选项
        comboBox_value = self.comboBox_filter.currentText()
        print(comboBox_value)
        res = -1
        if comboBox_value == 'IHSF':
            res = 1
        elif comboBox_value == 'GIHSF':
            res = 2
        elif comboBox_value == 'AIHSF':
            res = 3
        elif comboBox_value == 'IAIHSF':
            res = 4
        else:
            res = -1
        return res

    # 创建命令栏弹出窗口的方法
    def createCommandBarFlyout(self):
        view = CommandBarView(self)

        view.addAction(Action(FIF.SHARE, self.tr('Share')))
        view.addAction(Action(FIF.SAVE, self.tr('Save'), triggered=self.saveImage))
        view.addAction(Action(FIF.HEART, self.tr('Add to favorate')))
        view.addAction(Action(FIF.DELETE, self.tr('Delete')))

        view.addHiddenAction(Action(FIF.PRINT, self.tr('Print'), shortcut='Ctrl+P'))
        view.addHiddenAction(Action(FIF.SETTING, self.tr('Settings'), shortcut='Ctrl+S'))
        view.resizeToSuitableWidth()

        x = self.imageLabel.width()
        pos = self.imageLabel.mapToGlobal(QPoint(x, 0))
        Flyout.make(view, pos, self, FlyoutAnimationType.FADE_IN)

    # 保存图片的方法
    def saveImage(self):
        path, ok = QFileDialog.getSaveFileName(
            parent=self,
            caption=self.tr('Save image'),
            directory=QStandardPaths.writableLocation(QStandardPaths.DesktopLocation),
            filter='TIF (*.tif)'
        )
        if not ok:
            return

        self.imageLabel.image.save(path)

    # 导入图片A的方法
    def inputPhoto(self):
        # 打开一个QFileDialog并获取用户选择的图片路径
        filepath, _ = QFileDialog.getOpenFileName()
        if filepath:
            # 将用户选择的图片路径赋值给ImageLabel
            self.imageLabel.setPixmap(filepath)
            # 设置图片的最大宽度
            self.imageLabel.setMaximumWidth(800)
            self.imageLabel.scaledToWidth(500)  # 设置图片的宽度
            self.imagePathMs = filepath  # 保存图片路径
            self.src = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)  # 用opencv读取图片

    # 导入图片B的方法
    def inputPhoto_B(self):
        # 打开一个QFileDialog并获取用户选择的图片路径
        filepath, _ = QFileDialog.getOpenFileName()
        if filepath:
            # 将用户选择的图片路径赋值给ImageLabel
            self.imageLabel2.setPixmap(filepath)
            # 设置图片的最大宽度
            self.imageLabel2.setMaximumWidth(800)
            self.imageLabel2.scaledToWidth(500)  # 设置图片的宽度
            self.imagePathPan = filepath  # 保存图片路径
            self.src = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)  # 用opencv读取图片

        # 图像滤波的应用方法（使用OpenCV和NumPy实现融合）

    def Apply_IMGFusion(self):
        # 获取选择的融合方法
        enum = self.GetcomboBox_value()
        if self.imagePathMs == None or self.imagePathPan == None:
            self.showFlyout("WARNING", "灾难性错误： 请先导入图片！")
            return
        Ms = cv2.imread(self.imagePathMs)  # 读取多光谱图像
        Pan = cv2.imread(self.imagePathPan)  # 读取全色图像
        if enum == -1:
            self.showFlyout("WARNING", "灾难性错误： 请先选择图像融合方法！")
            return

        result = None
        if enum == 1:
            # IHS 图像融合（IHSF）
            result = self.IHSFusion(Ms, Pan)
        elif enum == 2:
            # GIHS 图像融合（GIHSF）
            result = self.GIHSFusion(Ms, Pan)
        elif enum == 3:
            # AIHS 图像融合（AIHSF）
            result = self.AIHSFusion(Ms, Pan)
        elif enum == 4:
            # IAIHS 图像融合（IAIHSF）
            result = self.IAIHSFusion(Ms, Pan)

        if result is not None:
            self.result = result


    def IHSFusion(self, Ms, Pan):
        # 将多光谱图像从BGR转换到HSV
        hsv = cv2.cvtColor(Ms, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        # 将全色图像归一化为[0, 255]范围
        pan_resized = cv2.resize(Pan, (Ms.shape[1], Ms.shape[0]))
        pan_gray = cv2.cvtColor(pan_resized, cv2.COLOR_BGR2GRAY)

        # 用全色图像的亮度替换多光谱图像的亮度
        v = pan_gray

        # 合并IHS
        ihs_fused = cv2.merge([h, s, v])

        # 将融合后的图像从HSV转换回BGR
        result = cv2.cvtColor(ihs_fused, cv2.COLOR_HSV2BGR)
        return result

        # GIHS 图像融合（GIHSF）

    def GIHSFusion(self, Ms, Pan):
        # 预处理：去噪
        Ms_denoised = cv2.fastNlMeansDenoisingColored(Ms, None, 10, 10, 7, 21)
        Pan_resized = cv2.resize(Pan, (Ms.shape[1], Ms.shape[0]))

        # IHS融合
        result = self.IHSFusion(Ms_denoised, Pan_resized)
        return result

    def AIHSFusion(self, Ms, Pan):
        # 自适应增强：局部对比度增强
        lab = cv2.cvtColor(Ms, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.equalizeHist(l)  # 对L通道进行直方图均衡化
        lab = cv2.merge([l, a, b])
        Ms_enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        # IHS融合
        result = self.IHSFusion(Ms_enhanced, Pan)
        return result

        # IAIHS 图像融合（IAIHSF）

    def IAIHSFusion(self, Ms, Pan):
        # IAIHS 是一种结合自适应方法和多尺度分析的融合方法
        result = self.IHSFusion(Ms, Pan)
        return result

    # 保存滤波图片的方法
    def Filter_saveImage(self):
        path, ok = QFileDialog.getSaveFileName(
            parent=self,
            caption=self.tr('保存图片'),
            directory=QStandardPaths.writableLocation(QStandardPaths.DesktopLocation),
            filter='TIF (*.tif)'
        )
        if not ok:
            return

        cv2.imwrite(path, self.result/255.0)

