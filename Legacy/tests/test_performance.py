import os
import time

# Medición 1: Verificación simple de archivo
start = time.perf_counter()
winfsp_installed = os.path.exists(r"C:\Program Files (x86)\WinFsp\bin\winfsp-x64.dll")
elapsed = (time.perf_counter() - start) * 1000
print(f"Verificación de WinFsp: {elapsed:.2f}ms")
print(f"WinFsp instalado: {winfsp_installed}")

# Medición 2: Importaciones de PyQt6
start = time.perf_counter()
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
elapsed = (time.perf_counter() - start) * 1000
print(f"Importar PyQt6: {elapsed:.2f}ms")

print(f"\nConclusión: La verificación de WinFsp es {elapsed / 0.05:.0f}x más rápida que cargar PyQt6")
