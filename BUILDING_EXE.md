# 🔨 Building Standalone EXE

## **Create a Windows Executable (.exe) File**

This guide shows how to build a standalone Windows .exe file for Soft Repeater Box that doesn't require Python installation.

---

## 🎯 **Why Build an EXE?**

```
✅ Share with non-technical users
✅ No Python installation needed
✅ Double-click to run
✅ Professional distribution
✅ Easier deployment
```

---

## 📋 **Requirements**

**Software:**
- Python 3.8+ installed
- PyInstaller package
- Soft Repeater Box source code

**Disk Space:**
- ~300MB for build process
- Final .exe will be ~50-80MB

---

## 🚀 **Method 1: PyInstaller** (Recommended)

### **Step 1: Install PyInstaller**

```bash
pip install pyinstaller
```

### **Step 2: Navigate to Project Folder**

```bash
cd soft-repeater-box
```

### **Step 3: Build EXE**

**Basic Build:**
```bash
pyinstaller --onefile --windowed soft_repeater_box.py
```

**Better Build (With Icon):**
```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="Soft Repeater Box" soft_repeater_box.py
```

**Recommended Build (All Options):**
```bash
pyinstaller ^
  --onefile ^
  --windowed ^
  --name="Soft_Repeater_Box_v1.01" ^
  --icon=icon.ico ^
  --add-data="README.md;." ^
  soft_repeater_box.py
```

### **Step 4: Find Your EXE**

EXE will be in: `dist\Soft_Repeater_Box_v1.01.exe`

### **Step 5: Test**

1. Copy .exe to different location
2. Double-click to run
3. Should open without Python!

---

## 🎨 **Adding an Icon**

### **Create/Get Icon:**

**Option A: Create Simple Icon:**
1. Create 256x256 PNG image
2. Use online converter: https://converticon.com/
3. Convert PNG → ICO
4. Save as `icon.ico` in project folder

**Option B: Use Existing:**
- Find free radio icon online
- Save as `icon.ico`

**Use in Build:**
```bash
pyinstaller --onefile --windowed --icon=icon.ico soft_repeater_box.py
```

---

## ⚙️ **PyInstaller Options Explained**

```
--onefile
  → Creates single .exe file (not folder with DLLs)
  → Easier to distribute
  
--windowed
  → No console window (GUI only)
  → Remove this if you want console for debugging
  
--icon=icon.ico
  → Custom icon for .exe
  → Optional but professional
  
--name="Soft Repeater Box"
  → Name of output .exe
  → Default is script name
  
--add-data="file;."
  → Include extra files
  → Format: "source;destination"
  
--hidden-import=module
  → Force include module
  → Use if imports not detected
```

---

## 🐛 **Troubleshooting Build**

### **Error: "failed to execute script"**

**Cause:** Missing dependencies

**Solution:**
```bash
# Include hidden imports
pyinstaller --onefile --windowed ^
  --hidden-import=pyttsx3.drivers ^
  --hidden-import=pyttsx3.drivers.sapi5 ^
  soft_repeater_box.py
```

### **Error: "pyaudio not found"**

**Solution:**
```bash
# Reinstall pyaudio
pip uninstall pyaudio
pip install pyaudio

# Then rebuild
pyinstaller --onefile --windowed soft_repeater_box.py
```

### **EXE is Too Large (>100MB)**

**Normal!** PyInstaller includes Python + all libraries.

**To reduce size:**
```bash
# Use UPX compression
pip install pyinstaller[upx]

pyinstaller --onefile --windowed --upx-dir=C:\upx soft_repeater_box.py
```

**Download UPX:** https://upx.github.io/

### **Console Window Still Shows**

**Make sure you used:**
```bash
--windowed
```

**Or use:**
```bash
--noconsole
```

---

## 📦 **Advanced: Spec File Method**

For more control, create a .spec file:

### **Step 1: Generate Spec File**

```bash
pyi-makespec --onefile --windowed soft_repeater_box.py
```

### **Step 2: Edit soft_repeater_box.spec**

```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['soft_repeater_box.py'],
    pathex=[],
    binaries=[],
    datas=[('README.md', '.')],  # Add extra files here
    hiddenimports=[
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Soft_Repeater_Box_v1.01',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Custom icon
)
```

### **Step 3: Build from Spec**

```bash
pyinstaller soft_repeater_box.spec
```

---

## 📤 **Distribution**

### **What to Include:**

**Minimum:**
- `Soft_Repeater_Box_v1.01.exe`
- `README.txt` (basic instructions)

**Recommended:**
- `Soft_Repeater_Box_v1.01.exe`
- `README.txt`
- `WIRING.md` (as PDF or TXT)
- `SETUP.txt` (quick start guide)

### **Create ZIP Package:**

```
Soft_Repeater_Box_v1.01.zip
├── Soft_Repeater_Box_v1.01.exe
├── README.txt
├── SETUP_GUIDE.txt
└── WIRING_DIAGRAM.pdf
```

### **README.txt Example:**

```
Soft Repeater Box v1.01
by NHscan

QUICK START:
1. Double-click Soft_Repeater_Box_v1.01.exe
2. Configure audio devices
3. Set your callsign
4. Click Start!

DOCUMENTATION:
https://github.com/nhscan/soft-repeater-box/wiki

SUPPORT:
Email: host@nhscan.com
GitHub: https://github.com/nhscan/soft-repeater-box/issues

DONATE:
CashApp: $NHlife

LICENSE: MIT
```

---

## 🔒 **Code Signing** (Optional)

For professional distribution, sign your .exe:

### **Why Sign?**
- Windows won't show warnings
- Users trust it more
- Professional appearance

### **How to Sign:**

**Get Certificate:**
- Purchase from: Sectigo, DigiCert, etc.
- Cost: ~$100-300/year

**Sign EXE:**
```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com Soft_Repeater_Box_v1.01.exe
```

**For hobbyist projects:** Not required, but nice to have!

---

## 📊 **Build Comparison**

```
┌─────────────────┬──────────┬─────────┬─────────────┐
│ Method          │ Size     │ Time    │ Difficulty  │
├─────────────────┼──────────┼─────────┼─────────────┤
│ Basic PyInstall │ 60-80MB  │ 2 min   │ Easy ⭐      │
│ With Icon       │ 60-80MB  │ 3 min   │ Easy ⭐      │
│ UPX Compressed  │ 30-40MB  │ 5 min   │ Medium ⭐⭐   │
│ Spec File       │ 60-80MB  │ 10 min  │ Medium ⭐⭐   │
│ Code Signed     │ 60-80MB  │ 15 min  │ Hard ⭐⭐⭐    │
└─────────────────┴──────────┴─────────┴─────────────┘
```

---

## 🎯 **Recommended Build Command**

**For Distribution:**
```bash
pyinstaller ^
  --onefile ^
  --windowed ^
  --name="Soft_Repeater_Box_v1.01" ^
  --icon=icon.ico ^
  --add-data="README.md;." ^
  --hidden-import=pyttsx3.drivers ^
  --hidden-import=pyttsx3.drivers.sapi5 ^
  soft_repeater_box.py
```

**Output:** `dist\Soft_Repeater_Box_v1.01.exe`

**Size:** ~60-80MB

**Time:** 2-3 minutes

---

## ✅ **Testing Checklist**

Before distributing:

- [ ] EXE runs on build computer
- [ ] EXE runs on different computer (without Python)
- [ ] GUI opens properly
- [ ] Audio devices detected
- [ ] PTT relay detection works
- [ ] DTMF commands work
- [ ] Weather integration works
- [ ] Configuration saves/loads
- [ ] No console window appears
- [ ] Icon shows correctly

---

## 💾 **Automated Build Script**

Save as `build.bat`:

```batch
@echo off
echo Building Soft Repeater Box EXE...
echo.

REM Clean old builds
if exist dist rd /s /q dist
if exist build rd /s /q build

REM Build EXE
pyinstaller ^
  --onefile ^
  --windowed ^
  --name="Soft_Repeater_Box_v1.01" ^
  --icon=icon.ico ^
  --add-data="README.md;." ^
  --hidden-import=pyttsx3.drivers ^
  --hidden-import=pyttsx3.drivers.sapi5 ^
  soft_repeater_box.py

REM Check if successful
if exist "dist\Soft_Repeater_Box_v1.01.exe" (
    echo.
    echo ✅ BUILD SUCCESSFUL!
    echo.
    echo EXE Location: dist\Soft_Repeater_Box_v1.01.exe
    echo.
) else (
    echo.
    echo ❌ BUILD FAILED!
    echo.
)

pause
```

**Usage:** Double-click `build.bat`

---

## 🌟 **Alternative: cx_Freeze**

If PyInstaller has issues:

### **Install:**
```bash
pip install cx_Freeze
```

### **Create setup.py:**
```python
from cx_Freeze import setup, Executable

setup(
    name="Soft Repeater Box",
    version="1.01",
    description="Ham/GMRS Repeater Controller",
    executables=[Executable("soft_repeater_box.py", base="Win32GUI", icon="icon.ico")]
)
```

### **Build:**
```bash
python setup.py build
```

---

## 📞 **Need Help?**

**Build errors?**
- Check PyInstaller docs: https://pyinstaller.org/
- Email: host@nhscan.com

**Missing dependencies?**
- Add to `--hidden-import`
- Or use spec file method

---

## 🎉 **Success!**

Once built:
```
✅ Share with anyone
✅ No Python needed
✅ Professional distribution
✅ Easy deployment
```

**Your users can now double-click and go!**

---

**73!** 🔨📻

---

**Guide Version:** 1.0  
**Last Updated:** February 2026  
**For:** Soft Repeater Box v1.01  
**Platform:** Windows
