# 🚀 Setup Guide - Soft Repeater Box v1.01

Complete setup instructions to get your repeater controller running!

---

## 📋 **System Requirements**

### Minimum Requirements
- **OS**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or newer
- **RAM**: 2GB minimum (4GB recommended)
- **Disk**: 100MB free space
- **Audio**: Sound card or USB audio interface

### Recommended Hardware
- USB relay module for PTT control (~$5-10)
- USB sound card/interface (~$10-30)
- VB-Audio Virtual Cable (free software)
- Radio with audio input/output

---

## 🔧 **Installation**

### Step 1: Install Python

**Windows**:
1. Download from [python.org](https://www.python.org/downloads/)
2. **IMPORTANT**: Check "Add Python to PATH" during installation!
3. Verify: Open CMD and type `python --version`

**Linux**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-tk
python3 --version
```

**macOS**:
```bash
brew install python3
python3 --version
```

### Step 2: Clone or Download Repository

**Option A: Git Clone** (recommended)
```bash
git clone https://github.com/nhscan/soft-repeater-box.git
cd soft-repeater-box
```

**Option B: Download ZIP**
1. Go to https://github.com/nhscan/soft-repeater-box
2. Click "Code" → "Download ZIP"
3. Extract to folder
4. Open terminal/CMD in that folder

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**If you get permission errors**:
```bash
pip install --user -r requirements.txt
```

**On Linux, if PyAudio fails**:
```bash
sudo apt install portaudio19-dev python3-pyaudio
pip install pyaudio
```

---

## 🎯 **First Run**

### Start the Application

**Windows**:
```cmd
python soft_repeater_box.py
```

**Linux/Mac**:
```bash
python3 soft_repeater_box.py
```

**If you get "python not found"**:
- Windows: Use `py` instead of `python`
- Check Python was added to PATH

### Initial Configuration

1. **Set Your Callsign**
   - Go to "Repeater Settings" tab
   - Enter your callsign (e.g., "W1ABC")
   - Set ID interval (default: 600 seconds)

2. **Configure Audio**
   - Go to "Audio Devices" tab
   - Select input device (where audio comes FROM)
   - Select output device (where audio goes TO)
   - Adjust gain sliders (start at 100%)

3. **Configure PTT**
   - Go to "VOX/PTT Settings" tab
   - Choose PTT mode:
     - **USB/Serial**: For relay module
     - **VOX (Radio's built-in)**: No relay needed
   - If using relay:
     - Select serial port
     - Choose DTR or RTS
     - Test with "Test PTT ON/OFF" buttons

4. **Save Configuration**
   - File menu → Save Configuration
   - Settings auto-save when changed

---

## 🔌 **Hardware Setup**

### Audio Connections

See [WIRING.md](WIRING.md) for detailed diagrams!

**Quick Setup**:
```
Computer → USB Sound Card → Radio
             ↓
        USB Relay → PTT
```

**For Web SDR**:
```
Computer → VB-Audio Cable → Browser/SDR
         ↓
   Enable Feedback Protection!
```

### PTT Relay Wiring

**Cheap Chinese USB Relay** (~$5-10):
```
USB to computer
Relay NO  → Radio PTT (Tip)
Relay COM → Radio GND (Sleeve)
```

**Radio Compatibility**:
- Baofeng UV-5R: 2.5mm Kenwood style
- Yaesu FT-60: 2.5mm Kenwood style  
- Icom IC-V86: 2.5mm Icom style (REVERSED!)
- See [WIRING.md](WIRING.md) for full list

---

## 🎛️ **Quick Start Guide**

### Test Mode (Without Radio)

1. **Mode 1: Manual**
   - Click "Manual Mode"
   - Click "Start Recording"
   - Speak into microphone
   - Click "Stop Recording"
   - Click "Start Playback"
   - Should hear yourself!

2. **Check Audio Levels**
   - Watch input level meter (should show 20-60%)
   - Watch output level meter during playback
   - Adjust gain sliders if needed

### Repeater Mode (With Radio)

1. **Set Mode**
   - Click "Repeater Mode (VOX/Pass-Through)"
   - Enable VOX if using software VOX
   - Or use radio's built-in VOX

2. **Configure Repeater**
   - Set courtesy tone (optional)
   - Set timeout (e.g., 180 seconds)
   - Enable Auto ID

3. **Start System**
   - Click "START SYSTEM"
   - Status should show "IDLE"

4. **Test**
   - Transmit on radio
   - Should see "VOX ACTIVE"
   - Should hear courtesy tone after
   - Check PTT LED on relay

### DTMF Commands Setup

1. **Enable DTMF**
   - Go to "DTMF Commands" tab
   - Check "Enable DTMF Detection"
   - **Note**: Only works in Repeater Mode!

2. **Configure Weather** (optional)
   - Check "Enable Weather Service"
   - Enter ZIP code OR
   - Enter manual coordinates
   - Click "Test Connection"

3. **Set Custom Messages**
   - 0003-0010: Enter your messages
   - Example: "Net every Wednesday at 8 PM"
   - Click "Save All DTMF Settings"

4. **Test Commands**
   - Set radio DTMF to SLOW
   - Key up, dial 0-0-0-1
   - Un-key, wait 1-3 seconds
   - Should hear weather!

---

## ⚙️ **Configuration Tips**

### Audio Settings

**Input Too Loud** (clipping):
- Lower input gain slider
- Reduce radio volume
- Move mic away

**Input Too Quiet**:
- Increase input gain slider
- Increase radio volume
- Check cable connections

**Output Too Loud**:
- Lower output gain slider
- Radio may overdrive

**Output Too Quiet**:
- Increase output gain slider
- Check radio input sensitivity

### VOX Settings

**Triggering Too Easily**:
- Increase VOX threshold (try 5-10%)
- Increase attack time
- Reduce input gain

**Not Triggering**:
- Lower VOX threshold (try 2-3%)
- Decrease attack time
- Increase input gain

**VOX Dropping Mid-Transmission**:
- Increase release time (try 1.0-2.0s)
- Check audio levels

### PTT Settings

**PTT Cutting Off Start of Transmission**:
- Increase PTT pre-key time
- Typical: 0.3-0.5 seconds

**PTT Staying On**:
- Check release time
- May need shorter tail silence
- Click "Test PTT OFF" to force off

---

## 🐛 **Troubleshooting**

### Application Won't Start

**Error: "No module named 'pyaudio'"**
```bash
pip install pyaudio
```

**Error: "tkinter not found"**
- Linux: `sudo apt install python3-tk`
- Windows: Reinstall Python with "tcl/tk" option checked

**Error: "Permission denied"**
```bash
pip install --user -r requirements.txt
```

### No Audio

**Can't hear input**:
1. Check Audio Devices tab
2. Verify correct input device selected
3. Watch input level meter
4. Increase input gain
5. Enable Debug Mode for diagnostics

**Can't hear output**:
1. Check Audio Devices tab
2. Verify correct output device selected
3. Test manual playback
4. Increase output gain
5. Check cable connections

### PTT Issues

**Relay not activating**:
1. Check serial port selection
2. Try DTR vs RTS
3. Use "Test PTT ON" button
4. Verify USB connection
5. Check Device Manager (Windows)

**Wrong serial port list**:
- Unplug/replug relay
- Restart application
- Check drivers installed

### DTMF Issues

**Not detecting digits**:
1. Must be in Repeater Mode!
2. Enable DTMF in settings
3. Set radio DTMF to SLOW
4. Hold each tone 300ms
5. Enable Debug Mode to see detection

**Getting wrong digits**:
- Slow down dialing
- Pause between digits (200ms)
- Check radio DTMF settings
- Lower DTMF speed

### Weather Issues

**"Failed to fetch"**:
1. Click "Test Connection"
2. Check internet connection
3. Try manual coordinates
4. Use lat/lon from latlong.net

**ZIP not found**:
- Try different ZIP
- Use manual coordinates instead
- Only works in United States!

---

## 💡 **Pro Tips**

### Performance

1. **Close Unnecessary Apps**: Free up CPU/RAM
2. **Use Quality Cables**: Avoid RF interference
3. **Keep Cables Short**: Reduce noise
4. **Use USB Hub**: If many USB devices
5. **Disable Power Saving**: For USB ports (Windows)

### Reliability

1. **Save Configuration**: Regularly back up config file
2. **Test Before Deployment**: Run for 24 hours first
3. **Monitor Levels**: Check for clipping
4. **Log Issues**: Enable Debug Mode
5. **Have Backup**: Keep spare relay/cables

### Best Practices

1. **FCC Compliance**: ID every 10 minutes
2. **Monitor Operation**: Don't leave unattended
3. **Set Timeout**: Prevent stuck transmissions
4. **Test Regularly**: Verify all functions
5. **Document Setup**: Take photos, notes

---

## 📱 **Remote Operation**

### Accessing Remotely

**Option 1: Remote Desktop**
- Windows: Use built-in Remote Desktop
- Linux: VNC, TeamViewer, AnyDesk
- Access full GUI remotely

**Option 2: VNC/TeamViewer**
- Install VNC server
- Access from anywhere
- Control complete setup

**Option 3: SSH + Screen** (Linux)
```bash
# Start in screen session
screen -S repeater
python3 soft_repeater_box.py

# Detach: Ctrl+A, D
# Reattach: screen -r repeater
```

### Auto-Start on Boot

**Windows**:
1. Create batch file `start_repeater.bat`:
```batch
@echo off
cd C:\path\to\soft-repeater-box
python soft_repeater_box.py
```
2. Add to Startup folder
3. Right-click batch file → Run as Administrator

**Linux** (systemd service):
1. Create `/etc/systemd/system/repeater.service`:
```ini
[Unit]
Description=Soft Repeater Box
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/soft-repeater-box
ExecStart=/usr/bin/python3 soft_repeater_box.py
Restart=always

[Install]
WantedBy=multi-user.target
```
2. Enable: `sudo systemctl enable repeater.service`
3. Start: `sudo systemctl start repeater.service`

---

## 🔄 **Updating**

### Git Method
```bash
cd soft-repeater-box
git pull origin main
pip install -r requirements.txt
```

### Manual Method
1. Download latest release
2. Extract to new folder
3. Copy your `repeater_config.json`
4. Run new version

### Check for Updates
- Watch GitHub releases
- Star the repo for notifications
- Join discussions

---

## 💾 **Backup Configuration**

### What to Backup
- `repeater_config.json` (your settings)
- `recordings/` folder (optional)
- Custom DTMF messages (in config)
- Wiring documentation/photos

### How to Backup
```bash
# Manual backup
cp repeater_config.json repeater_config_backup_2026-01-30.json

# Or use the GUI
File menu → Save Configuration
```

---

## 📞 **Getting Help**

### Before Asking for Help

1. **Enable Debug Mode** (VOX/PTT Settings tab)
2. **Copy Console Output**
3. **Note Your Configuration**:
   - OS and version
   - Python version
   - Radio model
   - Relay module
   - What you tried
4. **Check Documentation**:
   - README.md
   - WIRING.md
   - This SETUP.md

### Where to Get Help

- **Email**: host@nhscan.com
- **GitHub Issues**: [Report Problem](https://github.com/nhscan/soft-repeater-box/issues)
- **GitHub Discussions**: [Ask Question](https://github.com/nhscan/soft-repeater-box/discussions)

### What to Include

```
Subject: [Brief description of issue]

OS: Windows 11
Python: 3.11.0
Radio: Baofeng UV-5R
Relay: x003qjjrql USB module

Problem:
[Describe what's not working]

What I tried:
[Steps you've taken]

Console output (Debug Mode ON):
[Paste relevant output]

Configuration:
[Screenshot or description]
```

---

## 💝 **Support the Project**

Love Soft Repeater Box? Help keep it free!

**Donate**: CashApp [$NHlife](https://cash.app/$NHlife)

Your support helps with:
- Development time
- Testing equipment
- Server costs
- Documentation
- Feature requests

---

## 📚 **Next Steps**

After setup:
1. ✅ Test all modes
2. ✅ Configure DTMF commands
3. ✅ Set up weather
4. ✅ Test with radio
5. ✅ Run for 24 hours
6. ✅ Deploy for real use
7. ✅ Share your experience!

---

## 🎓 **Learning More**

### Documentation
- [README.md](README.md) - Overview
- [WIRING.md](WIRING.md) - Hardware setup
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to help

### Resources
- [Amateur Radio Subreddit](https://reddit.com/r/amateurradio)
- [FCC Rules Part 97](https://www.fcc.gov/wireless/bureau-divisions/mobility-division/amateur-radio-service)
- [ARRL](https://www.arrl.org/)

---

**Ready to Rock!** 🎸

You're all set up! Key up and test your repeater!

**73!** 📻

---

**Created by NHscan**
**Donate**: CashApp [$NHlife](https://cash.app/$NHlife)
