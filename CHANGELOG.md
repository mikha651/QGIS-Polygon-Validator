# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-06-26

### 🎉 Initial Release

- Added support for detecting and visualizing polygon anomalies:
  - 🟥 Slivers
  - 🧩 Overlaps
  - 🟡 Close Vertices
  - 🔁 Duplicate Vertices
  - 🔺 Sharp Angles
- Interactive UI with modern emoji-based layout.
- Allows selecting multiple anomaly types at once.
- Rubber band highlighting for map visualization.
- Auto-generation of memory layers:
  - `Error_Points` (for point-based anomalies)
  - `Error_Lines` (for linear issues)
  - `Error_Polygon` (for area overlaps and slivers)
- Zoom to anomaly feature.
- Cleanup tool for removing duplicate vertices.
- Angle threshold customization.
- Error layer CRS auto-matches selected input layer.

---

### 📌 Notes

- All generated layers are in-memory. Save them manually if needed.
- Designed for QGIS 3.16 and above.

