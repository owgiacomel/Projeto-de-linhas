# -*- coding: utf-8 -*-
"""Core implementation for the Flight Line Connector QGIS plugin."""

import os
from typing import List, Optional, Sequence, Tuple

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import (
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsLineString,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
)


class FlightLineConnectorPlugin:
    """Plugin that creates connecting lines and safety polygons for spray drones."""

    ACTION_TEXT = "Criar linhas contínuas e áreas de segurança"
    MENU_TEXT = "&Projeto de linhas"
    CONNECTION_LAYER_NAME = "Linhas de Ligação"
    POLYGON_LAYER_NAME = "Zonas de Não Pulverização"

    def __init__(self, iface):
        """Set up the plugin instance."""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.action: Optional[QAction] = None

    # ------------------------------------------------------------------
    # QGIS plugin lifecycle
    # ------------------------------------------------------------------
    def tr(self, message: str) -> str:
        """Translate using Qt translation API."""
        return QCoreApplication.translate("FlightLineConnectorPlugin", message)

    def initGui(self) -> None:
        """Create the menu entry and toolbar icon inside QGIS."""
        icon = QIcon(os.path.join(self.plugin_dir, "icon.svg"))
        self.action = QAction(icon, self.tr(self.ACTION_TEXT), self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(self.tr(self.MENU_TEXT), self.action)

    def unload(self) -> None:
        """Remove the plugin from QGIS UI."""
        if self.action is not None:
            self.iface.removePluginMenu(self.tr(self.MENU_TEXT), self.action)
            self.iface.removeToolBarIcon(self.action)
            self.action.deleteLater()
            self.action = None

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Execute the plugin main routine."""
        layer = self.iface.activeLayer()
        if layer is None or layer.geometryType() != QgsWkbTypes.LineGeometry:
            self._show_message(
                self.tr("Selecione uma camada de linhas ativa para executar o plugin."),
                level="warning",
            )
            return

        features = list(layer.selectedFeatures())
        if not features:
            features = list(layer.getFeatures())
        if len(features) < 2:
            self._show_message(
                self.tr("São necessárias pelo menos duas linhas para gerar as ligações."),
                level="warning",
            )
            return

        features.sort(key=lambda f: f.id())

        connection_layer = self._get_or_create_layer(
            self.CONNECTION_LAYER_NAME,
            QgsWkbTypes.LineString,
            layer.crs(),
            [QgsField("from_id", QVariant.LongLong), QgsField("to_id", QVariant.LongLong)],
        )
        polygon_layer = self._get_or_create_layer(
            self.POLYGON_LAYER_NAME,
            QgsWkbTypes.Polygon,
            layer.crs(),
            [
                QgsField("from_id", QVariant.LongLong),
                QgsField("to_id", QVariant.LongLong),
                QgsField("comprimento", QVariant.Double),
            ],
        )

        connection_features: List[QgsFeature] = []
        polygon_features: List[QgsFeature] = []

        for idx in range(len(features) - 1):
            source_feat = features[idx]
            target_feat = features[idx + 1]
            connection = self._create_connection_geometry(
                source_feat.geometry(), target_feat.geometry()
            )
            if connection is None or connection.isEmpty():
                continue

            connection_feature = QgsFeature(connection_layer.fields())
            connection_feature.setGeometry(connection)
            connection_feature.setAttribute("from_id", int(source_feat.id()))
            connection_feature.setAttribute("to_id", int(target_feat.id()))
            connection_features.append(connection_feature)

            polygon_geom = self._create_safety_polygon(connection)
            if polygon_geom is not None and not polygon_geom.isEmpty():
                polygon_feature = QgsFeature(polygon_layer.fields())
                polygon_feature.setGeometry(polygon_geom)
                polygon_feature.setAttribute("from_id", int(source_feat.id()))
                polygon_feature.setAttribute("to_id", int(target_feat.id()))
                polygon_feature.setAttribute("comprimento", connection.length())
                polygon_features.append(polygon_feature)

        if not connection_features:
            self._show_message(
                self.tr("Não foi possível gerar nenhuma ligação entre as linhas selecionadas."),
                level="warning",
            )
            return

        self._add_features(connection_layer, connection_features)

        if polygon_features:
            self._add_features(polygon_layer, polygon_features)

        self._show_message(
            self.tr(
                "Foram adicionadas {0} linhas de ligação e {1} zonas de não pulverização."
            ).format(len(connection_features), len(polygon_features)),
            level="info",
        )

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _show_message(self, message: str, level: str = "info") -> None:
        """Display a message on the QGIS message bar."""
        levels = {
            "info": self.iface.messageBar().INFO,
            "warning": self.iface.messageBar().WARNING,
            "critical": self.iface.messageBar().CRITICAL,
        }
        self.iface.messageBar().pushMessage(
            self.tr("Projeto de linhas"), message, level=levels.get(level, 0), duration=8
        )

    def _get_or_create_layer(
        self,
        name: str,
        geometry_type: QgsWkbTypes.GeometryType,
        crs,
        fields: Sequence[QgsField],
    ) -> QgsVectorLayer:
        """Return an existing layer by name or create a new memory layer."""
        matches = QgsProject.instance().mapLayersByName(name)
        if matches:
            layer = matches[0]
            provider = layer.dataProvider()
            existing_fields = {field.name() for field in layer.fields()}
            to_add = [field for field in fields if field.name() not in existing_fields]
            if to_add:
                layer.startEditing()
                provider.addAttributes(to_add)
                layer.commitChanges()
            return layer

        geometry_string = QgsWkbTypes.displayString(int(geometry_type))
        layer = QgsVectorLayer(f"{geometry_string}?crs={crs.authid()}", name, "memory")
        provider = layer.dataProvider()
        provider.addAttributes(list(fields))
        layer.updateFields()
        QgsProject.instance().addMapLayer(layer)
        return layer

    def _add_features(self, layer: QgsVectorLayer, features: Sequence[QgsFeature]) -> None:
        """Add features to a layer, managing edit sessions when required."""
        if not features:
            return

        provider = layer.dataProvider()
        if layer.isEditable():
            provider.addFeatures(features)
            layer.updateExtents()
            layer.triggerRepaint()
            return

        layer.startEditing()
        provider.addFeatures(features)
        layer.commitChanges()
        layer.updateExtents()
        layer.triggerRepaint()

    def _create_connection_geometry(
        self, source_geom: QgsGeometry, target_geom: QgsGeometry
    ) -> Optional[QgsGeometry]:
        """Build a straight line connecting the closest endpoints of two features."""
        source_points = self._extract_endpoints(source_geom)
        target_points = self._extract_endpoints(target_geom)
        if len(source_points) < 2 or len(target_points) < 2:
            return None

        candidates: List[Tuple[QgsPointXY, QgsPointXY, float]] = []
        for s in source_points:
            for t in target_points:
                candidates.append((s, t, s.distance(t)))

        candidates.sort(key=lambda item: item[2])
        if not candidates:
            return None

        best_source, best_target, _ = candidates[0]
        return QgsGeometry.fromPolylineXY([best_source, best_target])

    def _extract_endpoints(self, geometry: QgsGeometry) -> List[QgsPointXY]:
        """Extract start and end points from a line geometry."""
        if geometry is None or geometry.isEmpty():
            return []

        if geometry.isMultipart():
            multi_polyline = geometry.asMultiPolyline()
            if not multi_polyline:
                return []
            polyline: List[QgsPointXY] = [QgsPointXY(pt) for pt in multi_polyline[0]]
        else:
            line = geometry.constGet()
            if isinstance(line, QgsLineString):
                polyline = [QgsPointXY(pt) for pt in line.points()]
            else:
                polyline = [QgsPointXY(pt) for pt in geometry.asPolyline()]

        if len(polyline) < 2:
            return []

        return [polyline[0], polyline[-1]]

    def _create_safety_polygon(self, line_geom: QgsGeometry) -> Optional[QgsGeometry]:
        """Generate a polygon 10 m shorter than the line and 5 m wide on each side."""
        length = line_geom.length()
        if length <= 10:
            return None

        trimmed = line_geom.lineSubstring(5, length - 5)
        if trimmed is None or trimmed.isEmpty():
            return None

        polygon = trimmed.buffer(
            5,
            segments=5,
            endCapStyle=QgsGeometry.EndCapFlat,
            joinStyle=QgsGeometry.JoinStyleMiter,
            miterLimit=2.0,
        )
        return polygon if polygon is not None and not polygon.isEmpty() else None
