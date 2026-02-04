import hashlib
import os
import platform
import sys
from datetime import datetime
from pathlib import Path
from secrets import choice
from string import ascii_letters, digits, punctuation

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

APP_NAME = "Quantum Tool"
NOTES_PATH = Path.home() / ".quantum_tool_notes.txt"


class QuantumTool(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(840, 620)
        self._build_ui()
        self._load_notes()

    def _build_ui(self) -> None:
        self._create_menu()

        tabs = QTabWidget()
        tabs.addTab(self._build_system_tab(), "System")
        tabs.addTab(self._build_file_tab(), "File Tools")
        tabs.addTab(self._build_password_tab(), "Passwords")
        tabs.addTab(self._build_notes_tab(), "Notes")
        tabs.addTab(self._build_clipboard_tab(), "Clipboard")

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(tabs)
        self.setCentralWidget(container)

    def _create_menu(self) -> None:
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        save_action = QAction("Save Notes", self)
        save_action.triggered.connect(self._save_notes)
        file_menu.addAction(save_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _build_system_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("System Snapshot")
        group_layout = QFormLayout(group)

        self.os_label = QLabel()
        self.python_label = QLabel()
        self.cpu_label = QLabel()
        self.time_label = QLabel()

        group_layout.addRow("OS:", self.os_label)
        group_layout.addRow("Python:", self.python_label)
        group_layout.addRow("CPU:", self.cpu_label)
        group_layout.addRow("Local Time:", self.time_label)

        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._refresh_system_info)

        layout.addWidget(group)
        layout.addWidget(refresh_button, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)

        self._refresh_system_info()
        return widget

    def _refresh_system_info(self) -> None:
        self.os_label.setText(f"{platform.system()} {platform.release()}")
        self.python_label.setText(platform.python_version())
        self.cpu_label.setText(platform.processor() or "Unknown")
        self.time_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def _build_file_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        group = QGroupBox("File Hash Generator")
        group_layout = QGridLayout(group)

        self.file_path_edit = QLineEdit()
        self.file_path_edit.setPlaceholderText("Select a file to hash")
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._select_file)

        self.hash_output = QTextEdit()
        self.hash_output.setReadOnly(True)

        hash_button = QPushButton("Generate Hashes")
        hash_button.clicked.connect(self._generate_hashes)

        group_layout.addWidget(QLabel("File:"), 0, 0)
        group_layout.addWidget(self.file_path_edit, 0, 1)
        group_layout.addWidget(browse_button, 0, 2)
        group_layout.addWidget(hash_button, 1, 0, 1, 3)
        group_layout.addWidget(self.hash_output, 2, 0, 1, 3)

        layout.addWidget(group)
        layout.addStretch(1)
        return widget

    def _select_file(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if path:
            self.file_path_edit.setText(path)

    def _generate_hashes(self) -> None:
        path = self.file_path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "Missing File", "Please choose a file first.")
            return
        if not os.path.exists(path):
            QMessageBox.warning(self, "File Not Found", "The file path does not exist.")
            return

        hashes = self._calculate_hashes(Path(path))
        display = "\n".join(f"{name}: {value}" for name, value in hashes.items())
        self.hash_output.setPlainText(display)

    def _calculate_hashes(self, path: Path) -> dict[str, str]:
        results = {}
        for algo in ("md5", "sha1", "sha256", "sha512"):
            hasher = hashlib.new(algo)
            with path.open("rb") as handle:
                for chunk in iter(lambda: handle.read(8192), b""):
                    hasher.update(chunk)
            results[algo.upper()] = hasher.hexdigest()
        return results

    def _build_password_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        options_group = QGroupBox("Generator Settings")
        options_layout = QFormLayout(options_group)

        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 64)
        self.length_spin.setValue(16)

        self.include_symbols = QLineEdit()
        self.include_symbols.setText("!@#$%^&*()_+-=[]{}|;:,.<>?")

        options_layout.addRow("Length:", self.length_spin)
        options_layout.addRow("Symbols:", self.include_symbols)

        self.password_output = QLineEdit()
        self.password_output.setReadOnly(True)

        generate_button = QPushButton("Generate Password")
        generate_button.clicked.connect(self._generate_password)

        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self._copy_password)

        button_row = QHBoxLayout()
        button_row.addWidget(generate_button)
        button_row.addWidget(copy_button)

        layout.addWidget(options_group)
        layout.addWidget(QLabel("Generated Password:"))
        layout.addWidget(self.password_output)
        layout.addLayout(button_row)
        layout.addStretch(1)
        return widget

    def _generate_password(self) -> None:
        length = self.length_spin.value()
        symbol_set = self.include_symbols.text().strip() or punctuation
        alphabet = ascii_letters + digits + symbol_set
        password = "".join(choice(alphabet) for _ in range(length))
        self.password_output.setText(password)

    def _copy_password(self) -> None:
        password = self.password_output.text()
        if not password:
            QMessageBox.information(self, "Nothing to Copy", "Generate a password first.")
            return
        QApplication.clipboard().setText(password)
        QMessageBox.information(self, "Copied", "Password copied to clipboard.")

    def _build_notes_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Write quick notes here. They are saved locally.")

        save_button = QPushButton("Save Notes")
        save_button.clicked.connect(self._save_notes)

        layout.addWidget(self.notes_edit)
        layout.addWidget(save_button, alignment=Qt.AlignmentFlag.AlignRight)
        return widget

    def _build_clipboard_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.clipboard_text = QTextEdit()
        self.clipboard_text.setPlaceholderText("Type text to copy or use refresh to view clipboard.")

        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self._copy_clipboard_text)

        refresh_button = QPushButton("Load Clipboard")
        refresh_button.clicked.connect(self._load_clipboard_text)

        button_row = QHBoxLayout()
        button_row.addWidget(copy_button)
        button_row.addWidget(refresh_button)

        layout.addWidget(self.clipboard_text)
        layout.addLayout(button_row)
        return widget

    def _copy_clipboard_text(self) -> None:
        text = self.clipboard_text.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "Clipboard", "Nothing to copy yet.")
            return
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "Clipboard", "Text copied to clipboard.")

    def _load_clipboard_text(self) -> None:
        text = QApplication.clipboard().text()
        self.clipboard_text.setPlainText(text)

    def _save_notes(self) -> None:
        content = self.notes_edit.toPlainText()
        try:
            NOTES_PATH.write_text(content, encoding="utf-8")
        except OSError as exc:
            QMessageBox.warning(
                self,
                "Save Failed",
                f"Could not save notes: {exc}",
            )
            return
        QMessageBox.information(self, "Saved", "Notes saved locally.")

    def _load_notes(self) -> None:
        if not NOTES_PATH.exists():
            return
        try:
            content = NOTES_PATH.read_text(encoding="utf-8")
        except OSError:
            return
        self.notes_edit.setPlainText(content)


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    window = QuantumTool()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
