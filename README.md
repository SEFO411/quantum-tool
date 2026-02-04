# Quantum Tool
A multi-purpose Windows tool written in Python.

## New PyQt6 Desktop UI
This project now ships with a PyQt6-based desktop interface that bundles common utility features in one place.

### Features
- System snapshot (OS, Python, CPU, local time)
- File hash generator (MD5, SHA-1, SHA-256, SHA-512)
- Password generator with clipboard copy
- Notes panel with local persistence
- Clipboard helper for quick copy/paste

### Requirements
- Python 3.10+
- PyQt6 (install via `pip install -r requirements.txt`)

### Run
```bash
python main.py
```

### Notes storage
Notes are saved to `~/.quantum_tool_notes.txt` on your machine.
