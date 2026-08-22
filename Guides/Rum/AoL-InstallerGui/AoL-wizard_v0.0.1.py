#!/usr/bin/env python3
"""
AoL-InstallerGui (Affinity on Linux Installer)
Skeleton GUI Application
Author: Alexander Sierputowski (GameDirection LLC)
"""

import os
import sys
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QProgressBar,
    QFileDialog, QListWidget, QListWidgetItem,
    QMessageBox, QCheckBox
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# --- Config / Paths ---
USER_HOME = str(Path.home())
DOWNLOADS = Path(USER_HOME) / "Downloads"
REPO_PATH = Path(USER_HOME) / "Downloads/AffinityOnLinux"
PREFIX_PATH = Path(USER_HOME) / ".local/share/wine/prefixes/affinity"
RUNNER_PATH = Path(USER_HOME) / ".local/share/wine/runners"

INSTALLERS = {
    "Affinity Photo":  "affinity-photo",
    "Affinity Designer": "affinity-designer",
    "Affinity Publisher": "affinity-publisher"
}

# --- Helper Functions ---
def check_dependencies():
    """Check for required system dependencies."""
    deps = ["wget", "unzip", "git", "winetricks"]
    missing = []
    for dep in deps:
        if subprocess.call(["which", dep], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
            missing.append(dep)
    return missing

def find_installers():
    """Scan ~/Downloads for Affinity installers."""
    found = {}
    for app_name, pattern in INSTALLERS.items():
        for f in DOWNLOADS.glob(f"{pattern}*.exe"):
            found[app_name] = str(f)
    return found

def run_command(command, cwd=None):
    """Run shell command and return output."""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode("utf-8")
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.decode('utf-8')}"

# --- GUI Classes ---
class InstallerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Affinity On Linux Installer")
        self.setGeometry(200, 200, 600, 400)
        self.setWindowIcon(QIcon(str(REPO_PATH / "Assets/NewLogos/AffinityOnLinux.png")))

        # Layouts
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Title
        self.title = QLabel("🖼️ Affinity On Linux Installer")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)

        # Step Buttons
        self.btn_check_deps = QPushButton("1. Check Dependencies")
        self.btn_check_deps.clicked.connect(self.on_check_deps)
        self.layout.addWidget(self.btn_check_deps)

        self.btn_setup_wine = QPushButton("2. Setup Wine + Rum")
        self.btn_setup_wine.clicked.connect(self.on_setup_wine)
        self.layout.addWidget(self.btn_setup_wine)

        self.btn_choose_apps = QPushButton("3. Choose Installers")
        self.btn_choose_apps.clicked.connect(self.on_choose_apps)
        self.layout.addWidget(self.btn_choose_apps)

        self.btn_configure = QPushButton("4. Configure Wine Prefix")
        self.btn_configure.clicked.connect(self.on_configure_prefix)
        self.layout.addWidget(self.btn_configure)

        self.btn_install = QPushButton("5. Run Affinity Installers")
        self.btn_install.clicked.connect(self.on_run_installers)
        self.layout.addWidget(self.btn_install)

        self.btn_shortcuts = QPushButton("6. Create Desktop Shortcuts")
        self.btn_shortcuts.clicked.connect(self.on_create_shortcuts)
        self.layout.addWidget(self.btn_shortcuts)

        self.btn_done = QPushButton("✅ Finish")
        self.btn_done.clicked.connect(self.close)
        self.layout.addWidget(self.btn_done)

        # Progress Bar
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        # State
        self.selected_installers = {}

    # --- Callbacks ---
    def on_check_deps(self):
        missing = check_dependencies()
        if not missing:
            QMessageBox.information(self, "Dependencies", "All dependencies are installed ✓")
        else:
            QMessageBox.warning(
                self, "Missing Dependencies",
                f"The following are missing:\n{', '.join(missing)}\n\n"
                "Please install them manually."
            )

    def on_setup_wine(self):
        msg = run_command("mkdir -p ~/.local/share/wine/{runners,prefixes}")
        QMessageBox.information(self, "Wine & Rum Setup", f"Wine/Rum directories created.\n\n{msg[:200]}...")

    def on_choose_apps(self):
        found = find_installers()
        self.selected_installers = {}

        if not found:
            QMessageBox.warning(
                self, "No Installers Found",
                "No installers detected in ~/Downloads.\n"
                "You can download them here:\n\nhttps://store.serif.com/en-us/account/downloads/"
            )
        else:
            msg = "Found installers:\n"
            for app, path in found.items():
                msg += f" - {app}: {path}\n"
                self.selected_installers[app] = path
            QMessageBox.information(self, "Installers", msg)

    def on_configure_prefix(self):
        msg = run_command("wineboot --init", cwd=str(PREFIX_PATH))
        QMessageBox.information(self, "Wine Prefix", f"Wine prefix initialized.\n\n{msg[:200]}...")

    def on_run_installers(self):
        if not self.selected_installers:
            QMessageBox.warning(self, "No Apps Selected", "Please choose installers first!")
            return
        for app, installer in self.selected_installers.items():
            msg = run_command(f"wine \"{installer}\"")
            QMessageBox.information(self, f"{app} Install", f"Installer launched.\n\n{msg[:200]}...")

    def on_create_shortcuts(self):
        for app in self.selected_installers.keys():
            desktop_file = Path(USER_HOME) / f".local/share/applications/affinity-{app.lower().split()[1]}.desktop"
            content = f"""[Desktop Entry]
Name={app}
Exec=wine "{PREFIX_PATH}/drive_c/Program Files/Affinity/{app.split()[1]}/*.exe"
Type=Application
StartupNotify=true
Icon={REPO_PATH}/Assets/Icons/{app.split()[1]}.svg
Categories=Graphics;
"""
            desktop_file.write_text(content)
            desktop_file.chmod(0o755)
        QMessageBox.information(self, "Shortcuts", "Desktop entries created ✓")

# --- Main ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = InstallerWindow()
    win.show()
    sys.exit(app.exec())
