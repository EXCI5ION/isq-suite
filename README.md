# ISQ Suite

**ISQ Suite** es una colección de herramientas desarrolladas en Python para el análisis de espectros de Resonancia Magnética Nuclear (RMN) organizados en formato matricial (.csv o .txt). La suite está compuesta por tres programas principales:

- **iNMR** – Integración de señales en espectros de RMN.
- **sNMR** – Escalado y normalización de espectros.
- **qNMR** – Cuantificación de metabolitos utilizando referencia interna o externa.

Descarga disponible en: https://github.com/EXCI5ION/isq-suite

## 🚀 Aplicaciones incluidas

### 🟩 iNMR
Permite seleccionar regiones de interés e integrar los picos correspondientes en sets de datos de RMN.

### 🟦 sNMR
Escala y normaliza espectros en función de distintas estrategias (por ejemplo, intensidad máxima o área total).

### 🟥 qNMR
Cuantifica metabolitos a partir de integrales, utilizando estándares internos o externos según el diseño experimental.

---

## 📁 Estructura de los datos

Los datos de entrada deben estar organizados como una **matriz** donde:

- La **primera columna** contiene los valores de desplazamiento químico (ppm).
- Las **filas siguientes** contienen las intensidades para cada espectro.
- La **primera fila** (desde la segunda columna en adelante) contiene los nombres de las muestras.

Los archivos deben tener extensión `.csv` o `.txt` (con valores separados por coma).

> 📘 Una descripción más detallada del formato de los datos y de cada programa se encuentra disponible en el [manual de usuario](./MANUAL.md).

## 👤 Autoría

Desarrollado por **Gabriel Anderson**

Para dudas, sugerencias o contribuciones, podés abrir un [Issue](https://github.com/EXCI5ION/ISQ-Suite/issues).

---

## ⚙️ Requisitos

- Python 3.10
- [Ver archivo `requirements.txt`](./requirements.txt) para conocer todas las dependencias necesarias.

Instalación de dependencias:

```bash
pip install -r requirements.txt
