#!/bin/bash
# Build script for creating an AppImage

set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"
PARENT_DIR="$(dirname "$PROJECT_ROOT")"

# Create AppImage structure
APPIMAGE_BUILD_DIR="$PROJECT_ROOT/AppImage-build"
APP_DIR="$APPIMAGE_BUILD_DIR/iOS-Mount-GUI.AppDir"

echo "Creating AppImage structure..."
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/lib"
mkdir -p "$APP_DIR/usr/share/ios-mount-gui"
mkdir -p "$APP_DIR/usr/lib/python3/site-packages"

# Copy application files
cp "$PROJECT_ROOT/main.py" "$APP_DIR/usr/share/ios-mount-gui/"
cp "$PROJECT_ROOT/appimage/AppRun" "$APP_DIR/"
cp "$PROJECT_ROOT/appimage/ios-mount-gui.desktop" "$APP_DIR/"
cp "$PROJECT_ROOT/appimage/wrapper.py" "$APP_DIR/usr/share/ios-mount-gui/"
chmod +x "$APP_DIR/AppRun"

# Create icon
python3 << PYSCRIPT
import struct
import zlib
def create_png(filename, width=256, height=256):
    png_signature = b'\x89PNG\r\n\x1a\n'
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'
        for x in range(width):
            if 60 < x < 196 and 30 < y < 226:
                raw_data += bytes([255, 255, 255])
            else:
                raw_data += bytes([30, 144, 255])
    compressed = zlib.compress(raw_data)
    def make_chunk(chunk_type, data):
        chunk_data = chunk_type + data
        crc = zlib.crc32(chunk_data) & 0xffffffff
        return struct.pack('>I', len(data)) + chunk_data + struct.pack('>I', crc)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_chunk = make_chunk(b'IHDR', ihdr_data)
    idat_chunk = make_chunk(b'IDAT', compressed)
    iend_chunk = make_chunk(b'IEND', b'')
    with open(filename, 'wb') as f:
        f.write(png_signature)
        f.write(ihdr_chunk)
        f.write(idat_chunk)
        f.write(iend_chunk)
create_png("$APP_DIR/ios-mount-gui.png")
PYSCRIPT

# Copy bundled libraries and binaries
if [ -d "$PROJECT_ROOT/bundled/libs" ]; then
    echo "Copying bundled libraries..."
    cp -r "$PROJECT_ROOT/bundled/libs"/* "$APP_DIR/usr/lib/" 2>/dev/null || true
fi

if [ -d "$PROJECT_ROOT/bundled/bin" ]; then
    echo "Copying bundled binaries..."
    cp -r "$PROJECT_ROOT/bundled/bin"/* "$APP_DIR/usr/bin/" 2>/dev/null || true
fi

# Make binaries executable
chmod +x "$APP_DIR/usr/bin"/* 2>/dev/null || true

# Copy Python interpreter if available
echo "Setting up Python environment..."
# Don't copy Python binary - use system Python instead
# This avoids hardcoded library path issues

# Copy Python site-packages from venv if available
echo "Bundling Python dependencies..."
VENV_SITE_PACKAGES="$PARENT_DIR/.venv/lib/python*/site-packages"
if ls $VENV_SITE_PACKAGES 1> /dev/null 2>&1; then
    echo "  Found venv site-packages, copying..."
    for site_pkg in $VENV_SITE_PACKAGES; do
        if [ -d "$site_pkg" ]; then
            cp -r "$site_pkg"/* "$APP_DIR/usr/lib/python3/site-packages/" 2>/dev/null || true
            echo "  Copied $(du -sh "$site_pkg" 2>/dev/null | cut -f1) of dependencies"
        fi
    done
else
    echo "  Warning: venv site-packages not found at $VENV_SITE_PACKAGES"
    echo "  Make sure the venv is activated and dependencies are installed"
fi

# Find appimagetool
APPIMAGETOOL=$(which appimagetool || which appimagetool-x86_64.AppImage || echo "/tmp/appimagetool-x86_64.AppImage")

if [ ! -f "$APPIMAGETOOL" ]; then
    echo "appimagetool not found. Attempting to download..."
    APPIMAGETOOL="/tmp/appimagetool-x86_64.AppImage"
    if [ ! -f "$APPIMAGETOOL" ]; then
        echo "Downloading appimagetool..."
        wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O "$APPIMAGETOOL" || {
            echo "Failed to download appimagetool"
            exit 1
        }
    fi
fi

chmod +x "$APPIMAGETOOL"

# Create AppImage
echo "Building AppImage..."
OUTPUT_FILE="$PROJECT_ROOT/iOS-Mount-GUI-x86_64.AppImage"
"$APPIMAGETOOL" "$APP_DIR" "$OUTPUT_FILE" || {
    echo "AppImage build failed"
    exit 1
}

chmod +x "$OUTPUT_FILE"
echo ""
echo "✓ AppImage created successfully!"
echo "  Location: $OUTPUT_FILE"
echo ""
echo "To run the AppImage:"
echo "  $OUTPUT_FILE"
echo ""
echo "Or make it globally available:"
echo "  sudo mv $OUTPUT_FILE /usr/local/bin/"
echo "  # Then run: iOS-Mount-GUI-x86_64.AppImage"
