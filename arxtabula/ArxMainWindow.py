# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

__all__ = ['ArxMainWindow', ]

class ArxMainWindow(QMainWindow):
    """Main window class."""
    def __init__(self, parent = None):
        super(ArxMainWindow, self).__init__(parent)
        self.ui = Ui_ArxMainWindow(self)

class Ui_ArxMainWindow:
    """User interface for main window class."""
    def __init__(self, widget):
        # Appeareance
        widget.setWindowTitle(widget.tr("ArxTabula"))
        widget.resize(800, 600)
        # Actions
        self.newAct = QAction(widget.tr("&New"), widget)
        # Toolbars
        self.fileToolBar = widget.addToolBar(widget.tr("File"))
        self.fileToolBar.addAction(self.newAct)
