from PyQt4.QtCore import *
from PyQt4.QtGui import *
import random
import math

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

class CtrlPoint(QPointF):
    def __init__(self, name, x, y):
        super(CtrlPoint, self).__init__(x, y)
        self.setName(name)
    def name(self):
        return self._name
    def setName(self, name):
        self._name = name

class ImagePoint(QPoint):
    def __init__(self, name, x, y):
        super(ImagePoint, self).__init__(x, y)
        self.setName(name)
    def name(self):
        return self._name
    def setName(self, name):
        self._name = name

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
    def clear(self, brush = Qt.black):
        painter = QPainter(self)
        painter.fillRect(self.rect(), brush)
    def paintEvent(self, event):
        self.clear()
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


if __name__ == '__main__':
    app = QApplication([])

    #points = [QPointF(random.randint(-18000, 20000), random.randint(-25000, 25000)) for _ in range(20)]

    points = []
    points.append(CtrlPoint("A", 1000, 1000))
    points.append(CtrlPoint("B", 2000, 1000))
    points.append(CtrlPoint("C", 2000, 2000))
    points.append(CtrlPoint("D", 1000, 2000))
    points.append(CtrlPoint("E", 2000, 3000))
    points.append(CtrlPoint("F", 1000, 3000))
    points.append(CtrlPoint("X", 4000, 5000))

    window = PointsView(points)
    window.setWindowTitle("ArxTabula")
    window.resize(800, 600)
    window.setPadding(25)

    window.addImage("./411.png", [
        ImagePoint("D", 50, 50),
        ImagePoint("C", 250, 50),
        ImagePoint("E", 250, 250),
        ImagePoint("F", 50, 250), ]
    )
    window.addImage("./412b.png", [
        ImagePoint("A", 100, 100),
        ImagePoint("B", 350, 100),
        ImagePoint("C", 350, 350),
        ImagePoint("D", 100, 350), ]
    )

    window.show()

    app.exec_()