# 🔌 Wiring Guide - Soft Repeater Box

Complete wiring diagrams for connecting Soft Repeater Box to your radio equipment.

---

## 📋 **Table of Contents**

1. [USB Relay Module (Cheap Chinese Relay)](#usb-relay-module)
2. [Audio Connections](#audio-connections)
3. [Radio-Specific Wiring](#radio-specific-wiring)
4. [Troubleshooting](#troubleshooting)

---

## 🔌 **USB Relay Module (Recommended)**

### What You Need

**Cheap Chinese USB Relay Module** (~$5-10)
- Search Amazon/eBay for: "USB Relay Module"
- Common models: x003qjjrql, HW-655, LC Technology
- Usually has 1, 2, 4, or 8 relays
- USB powered, no external power needed!

### Module Pinout

```
┌─────────────────────────────┐
│    USB RELAY MODULE         │
│                             │
│  [USB] ← Connect to PC      │
│                             │
│  Relay 1:                   │
│    NO  (Normally Open)      │ ← Use these!
│    COM (Common)             │ ← Connect PTT here
│    NC  (Normally Closed)    │ ← Leave empty
│                             │
│  [LED] ← Lights when active │
└─────────────────────────────┘
```

### Basic PTT Wiring

```
Computer USB Port
    │
    └──> [USB Relay Module]
              │
              │ Relay Output (NO & COM)
              │
              ├── NO  ──┐
              │         │  When relay activates:
              └── COM ──┤  These connect together = PTT ON
                        │
                        └──> Radio PTT Jack
                             (Tip = PTT, Sleeve = Ground)
```

### Detailed Relay Connection

```
Radio PTT Jack (3.5mm or 2.5mm):
┌────────────┐
│   ┌────┐   │
│   │Tip │ ──┼──> Connect to Relay NO
│   └────┘   │
│            │
│   ┌────┐   │
│   │Ring│   │ ← Often unused (some radios use for mic)
│   └────┘   │
│            │
│   ┌────┐   │
│   │Slv │ ──┼──> Connect to Relay COM
│   └────┘   │
└────────────┘

When software activates relay:
- NO and COM connect
- This grounds PTT line
- Radio transmits!
```

---

## 🎙️ **Audio Connections**

### Option 1: USB Sound Card (Easiest!)

```
                    ┌─────────────────┐
                    │   USB SOUND     │
Computer USB ────> │   CARD/INTERFACE│
                    │                 │
                    │  [Mic In]       │ ──> Radio Speaker/Audio Out
                    │                 │
                    │  [Line Out]     │ ──> Radio Mic/Audio In
                    │                 │
                    └─────────────────┘

Examples:
- Behringer UCA202 (~$30)
- Sabrent USB Sound Card (~$8)
- Any USB audio interface
```

### Option 2: 3.5mm Audio Cables

```
Computer Sound Card:
    ├── Line Out (Green) ──> Cable ──> Radio Mic Input
    │                                   (with voltage divider!)
    │
    └── Mic In (Pink) ──> Cable ──> Radio Speaker Output
```

**⚠️ IMPORTANT**: Use voltage divider for mic input!

```
Computer Line Out ────┬──── 10kΩ ────┬──── Radio Mic Input
                      │               │
                      └─── 1kΩ ──── GND

This reduces 1V line out to ~100mV for mic input
Without this: YOU WILL OVERDRIVE THE RADIO!
```

### Option 3: Virtual Audio Cable (For Web SDR)

```
OpenWebRX/WebSDR in Browser
    │
    │ Audio via browser
    │
    ↓
VB-Audio Virtual Cable
    │
    │ Routes audio to/from software
    │
    ↓
Soft Repeater Box
    │
    │ Input: CABLE Output
    │ Output: CABLE Input
    │
    ↓
Browser plays repeater output
Repeater hears browser audio

⚠️ MUST ENABLE FEEDBACK PROTECTION!
```

---

## 📻 **Radio-Specific Wiring**

### Baofeng UV-5R / UV-82 / BF-F8HP

**PTT**: 2.5mm jack (Kenwood style)
```
2.5mm Plug:
┌──────────┐
│  ┌────┐  │
│  │Tip │ ─┼──> PTT (Ground to transmit)
│  └────┘  │
│          │
│  ┌────┐  │
│  │Slv │ ─┼──> Ground
│  └────┘  │
└──────────┘

Relay Wiring:
NO  → Tip (PTT)
COM → Sleeve (Ground)
```

**Audio**: 3.5mm jack (Kenwood style)
```
3.5mm Plug:
┌──────────┐
│  ┌────┐  │
│  │Tip │ ─┼──> Mic Input (from computer)
│  └────┘  │
│          │
│  ┌────┐  │
│  │Ring│ ─┼──> Ground
│  └────┘  │
│          │
│  ┌────┐  │
│  │Slv │ ─┼──> Speaker Output (to computer)
│  └────┘  │
└──────────┘
```

**Complete Cable** (Baofeng Programming Cable style):
```
Computer                      Baofeng
Line Out ──────────────────> Mic (Tip of 3.5mm)
Mic In ────────────────────> Speaker (Sleeve of 3.5mm)
Ground ────────────────────> Ground (Ring of 3.5mm)

Relay NO ──────────────────> PTT (Tip of 2.5mm)
Relay COM ─────────────────> Ground (Sleeve of 2.5mm)
```

---

### Yaesu FT-60R / VX-7R

**PTT**: Same as Baofeng (2.5mm Kenwood style)

**Audio**: 3.5mm jack
```
Similar to Baofeng wiring
Works with Baofeng-style cables!
```

---

### Kenwood TH-D74 / TM-D710G

**PTT**: 2.5mm jack
```
Same wiring as Baofeng
Ground tip to transmit
```

**Audio**: 3.5mm jack or special data cable
```
Radio Data Port (if available):
- Better audio quality
- Dedicated PTT line
- Use radio-specific data cable
```

---

### Icom IC-V86 / ID-51A

**PTT**: 2.5mm jack (Icom style)
```
⚠️ DIFFERENT from Kenwood!

2.5mm Plug (Icom):
Tip    → Ground
Sleeve → PTT

Relay Wiring:
NO  → Sleeve (PTT)
COM → Tip (Ground)

REVERSED from Kenwood!
```

**Audio**: 3.5mm jack
```
Tip    → Mic Input
Ring   → Mic Ground
Sleeve → Speaker Output

Use voltage divider for mic!
```

---

### Motorola/Kenwood/Icom Mobile Radios

**Use Radio-Specific Data Cable**

Most mobile radios have:
- Accessory port (13-pin, 6-pin, etc.)
- Dedicated PTT line
- Dedicated audio in/out
- Better audio quality than speaker/mic

**Example: Kenwood TM-V71A**
```
Accessory Port (mini-DIN 6):
Pin 1: Audio Out (to computer mic in)
Pin 2: Audio Ground
Pin 3: PTT (ground to transmit)
Pin 4: Audio In (from computer line out)
Pin 5: +8V (not needed)
Pin 6: Ground
```

**Recommended**: Buy radio-specific cable or make your own

---

## 🔧 **Software Configuration**

### PTT Settings

**For USB Relay:**
```
VOX/PTT Settings Tab:
├─ PTT Mode: ● USB/Serial (NOT VOX!)
├─ Serial Port: Select your relay (e.g., COM3)
└─ Relay Type: ● DTR or ● RTS (try both!)
```

**For Radio VOX:**
```
VOX/PTT Settings Tab:
├─ PTT Mode: ● VOX (Radio's built-in VOX)
└─ Software VOX: ☐ Disabled
```

### Audio Device Selection

```
Audio Devices Tab:
├─ Input Device: Select where audio comes FROM
│  (Radio speaker, USB sound card input, virtual cable)
│
└─ Output Device: Select where audio goes TO
   (Radio mic, USB sound card output, virtual cable)
```

---

## 🧪 **Testing**

### Step 1: Test Relay
```
1. Connect relay to USB
2. Go to VOX/PTT Settings tab
3. Click "Test PTT ON"
4. Relay LED should light up!
5. Click "Test PTT OFF"
6. LED should turn off
```

### Step 2: Test Audio Input
```
1. Connect audio from radio
2. Watch input level meter (Main Control tab)
3. Should see level when audio present
4. Adjust Input Gain slider if needed
```

### Step 3: Test Audio Output
```
1. In Manual mode
2. Record some audio
3. Play it back
4. Should hear it on radio
5. Adjust Output Gain if needed
```

### Step 4: Test PTT with Audio
```
1. Switch to Repeater Mode
2. Transmit on radio
3. Should see VOX activate
4. Should hear courtesy tone after
5. Check PTT LED if using relay
```

---

## ⚠️ **Safety & Best Practices**

### Audio Levels
```
✅ DO:
- Use voltage divider for mic input
- Start with low gain, increase slowly
- Watch for distortion
- Keep levels under 80%

❌ DON'T:
- Connect line-level directly to mic input!
- Max out gain sliders
- Allow clipping/distortion
- Overdrive your radio
```

### PTT Circuit
```
✅ DO:
- Use relay for isolation
- Test relay before connecting radio
- Use correct wiring for your radio brand
- Double-check polarity

❌ DON'T:
- Short PTT line to voltage!
- Use wrong pinout (Kenwood vs Icom)
- Connect relay backwards
- Apply external voltage to PTT
```

### Grounding
```
✅ DO:
- Use common ground for all connections
- Ground radio chassis
- Ground computer chassis if metal
- Use shielded audio cables

❌ DON'T:
- Create ground loops
- Use unshielded cables for long runs
- Forget to connect ground wires
```

---

## 🔍 **Troubleshooting**

### Problem: Relay doesn't activate
```
Solutions:
1. Check serial port selection
2. Try different relay type (DTR vs RTS)
3. Test with "Test PTT ON" button
4. Check USB connection
5. Try different USB port
6. Check Device Manager (Windows)
```

### Problem: No audio input
```
Solutions:
1. Check audio device selection
2. Verify cable connections
3. Check radio volume
4. Adjust input gain
5. Enable Debug Mode
6. Watch audio level meter
```

### Problem: Distorted audio
```
Solutions:
1. Lower output gain
2. Check for clipping in level meter
3. Add/adjust voltage divider
4. Lower radio volume
5. Use better quality cables
```

### Problem: PTT stuck on
```
Solutions:
1. Click "Test PTT OFF"
2. Restart software
3. Unplug relay module
4. Check for software crashes
5. Verify relay wiring
```

---

## 🛠️ **Tools Needed**

### Basic Setup
- 📏 Wire strippers
- 🔌 Soldering iron (optional but recommended)
- 🔧 Multimeter (for testing)
- ✂️ Cable cutters
- 🎚️ Resistors for voltage divider

### Connectors
- 3.5mm audio plugs (TRS)
- 2.5mm audio plugs (TS or TRS)
- Crimp connectors or solder
- Heat shrink tubing
- Shielded audio cable

---

## 📦 **Shopping List**

### Essential
- [ ] USB Relay Module (~$5-10)
- [ ] USB Sound Card (~$8-30)
- [ ] 3.5mm audio cables
- [ ] 2.5mm audio plug (for PTT)

### Optional but Recommended
- [ ] VB-Audio Virtual Cable (free software)
- [ ] Radio-specific data cable (~$20-50)
- [ ] Voltage divider components (~$1)
- [ ] Quality shielded cables (~$10-20)

### Where to Buy
- **Amazon**: USB relay, sound cards
- **eBay**: Cheap cables, connectors
- **Ham Radio Outlet**: Radio-specific cables
- **DX Engineering**: Quality accessories
- **AliExpress**: Cheap Chinese relay modules

---

## 💡 **Pro Tips**

1. **Label Everything**: Mark cables for input/output
2. **Test Before Connecting Radio**: Verify all connections
3. **Start with Low Volume**: Gradually increase levels
4. **Use Quality Cables**: Cheap cables = noise/issues
5. **Keep Cables Short**: Minimize RF interference
6. **Separate Power/Audio**: Avoid ground loops
7. **Document Your Setup**: Take photos, notes
8. **Back Up Working Config**: Save settings file

---

## 📞 **Need Help?**

Having wiring issues? Contact:
- **Email**: host@nhscan.com
- **GitHub Issues**: [Report Problem](https://github.com/nhscan/soft-repeater-box/issues)

Include photos of your setup for faster help!

---

**Made by NHscan | 73!** 📻

**Donate**: CashApp [$NHlife](https://cash.app/$NHlife)
