#!/usr/bin/env python3
"""
iOS Mount GUI - Modern PyQt6 Desktop Application
Professional standalone desktop app with modern UI
"""

import sys
import subprocess
import os
import threading
import json
from pathlib import Path
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QCheckBox, QRadioButton,
    QButtonGroup, QTextEdit, QListWidget, QListWidgetItem, QFileDialog,
    QMessageBox, QComboBox, QSpinBox, QProgressBar, QListWidgetItem,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QFont, QColor, QTextCursor, QIcon

# Modern Color Palette
DARK_BG = "#0a0e27"
SECONDARY_BG = "#11152d"
TERTIARY_BG = "#1a1f3a"
PRIMARY_COLOR = "#3b82f6"
PRIMARY_DARK = "#2563eb"
PRIMARY_LIGHT = "#60a5fa"
TEXT_PRIMARY = "#f1f5f9"
TEXT_SECONDARY = "#94a3b8"
BORDER_COLOR = "#2d3748"
SUCCESS_COLOR = "#10b981"
ERROR_COLOR = "#ef4444"
WARNING_COLOR = "#f59e0b"
ACCENT_COLOR = "#8b5cf6"

class CommandWorker(QThread):
    """Worker thread for running shell commands"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
    
    def run(self):
        try:
            result = subprocess.run(
                self.command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout or result.stderr
            self.output_signal.emit(output)
            self.finished_signal.emit(result.returncode == 0, output)
        except subprocess.TimeoutExpired:
            self.output_signal.emit("Command timeout")
            self.finished_signal.emit(False, "Command timeout")
        except Exception as e:
            self.output_signal.emit(f"Error: {str(e)}")
            self.finished_signal.emit(False, str(e))

class IOSMountApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("iOS Mount - Professional Device Browser")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 700)
        
        # Setup logging
        self.app_dir = Path.home() / ".ios_mount_gui"
        self.app_dir.mkdir(exist_ok=True)
        self.log_file = self.app_dir / "operation_log.json"
        
        # State
        self.selected_app = None
        self.current_browser_path = None
        self.app_map = {}
        
        # Setup UI
        self.setup_styles()
        self.setup_ui()
        
        self.log_operation("Application Started", "SUCCESS")
    
    def setup_styles(self):
        """Setup modern application stylesheet"""
        stylesheet = f"""
            QMainWindow {{
                background-color: {DARK_BG};
                color: {TEXT_PRIMARY};
            }}
            QWidget {{
                background-color: {DARK_BG};
                color: {TEXT_PRIMARY};
            }}
            QTabBar {{
                background-color: {DARK_BG};
                border-bottom: 2px solid {BORDER_COLOR};
            }}
            QTabBar::tab {{
                background-color: {SECONDARY_BG};
                color: {TEXT_SECONDARY};
                padding: 12px 28px;
                border: none;
                margin-right: 4px;
                border-radius: 8px 8px 0px 0px;
                font-weight: 500;
            }}
            QTabBar::tab:hover {{
                background-color: {TERTIARY_BG};
            }}
            QTabBar::tab:selected {{
                background-color: {PRIMARY_COLOR};
                color: white;
                font-weight: bold;
            }}
            QTabWidget::pane {{
                border: none;
                background-color: {DARK_BG};
            }}
            QLineEdit, QTextEdit {{
                background-color: {TERTIARY_BG};
                color: {TEXT_PRIMARY};
                border: 2px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 10px 12px;
                selection-background-color: {PRIMARY_COLOR};
                font-size: 11pt;
            }}
            QLineEdit:hover, QTextEdit:hover {{
                border: 2px solid {PRIMARY_LIGHT};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 2px solid {PRIMARY_COLOR};
                background-color: {TERTIARY_BG};
            }}
            QPushButton {{
                background-color: {PRIMARY_COLOR};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 11pt;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: {PRIMARY_DARK};
            }}
            QPushButton:focus {{
                outline: none;
            }}
            QPushButton#successBtn {{
                background-color: {SUCCESS_COLOR};
            }}
            QPushButton#successBtn:hover {{
                background-color: #059669;
            }}
            QPushButton#dangerBtn {{
                background-color: {ERROR_COLOR};
            }}
            QPushButton#dangerBtn:hover {{
                background-color: #dc2626;
            }}
            QLabel {{
                color: {TEXT_PRIMARY};
                font-size: 11pt;
            }}
            QLabel#secondary {{
                color: {TEXT_SECONDARY};
                font-size: 10pt;
            }}
            QLabel#title {{
                color: {PRIMARY_COLOR};
                font-weight: bold;
            }}
            QCheckBox, QRadioButton {{
                color: {TEXT_PRIMARY};
                spacing: 8px;
                padding: 4px;
                font-size: 11pt;
            }}
            QCheckBox:hover, QRadioButton:hover {{
                color: {PRIMARY_LIGHT};
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {TERTIARY_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 4px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {PRIMARY_COLOR};
                border: 2px solid {PRIMARY_COLOR};
                border-radius: 4px;
            }}
            QListWidget {{
                background-color: {TERTIARY_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 8px;
                color: {TEXT_PRIMARY};
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-radius: 6px;
                margin-bottom: 4px;
            }}
            QListWidget::item:hover {{
                background-color: {SECONDARY_BG};
            }}
            QListWidget::item:selected {{
                background-color: {PRIMARY_COLOR};
                color: white;
            }}
            QComboBox {{
                background-color: {TERTIARY_BG};
                color: {TEXT_PRIMARY};
                border: 2px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 8px 12px;
                min-height: 36px;
                font-size: 11pt;
            }}
            QComboBox:hover {{
                border: 2px solid {PRIMARY_LIGHT};
            }}
            QComboBox:focus {{
                border: 2px solid {PRIMARY_COLOR};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {TERTIARY_BG};
                color: {TEXT_PRIMARY};
                selection-background-color: {PRIMARY_COLOR};
                border: 2px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 4px;
            }}
            QSpinBox {{
                background-color: {TERTIARY_BG};
                color: {TEXT_PRIMARY};
                border: 2px solid {BORDER_COLOR};
                border-radius: 8px;
                padding: 6px;
            }}
            QProgressBar {{
                background-color: {SECONDARY_BG};
                border: 2px solid {BORDER_COLOR};
                border-radius: 8px;
                text-align: center;
                height: 24px;
            }}
            QProgressBar::chunk {{
                background-color: {PRIMARY_COLOR};
                border-radius: 6px;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def setup_ui(self):
        """Setup the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        title = QLabel("iOS Mount")
        title_font = QFont("Segoe UI", 28, QFont.Weight.Bold)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {PRIMARY_COLOR};")
        
        subtitle = QLabel("Professional Device Manager & Browser")
        subtitle.setObjectName("secondary")
        subtitle_font = QFont("Segoe UI", 11)
        subtitle.setFont(subtitle_font)
        
        header_layout.addWidget(title)
        header_layout.addSpacing(12)
        header_layout.addWidget(subtitle)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"color: {BORDER_COLOR};")
        layout.addWidget(divider)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"QTabWidget {{ border: none; }}")
        self.tabs.addTab(self.create_main_tab(), "🔧 Mount Control")
        self.tabs.addTab(self.create_device_tab(), "📱 Device Info")
        self.tabs.addTab(self.create_browser_tab(), "📂 File Browser")
        self.tabs.addTab(self.create_apps_tab(), "📦 App Documents")
        self.tabs.addTab(self.create_logs_tab(), "📋 Logs")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        self.status_label = QLabel("✓ Ready")
        self.status_label.setObjectName("secondary")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        layout.addLayout(status_layout)
        
        central_widget.setLayout(layout)
    
    def create_main_tab(self):
        """Create mount control tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Mount point section
        mount_section = QFrame()
        mount_section.setStyleSheet(f"QFrame {{ background-color: {TERTIARY_BG}; border: 2px solid {BORDER_COLOR}; border-radius: 8px; }}")
        mount_layout_outer = QVBoxLayout()
        mount_layout_outer.setContentsMargins(16, 16, 16, 16)
        mount_layout_outer.setSpacing(12)
        
        mount_label = QLabel("Mount Configuration")
        mount_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        mount_layout_outer.addWidget(mount_label)
        
        mount_layout = QHBoxLayout()
        mount_layout.setSpacing(10)
        mount_layout.addWidget(QLabel("Mount Point:"))
        self.mount_point = QLineEdit(os.path.expanduser("~/iPhone"))
        mount_layout.addWidget(self.mount_point)
        browse_btn = QPushButton("📁 Browse")
        browse_btn.setMaximumWidth(100)
        browse_btn.clicked.connect(self.browse_mount_point)
        mount_layout.addWidget(browse_btn)
        mount_layout_outer.addLayout(mount_layout)
        
        # Mount mode
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(12)
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_group = QButtonGroup()
        normal_radio = QRadioButton("Normal (Read/Write)")
        normal_radio.setChecked(True)
        readonly_radio = QRadioButton("Read-Only")
        self.mode_group.addButton(normal_radio, 0)
        self.mode_group.addButton(readonly_radio, 1)
        mode_layout.addWidget(normal_radio)
        mode_layout.addWidget(readonly_radio)
        mode_layout.addStretch()
        mount_layout_outer.addLayout(mode_layout)
        
        mount_section.setLayout(mount_layout_outer)
        layout.addWidget(mount_section)
        
        # Buttons section
        button_section = QFrame()
        button_section.setStyleSheet(f"QFrame {{ background-color: {TERTIARY_BG}; border: 2px solid {BORDER_COLOR}; border-radius: 8px; }}")
        button_layout_outer = QVBoxLayout()
        button_layout_outer.setContentsMargins(16, 16, 16, 16)
        button_layout_outer.setSpacing(12)
        
        button_label = QLabel("Device Control")
        button_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        button_layout_outer.addWidget(button_label)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        buttons = [
            ("✓ Check", self.check_device),
            ("🔐 Pair", self.pair_device),
            ("⬆️ Mount", self.mount_device),
            ("⬇️ Unmount", self.unmount_device),
            ("📂 Open", self.open_folder),
        ]
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            button_layout.addWidget(btn)
        button_layout_outer.addLayout(button_layout)
        
        button_section.setLayout(button_layout_outer)
        layout.addWidget(button_section)
        
        # Output section
        output_label = QLabel("Command Output")
        output_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(output_label)
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Courier", 9))
        self.output_text.setMinimumHeight(200)
        layout.addWidget(self.output_text)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_device_tab(self):
        """Create device info tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        btn_layout = QHBoxLayout()
        btn = QPushButton("🔄 Refresh Device Info")
        btn.setMinimumHeight(40)
        btn.clicked.connect(self.get_device_info)
        btn_layout.addWidget(btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.device_info = QTextEdit()
        self.device_info.setReadOnly(True)
        self.device_info.setFont(QFont("Courier", 10))
        layout.addWidget(self.device_info)
        
        widget.setLayout(layout)
        return widget
    
    def create_browser_tab(self):
        """Create file browser tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Toolbar section
        toolbar_section = QFrame()
        toolbar_section.setStyleSheet(f"QFrame {{ background-color: {TERTIARY_BG}; border: 2px solid {BORDER_COLOR}; border-radius: 8px; }}")
        toolbar_outer = QVBoxLayout()
        toolbar_outer.setContentsMargins(12, 12, 12, 12)
        toolbar_outer.setSpacing(8)
        
        toolbar_label = QLabel("Browser Controls")
        toolbar_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        toolbar_outer.addWidget(toolbar_label)
        
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMaximumWidth(120)
        refresh_btn.clicked.connect(self.browse_path)
        toolbar.addWidget(refresh_btn)
        
        self.show_hidden = QCheckBox("Show Hidden Files")
        self.show_hidden.stateChanged.connect(self.browse_path)
        toolbar.addWidget(self.show_hidden)
        
        toolbar.addWidget(QLabel("Path:"))
        self.browser_path = QLineEdit()
        self.browser_path.setReadOnly(True)
        toolbar.addWidget(self.browser_path)
        toolbar_outer.addLayout(toolbar)
        
        toolbar_section.setLayout(toolbar_outer)
        layout.addWidget(toolbar_section)
        
        # File list
        list_label = QLabel("Files & Folders")
        list_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(list_label)
        
        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.navigate_file)
        layout.addWidget(self.file_list)
        
        widget.setLayout(layout)
        return widget
    
    def create_apps_tab(self):
        """Create apps tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Buttons section
        btn_section = QFrame()
        btn_section.setStyleSheet(f"QFrame {{ background-color: {TERTIARY_BG}; border: 2px solid {BORDER_COLOR}; border-radius: 8px; }}")
        btn_layout_outer = QVBoxLayout()
        btn_layout_outer.setContentsMargins(12, 12, 12, 12)
        btn_layout_outer.setSpacing(8)
        
        btn_label = QLabel("App Management")
        btn_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        btn_layout_outer.addWidget(btn_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        refresh_btn = QPushButton("🔄 Refresh Apps")
        refresh_btn.clicked.connect(self.list_apps)
        btn_layout.addWidget(refresh_btn)
        
        mount_btn = QPushButton("⬆️ Mount App")
        mount_btn.setObjectName("successBtn")
        mount_btn.clicked.connect(self.mount_app)
        btn_layout.addWidget(mount_btn)
        
        browse_btn = QPushButton("📂 Browse Files")
        browse_btn.clicked.connect(self.browse_app_files)
        btn_layout.addWidget(browse_btn)
        
        btn_layout_outer.addLayout(btn_layout)
        btn_section.setLayout(btn_layout_outer)
        layout.addWidget(btn_section)
        
        # Apps list
        list_label = QLabel("Installed Applications")
        list_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(list_label)
        
        self.apps_list = QListWidget()
        self.apps_list.itemClicked.connect(self.select_app_from_list)
        layout.addWidget(self.apps_list)
        
        # Selected app info
        info_section = QFrame()
        info_section.setStyleSheet(f"QFrame {{ background-color: {TERTIARY_BG}; border: 2px solid {BORDER_COLOR}; border-radius: 8px; }}")
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(12, 12, 12, 12)
        
        info_label = QLabel("Selected Application")
        info_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        info_layout.addWidget(info_label)
        
        self.selected_app_label = QLabel("No selection")
        self.selected_app_label.setObjectName("secondary")
        self.selected_app_label.setFont(QFont("Courier", 10))
        info_layout.addWidget(self.selected_app_label)
        
        info_section.setLayout(info_layout)
        layout.addWidget(info_section)
        
        widget.setLayout(layout)
        return widget
    
    def create_logs_tab(self):
        """Create logs tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Buttons section
        btn_section = QFrame()
        btn_section.setStyleSheet(f"QFrame {{ background-color: {TERTIARY_BG}; border: 2px solid {BORDER_COLOR}; border-radius: 8px; }}")
        btn_layout_outer = QVBoxLayout()
        btn_layout_outer.setContentsMargins(12, 12, 12, 12)
        btn_layout_outer.setSpacing(8)
        
        btn_label = QLabel("Log Management")
        btn_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        btn_layout_outer.addWidget(btn_label)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setMaximumWidth(120)
        refresh_btn.clicked.connect(self.show_logs)
        btn_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("🗑️ Clear Logs")
        clear_btn.setObjectName("dangerBtn")
        clear_btn.setMaximumWidth(120)
        clear_btn.clicked.connect(self.clear_logs)
        btn_layout.addWidget(clear_btn)
        
        btn_layout.addStretch()
        btn_layout_outer.addLayout(btn_layout)
        btn_section.setLayout(btn_layout_outer)
        layout.addWidget(btn_section)
        
        # Logs display
        logs_label = QLabel("Operation Logs")
        logs_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(logs_label)
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.logs_text)
        
        widget.setLayout(layout)
        return widget
    
    # === Utility Methods ===
    
    def log_operation(self, operation, status, details=""):
        """Log operation to file"""
        try:
            logs = []
            if self.log_file.exists():
                logs = json.load(open(self.log_file))
            
            logs.append({
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "status": status,
                "details": details
            })
            
            with open(self.log_file, 'w') as f:
                json.dump(logs[-100:], f, indent=2)
        except:
            pass
    
    def append_output(self, text):
        """Append to output with timestamp"""
        self.output_text.insertPlainText(f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
        self.output_text.moveCursor(QTextCursor.MoveOperation.End)
    
    def run_command(self, command, description, callback=None):
        """Run command in thread"""
        self.status_label.setText(f"Running: {description}...")
        
        self.worker = CommandWorker(command)
        self.worker.output_signal.connect(self.append_output)
        self.worker.finished_signal.connect(
            lambda success, output: self.on_command_finished(success, description, output, callback)
        )
        self.worker.start()
    
    def on_command_finished(self, success, description, output, callback=None):
        """Handle command completion"""
        status = "SUCCESS" if success else "FAILED"
        self.status_label.setText(f"{description}: {status}")
        self.log_operation(description, status, output[:200] if output else "")
        
        if callback:
            callback(success, output)
    
    # === Mount Control ===
    
    def browse_mount_point(self):
        """Browse for mount point"""
        path = QFileDialog.getExistingDirectory(self, "Select Mount Point")
        if path:
            self.mount_point.setText(path)
    
    def check_device(self):
        self.run_command("idevicepair validate", "Check Device")
    
    def pair_device(self):
        self.run_command("idevicepair pair", "Pair Device")
    
    def mount_device(self):
        mount_point = self.mount_point.text()
        cmd = f"ifuse {mount_point}"
        if self.mode_group.checkedId() == 1:
            cmd += " -o ro"
        cmd += " -o allow_other"
        self.run_command(cmd, "Mount Device")
    
    def unmount_device(self):
        mount_point = self.mount_point.text()
        self.run_command(f"fusermount -u {mount_point}", "Unmount Device")
    
    def open_folder(self):
        mount_point = self.mount_point.text()
        if os.path.ismount(mount_point):
            subprocess.Popen(f"xdg-open {mount_point}", shell=True, stderr=subprocess.DEVNULL)
    
    # === Device Info ===
    
    def get_device_info(self):
        def callback(success, output):
            if success:
                result = subprocess.run("idevice_id -l", shell=True, capture_output=True, text=True)
                device_id = result.stdout.strip().split('\n')[0] if result.stdout else "Unknown"
                
                info = f"Device UDID: {device_id}\n\n"
                for flag, label in [("DeviceClass", "Class"), ("ProductType", "Type"), ("ProductVersion", "Version")]:
                    result = subprocess.run(f"ideviceinfo -u {device_id} -k {flag}", shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        info += f"{label}: {result.stdout.strip()}\n"
                
                self.device_info.setText(info)
        
        self.run_command("idevice_id -l", "Get Device Info", callback)
    
    # === File Browser ===
    
    def browse_path(self):
        """Browse current path"""
        mount_point = self.mount_point.text()
        self.current_browser_path = mount_point
        self.browser_path.setText(mount_point)
        
        self.file_list.clear()
        
        try:
            items = os.listdir(mount_point)
            if not self.show_hidden.isChecked():
                items = [i for i in items if not i.startswith('.')]
            
            for item in sorted(items):
                full_path = os.path.join(mount_point, item)
                prefix = "[DIR]  " if os.path.isdir(full_path) else "[FILE] "
                self.file_list.addItem(prefix + item)
        except Exception as e:
            self.file_list.addItem(f"Error: {str(e)}")
    
    def navigate_file(self, item):
        """Navigate to file/folder"""
        text = item.text()
        if text.startswith("[DIR]"):
            folder_name = text[7:]
            new_path = os.path.join(self.current_browser_path, folder_name)
            self.mount_point.setText(new_path)
            self.browse_path()
    
    # === Apps ===
    
    def list_apps(self):
        def callback(success, output):
            if success:
                self.apps_list.clear()
                self.app_map = {}
                
                for line in output.split('\n'):
                    if not line.strip():
                        continue
                    
                    bundle_id = None
                    display_name = line.strip()
                    
                    if '(' in line and ')' in line:
                        bundle_id = line.split('(')[1].split(')')[0]
                    elif line.startswith('"') and '","' in line:
                        parts = [p.strip('"').strip() for p in line.split('","')]
                        if len(parts) >= 3:
                            bundle_id = parts[0]
                            app_name = parts[2]
                            display_name = f"{app_name} ({bundle_id})"
                        elif len(parts) >= 1:
                            bundle_id = parts[0]
                    else:
                        bundle_id = line.strip()
                    
                    if bundle_id:
                        self.app_map[display_name] = bundle_id
                        self.apps_list.addItem(display_name)
        
        self.run_command("ifuse --list-apps", "List Apps", callback)
    
    def select_app_from_list(self, item):
        """Select app from list"""
        app_name = item.text()
        bundle_id = self.app_map.get(app_name)
        
        if bundle_id:
            self.selected_app = {"name": app_name, "bundle_id": bundle_id}
            self.selected_app_label.setText(f"{app_name}\n({bundle_id})")
    
    def mount_app(self):
        """Mount selected app"""
        if not self.selected_app:
            QMessageBox.warning(self, "No Selection", "Please select an app first")
            return
        
        bundle_id = self.selected_app["bundle_id"]
        app_name = self.selected_app["name"].split('(')[0].strip()
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in app_name)
        mount_point = os.path.expanduser(f"~/iPhone_Apps/{safe_name}")
        
        os.makedirs(mount_point, exist_ok=True)
        cmd = f"ifuse --documents {bundle_id} \"{mount_point}\""
        
        def callback(success, output):
            if success:
                QMessageBox.information(self, "Success", f"App mounted at:\n{mount_point}")
        
        self.run_command(cmd, "Mount App", callback)
    
    def browse_app_files(self):
        """Browse app files"""
        if not self.selected_app:
            QMessageBox.warning(self, "No Selection", "Please mount an app first")
            return
        
        app_name = self.selected_app["name"].split('(')[0].strip()
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in app_name)
        mount_point = os.path.expanduser(f"~/iPhone_Apps/{safe_name}")
        
        if os.path.exists(mount_point):
            subprocess.Popen(f"xdg-open {mount_point}", shell=True, stderr=subprocess.DEVNULL)
        else:
            QMessageBox.warning(self, "Not Mounted", f"App not mounted yet. Mount the app first.")
    
    # === Logs ===
    
    def show_logs(self):
        """Show logs"""
        try:
            if self.log_file.exists():
                logs = json.load(open(self.log_file))
                text = ""
                for log in logs[-50:]:
                    text += f"[{log['timestamp']}] {log['operation']}: {log['status']}\n"
                    if log['details']:
                        text += f"  {log['details'][:100]}\n"
                self.logs_text.setText(text)
            else:
                self.logs_text.setText("No logs yet")
        except:
            self.logs_text.setText("Error loading logs")
    
    def clear_logs(self):
        """Clear logs"""
        reply = QMessageBox.question(self, "Clear Logs", "Are you sure?")
        if reply == QMessageBox.StandardButton.Yes:
            self.log_file.write_text("[]")
            self.show_logs()

def main():
    app = QApplication(sys.argv)
    
    # Set a style that's guaranteed to be available (Fusion is built-in)
    # This suppresses the "invalid style override 'kvantum'" warning on systems
    # where kvantum isn't available in the AppImage
    try:
        app.setStyle('Fusion')
    except:
        pass  # Fall back to default if Fusion fails
    
    window = IOSMountApp()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
