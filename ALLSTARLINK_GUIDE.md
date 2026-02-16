# 🌟 AllStarLink Integration Guide

## **Link Your Repeater to the AllStarLink Network**

AllStarLink is the premier **FREE** network for linking amateur radio repeaters and nodes worldwide.

---

## 🎯 **What is AllStarLink?**

**AllStarLink** is an open-source VOIP network for amateur radio:

```
✅ FREE & Open Source
✅ 3000+ linked nodes worldwide
✅ Low latency VOIP
✅ DTMF remote control
✅ Raspberry Pi compatible
✅ Active community
✅ Excellent documentation
✅ Ham license required
```

**Website:** https://www.allstarlink.org/

---

## 🔌 **Integration Methods**

### **Method 1: Dedicated AllStar Node** (Recommended)
Use a Raspberry Pi as dedicated AllStar node, route audio to Soft Repeater Box

### **Method 2: Direct Integration** (Future)
Run AllStar software on same computer as Soft Repeater Box

### **Method 3: Audio Routing** (Easiest for Testing)
Route audio between Soft Repeater Box and AllStar node app

---

## 📋 **Method 1: Dedicated AllStar Node** (RECOMMENDED)

### **What You Need:**

**Hardware:**
- Raspberry Pi 3/4 (~$35-75)
- MicroSD card 16GB+ (~$10)
- USB sound card (~$8-30)
- Power supply for Pi
- (Optional) Case for Pi

**Total Cost:** ~$60-100

---

### **Step-by-Step Setup:**

#### **1. Download AllStarLink Image**

1. Go to: https://www.allstarlink.org/
2. Click "Downloads"
3. Download **AllStarLink Raspberry Pi Image**
4. Use **Etcher** or **Raspberry Pi Imager** to write to SD card

#### **2. Register Your Node**

1. Go to: https://www.allstarlink.org/
2. Create account (need callsign)
3. Register a new node number
4. **Save your node number!** (e.g., 12345)

#### **3. Configure Raspberry Pi**

1. Insert SD card in Raspberry Pi
2. Connect USB sound card
3. Connect ethernet (or setup WiFi)
4. Power on Pi
5. SSH into Pi: `ssh repeater@<pi-ip-address>`
6. Password: (default from AllStar image)

#### **4. Configure AllStar Node**

Edit node configuration:
```bash
sudo nano /etc/asterisk/rpt.conf
```

Find your node section and configure:
```ini
[12345]  ; Your node number
rxchannel = SimpleUSB/usb  ; USB sound card
duplex = 1                  ; For repeaters
hangtime = 1000             ; Tail after transmission
althangtime = 4000          ; Alternate tail
totime = 180000             ; Timeout timer (3 minutes)
idrecording = |iW1ABC       ; Your callsign
idtalkover = |iW1ABC
```

Save and exit: `Ctrl+X`, `Y`, `Enter`

#### **5. Configure Audio**

Edit SimpleUSB configuration:
```bash
sudo nano /etc/asterisk/simpleusb.conf
```

Configure for your USB sound card:
```ini
[usb]
rxboost = 1              ; Input gain boost
txboost = 1              ; Output gain boost
carrierfrom = usb        ; Use USB for carrier detect
ctcssfrom = no           ; No CTCSS (adjust if needed)
invertptt = 0            ; PTT polarity
```

#### **6. Route Audio to Soft Repeater Box**

**On Raspberry Pi:**
- Audio OUT → Your audio interface
- Audio IN ← Your audio interface

**On Computer (Soft Repeater Box):**
1. **Audio Devices Tab:**
   - Input: Receiver from AllStar Pi
   - Output: Transmitter to AllStar Pi

2. **Configure Mode:**
   - Mode: Repeater Mode
   - Enable VOX or PTT as needed

**Audio Flow:**
```
Radio → Soft Repeater Box → AllStar Pi → AllStarLink Network
Radio ← Soft Repeater Box ← AllStar Pi ← AllStarLink Network
```

#### **7. Test Your Node**

1. **Restart AllStar:**
   ```bash
   sudo astres.sh
   ```

2. **Connect to AllStar console:**
   ```bash
   sudo asterisk -r
   ```

3. **Check node status:**
   ```
   rpt fun 12345 *3<node>
   ```
   (Replace 12345 with your node, <node> with node to connect to)

4. **Disconnect:**
   ```
   rpt fun 12345 *1<node>
   ```

---

## 🎮 **DTMF Commands**

AllStarLink uses DTMF for remote control:

### **Common Commands:**

```
*3 + NODE#     Connect to node
*1 + NODE#     Disconnect from node
*2             Monitor (connect without TX)
*70            Enable disconnect
*71            Disable disconnect
*75            Enable echo
*76            Disable echo

Examples:
*3 27339       Connect to Hub 27339
*1 27339       Disconnect from Hub 27339
*73            Time announcement
```

### **Status Commands:**

```
*81            Force ID
*82            Last 10 calls
*A#            Check connection status
```

---

## 🌐 **Finding Nodes to Connect To**

### **AllStar Node Database:**
https://www.allstarlink.org/nodelist.php

### **Popular Hubs:**

```
Hub 27339 - International Hub (busy!)
Hub 29800 - Another popular hub
Hub 50525 - Regional hub
(Many more available - check nodelist!)
```

### **Local Repeaters:**
- Search by state/region in nodelist
- Many local repeaters on AllStar
- Can link directly to them!

---

## 🔧 **Method 2: Direct Software Integration** (Advanced)

Run AllStar Asterisk on same computer as Soft Repeater Box.

### **Requirements:**
- Linux computer (Ubuntu recommended)
- AllStar software installed
- Virtual audio routing

### **Process:**

1. **Install AllStar on Linux:**
   ```bash
   # Follow AllStar install guide
   curl -s https://allstarlink.org/install.sh | sudo bash
   ```

2. **Configure Virtual Audio:**
   - Use PulseAudio loopback
   - Route between Asterisk and Soft Repeater Box

3. **Configure both to use virtual devices**

**Status:** This is advanced - Method 1 (dedicated Pi) is easier!

---

## 🎵 **Method 3: Audio Routing** (Quick Test)

Use audio routing for quick testing without hardware.

### **Setup:**

1. **Install AllStar App on Windows/Mac:**
   - Download IAXRpt (Windows AllStar client)
   - Or use Zoiper with IAX2 support

2. **Configure Audio:**
   ```
   Soft Repeater Output → Virtual Cable → AllStar App Input
   Soft Repeater Input ← Virtual Cable ← AllStar App Output
   ```

3. **Connect to AllStar Hub**

4. **Test audio flow**

**Good for:** Testing, temporary use  
**Not good for:** Production/permanent setup

---

## 📊 **Audio Levels & Quality**

### **Raspberry Pi Settings:**

In `/etc/asterisk/simpleusb.conf`:
```ini
rxboost = 1    ; 0-4, start with 1
txboost = 1    ; 0-4, start with 1
```

### **Soft Repeater Box:**
- Input Gain: 50-100% (from AllStar Pi)
- Output Gain: 50-100% (to AllStar Pi)
- Watch for clipping!

### **Audio Quality Tips:**
- Use good quality USB sound card
- Keep cables short
- Use shielded cables
- Ground everything properly
- Monitor audio levels

---

## 🔍 **Troubleshooting**

### **AllStar Node Won't Connect:**
```
Check:
✓ Internet connection working?
✓ Firewall allowing IAX2 (port 4569)?
✓ Node registered properly?
✓ Correct node number in config?

Fix:
→ Check AllStar console: sudo asterisk -r
→ Try: rpt reload
→ Verify registration at allstarlink.org
→ Check /var/log/asterisk/messages
```

### **No Audio from AllStar:**
```
Check:
✓ USB sound card recognized?
✓ Audio levels configured?
✓ Cables connected properly?
✓ Soft Repeater Box input device correct?

Fix:
→ Test with: alsamixer (on Pi)
→ Increase rxboost/txboost
→ Check cable connections
→ Verify audio devices in Soft Repeater Box
```

### **No Audio to AllStar:**
```
Check:
✓ Soft Repeater Box output correct?
✓ AllStar Pi receiving audio?
✓ COR (Carrier Detect) working?
✓ Audio levels high enough?

Fix:
→ Increase Soft Repeater Box output gain
→ Check simpleusb.conf settings
→ Monitor Pi audio input: alsamixer
→ Verify carrierfrom = usb in config
```

### **Echo/Feedback:**
```
Cause:
→ Audio loop (output feeding back to input)

Fix:
→ Separate audio paths
→ Use different audio interfaces
→ Enable feedback protection in Soft Repeater Box
→ Check AllStar tail settings (hangtime)
```

---

## 🎓 **Learning Resources**

### **Official Documentation:**
- AllStarLink Wiki: https://wiki.allstarlink.org/
- Forum: https://community.allstarlink.org/
- YouTube: Search "AllStarLink setup"

### **Recommended Reading:**
- AllStarLink Setup Guide
- SimpleUSB Configuration
- DTMF Command Reference
- Node Registration Guide

---

## 💡 **Pro Tips**

### **Node Management:**
- Use web portal for easy management
- Monitor node via AllMon (web interface)
- Set up email notifications
- Regular backups of config files

### **Best Practices:**
- ID every 10 minutes (FCC requirement)
- Monitor your node regularly
- Keep software updated
- Join AllStar community for help

### **Advanced Features:**
- Autopatch (phone line connection)
- Echolink gateway
- Weather announcements
- Custom macros
- Remote base

---

## 📱 **AllStar Mobile Access**

### **Apps:**
- **AllStar Link** (iOS/Android)
- **Zoiper** (IAX2 support)
- **IAXRpt** (Windows)

### **Usage:**
```
Connect from anywhere!
→ Use app to connect to your node
→ Talk through your repeater remotely
→ Access full AllStar network
```

---

## 🌍 **What You Can Do with AllStar**

### **Local:**
```
→ Link multiple local repeaters
→ Create regional network
→ Emergency communications
→ Expand coverage area
```

### **Regional:**
```
→ Link to state/regional hubs
→ Participate in nets
→ Weekly check-ins
→ Emergency coordination
```

### **Worldwide:**
```
→ Connect to international hubs
→ Talk to hams globally
→ DX conversations
→ Special event stations
```

---

## 🎯 **Quick Start Checklist**

- [ ] Register at allstarlink.org
- [ ] Get node number assigned
- [ ] Purchase Raspberry Pi + USB sound card
- [ ] Download AllStar image
- [ ] Write image to SD card
- [ ] Boot Raspberry Pi
- [ ] Configure node (rpt.conf)
- [ ] Configure audio (simpleusb.conf)
- [ ] Connect audio to Soft Repeater Box
- [ ] Test local audio
- [ ] Connect to test hub
- [ ] Verify two-way audio
- [ ] Go live!

**Time:** 2-3 hours (first time)  
**Difficulty:** Medium  
**Cost:** ~$60-100  

---

## 📞 **Need Help?**

**AllStar Community:** https://community.allstarlink.org/  
**Email (this software):** host@nhscan.com

---

## 🏆 **Success Story Example**

```
W1ABC Repeater Setup:

Hardware:
→ Soft Repeater Box (PC)
→ AllStar Pi (Raspberry Pi 4)
→ USB sound card
→ 2m FM repeater

Configuration:
→ Node: 54321
→ Connected to Hub 27339
→ Coverage: 30 mile radius (RF)
→ Plus: Worldwide via AllStar!

Result:
→ Local hams: Use RF as normal
→ Traveling hams: Connect via AllStar app
→ Linked to 3000+ nodes
→ Emergency backup communications
→ Total cost: ~$80
```

---

**AllStarLink is the gold standard for linking ham radio repeaters!**

**73!** 📻🌟

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Author:** NHscan  
**License:** MIT
