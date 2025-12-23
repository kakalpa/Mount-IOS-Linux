# iOS Mount GUI

A modern, feature-rich GUI application for mounting iOS devices (iPhones, iPads) on Linux. Built with Electron frontend and Python Flask backend.

## 🎨 Architecture

- **Frontend**: Electron + Modern responsive UI
- **Backend**: Python Flask REST API  
- **Communication**: HTTP/JSON over localhost:5000
- **Distribution**: AppImage (standalone, no dependencies needed)

## ✨ Features

✨ **Core Features:**
- 🔌 One-click device mounting
- 📱 Device pairing validation and management
- 📁 Direct file browser integration
- 🔍 Device information display (model, iOS version, storage, UDID)
- 📋 Comprehensive operation logging with history
- 🔐 Automatic device ejection on exit
- 🚀 Support for custom iDevice commands
- 💾 Full operation history with timestamps

## 📋 Requirements

### System Dependencies

**For Arch Linux:**
```bash
sudo pacman -Syu
sudo pacman -S libimobiledevice ifuse usbmuxd
sudo systemctl enable --now usbmuxd.service
```

**For Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install libimobiledevice-utils libimobiledevice-dev ifuse libfuse-dev usbmuxd
sudo systemctl enable --now usbmuxd.service
```

**For Fedora/RHEL:**
```bash
sudo dnf install libimobiledevice ifuse fuse-devel usbmuxd
sudo systemctl enable --now usbmuxd.service
```

### Development Dependencies

- **Python**: 3.8+
- **Node.js**: 14+ with npm
- **pip/uv**: Python package manager

## 🚀 Installation & Running

### Quick Start (Development)

```bash
# Clone/download the project
cd ios_mount_gui

# Install Python backend
uv sync

# Install Node frontend
cd frontend
npm install

# Run development mode (starts both server and Electron)
npm run dev
```

### Production Mode

```bash
cd frontend
npm start
```

## 📦 Building AppImage

```bash
cd frontend
npm run build
```

The AppImage will be created with all dependencies bundled.

## 🎯 Usage

### Main Tab
- **Mount Point**: Choose where to mount (default: ~/iPhone)
- **One-Click Mount**: Validate, pair, and mount in one action
- **Quick Actions**: Individual controls for each operation
- **Output**: Real-time command output and feedback

### Device Info Tab
- View connected device details
- See iOS version, model, storage info
- Get device UDID

### Advanced Tab  
- Run custom iDevice commands
- Power-user features for advanced operations

### Logs Tab
- View complete operation history
- Clear logs when needed
- Timestamps for all operations

## 🔧 API Endpoints

The Python backend provides these REST endpoints:

```
POST   /api/check-device      - Validate pairing
POST   /api/pair-device       - Establish pairing
POST   /api/mount             - Mount device
POST   /api/unmount           - Unmount device
POST   /api/one-click-mount   - Combined operation
GET    /api/device-info       - Get device details
POST   /api/open-folder       - Open in file manager
POST   /api/is-mounted        - Check mount status
GET    /api/logs              - Get operation history
DELETE /api/logs              - Clear logs
GET    /api/health            - Health check
```

## 📁 Project Structure

```
ios_mount_gui/
├── backend/
│   └── server.py              # Flask REST API
├── frontend/
│   ├── main.js               # Electron main process
│   ├── preload.js            # Security layer
│   ├── package.json          # Node dependencies
│   ├── renderer/
│   │   ├── index.html        # Main UI
│   │   ├── styles.css        # Styling
│   │   └── app.js            # Frontend logic
│   └── build/                # Built files
├── pyproject.toml            # Python dependencies
├── README.md                 # This file
└── ELECTRON_SETUP.md         # Development guide
```

## 🌐 Communication Flow

```
┌─────────────────────────────────────┐
│    Electron User Interface          │
│   (HTML/CSS/JavaScript)             │
└──────────────┬──────────────────────┘
               │ HTTP Requests (JSON)
               ↓
┌─────────────────────────────────────┐
│    Python Flask REST API            │
│    (localhost:5000)                 │
└──────────────┬──────────────────────┘
               │ System Calls
               ↓
┌─────────────────────────────────────┐
│    System Tools                     │
│  - idevicepair, ifuse, usbmuxd      │
└──────────────┬──────────────────────┘
               │
               ↓
          iOS Device
```

## 🆘 Troubleshooting

### "Device not found" or "Could not connect"
- Unlock your iPhone
- Tap "Trust" when prompted
- Ensure usbmuxd is running: `sudo systemctl status usbmuxd`
- Try: `idevicepair validate`

### "Mount failed" error
- Check mount point exists and is writable
- Ensure no other app is using the mount point
- Try a different mount location
- Reinstall libimobiledevice: `sudo pacman -S --needed libimobiledevice`

### Only Photos Folder Visible
This is normal on non-jailbroken devices. iOS restricts access to:
- App sandboxed data
- System files
- User credentials

Accessible locations:
- `DCIM/` - Camera roll photos/videos
- `Books/` - eBooks (if available)
- `Downloads/` - App shared downloads

### Python server won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Install Flask if missing
uv sync
```

### Permission Denied Errors
```bash
# Add yourself to fuse group
sudo usermod -a -G fuse $USER

# Logout and login again for changes to take effect
```

## 🎯 Development

### Hot Reload
- Changes to UI files require manual page reload (Ctrl+R)
- Changes to Python require server restart

### Debug Mode
- Press F12 to open dev tools
- Check Console for JavaScript errors
- Check server terminal for Python errors

### Adding Features
1. **Frontend**: Modify `frontend/renderer/app.js` and `styles.css`
2. **Backend**: Add endpoints to `backend/server.py`
3. **Test**: Use `npm run dev` to test changes

## 📝 Configuration

Logs are stored at:
```
~/.ios_mount_gui/operation_log.json
```

Mount status is tracked at:
```
~/.ios_mount_gui/mount_status.json
```

## 🚀 Distribution

### Sharing the AppImage
The built AppImage works on any Linux with glibc 2.29+:
```bash
# Share the file
scp ios_mount_gui_linux.AppImage user@othercomputer:/tmp/

# Other user can run directly
chmod +x ios_mount_gui_linux.AppImage
./ios_mount_gui_linux.AppImage
```

### System-wide Installation
```bash
sudo cp ios_mount_gui_linux.AppImage /usr/local/bin/ios-mount-gui
# Now anyone can run: ios-mount-gui
```

## 🐛 Known Limitations

- Full iTunes-style backups not supported
- No access to Messages, Contacts, or Settings
- Requires root/sudo for some operations
- Non-jailbroken devices have limited file access
- Some older iOS versions may have compatibility issues

## 📄 License

Open source - Available for personal and commercial use

## 🙏 Credits

Built using:
- [Electron](https://www.electronjs.org/)
- [Flask](https://flask.palletsprojects.com/)
- [libimobiledevice](https://libimobiledevice.org/)

---

**Ready to mount your iOS device!** 📱✨


## Features

✨ **Core Features:**
- 🔌 One-click mount for easy mounting
- 📱 Device pairing validation and management
- 📁 Direct file browser integration (open mounted device in file manager)
- 🔍 Device information display (model, iOS version, storage, UDID)
- 📋 Comprehensive operation logging and history
- 🔐 Automatic device ejection on app close
- 🚀 Support for custom iDevice commands
- 💾 Operation history with timestamp

## Prerequisites

### Install Required System Packages

**For Arch Linux:**
```bash
sudo pacman -Syu
sudo pacman -S libimobiledevice ifuse usbmuxd
sudo systemctl enable --now usbmuxd.service
```

**For Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install libimobiledevice-utils libimobiledevice-dev ifuse libfuse-dev usbmuxd
sudo systemctl enable --now usbmuxd.service
```

**For Fedora/RHEL:**
```bash
sudo dnf install libimobiledevice ifuse fuse-devel usbmuxd
sudo systemctl enable --now usbmuxd.service
```

## Installation

### Option 1: Direct Installation (Recommended for Development)

1. Clone or download this project
2. Navigate to the project directory
3. Install dependencies: `uv sync`
4. Run: `uv run main.py` or `python main.py`

### Option 2: AppImage (Standalone Bundle - No System Dependencies)

AppImage bundles all required libraries and tools, so you don't need to install them separately on your system.

#### Building the AppImage:

1. Install `appimagetool` (if not already installed):
```bash
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
```

2. Build the bundled version:
```bash
python3 bundle_dependencies.py
bash build_appimage.sh
```

3. Run the AppImage:
```bash
./iOS-Mount-GUI-x86_64.AppImage
```

## Usage

### Main Tab
- **Mount Point**: Choose where to mount your device (default: ~/iPhone)
- **Quick Actions**: 
  - **One-Click Mount**: Automatically validates, pairs, and mounts your device
  - **Check Device**: Verify if your device is paired
  - **Pair Device**: Establish pairing with your iOS device
  - **Mount**: Mount the device to the specified location
  - **Unmount**: Safely unmount the device
  - **Eject Device**: Unmount and safely eject
  - **Open Folder**: Open the mounted device in your file manager

### Device Info Tab
- **Refresh Device Info**: Get complete device information including:
  - Device name
  - Device class (iPhone, iPad, etc.)
  - Product type
  - iOS version
  - Total and free storage space
  - UDID (Unique Device Identifier)
- **Get UDID**: Quickly retrieve your device's UDID

### Advanced Tab
- Run custom `idevice*` commands
- Useful for advanced operations or troubleshooting
- Examples:
  - `ideviceinfo` - Get all device info
  - `idevicesyslog` - View device system logs
  - `idevicebackup2` - Backup device

### Logs Tab
- View complete operation history with timestamps
- See success/failure status of each operation
- Clear logs when needed

## Troubleshooting

### "No device found" or "Could not connect"
- Ensure your iPhone is unlocked
- Tap "Trust" when the device asks to trust the computer
- Run "Check Device" button first
- Restart the connection: Unplug and reconnect your device
- Restart usbmuxd service:
```bash
sudo systemctl restart usbmuxd
```

### "Invalid mounting point" or "Mount failed"
- Make sure the mount point directory exists
- Check write permissions: `ls -la ~/iPhone`
- Try using a different mount location
- Ensure no other application is accessing the mount point

### Only Photos Folder Visible
This is normal on non-jailbroken devices. iOS restricts access to app data unless the app explicitly shares it. You can access:
- DCIM/ (Camera roll photos and videos)
- Books/ (eBooks if you use them)
- Downloads/ (Shared download folders from apps)

### "fusermount: command not found"
Install FUSE:
```bash
# Arch Linux
sudo pacman -S fuse

# Debian/Ubuntu
sudo apt-get install fuse libfuse-dev

# Fedora
sudo dnf install fuse fuse-devel
```

### Permission Denied Error
Add your user to the fuse group:
```bash
sudo usermod -a -G fuse $USER
# Then logout and login again
```

### App won't launch from AppImage
Make sure AppImage is executable:
```bash
chmod +x iOS-Mount-GUI-x86_64.AppImage
```

## Limitations

- Only basic file access (photos, documents) available on non-jailbroken devices
- Full iTunes-like backup/restore not supported
- No access to Messages, Contacts, or Settings without specialized tools
- Requires `usbmuxd` service running
- Some operations may require `sudo` (handled by the app)

## File Structure

```
ios_mount_gui/
├── main.py                  # Main application
├── bundle_dependencies.py   # Dependency bundler script
├── build_appimage.sh        # AppImage build script
├── appimage/
│   ├── AppRun              # AppImage entry point
│   └── ios-mount-gui.desktop # Desktop file
└── bundled/                # Generated bundle directory
    ├── libs/               # Bundled libraries
    └── bin/                # Bundled binaries
```

## Development

### Project Layout
- Python 3.8+
- Tkinter for GUI (built-in)
- Uses system `idevice*` utilities and `ifuse`

### Operation Logging
All operations are logged to `~/.ios_mount_gui/operation_log.json` for debugging and auditing purposes.

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.
