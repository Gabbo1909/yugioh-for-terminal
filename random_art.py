#!/usr/bin/env python3
import os
import random
import sys

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
ART_DIR = os.path.join(BASE_DIR, "ascii")

files = [f for f in os.listdir(ART_DIR) if os.path.isfile(os.path.join(ART_DIR, f))]
if not files:
    print("Nessun file trovato.")
    sys.exit(1)

chosen = random.choice(files)

with open(os.path.join(ART_DIR, chosen), "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

# 🔥 Qui convertiamo le “␛” nel vero codice ESC
s = s.replace("␛", "\x1b")
s = s.replace("\\e", "\x1b")     # se per caso contiene "\e"
s = s.replace("\\ESC", "\x1b")   # se contiene "\ESC"

print(s, end="")
