# 📻 Soft Repeater Box

**Professional Amateur Radio Repeater Controller Software**

[![Version](https://img.shields.io/badge/version-1.01-blue.svg)](https://github.com/nhscan/soft-repeater-box)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-yellow.svg)](https://www.python.org/)
[![Donate](https://img.shields.io/badge/donate-CashApp-brightgreen.svg)](https://cash.app/$NHlife)

Transform your computer into a full-featured amateur radio repeater controller with DTMF commands, weather integration, and professional PTT control!

**Created by NHscan** | [host@nhscan.com](mailto:host@nhscan.com)

---

## 💰 **Support Development**

Love Soft Repeater Box? Buy me a coffee!

**CashApp: [$NHlife](https://cash.app/$NHlife)**

Your support helps keep this project free and maintained!

---

## 🎯 **Features**

### Core Functionality
- 🎙️ **4 Operating Modes**: Manual, Timed Auto-Replay, Continuous Delay Line, Full Repeater
- 🔊 **VOX Detection**: Software voice-activated transmission
- 📡 **PTT Control**: USB relay support (DTR/RTS) for hardware PTT
- 💾 **Recording**: Save transmissions as WAV files
- 🎵 **Courtesy Tones**: Configurable beep after transmissions

### Repeater Features
- 🆔 **Automatic Station ID**: Configurable callsign with time/date/weather
- ⏱️ **Timeout Timer**: Prevent excessive key-ups
- 🔁 **Tail Silence**: Hang time after transmission
- 🎤 **TTS Integration**: Text-to-speech for announcements
- 🔇 **Feedback Protection**: Prevent audio loops

### Advanced Features
- 📟 **DTMF Commands**: 10 configurable remote commands (0001-0010)
- 🌤️ **Weather Integration**: Live weather via Weather.gov API
- 🎚️ **Audio Controls**: Real-time input/output gain adjustment
- 🔧 **Debug Mode**: Toggle verbose console output
- 💾 **Auto-Save Config**: All settings persist between sessions

---

## 🚀 **Quick Start**

### 1. Install Python
Download from [python.org](https://www.python.org/downloads/)

### 2. Clone Repository
```bash
git clone https://github.com/nhscan/soft-repeater-box.git
cd soft-repeater-box
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Application
```bash
python soft_repeater_box.py
```

---

## 📟 **DTMF Commands**

| Code | Function | Description |
|------|----------|-------------|
| **0001** | Weather | Full weather report |
| **0002** | Time/Date | Current time and date |
| **0003-0010** | Custom | Your configurable messages |

**Special Keys**: **\*** (clear), **#** (submit)

---

## 📚 **Documentation**

- [WIRING.md](WIRING.md) - Complete wiring diagrams
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [LICENSE](LICENSE) - MIT License

---

## 🤝 **Contributing**

Contributions welcome! Open an issue or submit a pull request.

---

## 📜 **License**

MIT License - Free for personal and commercial use!

---

## 🙏 **Credits**

**Author**: NHscan
- Email: [host@nhscan.com](mailto:host@nhscan.com)
- CashApp: [$NHlife](https://cash.app/$NHlife)

**Made with ❤️ for the amateur radio community**

**73!** 📻
