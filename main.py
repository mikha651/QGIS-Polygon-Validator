from qgis.PyQt.QtWidgets import (
    QDockWidget, QVBoxLayout, QWidget, QLabel, QPushButton,
    QComboBox, QListWidget, QCheckBox, QHBoxLayout, QSpinBox
)
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY,
    QgsWkbTypes, QgsField, QgsFields, QgsVectorDataProvider,
    QgsPoint, QgsLineString
)
from qgis.gui import QgsRubberBand
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QColor
import math

class AnomalyValidatorDockWidget(QDockWidget):
    def __init__(self, iface):
        super().__init__("🔷 Polygon Validator")
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.widget = QWidget()
        self.setWidget(self.widget)

        self.layout = QVBoxLayout()
        self.widget.setLayout(self.layout)

        self.label = QLabel("📂 Select Polygon Layer:")
        self.layerCombo = QComboBox()

        self.sliverCheck = QCheckBox("🟥 Slivers")
        self.sliverCheck.setChecked(True)

        self.overlapCheck = QCheckBox("🧩 Overlaps")
        self.overlapCheck.setChecked(True)

        self.closeCheck = QCheckBox("🟡 Close Vertices")
        self.closeCheck.setChecked(True)

        self.duplicateCheck = QCheckBox("🔁 Duplicate Vertices")
        self.duplicateCheck.setChecked(True)

        self.angleCheck = QCheckBox("🔺 Sharp Angles")
        self.angleCheck.setChecked(True)

        self.angleLabel = QLabel("🧭 Angle Threshold (°):")
        self.angleSpin = QSpinBox()
        self.angleSpin.setRange(1, 179)
        self.angleSpin.setValue(30)

        self.validateButton = QPushButton("✅ Validate")
        self.cleanButton = QPushButton("🧹 Clean Duplicates")
        self.clearButton = QPushButton("❌ Clear")

        self.anomalyList = QListWidget()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.layerCombo)
        self.layout.addWidget(self.sliverCheck)
        self.layout.addWidget(self.overlapCheck)
        self.layout.addWidget(self.closeCheck)
        self.layout.addWidget(self.duplicateCheck)

        angleLayout = QHBoxLayout()
        angleLayout.addWidget(self.angleCheck)
        angleLayout.addStretch()
        angleLayout.addWidget(self.angleLabel)
        angleLayout.addWidget(self.angleSpin)
        self.layout.addLayout(angleLayout)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.validateButton)
        buttonLayout.addWidget(self.cleanButton)
        buttonLayout.addWidget(self.clearButton)
        self.layout.addLayout(buttonLayout)

        self.layout.addWidget(QLabel("📋 Anomalies:"))
        self.layout.addWidget(self.anomalyList)

        self.validateButton.clicked.connect(self.run_validation)
        self.cleanButton.clicked.connect(self.remove_duplicate_vertices)
        self.clearButton.clicked.connect(self.clear_all)
        self.anomalyList.itemClicked.connect(self.zoom_to_anomaly)

        self.rubberBands = []
        self.anomalyGeometries = {}
        self.pointErrorLayer = None
        self.lineErrorLayer = None
        self.overlapLayer = None

        self.populate_layers()

    def closeEvent(self, event):
        self.clear_all()
        event.accept()

    def populate_layers(self):
        self.layerCombo.clear()
        for layer in QgsProject.instance().mapLayers().values():
            if isinstance(layer, QgsVectorLayer) and layer.geometryType() == QgsWkbTypes.PolygonGeometry:
                self.layerCombo.addItem(layer.name(), layer)

    def run_validation(self):
        self.clear_all()
        self.create_error_layers()
        layer = self.layerCombo.currentData()
        if not layer:
            return

        angle_threshold = self.angleSpin.value()
        features = list(layer.getFeatures())

        for feature in features:
            geom = feature.geometry()
            if not geom:
                continue

            if geom.isMultipart():
                polygons = geom.asMultiPolygon()
            else:
                polygons = [geom.asPolygon()]

            for polygon in polygons:
                for ring in polygon:
                    perimeter = geom.length()
                    area = geom.area()
                    if perimeter == 0:
                        continue

                    if self.sliverCheck.isChecked():
                        compactness = area / perimeter
                        if compactness < 0.5:
                            self.highlight_anomaly(ring, "Sliver", feature.id())

                    if self.closeCheck.isChecked():
                        for i in range(len(ring) - 1):
                            pt1 = QgsPointXY(ring[i])
                            pt2 = QgsPointXY(ring[i + 1])
                            if pt1.distance(pt2) < 0.01 * perimeter:
                                self.highlight_line(pt1, pt2, "Close Vertices", feature.id())

                    if self.duplicateCheck.isChecked():
                        seen_coords = set()
                        for pt in ring[:-1]:
                            coord = (round(pt.x(), 8), round(pt.y(), 8))
                            if coord in seen_coords:
                                self.highlight_point(QgsPointXY(pt), "Duplicate Vertices", feature.id())
                            else:
                                seen_coords.add(coord)

                    if self.angleCheck.isChecked():
                        for i in range(1, len(ring) - 1):
                            a = QgsPointXY(ring[i - 1])
                            b = QgsPointXY(ring[i])
                            c = QgsPointXY(ring[i + 1])
                            angle = self.calculate_angle(a, b, c)
                            if angle < angle_threshold:
                                self.highlight_point(b, f"Sharp Angle: {angle:.2f}°", feature.id())

        if self.overlapCheck.isChecked():
            for i in range(len(features)):
                for j in range(i + 1, len(features)):
                    geom_i = features[i].geometry()
                    geom_j = features[j].geometry()
                    if not geom_i or not geom_j:
                        continue
                    if geom_i.intersects(geom_j):
                        overlap_geom = geom_i.intersection(geom_j)
                        if overlap_geom and overlap_geom.isGeosValid() and overlap_geom.type() == QgsWkbTypes.PolygonGeometry:
                            self.highlight_overlap(overlap_geom, features[i].id(), features[j].id())

        self.pointErrorLayer.updateExtents()
        self.lineErrorLayer.updateExtents()
        self.overlapLayer.updateExtents()
        self.canvas.refresh()

    def highlight_anomaly(self, points, label, fid):
        rb = QgsRubberBand(self.canvas, QgsWkbTypes.PolygonGeometry)
        rb.setColor(QColor(255, 0, 0, 150))
        rb.setWidth(2)
        for pt in points:
            rb.addPoint(QgsPointXY(pt))
        rb.closePoints()
        self.rubberBands.append(rb)

        item_text = f"Feature {fid}: {label}"
        self.anomalyList.addItem(item_text)
        geom = QgsGeometry.fromPolygonXY([list(map(QgsPointXY, points))])
        self.anomalyGeometries[item_text] = geom

    def highlight_point(self, point, label, fid):
        rb = QgsRubberBand(self.canvas, QgsWkbTypes.PointGeometry)
        rb.setColor(QColor(255, 255, 0))
        rb.setWidth(10)
        rb.addPoint(point)
        self.rubberBands.append(rb)

        item_text = f"Feature {fid}: {label}"
        self.anomalyList.addItem(item_text)
        geom = QgsGeometry.fromPointXY(point)
        self.anomalyGeometries[item_text] = geom

        f = QgsFeature(self.pointErrorLayer.fields())
        f.setGeometry(geom)
        f.setAttributes([fid, label])
        self.pointErrorLayer.dataProvider().addFeature(f)

    def highlight_line(self, pt1, pt2, label, fid):
        rb = QgsRubberBand(self.canvas, QgsWkbTypes.LineGeometry)
        rb.setColor(QColor(0, 255, 255))
        rb.setWidth(3)
        rb.addPoint(pt1)
        rb.addPoint(pt2)
        self.rubberBands.append(rb)

        item_text = f"Feature {fid}: {label}"
        self.anomalyList.addItem(item_text)
        geom = QgsGeometry.fromPolylineXY([pt1, pt2])
        self.anomalyGeometries[item_text] = geom

        f = QgsFeature(self.lineErrorLayer.fields())
        f.setGeometry(geom)
        f.setAttributes([fid, label, geom.length()])
        self.lineErrorLayer.dataProvider().addFeature(f)

    def highlight_overlap(self, geom, fid1, fid2):
        item_text = f"Overlap: Features {fid1} & {fid2}"
        self.anomalyList.addItem(item_text)
        self.anomalyGeometries[item_text] = geom
        f = QgsFeature(self.overlapLayer.fields())
        f.setGeometry(geom)
        f.setAttributes([f"{fid1}&{fid2}", "Overlap", geom.length(), geom.area()])
        self.overlapLayer.dataProvider().addFeature(f)

    def create_error_layers(self):
        base_crs = self.layerCombo.currentData().crs().authid()
        self.pointErrorLayer = QgsVectorLayer(f"Point?crs={base_crs}", "Error_Points", "memory")
        self.lineErrorLayer = QgsVectorLayer(f"LineString?crs={base_crs}", "Error_Lines", "memory")
        self.overlapLayer = QgsVectorLayer(f"Polygon?crs={base_crs}", "Error_Polygon", "memory")

        self.pointErrorLayer.dataProvider().addAttributes([
            QgsField("feature_id", QVariant.String),
            QgsField("error_type", QVariant.String)
        ])
        self.lineErrorLayer.dataProvider().addAttributes([
            QgsField("feature_id", QVariant.String),
            QgsField("error_type", QVariant.String),
            QgsField("length", QVariant.Double)
        ])
        self.overlapLayer.dataProvider().addAttributes([
            QgsField("feature_id", QVariant.String),
            QgsField("error_type", QVariant.String),
            QgsField("perimeter", QVariant.Double),
            QgsField("area", QVariant.Double)
        ])
        for layer in [self.pointErrorLayer, self.lineErrorLayer, self.overlapLayer]:
            layer.updateFields()
            QgsProject.instance().addMapLayer(layer)

    def clear_all(self):
        for rb in self.rubberBands:
            self.canvas.scene().removeItem(rb)
        self.rubberBands.clear()
        self.anomalyList.clear()
        self.anomalyGeometries.clear()

        for lyr in [self.pointErrorLayer, self.lineErrorLayer, self.overlapLayer]:
            if lyr and QgsProject.instance().mapLayer(lyr.id()):
                QgsProject.instance().removeMapLayer(lyr.id())

        self.pointErrorLayer = self.lineErrorLayer = self.overlapLayer = None
        self.canvas.refresh()

    def zoom_to_anomaly(self, item):
        geom = self.anomalyGeometries.get(item.text())
        if geom:
            self.canvas.setExtent(geom.boundingBox())
            self.canvas.refresh()

    def calculate_angle(self, a, b, c):
        ba = (a.x() - b.x(), a.y() - b.y())
        bc = (c.x() - b.x(), c.y() - b.y())
        dot_product = ba[0] * bc[0] + ba[1] * bc[1]
        mag_ba = math.hypot(*ba)
        mag_bc = math.hypot(*bc)
        if mag_ba == 0 or mag_bc == 0:
            return 180
        cos_angle = dot_product / (mag_ba * mag_bc)
        cos_angle = min(1, max(-1, cos_angle))
        return math.degrees(math.acos(cos_angle))

    def remove_duplicate_vertices(self):
        layer = self.layerCombo.currentData()
        if not layer:
            return
        if not layer.isEditable():
            layer.startEditing()

        for feature in layer.getFeatures():
            geom = feature.geometry()
            if not geom or geom.isEmpty():
                continue

            polygons = geom.asMultiPolygon() if geom.isMultipart() else [geom.asPolygon()]
            new_polygons = []

            for polygon in polygons:
                new_rings = []
                for ring in polygon:
                    seen = set()
                    new_ring = []
                    for pt in ring[:-1]:
                        coord = (round(pt.x(), 8), round(pt.y(), 8))
                        if coord not in seen:
                            seen.add(coord)
                            new_ring.append(pt)
                    if new_ring and new_ring[0] != new_ring[-1]:
                        new_ring.append(new_ring[0])
                    new_rings.append(new_ring)
                new_polygons.append(new_rings)

            new_geom = QgsGeometry.fromMultiPolygonXY(new_polygons) if geom.isMultipart() else QgsGeometry.fromPolygonXY(new_polygons[0])
            layer.changeGeometry(feature.id(), new_geom)

        layer.triggerRepaint()
        self.iface.messageBar().pushMessage("✅ Done", "Duplicate vertices cleaned — changes not yet saved", level=0)
