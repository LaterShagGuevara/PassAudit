#!/usr/bin/env python3
"""Always launch the PassAudit GUI."""
import os
import sys

# Fix import path no matter how it's launched (VS, double-click, etc.)
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from passaudit.gui import start_gui

if __name__ == "__main__":
    start_gui()
