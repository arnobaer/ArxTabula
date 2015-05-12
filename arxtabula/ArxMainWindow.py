# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import math

__all__ = ['ArxMainWindow', 'CtrlPoint', ]

class CtrlPoint(QPointF):
    def __init__(self, name, x, y):
        super(CtrlPoint, self).__init__(x, y)
        self.setName(name)
    def name(self):
        return self._name
    def setName(self, name):
        self._name = name

def boundingRectF(points):
    """Calculate bounding rectangle for list of points."""
    topLeft = QPointF(
        min([point.x() for point in points]),
        min([point.y() for point in points])
    )
    bottomRight = QPointF(
        max([point.x() for point in points]),
        max([point.y() for point in points])
    )
    return QRectF(topLeft.x(), topLeft.y(), bottomRight.x() - topLeft.x(), bottomRight.y() - topLeft.y())

def dist(p, q):
    """Euclidean 2 dimensional distance."""
    return math.sqrt(math.pow(p.x() - q.x(), 2) + math.pow(p.y() - q.y(), 2))

class CorrectedImage(object):
    def __init__(self, filename, points):
        self.setImage(filename)
        self.setPoints(points)
    def setImage(self, filename):
        self._pixmap = QPixmap(filename)
    def image(self):
        return self._pixmap
    def setPoints(self, points):
        self._points = points
    def points(self):
        return self._points
    def point(self, name):
        return filter(lambda point: point.name() == name, self._points)[0]
    def scaleFactor(self, p1, p2):
        return dist(p1, p2) / dist(self.point(p1.name()), self.point(p2.name()))
    def scaled(self, p1, p2):
        scale = self.scaleFactor(p1, p2)
        return self.image().scaled(self.image().width() * scale, self.image().height() * scale)
    def isValid(self):
        return (not self.image().isNull()) and len(self.points()) >= 2

class PointsView(QWidget):
    def __init__(self, points = [], parent = None):
        super(PointsView, self).__init__(parent)
        self.setPoints(points)
        self.setPadding(0)
        self.clearImages()
    def points(self):
        return self._points
    def setPoints(self, points):
        self._points = points
    def padding(self):
        return self._padding
    def setPadding(self, padding):
        self._padding = padding
        self.setMinimumSize(2 * padding + 1, 2 * padding + 1)
    def clearImages(self):
        self._images = []
    def addImage(self, filename, points):
        self._images.append(CorrectedImage(filename, points))
    def images(self):
        return self._images
    def boundingRect(self):
        return boundingRectF(self.points())
    def _scale(self, size, rect, padding = 0):
        """Returns scaling factor for points to display."""
        scale_x = rect.width() / ((size.width() - 2 * padding) or 1) # Prevent division by zero
        scale_y = rect.height() / ((size.height() - 2 * padding) or 1) # Prevent division by zero
        return max((scale_x, scale_y))
    #def clear(self, brush = Qt.black):
        #painter = QPainter(self)
        #painter.fillRect(self.rect(), brush)
    def paintEvent(self, event):
        #self.clear()
        padding = self.padding()
        size = self.size()
        rect = self.boundingRect()
        scale = self._scale(size, rect, padding)
        new_points = []
        for point in self.points():
            x = ((point.x() - rect.x()) / scale) + padding
            y = ((point.y() - rect.y()) / scale) + padding
            new_points.append(CtrlPoint(point.name(), x, y))
        # Bounding rect for new transformed points.
        bounding_rect = boundingRectF(new_points)
        painter = QPainter(self)
        painter.setPen(Qt.yellow)
        offset = QSize(
            ((size.width() - 2 * padding) / 2) - (bounding_rect.width() / 2),
            ((size.height() - 2 * padding) / 2) - (bounding_rect.height() / 2)
        )
        #
        for image in self.images():
            if image.isValid():
                p1 = filter(lambda point: point.name() == image.points()[0].name(), new_points)[0]
                p2 = filter(lambda point: point.name() == image.points()[1].name(), new_points)[0]
                scale = image.scaleFactor(p1, p2)
                pixmap = image.scaled(p1, p2)
                painter.drawPixmap(
                    QPoint(
                        p1.x() + offset.width() - (image.point(p1.name()).x() * scale),
                        p1.y() + offset.height() - (image.point(p1.name()).y() * scale),
                    ),
                    pixmap,
                    pixmap.rect()
                )
        #
        for i, point in enumerate(new_points):
            # Center on widget.
            x = point.x() + offset.width()
            y = point.y() + offset.height()
            painter.drawPoint(x, y)
            painter.drawArc(QRect(x-5, y-5, 10, 10), 0, 16 * 360)
            painter.drawText(x+5, y-5, point.name())
    def onResizeEvent(self, event):
        event.accept()

class ArxMainWindow(QMainWindow):
    """Main window class."""
    def __init__(self, parent = None):
        super(ArxMainWindow, self).__init__(parent)
        self.ui = Ui_ArxMainWindow(self)
    def viewportSize(self):
        size = self.ui.area.size()
        return QSize(
            size.width() - self.ui.area.verticalScrollBar().size().width(),
            size.height() - self.ui.area.horizontalScrollBar().size().height()
        )
    def scaleImage(self, factor):
        size = self.ui.view.size()
        self.ui.view.setFixedSize(self.ui.view.size() * factor)
        self.adjustScrollBar(self.ui.area.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.ui.area.verticalScrollBar(), factor)
    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value() + ((factor - 1) * scrollBar.pageStep()/2)))
    def zoomAll(self):
        size = self.viewportSize()
        self.ui.view.setFixedSize(size)
    def zoomIn(self):
        self.scaleImage(1.25)
    def zoomOut(self):
        self.scaleImage(0.8)
    def setPoints(self, points):
        self.ui.view.setPoints(points)
    def addImage(self, filename, points):
        self.ui.view.addImage(filename, points)
    def clearImages(self):
        self.ui.view.clearImages()

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
        # View widgets
        self.view = PointsView([], widget)
        #self.view.setMinimumSize(800, 600)
        self.view.setPadding(25)
        # Area widget
        self.area = QScrollArea(widget)
        self.area.setWidget(self.view)
        self.area.setAlignment(Qt.AlignCenter)
        palette = self.area.palette()
        palette.setColor(QPalette.Window, Qt.black)

        self.area.setPalette(palette)
        #self.area.setWidgetResizable(True)
        widget.setCentralWidget(self.area)
        # Re-set widget size.
        self.view.setMinimumSize(800, 600)
