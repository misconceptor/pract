# Lab 3 — Basic Raster Algorithms

A desktop application (Python + Tkinter) that demonstrates and compares
the classic rasterization algorithms for lines and circles:

- **Step-by-step** (naive) line algorithm
- **DDA** (Digital Differential Analyzer) line algorithm
- **Bresenham's** line algorithm
- **Bresenham's** circle algorithm

Plus two bonus features:

- **Castle-Pitway** line algorithm (an independent 1967 formulation of
  what is now called Bresenham's line algorithm)
- **Xiaolin Wu's** anti-aliased line algorithm

The UI shows a math-style coordinate grid with axes, tick labels and a
scalable grid; each algorithm pixel is rendered as the unit cell
`[x, x+1] × [y, y+1]`, and a red dashed overlay shows the ideal
mathematical shape the raster approximates.

---

## Table of contents

- [Lab 3 — Basic Raster Algorithms](#lab-3--basic-raster-algorithms)
  - [Table of contents](#table-of-contents)
  - [Requirements](#requirements)
- [Quick Start](#quick-start)
  - [1. Clone / unzip the project, then from the project root:](#1-clone--unzip-the-project-then-from-the-project-root)
  - [2. Activate the virtual environment](#2-activate-the-virtual-environment)
    - [Linux / macOS:](#linux--macos)
    - [Windows (PowerShell):](#windows-powershell)
  - [Windows (cmd):](#windows-cmd)
  - [3. Install dependencies (pytest + pyinstaller)](#3-install-dependencies-pytest--pyinstaller)
  - [4. Run the application](#4-run-the-application)

---

## Requirements

- **Python 3.8+** (tested on 3.13).
- **Tkinter** — part of the Python standard library on Windows and
  macOS. On Debian/Ubuntu install the system package:

  ```bash
  sudo apt install python3-tk


# Quick Start

## 1. Clone / unzip the project, then from the project root:
python -m venv .venv

## 2. Activate the virtual environment
###    Linux / macOS:
source .venv/bin/activate
###    Windows (PowerShell):
.venv\Scripts\Activate.ps1
##    Windows (cmd):
.venv\Scripts\activate.bat

## 3. Install dependencies (pytest + pyinstaller)
pip install --upgrade pip
pip install -r requirements.txt

## 4. Run the application
python main.py

