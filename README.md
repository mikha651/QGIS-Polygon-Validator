# 🔷 Polygon Validator

[![QGIS Plugin](https://img.shields.io/badge/QGIS-Plugin-green)](https://plugins.qgis.org/plugins/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Repo](https://img.shields.io/badge/GitHub-View%20Repository-black)](https://github.com/mikha651/QGIS-Polygon-Validator)


A QGIS Plugin for detecting and visualizing polygon geometry anomalies such as:

- 🟥 Slivers  
- 🧩 Overlaps  
- 🟡 Close Vertices  
- 🔁 Duplicate Vertices  
- 🔺 Sharp Angles  

## 📌 Description

**Polygon Validator** helps you validate polygon geometries in any QGIS vector layer and identify common topological issues. It visually highlights errors directly on the map canvas and creates separate memory layers to store each type of anomaly.

## ⚙️ Features

- ✅ Validate a polygon layer for multiple anomaly types simultaneously.  
- 🖍️ Highlight anomalies with rubber bands (visual indicators).  
- 🗂️ Create temporary error layers (`Error_Points`, `Error_Lines`, `Error_Polygon`) for further analysis.  
- 🔍 Zoom to each anomaly from the result list.  
- 🧹 Option to clean duplicate vertices.  
- 🧭 Customize the sharp angle threshold.  
- 🎨 Emoji-based modern UI for clarity and engagement.  

## 📥 Installation

1. Clone or download this plugin into your QGIS plugins directory:
2. Restart QGIS.  
3. Go to **Plugins > Manage and Install Plugins**, then enable **Polygon Validator**.

## ▶️ Usage

1. Open the **Polygon Validator** panel from the **Plugins** menu.  
2. Select a polygon vector layer from the dropdown.  
3. Check the anomaly types you want to validate.  
4. Set the angle threshold if needed (for sharp angles).  
5. Click **✅ Validate**.  
6. Review anomalies in the list and zoom to each one by clicking.  
7. Use **🧹 Clean Duplicates** to automatically remove repeated vertices.  
8. Use **❌ Clear** to remove results and reset the interface.

## 📂 Output

- **Error_Points**: Memory layer for point-related errors (e.g., sharp angles, duplicates).
- **Error_Lines**: Memory layer for linear errors (e.g., close vertices).
- **Error_Polygon**: Memory layer for areal anomalies (e.g., slivers, overlaps), including attributes:
- `feature_id`: ID(s) of affected feature(s)
- `error_type`: Description of the anomaly
- `area`: Area of the polygon (for overlaps and slivers)
- `perimeter`: Perimeter of the polygon

## 🛠️ Requirements

- QGIS 3.16 or later  
- Python 3.7+

## 🧠 Notes

- All error layers are memory-based and will be lost unless saved manually.  
- The plugin automatically adapts the CRS of all error layers to match the selected input layer.

## 📧 Support

For questions, suggestions, or contributions, feel free to reach out.

---

Made with ❤️ by **Michel El Hourani**
