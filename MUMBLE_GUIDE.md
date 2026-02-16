# 🎤 Mumble Integration Guide

## **Link Repeaters Using Mumble VOIP**

Mumble is a **FREE**, low-latency VOIP solution perfect for linking repeaters - works for both HAM and GMRS!

---

## 🎯 **What is Mumble?**

**Mumble** is an open-source VOIP application designed for low latency:

```
✅ FREE & Open Source
✅ VERY low latency (<50ms typical)
✅ Self-hosted OR cloud hosted
✅ Excellent audio quality
✅ No license required (works for GMRS!)
✅ Cross-platform (Windows/Linux/Mac)
✅ Easy setup
✅ Privacy (you control the server)
```

**Website:** https://www.mumble.info/

---

## 🔌 **Why Mumble for Repeater Linking?**

### **vs AllStarLink:**
```
AllStarLink:
✅ Ham-specific features
✅ Huge existing network
❌ Ham license required
❌ More complex setup

Mumble:
✅ Works for GMRS too!
✅ Simpler setup
✅ Lower latency
✅ You control everything
❌ No existing network (you build your own)
```

### **Perfect For:**
- GMRS repeater networks
- Private ham networks
- Family/business communications
- Learning/experimentation
- Emergency backup systems

---

## 📋 **Setup Methods**

### **Method 1: Audio Routing** (Easiest - 15 min)
Route audio between Mumble client and Soft Repeater Box

### **Method 2: Cloud Server** (Recommended - 1 hour)
Set up Mumble server in cloud, connect multiple repeaters

### **Method 3: Self-Hosted** (Advanced - 2 hours)
Run Mumble server on your own computer/server

---

## 🚀 **Method 1: Audio Routing** (QUICK START)

Connect one repeater to Mumble for testing or single-site use.

### **What You Need:**
- Mumble client (free download)
- VB-Audio Virtual Cable
- Access to a Mumble server (or create one)

---

### **Step 1: Install Mumble Client**

1. **Download:** https://www.mumble.info/downloads/
2. **Install** for your OS
3. **Run** Mumble
4. **Complete** audio wizard (first time only)

---

### **Step 2: Connect to Mumble Server**

#### **Option A: Use Public Test Server**
```
Server: mumble.info
Port: 64738
Username: Your_Callsign
```

#### **Option B: Create Your Own** (See Method 2)

**Connect:**
1. Click "Server" → "Connect"
2. Click "Add New..."
3. Enter server info
4. Click "Connect"

---

### **Step 3: Configure Audio Routing**

**Install VB-Audio Cable** (if not already installed):
- Download: https://vb-audio.com/Cable/
- Install and restart

**Configure Mumble:**
1. Click **Configure** → **Settings**
2. Go to **Audio Input**:
   ```
   Device: CABLE Output (VB-Audio Virtual Cable)
   ```
3. Go to **Audio Output**:
   ```
   Device: Your speakers/headphones
   ```
4. **Transmit Method:** 
   - Select "Voice Activity" (like VOX)
   - Adjust threshold (start around 50%)
5. Click **OK**

**Configure Soft Repeater Box:**
1. Go to **Audio Devices** tab
2. Set:
   ```
   Input Device:  Your radio input
   Output Device: CABLE Input (VB-Audio Virtual Cable)
   ```

---

### **Step 4: Test!**

**Test Radio → Mumble:**
1. Key up your radio
2. Talk normally
3. Watch Mumble (should show your username talking)
4. Ask someone on Mumble to confirm they hear you

**Test Mumble → Radio:**
1. Have someone talk on Mumble
2. You should hear them through your speakers
   (Or through radio if using two-way routing)

---

## ☁️ **Method 2: Cloud Mumble Server** (RECOMMENDED)

Set up your own Mumble server in the cloud to link multiple repeaters.

### **Why Cloud Server?**
- ✅ Always online (24/7)
- ✅ No port forwarding needed
- ✅ Fast connection
- ✅ Multiple repeaters can connect
- ✅ Very cheap ($5-10/month)

---

### **Option A: Digital Ocean** (~$6/month)

#### **Step 1: Create Droplet**

1. **Sign up:** https://www.digitalocean.com/
2. **Create Droplet:**
   - Choose: **Ubuntu 22.04 LTS**
   - Plan: **Basic** ($6/month)
   - CPU: **Regular, 1GB RAM**
   - Datacenter: Choose closest to you
   - Authentication: **SSH key** or **password**
   - Hostname: `mumble-server`

3. **Create Droplet** (wait 1 minute)

#### **Step 2: Install Mumble Server**

**SSH into server:**
```bash
ssh root@YOUR_DROPLET_IP
```

**Update system:**
```bash
apt update && apt upgrade -y
```

**Install Mumble Server (Murmur):**
```bash
apt install mumble-server -y
```

**Configure:**
```bash
dpkg-reconfigure mumble-server
```

Answer questions:
```
Autostart: YES
High priority: NO
SuperUser password: [choose a strong password]
```

**Edit config for external access:**
```bash
nano /etc/mumble-server.ini
```

Find and set:
```ini
bandwidth=130000        # Good quality
users=100              # Max users
serverpassword=        # Leave blank or set password
registerName=My Repeater Network
port=64738            # Default port
```

Save: `Ctrl+X`, `Y`, `Enter`

**Restart Mumble:**
```bash
systemctl restart mumble-server
```

**Check status:**
```bash
systemctl status mumble-server
```

Should show "active (running)" in green!

#### **Step 3: Configure Firewall**

```bash
ufw allow 64738
ufw allow 22
ufw enable
```

#### **Step 4: Connect Your Repeaters**

On each repeater's computer:

1. **Open Mumble client**
2. **Add server:**
   ```
   Label: My Repeater Network
   Address: YOUR_DROPLET_IP
   Port: 64738
   Username: W1ABC-Repeater-1 (use descriptive name)
   ```
3. **Connect!**

All repeaters connected to same server = linked network!

---

### **Option B: Free Oracle Cloud** (FREE Forever!)

Oracle Cloud offers free tier with 2 VMs forever!

1. **Sign up:** https://www.oracle.com/cloud/free/
2. **Create VM Instance:**
   - Shape: VM.Standard.E2.1.Micro (free tier)
   - OS: Ubuntu 22.04
3. **Follow same installation steps** as Digital Ocean above
4. **Configure firewall** in Oracle console + UFW

**Cost:** FREE! ✅

---

## 🏠 **Method 3: Self-Hosted Server** (Advanced)

Run Mumble server on your own computer/Raspberry Pi.

### **Requirements:**
- Computer that's always on
- Static IP or Dynamic DNS
- Port forwarding on router
- Basic Linux knowledge (for Pi)

---

### **Option A: Windows Server**

1. **Download Mumble Server:** 
   - https://www.mumble.info/downloads/
   - Choose "Server" version

2. **Install:**
   - Run installer
   - Choose strong SuperUser password

3. **Configure:**
   - Located in: `C:\Program Files\Mumble\murmur.ini`
   - Edit as needed (ports, passwords, etc.)

4. **Port Forward:**
   - Router settings
   - Forward port 64738 (TCP+UDP) to server IP

5. **Connect:**
   - Use your public IP or hostname
   - Connect from Mumble clients

---

### **Option B: Raspberry Pi Server**

Perfect for low-power, always-on server!

**Hardware Needed:**
- Raspberry Pi 3/4
- MicroSD card
- Power supply
- Network connection

**Install:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Mumble Server
sudo apt install mumble-server -y

# Configure
sudo dpkg-reconfigure mumble-server

# Start on boot
sudo systemctl enable mumble-server

# Start now
sudo systemctl start mumble-server
```

**Port Forward:**
- Your router → Port 64738 → Pi's local IP

**Dynamic DNS** (if no static IP):
- Use No-IP.com or DynDNS
- Install updater on Pi
- Use hostname instead of IP

---

## 🔄 **Two-Way Audio Setup**

For Mumble audio to play through radio (not just speakers):

### **Using VoiceMeeter Banana:**

1. **Install VoiceMeeter Banana**
   - Download: https://vb-audio.com/Voicemeeter/banana.htm

2. **Configure Soft Repeater Box:**
   ```
   Output: VoiceMeeter Input
   ```

3. **Configure Mumble:**
   ```
   Input: VoiceMeeter Output
   Output: VoiceMeeter Aux Input
   ```

4. **In VoiceMeeter:**
   - Route inputs to outputs
   - Mix radio and Mumble audio
   - Send to radio transmitter

**Audio Flow:**
```
Radio Mic → Repeater → VoiceMeeter → Mumble → Network
Radio Speaker ← Repeater ← VoiceMeeter ← Mumble ← Network
```

---

## 🎛️ **Mumble Features**

### **Channels:**
Create channels for organization:
```
📁 My Repeater Network
  📁 Main Talk
  📁 Simplex
  📁 Emergency
  📁 Testing
```

Right-click server → Add Channel

### **User Management:**
- Create user accounts
- Set permissions
- Mute/deafen users
- Kick/ban if needed

### **Quality Settings:**
```
Audio Quality: 72 kbps (excellent)
             40 kbps (good, lower bandwidth)
             24 kbps (acceptable, very low bandwidth)

Latency: "Low" setting for best performance
```

### **Voice Activity:**
```
Like VOX for radio!

Threshold: Adjust so it triggers on voice, not noise
Gate: How long before it cuts off

Test with: Settings → Audio Input → preview
```

---

## 🎯 **Use Case Examples**

### **Example 1: Two GMRS Repeaters**

**Location A (Your house):**
```
GMRS Repeater → Soft Repeater Box → Mumble Client
                                        ↓
                                  Cloud Server
                                        ↑
GMRS Repeater ← Soft Repeater Box ← Mumble Client
```

**Location B (Friend's house):**
```
Same setup at remote location
```

**Result:**
- Users on Repeater A hear users on Repeater B
- Linked GMRS network across town/state/country!

---

### **Example 2: Ham Radio Emergency Network**

**Setup Multiple Nodes:**
```
Node 1: W1ABC repeater (Boston)
Node 2: W1XYZ repeater (Worcester)  
Node 3: W1QRP portable (Field)
```

**All connect to same Mumble server**

**Result:**
- Full coverage across region
- Emergency backup communications
- Coordinated response
- Can add more nodes anytime

---

### **Example 3: Family GMRS Network**

**Base Station:** Home with Mumble + Repeater
**Mobile Units:** 
- Dad's truck (GMRS radio)
- Mom's car (GMRS radio)
- Kids with Mumble app on phones

**Result:**
- Everyone stays in contact
- Beyond RF range via internet
- Mix of radio and smartphones

---

## 📱 **Mumble Mobile Apps**

### **Smartphones:**
- **Mumble** (iOS) - Official app
- **Mumble** (Android) - Official app

### **Usage:**
```
Download Mumble app
→ Add your server
→ Connect from anywhere
→ Talk through repeater network remotely!
```

Perfect for:
- Net control from anywhere
- Remote monitoring
- Emergency access
- Testing

---

## 🔧 **Troubleshooting**

### **Can't Connect to Server:**
```
Check:
✓ Server IP correct?
✓ Port 64738 open?
✓ Firewall allowing connection?
✓ Server actually running?

Fix:
→ Verify IP address
→ Check firewall: ufw status
→ Check server: systemctl status mumble-server
→ Try different port (edit murmur.ini)
```

### **No Audio from Mumble:**
```
Check:
✓ Mumble output device correct?
✓ Volume not muted?
✓ Voice Activity threshold too high?
✓ Other users actually talking?

Fix:
→ Settings → Audio Output → test
→ Check Windows sound mixer
→ Lower Voice Activity threshold
→ Check preview in Audio Input settings
```

### **Mumble Can't Hear You:**
```
Check:
✓ Soft Repeater Box output = CABLE Input?
✓ Mumble input = CABLE Output?
✓ Voice Activity enabled?
✓ Not muted in Mumble?

Fix:
→ Increase Repeater output gain
→ Lower Mumble VA threshold
→ Check preview (should show activity)
→ Ensure not muted (red icon)
```

### **High Latency:**
```
Check:
✓ Internet connection speed?
✓ Server location far away?
✓ Other network activity?
✓ Audio quality set too high?

Fix:
→ Use wired connection
→ Choose closer server
→ Lower audio quality (40 kbps)
→ Check Settings → Network
```

### **Echo/Feedback:**
```
Cause:
→ Audio loop (Mumble hearing itself)

Fix:
→ Use different audio devices
→ Enable Feedback Protection in Soft Repeater Box
→ Increase Voice Activity threshold
→ Check routing (no loops!)
```

---

## 💡 **Pro Tips**

### **Server Management:**
```
✅ Regular backups of murmur.db (user database)
✅ Monitor server resources
✅ Keep software updated
✅ Set up monitoring (uptime alerts)
```

### **Audio Quality:**
```
✅ Start with 72 kbps, adjust if needed
✅ Lower to 40 kbps for mobile data
✅ Test different settings
✅ Balance quality vs bandwidth
```

### **Security:**
```
✅ Use strong SuperUser password
✅ Create user accounts (don't use guest)
✅ Set channel passwords if needed
✅ Regular server updates
✅ Firewall properly configured
```

### **Network Optimization:**
```
✅ Use wired connection for server
✅ Choose datacenter close to users
✅ Monitor ping times
✅ Use QoS on router if needed
```

---

## 📊 **Cost Comparison**

### **Method 1: Audio Routing**
```
Cost: FREE
Time: 15 minutes
Good for: Single site, testing
```

### **Method 2: Cloud Server**
```
Cost: $0-6/month
Time: 1 hour setup
Good for: Multiple sites, permanent
Best: Oracle free tier or Digital Ocean
```

### **Method 3: Self-Hosted**
```
Cost: $35-50 (Raspberry Pi) or FREE (existing PC)
Time: 2 hours setup
Good for: Privacy, learning, full control
```

---

## 🎓 **Learning Resources**

### **Official Documentation:**
- Mumble Wiki: https://wiki.mumble.info/
- GitHub: https://github.com/mumble-voip/mumble
- Forums: https://forums.mumble.info/

### **Video Tutorials:**
- YouTube: "Mumble server setup"
- YouTube: "Mumble for radio"

---

## 🚀 **Quick Start Summary**

**Fastest Method (15 min):**
1. Install Mumble client
2. Install VB-Audio Cable  
3. Connect to public Mumble server
4. Configure audio routing
5. Test!

**Best Long-Term (1 hour):**
1. Create free Oracle Cloud account
2. Deploy Ubuntu VM
3. Install Mumble server
4. Connect repeaters
5. Enjoy worldwide linking!

---

## 📞 **Need Help?**

**Mumble Community:** https://forums.mumble.info/  
**Email (this software):** host@nhscan.com  
**GitHub Issues:** For software bugs/features

---

## 🏆 **Success Story Example**

```
GMRS Family Network via Mumble:

Setup:
→ Base station: GMRS repeater + Mumble
→ Oracle Cloud free server
→ 4 mobile radios
→ 3 smartphones with Mumble app

Coverage:
→ RF: 15 mile radius
→ Via Mumble: Anywhere with internet!

Cost:
→ $0/month (Oracle free tier)
→ Setup time: 2 hours
→ Working perfectly for 6 months

Result:
→ Family stays in contact anywhere
→ No range limitations
→ Mix of radios and phones
→ Emergency backup communications
```

---

**Mumble: The flexible, free solution for linking repeaters!**

**Works for Ham AND GMRS!** 🎤📻

**73!**

---

**Version:** 1.0  
**Last Updated:** February 2026  
**Author:** NHscan  
**License:** MIT
