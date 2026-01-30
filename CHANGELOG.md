# Changelog - Soft Repeater Box

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.01] - 2026-01-30

### Initial Public Release 🎉

#### Added
- **4 Operating Modes**: Manual, Timed Auto-Replay, Continuous Delay Line, Full Repeater
- **VOX Detection**: Software voice-activated transmission with configurable threshold/attack/release
- **PTT Control**: USB relay module support (DTR/RTS) for hardware PTT
- **Audio Controls**: Real-time input/output gain adjustment with live level meters
- **Repeater Mode Features**:
  - Automatic station ID with configurable callsign
  - Configurable ID interval (default 10 minutes)
  - Courtesy tones after transmissions
  - Timeout timer to prevent excessive key-ups
  - Tail silence (hang time) after transmission
  - TTS integration for announcements
- **DTMF Command System** (10 configurable commands):
  - 0001: Weather report (full conditions)
  - 0002: Time & date announcement
  - 0003-0010: Custom user-configurable messages
  - Special keys: * (clear), # (submit)
  - Time-based debouncing for reliable detection
- **Weather Integration**:
  - Weather.gov API support (US only, no API key required)
  - ZIP code to coordinates conversion
  - Manual coordinate entry (bypass ZIP lookup)
  - Temperature in station ID (optional)
  - Cached updates (30-minute refresh)
  - Connection test diagnostics
- **Recording Features**:
  - Save transmissions as WAV files
  - Configurable recording modes
  - PTT look-ahead timing (prevents audio cut-off)
  - Recording save functionality in all modes
- **Feedback Protection**: Prevents audio loops when using web SDR or stereo mix
- **Debug Mode**: Toggle verbose console output (perfect for .exe distribution)
- **Configuration Management**:
  - All settings auto-save to JSON config file
  - Persistent settings between sessions
  - Audio device selection memory
  - Complete configuration GUI
- **Professional GUI**:
  - Tabbed interface (Main, Audio, Repeater, Mode, VOX/PTT, Recordings, DTMF Commands)
  - Real-time status indicators
  - Level meters for audio monitoring
  - Easy-to-use controls
- **Documentation**:
  - Comprehensive README
  - Detailed wiring guide for multiple radio types
  - Troubleshooting guides
  - DTMF timing explanations

#### Technical Details
- Python 3.8+ support
- Cross-platform (Windows primary, Linux/Mac community support)
- Goertzel algorithm for DTMF detection (no external dependencies)
- PTT pre-key timing (configurable 0-2 seconds)
- Audio buffer management with deque
- Background TTS generation thread
- Serial port auto-detection
- PyAudio integration for audio I/O
- NumPy for audio processing

#### Known Issues
- Weather.gov API is US-only (international users must use OpenWeatherMap - future)
- DTMF detection works only in Repeater Mode (by design)
- Some audio device combinations may require virtual audio cables

---

## [Unreleased]

### Planned for 1.1
- [ ] OpenWeatherMap API support (international users)
- [ ] More DTMF commands (0011-0020)
- [ ] Timed announcement scheduler
- [ ] EchoLink integration
- [ ] Web interface

### Planned for 1.2
- [ ] CTCSS/PL tone encoding/decoding
- [ ] Multiple repeater support
- [ ] Remote administration
- [ ] Statistics and logging
- [ ] Mobile app

---

## Version History

### Version Naming
- **Major.Minor format** (e.g., 1.01)
- Major: Significant new features or breaking changes
- Minor: Bug fixes, small features, improvements

### Support Policy
- Latest version: Full support
- Previous major version: Security fixes only
- Older versions: Community support

---

**Author**: NHscan  
**Email**: host@nhscan.com  
**Donate**: CashApp [$NHlife](https://cash.app/$NHlife)

**73!** 📻
