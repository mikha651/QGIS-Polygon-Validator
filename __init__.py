def classFactory(iface):
    from .plugin import PolygonValidator
    return PolygonValidator(iface)
