# coding:utf-8
import os
import sys

import numpy as np
import rasterio
from rasterio import open as rio_open
from rasterio.merge import merge
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
class ImageMosaic(GalleryInterface):
    """ Material interface """

    # 初始化方法
    def __init__(self, parent=None):
        t = Translator()
        self.src = None
        self.result = None
        super().__init__(
            title=t.mosaic,
            subtitle='遥感原理与图像处理-影像镶嵌',
            parent=parent
        )
        self.folderPath = None
        self.setObjectName('imagemosaic')
        self.mosaic_array = None
        self.transform = None
        self.crs = None
        self.widget = QWidget(self)
        self.widget.setLayout(QVBoxLayout())
        self.widget.layout().setContentsMargins(0, 0, 0, 0)
        self.widget.layout().setSpacing(10)

        # 创建导入图片按钮B
        self.button_input_B = PushButton(self.tr("选择影像文件夹"))
        self.button_input_B.setFixedWidth(150)
        self.h_layout = QHBoxLayout(self.widget)
        self.h_layout.setSpacing(10)
        self.h_layout.addWidget(self.button_input_B, 0, Qt.AlignLeft)
        self.vBoxLayout.addLayout(self.h_layout)
        self.button_input_B.clicked.connect(self.inputPhoto_B)

        # 创建下拉框
        self.comboBox_filter = ComboBox()
        self.comboBox_filter.setPlaceholderText("请选择影像文件夹")
        self.comboBox_filter.setCurrentIndex(-1)
        self.comboBox_filter.setFixedWidth(100)
        self.comboBox_filter.setMaximumWidth(180)
        self.h_layout.addWidget(self.comboBox_filter, 0, Qt.AlignLeft)
        self.comboBox_filter.currentIndexChanged.connect(self.GetcomboBox_value)

        # 创建Apply按钮
        self.button_input_apply = PushButton(self.tr("Apply"))
        self.button_input_apply.setFixedWidth(100)
        self.button_input_apply.clicked.connect(self.Apply_IMGFusion)
        self.h_layout.addWidget(self.button_input_apply, 0, Qt.AlignLeft)

        # 创建保存滤波图像按钮
        self.button_input_save = PrimaryPushButton(self.tr("保存镶嵌图像"))
        self.button_input_save.setFixedWidth(120)
        self.h_layout.addWidget(self.button_input_save, 0, Qt.AlignLeft)
        self.button_input_save.clicked.connect(self.save_mosaic)

        label = QLabel(self.tr('单击图片打开命令栏，图片将在镶嵌后自动更换！'))
        self.imageLabel = ImageLabel(resource_path('Photos/resource/interface_background/lingsheyinchun.jpg'))
        self.imageLabel2 = ImageLabel(resource_path('Photos/resource/interface_background/doupocangqiong.jpg'))

        self.imageLabel.scaledToWidth(500)
        self.imageLabel2.scaledToWidth(500)
        self.imageLabel.setBorderRadius(8, 8, 8, 8)
        self.imageLabel2.setBorderRadius(8, 8, 8, 8)
        self.imageLabel.clicked.connect(self.createCommandBarFlyout)
        self.imageLabel2.clicked.connect(self.createCommandBarFlyout)

        self.h_layout_photos = QHBoxLayout(self.widget)
        self.h_layout_photos.setSpacing(10)
        self.h_layout_photos.addWidget(self.imageLabel, 0, Qt.AlignLeft)
        self.h_layout_photos.addWidget(self.imageLabel2, 0, Qt.AlignLeft)

        self.widget.layout().addWidget(label)
        self.widget.layout().addLayout(self.h_layout_photos)

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
    # 导入图片的方法
    def inputPhoto_B(self):
        # 打开文件夹选择对话框

        folder_path = QFileDialog.getExistingDirectory(self, "选择影像文件夹")
        self.folderPath =  folder_path
        print(folder_path)
        if folder_path:
            # 获取文件夹内所有支持的影像文件
            supported_formats = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
            self.image_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                                f.lower().endswith(supported_formats)]

            if not self.image_files:
                self.showFlyout("WARNING", "灾难性错误： 文件夹中没有有效的影像文件！")
                return
            # 默认显示第一张影像
            self.current_image_index = 0
            self.display_image_in_label1(self.image_files[self.current_image_index])

            # 更新下拉框内容
            self.comboBox_filter.clear()  # 清空下拉框
            self.comboBox_filter.addItems([os.path.basename(f) for f in self.image_files])  # 填充文件名
            self.comboBox_filter.setCurrentIndex(0)  # 默认选中第一张
            self.comboBox_filter.currentIndexChanged.connect(self.on_dropdown_selection_changed)

    # 显示指定影像到 imageLabel1
    def display_image_in_label1(self, image_path):
        pixmap = QPixmap(image_path)
        self.imageLabel.setPixmap(pixmap)
        self.imageLabel.setMaximumWidth(800)
        self.imageLabel.scaledToWidth(500)  # 设置图片的宽度
        self.imagePathPan = image_path  # 保存当前显示的影像路径
        self.src = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # 用 OpenCV 读取图片

    # 当下拉框选项改变时触发，更新 imageLabel1 显示
    def on_dropdown_selection_changed(self):
        index = self.comboBox_filter.currentIndex()
        if 0 <= index < len(self.image_files):
            self.display_image_in_label1(self.image_files[index])

    def mosaic_rasters(self, input_dir):
        # 读取文件夹中的 GeoTIFF 文件
        rasters = []
        for filename in os.listdir(input_dir):
            if filename.endswith(".tif"):
                file_path = os.path.join(input_dir, filename)
                rasters.append(rio_open(file_path))

        if not rasters:
            raise Exception("输入文件夹中没有找到任何 GeoTIFF 文件！")

        # 执行影像镶嵌
        mosaic_array, out_transform = merge(rasters)

        # 关闭所有影像文件
        for raster in rasters:
            raster.close()

        # 假设镶嵌结果是单波段影像，处理成伪彩色RGB图像
        if mosaic_array.shape[0] == 1:  # 单波段图像
            mosaic_rgb = np.zeros((mosaic_array.shape[1], mosaic_array.shape[2], 3), dtype=np.uint8)
            mosaic_rgb[:, :, 0] = mosaic_array[0]  # 红色通道
            mosaic_rgb[:, :, 1] = mosaic_array[0]  # 绿色通道
            mosaic_rgb[:, :, 2] = mosaic_array[0]  # 蓝色通道
        else:
            # 如果是多波段图像，则取RGB的前三个波段
            mosaic_rgb = np.zeros((mosaic_array.shape[1], mosaic_array.shape[2], 3), dtype=np.uint8)
            mosaic_rgb[:, :, 0] = mosaic_array[0]  # 红色通道
            mosaic_rgb[:, :, 1] = mosaic_array[1]  # 绿色通道
            mosaic_rgb[:, :, 2] = mosaic_array[2]  # 蓝色通道

        # 将RGB图像转换为QImage并显示在ImageLabel2中
        self.display_mosaic(mosaic_rgb)

        return mosaic_array, out_transform, rasters[0].crs

    def display_mosaic(self, mosaic_rgb):
        # 从 numpy 数组创建 QImage
        height, width, _ = mosaic_rgb.shape
        qimage_result = QImage(
            mosaic_rgb.data,
            width,
            height,
            width * 3,
            QImage.Format_RGB888
        )
        # 转为 QPixmap 并显示在 ImageLabel2
        pixmap_result = QPixmap.fromImage(qimage_result)
        self.imageLabel2.setPixmap(pixmap_result)
        self.imageLabel2.scaledToWidth(500)
    def Apply_IMGFusion(self):
        if self.folderPath == None:
            self.showFlyout("WARNING", "灾难性错误： 请先导入图片！")
            return
        self.mosaic_array,self.transform,self.crs = self.mosaic_rasters(self.folderPath)

    def save_mosaic(self):
        try:
            # 打开保存文件对话框，让用户选择保存路径
            path, ok = QFileDialog.getSaveFileName(
                parent=self,
                caption=self.tr('保存影像'),
                directory=QStandardPaths.writableLocation(QStandardPaths.DesktopLocation),
                filter='TIF (*.tif)'
            )

            # 如果用户未选择保存路径，终止操作
            if not ok:
                return

            # 保存镶嵌结果到用户选择的路径
            with rasterio.open(
                    path,  # 使用用户选择的路径
                    'w',
                    driver='GTiff',
                    height=self.mosaic_array.shape[1],
                    width=self.mosaic_array.shape[2],
                    count=self.mosaic_array.shape[0],
                    dtype=self.mosaic_array.dtype,
                    crs=self.crs,
                    transform=self.transform,
            ) as dst:
                for i in range(1, self.mosaic_array.shape[0] + 1):
                    dst.write(self.mosaic_array[i - 1], i)
        except Exception as e:
            raise Exception(f"影像镶嵌失败: {e}")

