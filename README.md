# 🎙️ Soft Repeater Box v1.01

**Professional Ham/GMRS Repeater Controller Software**

Transform your computer into a full-featured repeater controller with DTMF commands, weather integration, auto station ID, and more!

[![Version](https://img.shields.io/badge/version-1.01-blue.svg)](https://github.com/nhscan/soft-repeater-box/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Donate](https://img.shields.io/badge/donate-CashApp-brightgreen.svg)](https://cash.app/$NHlife)

---

## ✨ Features

### 🎛️ **Four Operating Modes**
- **Repeater Mode** - Full-duplex pass-through with minimal delay
- **Duplex Mode** - Adjustable delay for delayed repeat
- **Parrot Mode** - Record and auto-replay (testing)
- **Manual Mode** - Manual record/playback control

### 📡 **Core Features**
- ✅ **VOX Detection** - Software-based voice activation
- ✅ **PTT Control** - USB relay or VOX modes
- ✅ **DTMF Commands** - 10 customizable commands (0001-0010)
- ✅ **Weather Integration** - Weather.gov announcements
- ✅ **Auto Station ID** - Morse or voice with callsign
- ✅ **Courtesy Tones** - Customizable frequency/duration
- ✅ **Debug Mode** - Verbose console output
- ✅ **Audio Gain Control** - Live input/output adjustment
- ✅ **Feedback Protection** - Prevents audio loops

### 🎯 **Advanced Features**
- Weather announcements via DTMF
- Custom DTMF messages
- Adjustable ID interval
- Configurable timeout
- PTT pre-delay and tail silence
- Multiple audio device support
- Configuration save/load

---

## 🚀 Quick Start

### **1. Install Python**
Download and install Python 3.8 or higher from [python.org](https://www.python.org/downloads/)

**Windows:** Check ✓ "Add Python to PATH" during installation!

### **2. Download Soft Repeater Box**
```bash
git clone https://github.com/nhscan/soft-repeater-box.git
cd soft-repeater-box
```

**Or download ZIP:** [Latest Release](https://github.com/nhscan/soft-repeater-box/releases)

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**Dependencies:**
- `pyaudio` - Audio I/O
- `numpy` - Audio processing
- `pyserial` - PTT control
- `pyttsx3` - Text-to-speech
- `requests` - Weather API

### **4. Run**
```bash
python soft_repeater_box.py
```

GUI will open and create default config on first run!

---

## 📋 System Requirements

**Software:**
- Python 3.8 or higher
- Windows, Linux, or macOS

**Hardware:**
- Computer with audio interface
- Radio with audio input/output
- (Optional) USB PTT relay module (~$5-10)

**Recommended:**
- USB sound card for better audio quality
- PTT relay for hardware PTT control
- Decent internet for weather features

---

## 🔧 Configuration

### **Audio Setup**
1. Go to **"Audio Devices"** tab
2. Select input device (radio/mic)
3. Select output device (radio/speaker)
4. Adjust gain sliders (start at 50%)

### **Set Your Callsign**
1. Go to **"Repeater Settings"** tab
2. Enter your callsign (e.g., W1ABC)
3. Set ID interval (recommended: 600 seconds / 10 min)
4. Enable Auto Station ID

### **Choose Operating Mode**
1. Go to **"Mode Settings"** tab
2. Select mode (Repeater recommended)
3. Configure mode-specific settings

### **PTT Control**
1. Go to **"VOX/PTT Settings"** tab
2. Choose PTT mode:
   - **VOX** - Software voice activation (no hardware)
   - **USB Relay** - Hardware PTT control
3. Configure VOX threshold or select USB port

---

## 📖 Documentation

### **📚 Full Wiki:** [GitHub Wiki](https://github.com/nhscan/soft-repeater-box/wiki)

**Quick Links:**
- [Installation Guide](https://github.com/nhscan/soft-repeater-box/wiki/Installation)
- [Hardware Wiring](WIRING.md) - Complete wiring diagrams
- [Setup Guide](SETUP.md) - First-time configuration
- [Troubleshooting](https://github.com/nhscan/soft-repeater-box/wiki/Troubleshooting)
- [DTMF Commands](https://github.com/nhscan/soft-repeater-box/wiki/DTMF-Commands)

### **Integration Guides:**
- [Zello Audio Routing](ZELLO_AUDIO_ROUTING.md) - Connect to Zello channels
- [AllStarLink Integration](ALLSTARLINK_GUIDE.md) - Link to AllStar network
- [Mumble Integration](MUMBLE_GUIDE.md) - Link repeaters with Mumble

---

## 🎮 DTMF Commands

**Default Commands (Customizable):**

| Code | Function | Description |
|------|----------|-------------|
| 0001 | Weather | Current weather conditions |
| 0002 | Time | Current time announcement |
| 0003-0010 | Custom | Your custom messages |

**Usage:** Key DTMF tones on your radio (works in Repeater mode only)

---

## 🌤️ Weather Integration

**Features:**
- Weather.gov integration (US only currently)
- Temperature, conditions, wind
- DTMF-triggered announcements
- Optional inclusion in station ID
- Manual coordinate entry (firewall bypass)

**Setup:**
1. Enable in DTMF Commands tab
2. Enter ZIP code OR manual coordinates
3. Test with DTMF 0001

---

## 🔌 Hardware Setup

### **Basic Setup (VOX Mode)**
```
Radio Audio Out → Computer Line In
Computer Line Out → Radio Audio In
```
No PTT relay needed!

### **Advanced Setup (USB Relay PTT)**
```
Radio Audio Out → Computer Line In
Computer Line Out → Radio Audio In
USB Relay → Radio PTT Pin
```

**See [WIRING.md](WIRING.md) for:**
- Complete wiring diagrams
- Radio-specific pinouts (Baofeng, Yaesu, Kenwood, Icom)
- USB relay module setup
- Voltage divider circuits
- Shopping list with links

---

## 🔗 Linking Repeaters

Connect multiple repeaters for wider coverage!

### **AllStarLink** (Ham Radio)
- Link to 3000+ nodes worldwide
- Raspberry Pi + USB sound card (~$60-100)
- [Complete Guide](ALLSTARLINK_GUIDE.md)

### **Mumble** (Ham & GMRS)
- FREE cloud or self-hosted VOIP
- Works for GMRS (no ham license needed!)
- [Complete Guide](MUMBLE_GUIDE.md)

### **Zello** (Mobile App Integration)
- Audio routing method (no API needed)
- Connect radio to Zello channels
- [Complete Guide](ZELLO_AUDIO_ROUTING.md)

---

## 🐛 Troubleshooting

### **No Audio?**
1. Check audio device selection
2. Verify cables connected
3. Try different devices
4. Increase gain sliders
5. Check Windows sound settings

### **PTT Not Working?**
1. Verify USB relay connected
2. Check serial port selection
3. Test relay manually
4. Try VOX mode instead

### **Weather Not Loading?**
1. Check internet connection
2. Verify ZIP code or coordinates
3. Try manual coordinate entry
4. Check firewall settings

**More:** [Troubleshooting Wiki](https://github.com/nhscan/soft-repeater-box/wiki/Troubleshooting)

---

## 📦 Building EXE

Create standalone Windows executable:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name="Soft_Repeater_Box_v1.01" soft_repeater_box.py
```

**Output:** `dist\Soft_Repeater_Box_v1.01.exe`

**See:** [Building EXE Guide](BUILDING_EXE.md) for complete instructions

---

## 🤝 Contributing

Contributions welcome!

- Report bugs: [Issues](https://github.com/nhscan/soft-repeater-box/issues)
- Request features: [Discussions](https://github.com/nhscan/soft-repeater-box/discussions)
- Submit PRs: [Contributing Guide](CONTRIBUTING.md)

---

## 📝 License

**MIT License** - Free for personal and commercial use!

See [LICENSE](LICENSE) for details.

---

## 💝 Support Development

Love Soft Repeater Box? Support development!

**CashApp:** [$NHlife](https://cash.app/$NHlife)

Your support helps add new features and maintain the project!

---

## 📞 Contact

**Email:** host@nhscan.com  
**GitHub:** [nhscan/soft-repeater-box](https://github.com/nhscan/soft-repeater-box)  
**Issues:** [Report Bug](https://github.com/nhscan/soft-repeater-box/issues)

---

## 🏆 Credits

**Created by:** NHscan  
**License:** MIT  
**Version:** 1.01  
**Platform:** Windows, Linux, macOS

---

## 🔄 Changelog

### **v1.01** (Current)
- ✅ Four operating modes
- ✅ DTMF commands (10 configurable)
- ✅ Weather integration
- ✅ Auto station ID
- ✅ PTT control (USB/VOX)
- ✅ Courtesy tones
- ✅ Debug mode
- ✅ Complete documentation

**See:** [CHANGELOG.md](CHANGELOG.md) for full history

---

## 📚 Documentation Files

- **README.md** - This file (overview)
- **SETUP.md** - First-time setup guide
- **WIRING.md** - Complete wiring diagrams
- **CHANGELOG.md** - Version history
- **CONTRIBUTING.md** - How to contribute
- **LICENSE** - MIT license text
- **requirements.txt** - Python dependencies
- **ZELLO_AUDIO_ROUTING.md** - Zello integration
- **ALLSTARLINK_GUIDE.md** - AllStarLink setup
- **MUMBLE_GUIDE.md** - Mumble linking
- **BUILDING_EXE.md** - Create Windows EXE
- **WIKI_SETUP_GUIDE.md** - GitHub wiki setup

---

**Transform your computer into a $1000+ repeater controller for FREE!**

**73!** 📻

---

<p align="center">
  <a href="https://cash.app/$NHlife">
    <img src="https://img.shields.io/badge/Donate-CashApp-brightgreen.svg" alt="Donate">
  </a>
  <a href="https://github.com/nhscan/soft-repeater-box/wiki">
    <img src="https://img.shields.io/badge/Docs-Wiki-blue.svg" alt="Documentation">
  </a>
  <a href="https://github.com/nhscan/soft-repeater-box/issues">
    <img src="https://img.shields.io/badge/Support-Issues-red.svg" alt="Support">
  </a>
</p>
