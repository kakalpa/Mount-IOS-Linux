# iOS Mount GUI

Browse files from iOS apps on your Linux desktop build using ifuse.


## Usage

### Option 1: AppImage (Easy)

DOwnload the latest `iOS-Mount-GUI-x86_64.AppImage` from Releases:
```bash
chmod +x iOS-Mount-GUI-x86_64.AppImage
./iOS-Mount-GUI-x86_64.AppImage
```

### Option 2: Python DIY (Advanced)

## Installation

```bash
# Arch
sudo pacman -S libimobiledevice-tools fuse3

# Ubuntu/Debian
sudo apt-get install libimobiledevice-utils libfuse-dev fuse3
```

```bash
cd ios_mount_gui
python3 main.py
```

## Quick Steps

1. Connect iPhone via USB → tap "Trust"
2. Click **Apps** tab
3. Click **Refresh Apps** 
4. Select an app (VLC, Dropbox, etc.)
5. Click **Mount App** then **Browse Files**

## Features

✅ Mount iOS device  
✅ Browse 100+ apps (VLC, Dropbox, Chrome, OneDrive, etc.)  
✅ Copy files to computer  
✅ View device info  
✅ Modern dark theme GUI  

## Important

⚠️ Keep iPhone plugged in and unlocked while browsing  
✅ Browsing and copying is safe  
✅ Read-only mode available  
