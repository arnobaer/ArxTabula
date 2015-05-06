# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

__all__ = ['ArxMainWindow', ]

class ArxMainWindow(QMainWindow):
    """Main window class."""
    def __init__(self, parent = None):
        super(ArxMainWindow, self).__init__(parent)
        self.ui = Ui_ArxMainWindow(self)
    def viewportSize(self):
        size = self.area.size()
        return QSize(
            size.width() - self.area.verticalScrollBar().size().width(),
            size.height() - self.area.horizontalScrollBar().size().height()
        )
    def scaleImage(self, factor):
        size = self.view.size()
        self.view.setFixedSize(self.view.size() * factor)
        self.adjustScrollBar(self.area.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.area.verticalScrollBar(), factor)
    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))
    def zoomAll(self):
        size = self.viewportSize()
        self.view.setFixedSize(size)
    def zoomIn(self):
        self.scaleImage(1.25)
    def zoomOut(self):
        self.scaleImage(0.8)

class Ui_ArxMainWindow:
    """User interface for main window class."""
    def __init__(self, widget):
        # Appeareance
        widget.setWindowTitle(widget.tr("ArxTabula"))
        widget.resize(800, 600)
        # Actions
        self.zoomAllAct = QAction(widget.tr("Zoom &All"), widget)
        self.zoomAllAct.triggered.connect(widget.zoomAll)
        self.zoomInAct = QAction(widget.tr("Zoom &In"), widget)
        self.zoomInAct.triggered.connect(widget.zoomIn)
        self.zoomOutAct = QAction(widget.tr("Zoom &Out"), widget)
        self.zoomOutAct.triggered.connect(widget.zoomOut)
        # Toolbars
        self.fileToolBar = widget.addToolBar(widget.tr("File"))
        self.fileToolBar.addAction(self.zoomInAct)
        self.fileToolBar.addAction(self.zoomOutAct)
        self.fileToolBar.addAction(self.zoomAllAct)
