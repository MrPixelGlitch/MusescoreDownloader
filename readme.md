# 🎼 Musescore Downloader

This tool allows you to download and convert MuseScore scores into high-quality PDFs.  
It is available as both a **command-line interface (CLI)** tool and a **graphical user interface (GUI)** application (Windows `.exe`).

---

## ✨ Features

- 🖼️ Downloads all score pages from MuseScore
- 📄 Converts SVGs to A4-sized PDF pages
- 🧾 Merges all pages into a single PDF
- 🖱️ GUI version with status display and save dialog
- ⚙️ CLI version for terminal or script use

---

## 🔧 Requirements (CLI version)

- Python 3.8+
- Google Chrome installed
- Required Python packages:

### Install dependencies:
```bash
pip install -r requirements.txt
```

## 🖥️ Usage
### CLI Version
```bash
python cli_version/musescoreDownloader.py
```
Then paste the MuseScore URL when prompted.

### 🖱️ GUI Version (Windows .exe)
1. Download MusescoreDownloader.exe from the [Releases](https://github.com/MrPixelGlitch/MusescoreDownloader/releases) page.
2. Run the application.
3. Paste the MuseScore URL into the input field.
4. Click Start Conversion.
5. Once done, click Save Final PDF and choose where to save.

## 🛠️ Build GUI Executable Yourself (Optional)
To build your own .exe from the Python GUI version:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed ^
--add-binary "cairo_dlls/libcairo-2.dll;." ^
--add-binary "cairo_dlls/libpng16-16.dll;." ^
--add-binary "cairo_dlls/zlib1.dll;." ^
--add-binary "cairo_dlls/libfreetype-6.dll;." ^
musescoreDownloaderGUI.py
```
The standalone executable will be in the dist/ folder.

## 📜 License
This project is licensed under the MIT License.