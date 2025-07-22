# ISQ Suite

**ISQ Suite** is a collection of tools developed in Python for the analysis of Nuclear Magnetic Resonance (NMR) spectra organized in matrix format (.csv or .txt).
The suite includes three main programs:

- **iNMR** – Signal integration in NMR spectra datasets.  
- **sNMR** – Spectra scaling and normalization.  
- **qNMR** – Metabolite quantification using internal or external reference.

Download available at: https://github.com/EXCI5ION/isq-suite/releases/

## 🚀 Included Applications

### 🟩 iNMR  
Allows selecting regions of interest and integrating the corresponding peaks in NMR datasets. It exports data tables with relative or absolute integrals.

### 🟦 sNMR  
Scales and normalizes spectra based on various strategies (e.g., internal standard, PQN, or total area).

### 🟥 qNMR  
Quantifies metabolites based on integrals, using internal or external standards depending on the experimental design.

---

## 📁 Data Structure

Input data must be organized as a **matrix** where:

- The **first column** contains chemical shift values (ppm).  
- The **following rows** contain intensity values for each spectrum.  
- The **first row** (starting from the second column onward) contains the sample names.

Files must have a `.csv` or `.txt` extension (with comma-separated values).

> 📘 A more detailed description of the data format and each program is available in the [User Manual](./MANUAL.md).

## 👤 Author

Developed by **Gabriel Anderson**

For questions, suggestions, or contributions, feel free to open an [Issue](https://github.com/EXCI5ION/ISQ-Suite/issues).

---

## ⚙️ Requirements

- Python 3.12  
- [See the `requirements.txt` file](./requirements.txt) for a list of all required dependencies.

To install the dependencies:

```bash
pip install -r requirements.txt
