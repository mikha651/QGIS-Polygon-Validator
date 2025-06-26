from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .main import AnomalyValidatorDockWidget
from PyQt5.QtCore import Qt

class PolygonValidator:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dockWidget = None

    def initGui(self):
        self.action = QAction(QIcon(), "🔷 Polygon Validator", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&Polygon Validator", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.dockWidget:
            self.iface.removeDockWidget(self.dockWidget)
        self.iface.removePluginMenu("&Polygon Validator", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        if not self.dockWidget:
            self.dockWidget = AnomalyValidatorDockWidget(self.iface)
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockWidget)
        else:
            self.dockWidget.populate_layers()
            self.dockWidget.show()
