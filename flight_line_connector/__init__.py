# -*- coding: utf-8 -*-
"""QGIS plugin entry point for the Flight Line Connector plugin."""


def classFactory(iface):
    """Load FlightLineConnectorPlugin class."""
    from .plugin import FlightLineConnectorPlugin
    return FlightLineConnectorPlugin(iface)
