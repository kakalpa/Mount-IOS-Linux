# Release Instructions

## For Developers (GitHub/GitLab)

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd ios_mount
   ```

2. **Install dependencies:**
   ```bash
   # Using UV
   pip install uv
   uv sync
   
   # Or with pip
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   cd ios_mount_gui
   python3 main.py
   ```

## For End Users (Using AppImage)

1. **Download** `iOS-Mount-GUI-x86_64.AppImage` from Releases

2. **Make it executable:**
   ```bash
   chmod +x iOS-Mount-GUI-x86_64.AppImage
   ```

3. **Run it:**
   ```bash
   ./iOS-Mount-GUI-x86_64.AppImage
   ```

That's it! No installation needed. Works on any Linux distribution.

## Uploading AppImage to GitHub Releases

1. Go to your GitHub repository
2. Click **Releases** → **Create a new release**
3. Tag: `v1.0.0` (or your version)
4. Title: `iOS Mount GUI v1.0.0`
5. Upload the file: `iOS-Mount-GUI-x86_64.AppImage`
6. Add description and publish

## Git Workflow

```bash
# Make changes
git add .
git commit -m "Your message"
git push origin main

# Create a tag for release
git tag v1.0.0
git push origin v1.0.0
```
