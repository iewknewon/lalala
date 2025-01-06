# coding:utf-8
import os
os.environ["PYTHONIOENCODING"] = "utf-8"
import sys
# 获取当前文件的目录路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 将 libGD_f 文件夹路径添加到 sys.path 中
libgd_path = os.path.join(current_dir, 'libGD_f')
sys.path.append(libgd_path)

# 将 DLL 文件路径添加到环境变量中
os.environ['PATH'] = libgd_path + os.pathsep + os.environ['PATH']
from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from app.common.config import cfg
from app.view.main_window import MainWindow


# 启用 DPI 缩放
# 如果配置为 "Auto"，则启用高 DPI 缩放并设置缩放因子舍入策略为 "PassThrough"
# 否则，禁用高 DPI 缩放并设置缩放因子为配置值
if cfg.get(cfg.dpiScale) == "Auto":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

# 设置应用程序以使用高 DPI 图像
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# 创建 QApplication 实例
app = QApplication(sys.argv)
# 设置不创建本地窗口小部件兄弟
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

# 国际化设置，汉化中文
# 获取配置的语言值
locale = cfg.get(cfg.language).value
translator = FluentTranslator(locale)
galleryTranslator = QTranslator()
galleryTranslator.load(locale, "gallery", ".", ":/gallery/i18n")

# 将这两个翻译器安装到应用程序中
app.installTranslator(translator)
app.installTranslator(galleryTranslator)

# libGD.testWorking()

# 创建主窗口实例
w = MainWindow()
w.show()

app.exec_()

