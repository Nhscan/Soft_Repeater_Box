# 📱 Using Zello with Soft Repeater Box

## **Audio Routing Method** (WORKING Solution!)

Integrate Zello with your repeater using audio routing - no API needed!

---

## 🎯 **Overview**

Instead of direct API integration, we route audio between:
```
Radio ↔ Soft Repeater Box ↔ Virtual Audio Cable ↔ Zello Desktop App
```

This method:
- ✅ **WORKS** reliably
- ✅ FREE
- ✅ No authentication issues
- ✅ Uses your existing Zello account
- ✅ Setup takes 15-20 minutes

---

## 📋 **What You Need**

### Software:
1. **Zello Desktop** - Older version recommended (see below)
2. **VB-Audio Virtual Cable** - FREE audio router
3. **Soft Repeater Box** - Your repeater software

### Hardware:
- Computer running Windows
- Radio with audio input/output
- Audio interface (USB sound card or computer audio)

---

## 🔧 **Setup Instructions**

### **Step 1: Install VB-Audio Virtual Cable**

1. Download from: https://vb-audio.com/Cable/
2. Run installer
3. Restart computer (required!)

This creates virtual audio devices:
- `CABLE Input` (what you send TO the cable)
- `CABLE Output` (what comes OUT of the cable)

---

### **Step 2: Install Zello Desktop**

#### **IMPORTANT: Use Older Version!**

The **newer Zello desktop** versions focus on "Workflow" features and may have connection issues.

**Recommended: Use older Zello version (pre-Workflow)**

**Where to find older versions:**
- Check your Downloads folder if you previously installed it
- Search for "Zello desktop 1.x" (older builds)
- **OR** use current version with TLS fix (see below)

#### **TLS Settings Fix (For Newer Versions):**

If using newer Zello:
1. Open Zello Desktop
2. Click **Settings** (gear icon)
3. Go to **Network** or **Advanced**
4. **UNCHECK** "Enable TLS"
5. Restart Zello
6. Try connecting again

**Why this is needed:**
- Newer Zello versions enforce TLS/SSL
- Older servers may not support it
- Unchecking TLS allows connection to all servers

---

### **Step 3: Configure Zello Desktop**

1. **Open Zello**
2. **Login** with your account
3. **Click Settings** (gear icon)

4. **Audio Settings:**
   ```
   Microphone: CABLE Output (VB-Audio Virtual Cable)
   Speakers:   Your actual speakers/headphones
   ```

5. **Enable Voice Activation (VOX):**
   - Check ✓ "Voice Activation"
   - Adjust sensitivity (start around 50%)
   - This auto-triggers PTT when audio is detected!

6. **Join Your Channel:**
   - Click "Channels"
   - Join "GMRS New Hampshire Network" (or your channel)
   - Channel should show as "Connected"

---

### **Step 4: Configure Soft Repeater Box**

1. **Open Soft Repeater Box**

2. **Go to Audio Devices Tab:**
   ```
   Input Device:  Your radio/microphone input
   Output Device: CABLE Input (VB-Audio Virtual Cable)
   ```

3. **Configure Your Mode:**
   - Recommended: **Repeater Mode**
   - Enable VOX if using software VOX
   - Set up PTT if using hardware PTT

4. **Test Audio Levels:**
   - Adjust Input Gain (radio → computer)
   - Adjust Output Gain (computer → Zello)
   - Watch level meters - aim for 50-80%

---

## 🎙️ **How It Works**

### **Radio User Transmits:**
```
1. Ham keys up radio
2. Audio → Computer input
3. Soft Repeater Box receives audio
4. Passes to CABLE Input (output device)
5. Zello hears audio on CABLE Output (microphone)
6. Zello VOX triggers (auto-PTT!)
7. Zello transmits to channel
8. Everyone on Zello hears radio user!
```

### **Zello User Transmits:**
```
1. Zello user talks
2. Zello plays audio to Speakers
3. Radio users hear through computer speakers
   (OR route back through radio - see Two-Way setup below)
```

---

## 🔄 **Two-Way Audio Setup** (Advanced)

For Zello audio to play through the radio (not just speakers):

### **Option A: Use VoiceMeeter Banana** (Recommended)

**Download:** https://vb-audio.com/Voicemeeter/banana.htm

VoiceMeeter Banana is a virtual audio mixer that routes audio both ways.

**Setup:**
1. Install VoiceMeeter Banana
2. **Soft Repeater Box:**
   - Output: `VoiceMeeter Input`
3. **Zello Desktop:**
   - Microphone: `VoiceMeeter Output`
   - Speakers: `VoiceMeeter Aux Input`
4. **In VoiceMeeter:**
   - Route hardware inputs to outputs
   - Mix Zello and Radio audio
   - Send combined audio to radio

### **Option B: Two Virtual Cables**

1. Install VB-Cable (already done)
2. Install VB-Cable B (additional cable)
3. Route:
   ```
   Repeater → CABLE A Input → Zello Microphone (CABLE A Output)
   Zello Speakers → CABLE B Input → Repeater Input (CABLE B Output)
   ```

---

## 📊 **Audio Flow Diagram**

```
╔═══════════════════════════════════════════════════════════╗
║                    ONE-WAY SETUP                          ║
╚═══════════════════════════════════════════════════════════╝

Radio Mic → Computer → Soft Repeater Box → CABLE → Zello
                                                      ↓
Zello → Computer Speakers (you hear Zello users)


╔═══════════════════════════════════════════════════════════╗
║                   TWO-WAY SETUP                           ║
╚═══════════════════════════════════════════════════════════╝

Radio Mic → Computer → Soft Repeater Box → VoiceMeeter → Zello
              ↑                                  ↓          ↓
Radio Speaker ←───────────────────── VoiceMeeter ←──── Zello
```

---

## 🔧 **Troubleshooting**

### **Zello Can't Hear Radio**
```
Check:
✓ Soft Repeater output = CABLE Input?
✓ Zello microphone = CABLE Output?
✓ Audio levels high enough in Repeater?
✓ Zello VOX enabled?
✓ Zello VOX sensitivity not too high?

Fix:
→ Increase Output Gain in Soft Repeater
→ Lower VOX threshold in Zello
→ Watch Zello's input meter (should show activity)
→ Disable Zello VOX and try manual PTT first
```

### **Can't Hear Zello Users**
```
Check:
✓ Zello speakers set to actual output?
✓ Windows volume not muted?
✓ Zello output volume up?
✓ Zello channel actually active?

Fix:
→ Check Windows sound mixer
→ Increase Zello speaker volume
→ Test Zello with built-in test call
```

### **Zello Won't Connect to Servers**
```
Check:
✓ Using older Zello version?
✓ TLS disabled in settings?
✓ Internet connection working?
✓ Firewall blocking Zello?

Fix:
→ Settings → Uncheck "Enable TLS"
→ Restart Zello
→ Try different network (mobile hotspot)
→ Check firewall settings (allow Zello)
```

### **Echo / Feedback**
```
Cause:
→ Zello hearing itself (audio loop)

Fix:
→ Use separate devices for input/output
→ Lower Repeater output volume
→ Increase Zello VOX threshold
→ Don't use same device for in AND out
→ Enable "Feedback Protection" in Soft Repeater Box
```

### **Audio Quality Poor**
```
Check:
✓ Sample rates match (use 44100 Hz everywhere)
✓ Levels not clipping (keep under 80%)
✓ Good internet connection
✓ Not overdriving Zello input

Fix:
→ Reduce Repeater output gain if distorted
→ Check all audio settings at 44100 Hz
→ Lower VOX sensitivity if triggering on noise
→ Use wired internet vs WiFi
```

---

## 💡 **Tips for Best Results**

### **Audio Levels:**
- Start with 50% gain on everything
- Gradually increase until good volume
- Watch for clipping (level meters red)
- Keep peaks around 70-80%

### **VOX Settings:**
- Zello VOX: Start at 50% sensitivity
- Too sensitive = triggers on noise
- Too low = cuts off beginning of words
- Test and adjust!

### **Network:**
- Use wired internet (not WiFi) if possible
- Zello uses ~20 kbps (very low bandwidth)
- Most connections work fine

### **Zello Channels:**
- Public channels: Anyone can join
- Private channels: Need invitation
- Create your own for testing!

---

## 📱 **Zello Channel Setup**

### **Create Your Own Channel:**

1. **Go to** https://zello.com (web browser)
2. **Login** to your account
3. **Click** "Channels"
4. **Create Channel:**
   - Name: "My Repeater Network"
   - Type: Public or Private
   - Description: "Ham/GMRS repeater on Zello"
5. **Join** the channel in Zello Desktop
6. **Share** channel name with others!

---

## 🎯 **Use Cases**

### **Extend Repeater Coverage:**
```
Local Area (RF) + Internet (Zello) = Worldwide!

Example:
→ Local hams use RF
→ Traveling hams use Zello app
→ Everyone in same conversation
→ Net participants from anywhere
```

### **GMRS Family Network:**
```
Family stays connected beyond RF range!

Example:
→ Dad at work (GMRS radio)
→ Mom at home (GMRS radio + repeater)
→ Kids at school (Zello app on phones)
→ All can talk together!
```

### **Emergency Backup:**
```
RF down? Internet still works!

Example:
→ Primary: Amateur radio repeater
→ Backup: Zello for connectivity loss
→ Non-hams can monitor via Zello
→ Redundant communications
```

---

## ⚠️ **Legal Considerations**

### **FCC Part 97 (Ham Radio):**
- Phone patches generally allowed
- Must identify with callsign
- Announce Zello connection during station ID
- Example: "W1ABC repeater with Zello gateway"

### **GMRS:**
- Check FCC Part 95 for current rules
- Phone patch rules may vary
- Use responsibly
- Consult regulations

### **Privacy:**
- Zello conversations may be recorded
- Anyone can join public channels
- Follow Zello Terms of Service
- No expectation of privacy

---

## 🚀 **Quick Start Summary**

1. **Install** VB-Audio Cable (restart PC)
2. **Install** Zello Desktop (older version recommended)
3. **Configure Zello:**
   - Microphone: CABLE Output
   - Enable VOX
   - Disable TLS if needed
4. **Configure Soft Repeater Box:**
   - Output: CABLE Input
5. **Test:** Key radio, should transmit to Zello!

**Time:** 15-20 minutes  
**Cost:** FREE  
**Difficulty:** Easy  

---

## 📞 **Need Help?**

**Email:** host@nhscan.com  
**GitHub:** Issues tab for bugs/features

---

## 🔗 **Related Resources**

- **VB-Audio Cable:** https://vb-audio.com/Cable/
- **VoiceMeeter Banana:** https://vb-audio.com/Voicemeeter/banana.htm
- **Zello Website:** https://zello.com
- **Zello Support:** https://support.zello.com

---

**This method WORKS and is actively used by many repeater operators!**

**73!** 📻📱

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Author:** NHscan
