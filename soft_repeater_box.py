#!/usr/bin/env python3
"""
Soft Repeater Box v1.01
Ham Radio Repeater Controller Software

Created by: NHscan
Email: host@nhscan.com
GitHub: https://github.com/nhscan/soft-repeater-box
Donate: CashApp $NHlife
License: MIT

Features: VOX, PTT Control, DTMF Commands, Weather Integration, 
Recording Modes, Auto ID, Courtesy Tones, Debug Mode
"""

import pyaudio
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import queue
import time
import wave
import os
import sys
import json
from datetime import datetime, timedelta
from collections import deque
from enum import Enum
import serial
import serial.tools.list_ports
import pyttsx3
import io
import tempfile
import requests
import math
import uuid

class PTTMode(Enum):
    VOX = "VOX"
    USB = "USB"

class RecordingMode(Enum):
    MANUAL = "Manual"
    TIMED_REPLAY = "Timed Auto-Replay"
    CONTINUOUS_DELAY = "Continuous Delay Line"
    REPEATER = "Repeater Mode"

class WeatherService:
    """Fetches weather information from Weather.gov API (US only, no API key needed)"""
    def __init__(self):
        self.enabled = False
        self.zip_code = "03894"  # Default: Wolfeboro, NH
        self.latitude = None
        self.longitude = None
        self.last_weather = None
        self.last_update = 0
        self.update_interval = 1800  # 30 minutes
        self.user_agent = "HamRadioRepeater/1.0 (Python-requests)"
        self.use_manual_coords = False  # New: Skip ZIP lookup
        self.debug_mode = False  # Toggle verbose output
        
    def set_coordinates(self, lat, lon):
        """Manually set coordinates (bypass ZIP lookup)"""
        self.latitude = lat
        self.longitude = lon
        self.use_manual_coords = True
        print(f"📍 Manual coordinates set: {lat:.4f}, {lon:.4f}")
        
    def zip_to_coordinates(self, zip_code):
        """Convert ZIP code to lat/lon using Census.gov geocoding API"""
        if self.debug_mode:
            print(f"\n🔍 Looking up ZIP code: {zip_code}")
        try:
            url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
            params = {
                "address": zip_code,
                "benchmark": "2020",
                "format": "json"
            }
            if self.debug_mode:
                print(f"   Calling: {url}")
                print(f"   Params: {params}")
            
            response = requests.get(url, params=params, timeout=10)
            if self.debug_mode:
                print(f"   Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if self.debug_mode:
                    print(f"   Response data keys: {data.keys()}")
                
                if data.get("result", {}).get("addressMatches"):
                    matches = data["result"]["addressMatches"]
                    if self.debug_mode:
                        print(f"   Found {len(matches)} address match(es)")
                    coords = matches[0]["coordinates"]
                    self.latitude = coords["y"]
                    self.longitude = coords["x"]
                    print(f"✅ ZIP {zip_code} → Lat: {self.latitude:.4f}, Lon: {self.longitude:.4f}")
                    return True
                else:
                    print(f"❌ No matches found for ZIP: {zip_code}")
                    if self.debug_mode:
                        print(f"   Try a different ZIP code or use lat/lon directly")
                    return False
            else:
                print(f"❌ Geocoding API returned status {response.status_code}")
                if self.debug_mode:
                    print(f"   Response: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            print(f"❌ ZIP code lookup timed out - check internet connection")
            return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to geocoding service - check internet/firewall")
            return False
        except Exception as e:
            print(f"❌ ZIP code lookup failed: {type(e).__name__}: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            return False
    
    def fetch_weather(self):
        """Fetch current weather from Weather.gov"""
        if not self.enabled:
            if self.debug_mode:
                print("⚠️ Weather service not enabled")
            return None
            
        # Check if we need to update
        if time.time() - self.last_update < self.update_interval and self.last_weather:
            if self.debug_mode:
                print(f"ℹ️ Using cached weather (updated {int(time.time() - self.last_update)}s ago)")
            return self.last_weather
        
        # Get coordinates if we don't have them
        if not self.latitude or not self.longitude:
            if self.debug_mode:
                print("📍 Need to get coordinates first...")
            if not self.zip_to_coordinates(self.zip_code):
                print("❌ Cannot fetch weather without valid coordinates")
                return None
        
        if self.debug_mode:
            print(f"\n🌤️ Fetching weather for: {self.latitude:.4f}, {self.longitude:.4f}")
        
        try:
            # Get weather station URL
            headers = {
                "User-Agent": self.user_agent,
                "Accept": "application/geo+json"
            }
            points_url = f"https://api.weather.gov/points/{self.latitude:.4f},{self.longitude:.4f}"
            if self.debug_mode:
                print(f"   Step 1: Getting weather station...")
                print(f"   URL: {points_url}")
            
            points_response = requests.get(points_url, headers=headers, timeout=10)
            if self.debug_mode:
                print(f"   Response status: {points_response.status_code}")
            
            if points_response.status_code == 200:
                points_data = points_response.json()
                
                # Check for forecast URL
                if "properties" not in points_data:
                    print(f"❌ Invalid response from weather.gov")
                    if self.debug_mode:
                        print(f"   Response keys: {points_data.keys()}")
                    return None
                    
                if "forecastHourly" not in points_data["properties"]:
                    print(f"❌ No forecast URL in response")
                    if self.debug_mode:
                        print(f"   Available properties: {points_data['properties'].keys()}")
                    return None
                
                forecast_url = points_data["properties"]["forecastHourly"]
                if self.debug_mode:
                    print(f"   Forecast URL: {forecast_url}")
                
                # Get forecast
                if self.debug_mode:
                    print(f"   Step 2: Getting forecast data...")
                forecast_response = requests.get(forecast_url, headers=headers, timeout=10)
                if self.debug_mode:
                    print(f"   Response status: {forecast_response.status_code}")
                
                if forecast_response.status_code == 200:
                    forecast_data = forecast_response.json()
                    
                    if "properties" not in forecast_data or "periods" not in forecast_data["properties"]:
                        print(f"❌ Invalid forecast data structure")
                        if self.debug_mode:
                            print(f"   Keys: {forecast_data.keys()}")
                        return None
                    
                    periods = forecast_data["properties"]["periods"]
                    if not periods:
                        print(f"❌ No forecast periods available")
                        return None
                        
                    current = periods[0]
                    if self.debug_mode:
                        print(f"   Current period: {current.get('name', 'Unknown')}")
                    
                    # Parse weather data
                    weather = {
                        "temperature": current.get("temperature", 0),
                        "unit": current.get("temperatureUnit", "F"),
                        "conditions": current.get("shortForecast", "Unknown"),
                        "wind_speed": current.get("windSpeed", "Unknown"),
                        "wind_direction": current.get("windDirection", "Unknown"),
                        "timestamp": time.time()
                    }
                    
                    self.last_weather = weather
                    self.last_update = time.time()
                    print(f"✅ Weather updated: {weather['temperature']}°{weather['unit']}, {weather['conditions']}")
                    return weather
                else:
                    print(f"❌ Forecast request failed with status {forecast_response.status_code}")
                    print(f"   Response: {forecast_response.text[:200]}")
                    return None
            else:
                print(f"❌ Points request failed with status {points_response.status_code}")
                print(f"   Response: {points_response.text[:200]}")
                
                if points_response.status_code == 404:
                    print(f"   This location may be outside the US")
                    print(f"   Weather.gov only covers United States")
                elif points_response.status_code == 500:
                    print(f"   Weather.gov server error - try again later")
                    
                return None
                    
        except requests.exceptions.Timeout:
            print(f"❌ Weather request timed out - check internet connection")
            return None
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to weather.gov - check internet/firewall")
            return None
        except Exception as e:
            print(f"❌ Weather fetch failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_weather_announcement(self):
        """Generate weather announcement text"""
        weather = self.fetch_weather()
        if not weather:
            return "Weather information unavailable"
        
        text = f"Current weather: {weather['temperature']} degrees {weather['unit']}, "
        text += f"{weather['conditions']}, "
        text += f"wind {weather['wind_speed']} from the {weather['wind_direction']}"
        return text
    
    def get_temperature_only(self):
        """Get just temperature for ID"""
        weather = self.fetch_weather()
        if not weather:
            return ""
        return f"temperature {weather['temperature']} degrees"

class DTMFDetector:
    """Detects DTMF tones in audio using Goertzel algorithm"""
    
    # DTMF frequency pairs
    DTMF_FREQS = {
        '1': (697, 1209), '2': (697, 1336), '3': (697, 1477), 'A': (697, 1633),
        '4': (770, 1209), '5': (770, 1336), '6': (770, 1477), 'B': (770, 1633),
        '7': (852, 1209), '8': (852, 1336), '9': (852, 1477), 'C': (852, 1633),
        '*': (941, 1209), '0': (941, 1336), '#': (941, 1477), 'D': (941, 1633)
    }
    
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.enabled = False
        self.buffer = deque(maxlen=int(sample_rate * 0.1))  # 100ms buffer
        self.last_tone = None
        self.last_tone_time = 0
        self.tone_timeout = 0.5  # seconds
        self.digit_buffer = ""
        self.digit_timeout = 5.0  # 5 seconds between digits (was 3.0) - more time to dial
        self.last_digit_time = 0
        self.min_tone_duration = 0.08  # 80ms minimum (was 50ms) - reduces false positives
        self.detection_threshold = 0.15  # Higher threshold = less sensitive = fewer false positives
        self.debug_mode = False  # Toggle verbose output
        
    def goertzel(self, samples, freq):
        """Goertzel algorithm for detecting specific frequency"""
        n = len(samples)
        k = int(0.5 + (n * freq / self.sample_rate))
        omega = (2.0 * math.pi * k) / n
        coeff = 2.0 * math.cos(omega)
        
        q0 = 0.0
        q1 = 0.0
        q2 = 0.0
        
        for sample in samples:
            q0 = coeff * q1 - q2 + sample
            q2 = q1
            q1 = q0
        
        magnitude = math.sqrt(q1 * q1 + q2 * q2 - q1 * q2 * coeff)
        return magnitude
    
    def detect_tone(self, audio_chunk):
        """Detect DTMF tone in audio chunk"""
        if not self.enabled:
            return None
        
        # Add to buffer
        samples = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        self.buffer.extend(samples)
        
        # Need enough samples
        if len(self.buffer) < self.sample_rate * self.min_tone_duration:
            return None
        
        # Get samples for analysis
        analyze_samples = list(self.buffer)[-int(self.sample_rate * 0.05):]  # Last 50ms
        
        # Detect all frequency pairs
        best_tone = None
        best_magnitude = 0
        
        for digit, (low_freq, high_freq) in self.DTMF_FREQS.items():
            low_mag = self.goertzel(analyze_samples, low_freq)
            high_mag = self.goertzel(analyze_samples, high_freq)
            
            # Both frequencies must be present
            magnitude = min(low_mag, high_mag)
            
            if magnitude > self.detection_threshold and magnitude > best_magnitude:
                best_magnitude = magnitude
                best_tone = digit
        
        # Debounce - same tone must be consistent
        current_time = time.time()
        if best_tone:
            if best_tone == self.last_tone:
                # Same tone, check if we should register it
                if current_time - self.last_tone_time > self.min_tone_duration:
                    return best_tone
            else:
                # New tone detected
                self.last_tone = best_tone
                self.last_tone_time = current_time
        else:
            # No tone - reset after timeout
            if current_time - self.last_tone_time > self.tone_timeout:
                self.last_tone = None
        
        return None
    
    def add_digit(self, digit):
        """Add digit to buffer and check for timeout"""
        current_time = time.time()
        
        # Check for timeout (clear buffer if too much time passed)
        if self.digit_buffer and current_time - self.last_digit_time > self.digit_timeout:
            if self.debug_mode:
                print(f"⏰ DTMF timeout - clearing buffer: {self.digit_buffer}")
            self.digit_buffer = ""
        
        # Handle special keys
        if digit == '*':
            # * = Clear buffer
            if self.digit_buffer:
                print(f"❌ DTMF buffer cleared (was: {self.digit_buffer})")
                self.digit_buffer = ""
            return ""
        
        elif digit == '#':
            # # = Submit current buffer as command (even if less than 4 digits)
            if self.digit_buffer:
                print(f"✅ DTMF submit: {self.digit_buffer}")
                return self.digit_buffer
            return ""
        
        # Only accept numeric digits 0-9
        elif digit in '0123456789':
            # Time-based debouncing: Allow duplicate digit if enough time has passed
            # This allows commands like "0001" where you press 0 multiple times
            time_since_last = current_time - self.last_digit_time if self.digit_buffer else 999
            is_duplicate = self.digit_buffer and self.digit_buffer[-1] == digit
            debounce_time = 0.15  # 150ms - if more time passed, it's a new press, not a hold
            
            # Add digit if:
            # 1. Buffer is empty (first digit), OR
            # 2. Different digit than last, OR  
            # 3. Same digit but enough time passed (new press, not holding)
            if not is_duplicate or time_since_last > debounce_time:
                self.digit_buffer += digit
                self.last_digit_time = current_time
                # Always show when command is ready, only show progress in debug mode
                if len(self.digit_buffer) >= 4:
                    print(f"📟 DTMF: {self.digit_buffer} ▶️ READY")
                elif self.debug_mode:
                    print(f"📟 DTMF: {self.digit_buffer}")
            else:
                # Duplicate within debounce time - ignore (key still held)
                pass
            return self.digit_buffer
        
        else:
            # Ignore A, B, C, D keys
            if self.debug_mode:
                print(f"⚠️ Ignoring DTMF key: {digit}")
            return self.digit_buffer
    
    def get_command(self):
        """Get complete DTMF command if buffer has one"""
        # Check for 4-digit command (e.g., "0001", "0002")
        if len(self.digit_buffer) >= 4:
            command = self.digit_buffer[:4]
            self.digit_buffer = self.digit_buffer[4:]  # Remove used digits
            print(f"🎯 Extracted command: {command}")
            if self.digit_buffer:
                print(f"📟 Buffer now: {self.digit_buffer}")
            return command
        return None
    
    def reset(self):
        """Reset detector state"""
        self.digit_buffer = ""
        self.last_tone = None
        self.last_digit_time = 0

class ConfigManager:
    """Manages saving and loading configuration"""
    def __init__(self, config_file="repeater_config.json"):
        self.config_file = config_file
        self.default_config = {
            # Repeater settings
            "callsign": "WRKC123",
            "id_interval": 10.0,  # minutes
            "courtesy_tone_enabled": True,
            "courtesy_tone_freq": 1000,
            "courtesy_tone_volume": 0.5,  # 0.0 to 1.0
            "courtesy_tone_duration": 0.5,  # seconds
            "timeout_duration": 180,
            "ptt_pre_delay": 1.0,
            "tail_silence": 0.5,
            "auto_id_enabled": True,  # Enable/disable automatic ID
            
            # Audio levels
            "input_gain": 1.0,  # 0.0 to 2.0
            "output_gain": 1.0,  # 0.0 to 2.0
            
            # VOX settings
            "vox_enabled": False,
            "vox_threshold": 5.0,
            "vox_attack": 0.1,
            "vox_release": 0.5,
            
            # Feedback protection
            "feedback_protection_enabled": True,
            "feedback_holdoff_time": 1.5,
            
            # PTT settings
            "ptt_mode": "VOX",
            "serial_port": "",
            
            # Mode settings
            "recording_mode": "Repeater Mode",
            "max_record_time": 30.0,
            "delay_time": 2.0,
            "ptt_prekey_time": 0.5,  # PTT pre-key for delay mode
        }
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"Configuration loaded from {self.config_file}")
                return config
            else:
                print("No config file found, using defaults")
                return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
            return self.default_config.copy()
    
    def save_config(self, config):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

class PTTController:
    """Handles PTT control via serial/USB GPIO"""
    def __init__(self):
        self.serial_port = None
        self.port_name = None
        self.is_connected = False
        self.ptt_active = False
        self.relay_type = "RTS"  # "RTS" or "COMMAND"
        
    def set_relay_type(self, relay_type):
        """Set relay type: 'RTS' for RTS/DTR control, 'COMMAND' for byte commands"""
        self.relay_type = relay_type
        print(f"Relay type set to: {relay_type}")
        
    def connect(self, port_name, baudrate=9600):
        """Connect to serial port"""
        try:
            if self.serial_port:
                self.disconnect()
                
            self.serial_port = serial.Serial(port_name, baudrate, timeout=1)
            self.port_name = port_name
            self.is_connected = True
            print(f"Connected to {port_name} at {baudrate} baud")
            return True
        except Exception as e:
            print(f"Failed to connect to {port_name}: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self):
        """Disconnect from serial port"""
        if self.serial_port:
            self.ptt_off()
            self.serial_port.close()
            self.serial_port = None
            self.is_connected = False
            print("Disconnected from serial port")
    
    def ptt_on(self):
        """Activate PTT"""
        if self.is_connected and self.serial_port:
            try:
                if self.relay_type == "COMMAND":
                    # Command-based relay (x003qjjrql and similar Chinese modules)
                    # Try common relay ON commands
                    commands = [
                        bytes([0xA0, 0x01, 0x01, 0xA2]),  # Common format 1
                        bytes([0xFF, 0x01, 0x01]),         # Common format 2
                        bytes([0x01]),                     # Simple single byte
                    ]
                    for cmd in commands:
                        self.serial_port.write(cmd)
                        print(f"🔴 PTT ON - Sent command: {cmd.hex()}")
                else:
                    # RTS/DTR control
                    self.serial_port.setRTS(True)
                    self.serial_port.setDTR(True)
                    print("🔴 PTT ON - RTS/DTR set HIGH")
                    
                self.ptt_active = True
            except Exception as e:
                print(f"PTT ON failed: {e}")
    
    def ptt_off(self):
        """Deactivate PTT"""
        if self.is_connected and self.serial_port:
            try:
                if self.relay_type == "COMMAND":
                    # Command-based relay OFF
                    commands = [
                        bytes([0xA0, 0x01, 0x00, 0xA1]),  # Common format 1
                        bytes([0xFF, 0x01, 0x00]),         # Common format 2
                        bytes([0x00]),                     # Simple single byte
                    ]
                    for cmd in commands:
                        self.serial_port.write(cmd)
                        print(f"⚪ PTT OFF - Sent command: {cmd.hex()}")
                else:
                    # RTS/DTR control
                    self.serial_port.setRTS(False)
                    self.serial_port.setDTR(False)
                    print("⚪ PTT OFF - RTS/DTR set LOW")
                    
                self.ptt_active = False
            except Exception as e:
                print(f"PTT OFF failed: {e}")
    
    @staticmethod
    def get_available_ports():
        """Get list of available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

class VOXDetector:
    """Voice activity detection"""
    def __init__(self, threshold=5.0, attack_time=0.1, release_time=0.5):
        self.threshold = threshold
        self.attack_time = attack_time
        self.release_time = release_time
        self.sample_rate = 44100
        self.attack_samples = int(self.sample_rate * attack_time / 1024)
        self.release_samples = int(self.sample_rate * release_time / 1024)
        self.level_history = deque(maxlen=max(self.attack_samples, self.release_samples))
        self.is_active = False
        self.consecutive_high = 0
        self.consecutive_low = 0
    
    def process(self, audio_level):
        """Process audio level and return VOX state"""
        self.level_history.append(audio_level)
        
        if audio_level > self.threshold:
            self.consecutive_high += 1
            self.consecutive_low = 0
            
            if self.consecutive_high >= self.attack_samples:
                self.is_active = True
        else:
            self.consecutive_low += 1
            self.consecutive_high = 0
            
            if self.consecutive_low >= self.release_samples:
                self.is_active = False
        
        return self.is_active
    
    def reset(self):
        """Reset VOX state"""
        self.is_active = False
        self.consecutive_high = 0
        self.consecutive_low = 0
       
class TTSGenerator:
    """Text-to-speech generator for announcements.

    NOTE:
    pyttsx3 can occasionally deadlock/hang after the first run on some systems when
    a single engine instance is reused from a background thread. To make repeated
    announcements reliable (and allow clean stop/start), we create a fresh engine
    per announcement under a lock and write to a unique temp WAV each time.
    """
    def __init__(self, sample_rate=44100, rate=150, volume=0.9):
        self.sample_rate = sample_rate
        self.rate = rate
        self.volume = volume
        self._lock = threading.Lock()

    def _new_engine(self):
        engine = pyttsx3.init()
        engine.setProperty('rate', self.rate)
        engine.setProperty('volume', self.volume)
        return engine

    def generate_announcement(self, text, pre_delay=1.0):
        """Generate audio data from text with optional pre-delay silence."""
        temp_path = None
        try:
            # Use a unique temp file every time (avoids Windows file-lock edge cases)
            with tempfile.NamedTemporaryFile(prefix="parrot_tts_", suffix=".wav", delete=False) as tf:
                temp_path = tf.name

            print(f"TTS: Generating speech for: '{text}'")

            # Serialize TTS access: pyttsx3 is not reliably thread-safe.
            with self._lock:
                engine = self._new_engine()
                try:
                    engine.save_to_file(text, temp_path)
                    engine.runAndWait()
                finally:
                    try:
                        engine.stop()
                    except Exception:
                        pass

            # Verify file exists and has content
            if not temp_path or not os.path.exists(temp_path) or os.path.getsize(temp_path) == 0:
                print("ERROR: TTS did not create a valid audio file!")
                return np.zeros(int(self.sample_rate * 2), dtype=np.int16)

            # Read WAV and convert to int16 mono
            with wave.open(temp_path, 'rb') as wf:
                print(f"TTS: WAV file - Rate: {wf.getframerate()}, Channels: {wf.getnchannels()}, Frames: {wf.getnframes()}")

                frames = wf.readframes(wf.getnframes())
                if not frames:
                    print("ERROR: TTS generated empty audio!")
                    return np.zeros(int(self.sample_rate * 2), dtype=np.int16)

                audio_data = np.frombuffer(frames, dtype=np.int16)

                # If multi-channel, downmix by taking one channel (pyttsx3 usually outputs mono)
                if wf.getnchannels() > 1:
                    audio_data = audio_data[::wf.getnchannels()]

                # Resample if needed
                original_rate = wf.getframerate()
                if original_rate != self.sample_rate and original_rate > 0:
                    print(f"TTS: Resampling from {original_rate} to {self.sample_rate}")
                    duration = len(audio_data) / original_rate
                    new_length = max(1, int(duration * self.sample_rate))
                    audio_data = np.interp(
                        np.linspace(0, len(audio_data), new_length, endpoint=False),
                        np.arange(len(audio_data)),
                        audio_data
                    ).astype(np.int16)

                # Boost volume by 50% to ensure it's audible
                audio_data = np.clip(audio_data.astype(np.float32) * 1.5, -32768, 32767).astype(np.int16)
                print(f"TTS: Audio data length: {len(audio_data)} samples, peak: {np.abs(audio_data).max()}")

            # Add pre-delay silence for PTT to key up
            if pre_delay and pre_delay > 0:
                pre_silence_samples = int(self.sample_rate * float(pre_delay))
                if pre_silence_samples > 0:
                    audio_data = np.concatenate([np.zeros(pre_silence_samples, dtype=np.int16), audio_data])
                    print(f"TTS: Added {pre_delay}s pre-delay, total length: {len(audio_data)} samples ({len(audio_data)/self.sample_rate:.2f}s)")

            print("TTS: Generation complete!")
            return audio_data

        except Exception as e:
            print(f"TTS generation failed: {e}")
            import traceback
            traceback.print_exc()
            return np.zeros(int(self.sample_rate * 2), dtype=np.int16)
        finally:
            if temp_path:
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    def set_voice_properties(self, rate=150, volume=0.9):
        """Set TTS voice properties for future announcements."""
        self.rate = rate
        self.volume = volume


class RepeaterController:
    """Manages repeater-specific functions"""
    def __init__(self, callsign="WRKC123", id_interval=600):
        self.callsign = callsign
        self.id_interval = id_interval  # seconds (10 minutes default)
        self.last_id_time = time.time()
        self.last_activity_time = 0
        self.timeout_duration = 180  # 3 minutes max transmission
        self.tail_message = "73"  # End of transmission message
        self.enable_courtesy_tone = True
        self.enable_tail_message = False
        self.courtesy_tone_freq = 1000  # Hz
        self.courtesy_tone_duration = 0.5  # seconds (increased from 0.2 for better audibility)
        self.courtesy_tone_volume = 0.5  # 0.0 to 1.0 (50% default)
        self.tail_silence_duration = 0.5  # seconds of silence after TX to drop VOX
        self.auto_id_enabled = True  # Enable/disable automatic ID announcements
        
    def needs_id(self):
        """Check if station ID is needed"""
        elapsed = time.time() - self.last_id_time
        return elapsed >= self.id_interval
    
    def generate_id_announcement(self):
        """Generate station ID announcement text"""
        now = datetime.now()
        date_str = now.strftime("%B %d")
        time_str = now.strftime("%I:%M %p")
        
        announcement = f"{self.callsign} repeater. "
        announcement += f"The time is {time_str}. "
        announcement += f"Today's date is {date_str}."
        
        # Add weather if enabled (passed from parent)
        if hasattr(self, 'weather_service') and hasattr(self, 'include_weather'):
            if self.include_weather and self.weather_service.enabled:
                weather_text = self.weather_service.get_temperature_only()
                if weather_text:
                    announcement += f" {weather_text}."
        
        return announcement
    
    def mark_id_sent(self):
        """Mark that ID was just sent"""
        self.last_id_time = time.time()
    
    def mark_activity(self):
        """Mark recent activity"""
        self.last_activity_time = time.time()
    
    def is_timeout(self):
        """Check if transmission timeout exceeded"""
        if self.last_activity_time == 0:
            return False
        elapsed = time.time() - self.last_activity_time
        return elapsed >= self.timeout_duration
    
    def generate_courtesy_tone(self, sample_rate=44100):
        """Generate courtesy tone beep"""
        duration = self.courtesy_tone_duration
        t = np.linspace(0, duration, int(sample_rate * duration))
        tone = np.sin(2 * np.pi * self.courtesy_tone_freq * t)
        
        # Envelope to prevent clicks
        envelope = np.ones_like(tone)
        fade_samples = int(0.01 * sample_rate)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        tone = tone * envelope * self.courtesy_tone_volume  # Use configurable volume
        return (tone * 32767).astype(np.int16)
    
    def generate_prekey_beep(self, sample_rate=44100):
        """Generate a lead-in tone to wake radio VOX before speech.

        Many radio VOX circuits need a few hundred milliseconds to fully open.
        A longer lead-in tone greatly reduces clipped first syllables/words.
        """
        duration = 0.50  # 500ms lead-in (VOX wakeup)
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        # Use a higher tone that reliably triggers VOX without being too harsh
        tone = np.sin(2 * np.pi * 1500 * t)
        
        # Envelope to prevent clicks
        envelope = np.ones_like(tone)
        fade_samples = int(0.01 * sample_rate)
        envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
        envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
        
        tone = tone * envelope * 0.45  # Moderate volume to reliably trigger VOX
        return (tone * 32767).astype(np.int16)
    
    def generate_tail_silence(self, sample_rate=44100):
        """Generate tail silence to drop VOX"""
        duration = self.tail_silence_duration
        samples = int(sample_rate * duration)
        return np.zeros(samples, dtype=np.int16)

class ParrotBox:
    def __init__(self):
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.DELAY_SECONDS = 2.0
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False
        
        # Audio device selection
        self.input_device_index = None  # None = default device
        self.output_device_index = None  # None = default device
        
        # Recording mode
        self.recording_mode = RecordingMode.REPEATER
        self.max_record_time = 30.0
        
        # Buffer management
        self.buffer_size = int(self.RATE / self.CHUNK * self.DELAY_SECONDS)
        self.audio_buffer = deque(maxlen=self.buffer_size)
        
        # Recording storage
        self.recorded_audio = []
        self.is_recording = False
        self.is_playing_back = False
        self.record_start_time = 0
        self.playback_index = 0
        self.playback_audio = []  # separate playback buffer (keeps recordings clean)
        
        # Fill buffer with silence
        silence = np.zeros(self.CHUNK, dtype=np.int16)
        for _ in range(self.buffer_size):
            self.audio_buffer.append(silence.tobytes())
        
        # PTT Control
        self.ptt_controller = PTTController()
        self.ptt_mode = PTTMode.VOX
        
        # VOX
        self.vox = VOXDetector()
        self.vox_enabled = False
        
        # Repeater mode
        self.repeater = RepeaterController()
        self.tts = TTSGenerator(self.RATE)
        self.announcement_queue = queue.Queue()
        self.announcement_ready_queue = queue.Queue()  # Pre-generated announcements
        self.is_announcing = False
        self.announcement_audio = None
        self.announcement_index = 0
        self.pending_courtesy_tone = False
        self.courtesy_tone_audio = None
        self.courtesy_tone_index = 0
        self.pending_tail_silence = False
        self.tail_silence_audio = None
        self.tail_silence_index = 0
        self.ptt_pre_delay = 1.0  # 1 second PTT delay
        self.last_vox_state = False  # Track VOX state changes
        
        # Feedback protection
        self.feedback_protection_enabled = True
        self.feedback_holdoff_time = 1.5  # seconds to ignore input after output
        self.last_output_time = 0
        self.is_in_holdoff = False
        
        # VOX grace period - keep VOX off briefly after announcements to allow next to start
        self.vox_grace_period = 0.3  # 300ms grace period after announcements
        self.last_announcement_time = 0
        
        # Start TTS generation thread
        self.tts_thread = None
        self.tts_running = False
        
        # Audio levels
        self.input_level = 0
        self.output_level = 0
        
        # Audio gain controls (live volume adjustment)
        self.input_gain = 1.0  # 0.0 to 2.0
        self.output_gain = 1.0  # 0.0 to 2.0
        
        # Feedback protection
        self.feedback_protection_enabled = True
        self.feedback_holdoff_time = 1.0  # seconds to mute input after output
        self.last_output_time = 0
        self.is_in_holdoff = False
        
        # Continuous delay mode
        self.delay_has_audio = False  # Track if delay buffer has active audio
        self.delay_needs_prekey = False  # Track if we need to send pre-key beep
        self.delay_prekey_audio = None
        self.delay_prekey_index = 0
        self.ptt_prekey_time = 0.5  # Seconds to activate PTT before audio (adjustable)
        
        # Weather service
        self.weather = WeatherService()
        self.include_weather_in_id = False
        
        # DTMF detection and commands
        self.dtmf = DTMFDetector(self.RATE)
        self.dtmf_commands = {
            "0001": "weather",
            "0002": "time",
            "0003": "custom1",
            "0004": "custom2",
            "0005": "custom3",
            "0006": "custom4",
            "0007": "custom5",
            "0008": "custom6",
            "0009": "custom7",
            "0010": "custom8",
        }
        self.dtmf_messages = {
            "custom1": "Custom message 1",
            "custom2": "Custom message 2",
            "custom3": "Custom message 3",
            "custom4": "Custom message 4",
            "custom5": "Custom message 5",
            "custom6": "Custom message 6",
            "custom7": "Custom message 7",
            "custom8": "Custom message 8",
        }
        
        # Link weather service to repeater for ID announcements
        self.repeater.weather_service = self.weather
        self.repeater.include_weather = lambda: self.include_weather_in_id
        
        # Debug mode
        self.debug_mode = False  # Toggle verbose console output
        
        # Callbacks
        self.on_recording_complete = None
        self.on_vox_state_change = None
        self.on_repeater_state_change = None
    def _drain_queue(self, q):
        """Remove all items from a Queue without blocking."""
        try:
            while True:
                q.get_nowait()
        except queue.Empty:
            return

    def reset_runtime_state(self, clear_queues=True):
        """Reset transient runtime flags so announcements/ID can be sent repeatedly."""
        # Announcement/Tone state
        self.is_announcing = False
        self.announcement_audio = None
        self.announcement_index = 0

        self.pending_courtesy_tone = False
        self.courtesy_tone_audio = None
        self.courtesy_tone_index = 0

        self.pending_tail_silence = False
        self.tail_silence_audio = None
        self.tail_silence_index = 0

        # Feedback/VOX state
        self.last_vox_state = False
        self.vox.reset()
        self.last_output_time = 0
        self.is_in_holdoff = False
        self.last_announcement_time = 0

        # Mode recording state
        self.is_recording = False
        self.is_playing_back = False
        self.recorded_audio = []
        self.playback_index = 0
        self.record_start_time = 0
        self.playback_audio = []

        if clear_queues:
            self._drain_queue(self.announcement_queue)
            self._drain_queue(self.announcement_ready_queue)


    
    def start(self):
        """Start the parrot box"""
        if self.is_running:
            return

        # Ensure a clean state on every start (fixes 'ID/message only sends once' issue)
        self.reset_runtime_state(clear_queues=True)
            
        try:
            # List audio devices for debugging
            print("\n=== Audio Devices ===")
            for i in range(self.audio.get_device_count()):
                info = self.audio.get_device_info_by_index(i)
                if info['maxOutputChannels'] > 0:  # Only show output devices
                    print(f"Output Device {i}: {info['name']} (Rate: {info['defaultSampleRate']})")
            print("===================\n")
            
            print(f"Opening audio stream...")
            print(f"Format: {self.FORMAT}, Channels: {self.CHANNELS}, Rate: {self.RATE}, Chunk: {self.CHUNK}")
            
            # Prepare stream parameters
            stream_params = {
                'format': self.FORMAT,
                'channels': self.CHANNELS,
                'rate': self.RATE,
                'input': True,
                'output': True,
                'frames_per_buffer': self.CHUNK,
                'stream_callback': self.audio_callback
            }
            
            # Add device indices if specified
            use_input_device = self.input_device_index is not None
            use_output_device = self.output_device_index is not None
            
            if use_input_device:
                stream_params['input_device_index'] = self.input_device_index
                print(f"Using input device index: {self.input_device_index}")
            else:
                print("Using default input device")
                
            if use_output_device:
                stream_params['output_device_index'] = self.output_device_index
                print(f"Using output device index: {self.output_device_index}")
            else:
                print("Using default output device")
            
            # Try to open with selected devices
            try:
                self.stream = self.audio.open(**stream_params)
                print("✅ Audio stream opened successfully with selected devices")
            except OSError as e:
                if "Illegal combination" in str(e):
                    print(f"⚠️ ERROR: Selected devices are incompatible!")
                    print(f"⚠️ Input device {self.input_device_index} and output device {self.output_device_index} cannot be used together")
                    print(f"⚠️ This happens when devices are on different hardware")
                    print(f"⚠️ SOLUTION: Use VB-Audio Virtual Cable for BOTH input AND output!")
                    print(f"⚠️ Falling back to default devices...")
                    
                    # Try with default devices
                    stream_params = {
                        'format': self.FORMAT,
                        'channels': self.CHANNELS,
                        'rate': self.RATE,
                        'input': True,
                        'output': True,
                        'frames_per_buffer': self.CHUNK,
                        'stream_callback': self.audio_callback
                    }
                    try:
                        self.stream = self.audio.open(**stream_params)
                        print("✅ Audio stream opened with DEFAULT devices")
                        print("⚠️ Please select VIRTUAL CABLE devices (same hardware) in Audio Devices tab!")
                    except Exception as e2:
                        print(f"❌ Failed to open even default devices: {e2}")
                        raise
                else:
                    raise
            
            print("Audio stream opened successfully")
            
            self.is_running = True
            self.stream.start_stream()
            self.vox.reset()
            
            # Start TTS generation thread
            self.tts_running = True
            self.tts_thread = threading.Thread(target=self.tts_generation_loop, daemon=True)
            self.tts_thread.start()
            
            # Start ID timer thread for repeater mode
            if self.recording_mode == RecordingMode.REPEATER:
                self.id_timer_thread = threading.Thread(target=self.id_timer_loop, daemon=True)
                self.id_timer_thread.start()
            
            print(f"Parrot Box started - Mode: {self.recording_mode.value}")
            
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def stop(self):
        """Stop the parrot box"""
        if not self.is_running:
            return

        # Stop threads first
        self.is_running = False
        self.tts_running = False

        # Reset transient state so manual ID / messages work after stopping
        self.reset_runtime_state(clear_queues=True)
        
        if self.stream:
            try:
                # Give the stream a moment to finish current callback
                time.sleep(0.1)
                self.stream.stop_stream()
                self.stream.close()
            except Exception as e:
                print(f"Error stopping stream: {e}")
                # Force close if normal stop fails
                try:
                    self.stream.close()
                except:
                    pass
            finally:
                self.stream = None
        
        self.ptt_controller.ptt_off()
        print("Parrot Box stopped")
    
    def tts_generation_loop(self):
        """Background thread for generating TTS announcements"""
        while self.tts_running:
            try:
                # Wait for announcement request (with timeout so we can check tts_running)
                try:
                    text = self.announcement_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                print(f"🎤 Generating TTS in background: {text[:60]}...")
                # Generate the audio (this takes time, but it's in a background thread)
                audio_data = self.tts.generate_announcement(text, self.ptt_pre_delay)
                
                # Put the pre-generated audio in the ready queue
                self.announcement_ready_queue.put(audio_data)
                queue_size = self.announcement_ready_queue.qsize()
                print(f"✅ TTS generation complete! Ready to play (queue size: {queue_size})")
                print(f"   ⏳ Waiting for VOX to drop and system to be free...")
                
            except Exception as e:
                print(f"TTS generation thread error: {e}")
    
    def id_timer_loop(self):
        """Background thread for repeater ID timing"""
        while self.is_running:
            time.sleep(10)  # Check every 10 seconds
            
            if self.recording_mode == RecordingMode.REPEATER:
                if self.repeater.auto_id_enabled and self.repeater.needs_id() and not self.vox.is_active:
                    # Queue ID announcement
                    self.queue_announcement(self.repeater.generate_id_announcement())
                    self.repeater.mark_id_sent()
    
    def queue_announcement(self, text):
        """Queue a TTS announcement"""
        self.announcement_queue.put(text)
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Process audio input and output based on mode"""
        try:
            if status:
                print(f"Audio status: {status}")
            
            # Calculate input level
            input_array = np.frombuffer(in_data, dtype=np.int16)
            raw_peak = np.abs(input_array).max()
            raw_mean = np.abs(input_array).mean()
            self.input_level = raw_mean / 32768.0 * 100
            
            # Debug audio input periodically (every 2 seconds when there's audio)
            if self.debug_mode:
                if not hasattr(self, '_last_audio_debug'):
                    self._last_audio_debug = 0
                    self._audio_debug_counter = 0
                
                self._audio_debug_counter += 1
                if self._audio_debug_counter % 86 == 0:  # About every 2 seconds at 44100/1024
                    if raw_peak > 0:
                        print(f"🔊 AUDIO INPUT DEBUG:")
                        print(f"   Raw peak: {raw_peak} (max: 32767)")
                        print(f"   Raw mean: {raw_mean:.0f}")
                        print(f"   Input level: {self.input_level:.1f}%")
                        print(f"   Input gain: {self.input_gain*100:.0f}%")
                    else:
                        print(f"⚠️ NO AUDIO INPUT - Raw peak: 0, mean: 0")
            
            # Apply input gain
            if self.input_gain != 1.0:
                input_array = np.clip(input_array * self.input_gain, -32768, 32767).astype(np.int16)
                in_data = input_array.tobytes()
            
            # DTMF Detection (only in repeater mode when VOX is active)
            if self.recording_mode == RecordingMode.REPEATER and self.dtmf.enabled:
                digit = self.dtmf.detect_tone(in_data)
                if digit:
                    self.dtmf.add_digit(digit)
                    command = self.dtmf.get_command()
                    if command:
                        self.handle_dtmf_command(command)
            
            # VOX processing
            # Note: Repeater mode ALWAYS uses VOX to detect incoming audio
            # Other modes only use VOX if enabled by user
            should_use_vox = self.recording_mode == RecordingMode.REPEATER or self.vox_enabled
            
            if should_use_vox:
                # Check VOX grace period - keep VOX off briefly after announcements
                in_grace_period = False
                if self.last_announcement_time > 0:
                    grace_elapsed = time.time() - self.last_announcement_time
                    if grace_elapsed < self.vox_grace_period:
                        in_grace_period = True
                    elif grace_elapsed < self.vox_grace_period + 0.05:  # Just expired
                        print("✅ Grace period complete - VOX can trigger normally")
                        self.last_announcement_time = 0  # Reset
                
                # Determine if system is busy (don't process VOX when busy or in grace period)
                not_busy = (not self.is_announcing and 
                           not self.pending_courtesy_tone and
                           not self.pending_tail_silence and
                           not self.is_in_holdoff and
                           not in_grace_period)
                
                if not_busy:
                    # Only process VOX when not busy and not in grace period
                    vox_state = self.vox.process(self.input_level)
                else:
                    # Force VOX inactive when busy or in grace period
                    vox_state = False
                    was_active = self.vox.is_active
                    self.vox.is_active = False
                    if was_active and in_grace_period:
                        print("🔇 Forcing VOX inactive (grace period - preventing re-trigger)")
                    elif was_active:
                        print("🔇 Forcing VOX inactive (system busy)")
                
                # Detect VOX state changes for repeater mode
                if self.recording_mode == RecordingMode.REPEATER:
                    # Debug: Show VOX transitions
                    if not_busy and self.last_vox_state != vox_state:
                        if vox_state:
                            print(f"🎤 VOX ACTIVE (level: {self.input_level:.1f}%)")
                        else:
                            print(f"🔇 VOX INACTIVE (level: {self.input_level:.1f}%)")
                    
                    # VOX just dropped - add courtesy tone then tail silence (only when not busy)
                    if (self.last_vox_state and not vox_state and 
                        not self.pending_tail_silence and not_busy):
                        print("🎙️ VOX dropped after transmission")
                        
                        # Add courtesy tone if enabled
                        if self.repeater.enable_courtesy_tone:
                            self.pending_courtesy_tone = True
                            self.courtesy_tone_audio = self.repeater.generate_courtesy_tone(self.RATE)
                            self.courtesy_tone_index = 0
                            print(f"🔔 Queuing courtesy tone: {len(self.courtesy_tone_audio)} samples, volume: {self.repeater.courtesy_tone_volume*100:.0f}%")
                        else:
                            # No courtesy tone, go straight to tail silence
                            self.pending_tail_silence = True
                            self.tail_silence_audio = self.repeater.generate_tail_silence(self.RATE)
                            self.tail_silence_index = 0
                    
                    # Only update last_vox_state when not busy
                    if not_busy:
                        self.last_vox_state = vox_state
                    
                    if vox_state and not_busy:
                        self.repeater.mark_activity()
                
                # Handle mode-specific VOX behavior for other modes
                elif self.recording_mode == RecordingMode.CONTINUOUS_DELAY:
                    if vox_state and not self.is_recording:
                        self.start_recording()
                    elif not vox_state and self.is_recording:
                        self.stop_recording()
                
                elif self.recording_mode == RecordingMode.TIMED_REPLAY:
                    if vox_state and not self.is_recording and not self.is_playing_back:
                        self.start_recording()
            
            # Handle different recording modes
            output_data = self.process_audio_mode(in_data)
            
            # Calculate output level
            output_array = np.frombuffer(output_data, dtype=np.int16)
            self.output_level = np.abs(output_array).mean() / 32768.0 * 100
            
            # Apply output gain
            if self.output_gain != 1.0:
                output_array = np.clip(output_array * self.output_gain, -32768, 32767).astype(np.int16)
                output_data = output_array.tobytes()
            
            # PTT Control
            self.handle_ptt()
            
            return (output_data, pyaudio.paContinue)
            
        except Exception as e:
            print(f"ERROR in audio_callback: {e}")
            # Return silence to prevent crash
            silence = np.zeros(frame_count, dtype=np.int16).tobytes()
            return (silence, pyaudio.paContinue)
    
    def process_audio_mode(self, in_data):
        """Process audio based on current mode"""
        
        # Check for ready announcements (priority over everything except active transmission)
        # Allow announcements during holdoff, but not during active VOX or existing announcement
        can_start = not self.is_announcing and not self.pending_courtesy_tone and not self.vox.is_active
        queue_has_item = not self.announcement_ready_queue.empty()
        
        if can_start:
            try:
                # Non-blocking check for ready announcement
                audio_data = self.announcement_ready_queue.get_nowait()
                print("\n" + "🔊"*30)
                print("▶️  PLAYING DTMF RESPONSE NOW!")
                print("🔊"*30 + "\n")
                
                # Add pre-key beep to trigger radio VOX before actual audio
                prekey_beep = self.repeater.generate_prekey_beep(self.RATE)
                audio_data = np.concatenate([prekey_beep, audio_data])
                print(f"   Added {len(prekey_beep)/self.RATE:.3f}s pre-key beep to wake radio VOX")
                
                self.announcement_audio = audio_data
                self.announcement_index = 0
                self.is_announcing = True
                # Clear any pending tail silence when starting announcement
                self.pending_tail_silence = False
                # Exit holdoff state when starting announcement
                self.is_in_holdoff = False
                # Reset VOX state to prevent false drop detection after announcement
                self.last_vox_state = False
                # Force VOX inactive so announcements can start even with noise
                self.vox.is_active = False
            except queue.Empty:
                pass
        elif queue_has_item:
            # Debug: Why can't we start announcement?
            reasons = []
            if self.is_announcing:
                reasons.append("is_announcing")
            if self.pending_courtesy_tone:
                reasons.append("pending_courtesy_tone")
            if self.vox.is_active:
                reasons.append("vox.is_active")
            print(f"⏸️  Announcement ready but blocked by: {', '.join(reasons)}")
        
        # Play announcement if active
        if self.is_announcing:
            output = self.get_announcement_chunk()
            if output is not None:
                return output
            else:
                self.is_announcing = False
                print("Announcement playback complete")
                # Force VOX inactive to ensure next announcement can start
                self.vox.is_active = False
                self.last_vox_state = False
                # After announcement, send courtesy tone
                if self.recording_mode == RecordingMode.REPEATER and self.repeater.enable_courtesy_tone:
                    self.pending_courtesy_tone = True
                    self.courtesy_tone_audio = self.repeater.generate_courtesy_tone(self.RATE)
                    self.courtesy_tone_index = 0
                    print(f"🔔 Queuing courtesy tone: {len(self.courtesy_tone_audio)} samples, volume: {self.repeater.courtesy_tone_volume*100:.0f}%")
                else:
                    # No courtesy tone, go straight to tail silence
                    self.pending_tail_silence = True
                    self.tail_silence_audio = self.repeater.generate_tail_silence(self.RATE)
                    self.tail_silence_index = 0
        
        # Play courtesy tone if pending
        if self.pending_courtesy_tone:
            output = self.get_courtesy_tone_chunk()
            if output is not None:
                return output
            else:
                self.pending_courtesy_tone = False
                print("Courtesy tone complete")
                # Force VOX inactive to ensure next announcement can start
                self.vox.is_active = False
                self.last_vox_state = False
                # After courtesy tone, always add tail silence
                self.pending_tail_silence = True
                self.tail_silence_audio = self.repeater.generate_tail_silence(self.RATE)
                self.tail_silence_index = 0
        
        # Play tail silence if pending (ensures VOX drops)
        if self.pending_tail_silence:
            output = self.get_tail_silence_chunk()
            if output is not None:
                return output
            else:
                self.pending_tail_silence = False
                # Reset VOX state to prevent false drop detection
                self.last_vox_state = False
                print("Tail silence complete - VOX should drop now")
        
        # Normal mode processing
        if self.recording_mode == RecordingMode.REPEATER:
            # Repeater mode: pass-through with minimal delay
            return self.process_repeater_mode(in_data)
        
        elif self.recording_mode == RecordingMode.CONTINUOUS_DELAY:
            self.audio_buffer.append(in_data)
            if self.is_recording:
                self.recorded_audio.append(in_data)
            
            # Get delayed audio from buffer
            delayed_audio = self.audio_buffer[0]
            
            # PTT PRE-KEY: Look ahead in buffer to activate PTT BEFORE audio arrives
            # Calculate how many chunks ahead to look (pre-key time)
            prekey_chunks = int((self.ptt_prekey_time * self.RATE) / self.CHUNK)
            
            # Check audio level at look-ahead position (newer audio not yet output)
            lookahead_has_audio = False
            if len(self.audio_buffer) > prekey_chunks:
                # Look at audio that will be output in 'ptt_prekey_time' seconds
                lookahead_index = min(prekey_chunks, len(self.audio_buffer) - 1)
                lookahead_audio = self.audio_buffer[lookahead_index]
                lookahead_array = np.frombuffer(lookahead_audio, dtype=np.int16)
                lookahead_level = np.abs(lookahead_array).mean() / 32768.0 * 100
                lookahead_has_audio = lookahead_level > 0.5
            
            # Also check current output audio
            audio_array = np.frombuffer(delayed_audio, dtype=np.int16)
            audio_level = np.abs(audio_array).mean() / 32768.0 * 100
            current_has_audio = audio_level > 0.5
            
            # PTT should be active if EITHER:
            # 1. Audio is coming soon (look-ahead detected), OR
            # 2. Audio is currently playing (already transmitting)
            was_active = self.delay_has_audio
            self.delay_has_audio = lookahead_has_audio or current_has_audio
            
            # Debug PTT state changes with look-ahead info
            if self.delay_has_audio and not was_active:
                if lookahead_has_audio:
                    print(f"🔴 PTT PRE-KEY ACTIVE (Delay Line) - Audio coming in {self.ptt_prekey_time:.1f}s")
                    print(f"   Look-ahead level: {lookahead_level:.1f}%, Current level: {audio_level:.1f}%")
                else:
                    print(f"🔴 PTT ACTIVE (Delay Line) - Audio level: {audio_level:.1f}%")
            elif not self.delay_has_audio and was_active:
                print(f"⚪ PTT INACTIVE (Delay Line) - Audio level: {audio_level:.1f}%")
            
            return delayed_audio
        
        elif self.recording_mode == RecordingMode.TIMED_REPLAY:
            # Timed Auto-Replay:
            # Continuously loop: record for max_record_time, then play back, then record again.
            # This mode should work even if software VOX is disabled.
            if not self.is_recording and not self.is_playing_back:
                self.start_recording()

            if self.is_recording:
                self.recorded_audio.append(in_data)
                elapsed = time.time() - self.record_start_time
                if elapsed >= self.max_record_time:
                    self.stop_recording()
                    self.start_playback()
                return np.zeros(self.CHUNK, dtype=np.int16).tobytes()
            
            elif self.is_playing_back:
                if self.playback_index < len(self.playback_audio):
                    output = self.playback_audio[self.playback_index]
                    self.playback_index += 1
                    return output
                else:
                    self.stop_playback()
                    return np.zeros(self.CHUNK, dtype=np.int16).tobytes()
            else:
                return np.zeros(self.CHUNK, dtype=np.int16).tobytes()
        
        elif self.recording_mode == RecordingMode.MANUAL:
            if self.is_recording:
                self.recorded_audio.append(in_data)
                return np.zeros(self.CHUNK, dtype=np.int16).tobytes()
            elif self.is_playing_back:
                if self.playback_index < len(self.playback_audio):
                    output = self.playback_audio[self.playback_index]
                    self.playback_index += 1
                    return output
                else:
                    self.stop_playback()
                    return np.zeros(self.CHUNK, dtype=np.int16).tobytes()
            else:
                return np.zeros(self.CHUNK, dtype=np.int16).tobytes()
    
    def process_repeater_mode(self, in_data):
        """Process audio in repeater mode (pass-through)"""
        # Feedback protection: check if we're in holdoff period
        if self.feedback_protection_enabled:
            # Check if we're currently outputting or recently finished
            currently_outputting = (self.is_announcing or 
                                   self.pending_courtesy_tone or 
                                   self.pending_tail_silence)
            
            if currently_outputting:
                # We're actively outputting - definitely in holdoff
                self.is_in_holdoff = True
                self.last_output_time = time.time()
                return np.zeros(self.CHUNK, dtype=np.int16).tobytes()
            
            # Check if still in holdoff period after output stopped
            if self.last_output_time > 0:
                elapsed = time.time() - self.last_output_time
                if elapsed < self.feedback_holdoff_time:
                    # Still in holdoff
                    if not self.is_in_holdoff:
                        self.is_in_holdoff = True
                        print(f"🔇 Feedback holdoff active ({self.feedback_holdoff_time}s) - muting input")
                    return np.zeros(self.CHUNK, dtype=np.int16).tobytes()
                else:
                    # Holdoff expired
                    if self.is_in_holdoff:
                        self.is_in_holdoff = False
                        # Reset VOX state to prevent false drop detection
                        self.last_vox_state = False
                        # Start grace period to prevent immediate VOX re-trigger
                        self.last_announcement_time = time.time()
                        print("🔊 Feedback holdoff complete - starting grace period")
        
        # Normal operation - pass through when VOX active
        if self.vox.is_active:
            return in_data  # Pass through immediately
        else:
            return np.zeros(self.CHUNK, dtype=np.int16).tobytes()
    
    def get_announcement_chunk(self):
        """Get next chunk of announcement audio"""
        if self.announcement_audio is None or self.announcement_index >= len(self.announcement_audio):
            return None
        
        # Mark that we're outputting audio (for feedback protection)
        if self.feedback_protection_enabled:
            self.last_output_time = time.time()
        
        end_index = min(self.announcement_index + self.CHUNK, len(self.announcement_audio))
        chunk = self.announcement_audio[self.announcement_index:end_index]
        
        # Debug: Check if we're actually outputting audio
        if self.announcement_index == 0:
            print(f"Starting announcement playback - total samples: {len(self.announcement_audio)}")
        
        # Pad if needed
        if len(chunk) < self.CHUNK:
            chunk = np.pad(chunk, (0, self.CHUNK - len(chunk)), mode='constant')
        
        self.announcement_index = end_index
        
        # Debug every second
        if self.announcement_index % (self.RATE) < self.CHUNK:
            progress = (self.announcement_index / len(self.announcement_audio)) * 100
            print(f"Announcement playback: {progress:.1f}% - chunk peak: {np.abs(np.frombuffer(chunk.tobytes(), dtype=np.int16)).max()}")
        
        return chunk.tobytes()
    
    def get_courtesy_tone_chunk(self):
        """Get next chunk of courtesy tone audio"""
        if self.courtesy_tone_audio is None or self.courtesy_tone_index >= len(self.courtesy_tone_audio):
            return None
        
        # Mark that we're outputting audio (for feedback protection)
        if self.feedback_protection_enabled:
            self.last_output_time = time.time()
        
        end_index = min(self.courtesy_tone_index + self.CHUNK, len(self.courtesy_tone_audio))
        chunk = self.courtesy_tone_audio[self.courtesy_tone_index:end_index]
        
        # Calculate progress percentage
        progress = (self.courtesy_tone_index / len(self.courtesy_tone_audio)) * 100
        if progress < 10:  # Only print at the start
            peak = np.abs(chunk).max()
            print(f"🔔 Playing courtesy tone: {progress:.1f}% - peak level: {peak}")
        
        # Pad if needed
        if len(chunk) < self.CHUNK:
            chunk = np.pad(chunk, (0, self.CHUNK - len(chunk)), mode='constant')
        
        self.courtesy_tone_index = end_index
        return chunk.tobytes()
    
    def get_tail_silence_chunk(self):
        """Get next chunk of tail silence audio"""
        if self.tail_silence_audio is None or self.tail_silence_index >= len(self.tail_silence_audio):
            # Tail silence complete - start holdoff period
            if self.feedback_protection_enabled:
                self.last_output_time = time.time()
                self.is_in_holdoff = True
                # Reset VOX state to prevent false drop detection after holdoff
                self.last_vox_state = False
                print(f"Starting feedback protection holdoff ({self.feedback_holdoff_time}s)")
            return None
        
        end_index = min(self.tail_silence_index + self.CHUNK, len(self.tail_silence_audio))
        chunk = self.tail_silence_audio[self.tail_silence_index:end_index]
        
        # Pad if needed
        if len(chunk) < self.CHUNK:
            chunk = np.pad(chunk, (0, self.CHUNK - len(chunk)), mode='constant')
        
        self.tail_silence_index = end_index
        return chunk.tobytes()
    
    def handle_ptt(self):
        """Handle PTT control based on mode"""
        should_ptt = False
        
        # Determine if PTT should be active
        if self.recording_mode == RecordingMode.REPEATER:
            # In repeater mode, PTT when VOX active OR announcing OR playing tones/silence
            should_ptt = (self.vox.is_active or 
                         self.is_announcing or 
                         self.pending_courtesy_tone or 
                         self.pending_tail_silence)
        elif self.recording_mode == RecordingMode.CONTINUOUS_DELAY:
            # In continuous delay mode, PTT when there's audio in the delayed output
            should_ptt = self.delay_has_audio
        else:
            # Other modes - PTT during playback
            should_ptt = self.is_playing_back
        
        # Apply PTT based on mode
        if self.ptt_mode == PTTMode.USB:
            if should_ptt and not self.ptt_controller.ptt_active:
                self.ptt_controller.ptt_on()
            elif not should_ptt and self.ptt_controller.ptt_active:
                self.ptt_controller.ptt_off()
        elif self.ptt_mode == PTTMode.VOX:
            # VOX mode - ensure PTT is off (radio handles it via audio)
            if self.ptt_controller.ptt_active:
                self.ptt_controller.ptt_off()
            # Debug: Show when VOX mode is preventing serial PTT
            if should_ptt and not hasattr(self, '_vox_mode_warned'):
                print("ℹ️ PTT Mode is set to VOX - radio handles PTT via audio VOX")
                print("   To use serial PTT relay, select 'USB/Serial' in VOX/PTT Settings")
                self._vox_mode_warned = True
    
    def start_recording(self):
        """Start recording audio"""
        if not self.is_recording:
            self.recorded_audio = []
            self.is_recording = True
            self.record_start_time = time.time()
            print("Recording started")
            if self.on_vox_state_change:
                self.on_vox_state_change(True)
    
    def stop_recording(self):
        """Stop recording audio"""
        if self.is_recording:
            self.is_recording = False
            print(f"Recording stopped - {len(self.recorded_audio)} chunks")
            if self.on_vox_state_change:
                self.on_vox_state_change(False)
            
            # NOTE: Timed Auto-Replay now controls the record/play loop in the
            # audio processing state machine. We intentionally do not auto-start
            # playback here to avoid double-starts.
    
    def start_playback(self):
        """Start playing back recorded audio"""
        if not self.is_playing_back and len(self.recorded_audio) > 0:
            # Add pre-key beep at start to trigger radio VOX
            prekey_beep = self.repeater.generate_prekey_beep(self.RATE)
            beep_bytes = prekey_beep.tobytes()
            # IMPORTANT: don't mutate recorded_audio (so saved WAVs don't include the beep)
            self.playback_audio = [beep_bytes] + list(self.recorded_audio)
            print(f"Playback started (with {len(prekey_beep)/self.RATE:.3f}s pre-key beep)")
            
            self.is_playing_back = True
            self.playback_index = 0
    
    def stop_playback(self):
        """Stop playback"""
        if self.is_playing_back:
            self.is_playing_back = False
            self.playback_index = 0
            self.playback_audio = []
            print("Playback stopped")
            
            if self.on_recording_complete:
                self.on_recording_complete()

            # In Timed Auto-Replay, immediately go back into recording so it keeps looping
            if self.recording_mode == RecordingMode.TIMED_REPLAY and self.is_running:
                # Small delay avoids capturing any lingering audio from the end of playback
                threading.Timer(0.15, self.start_recording).start()
    
    def save_recording(self, filename):
        """Save recorded audio to WAV file"""
        if not self.recorded_audio:
            return False
        
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                
                for chunk in self.recorded_audio:
                    wf.writeframes(chunk)
            
            print(f"Recording saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving recording: {e}")
            return False
    
    def handle_dtmf_command(self, command):
        """Handle DTMF command"""
        print(f"\n" + "="*60)
        print(f"📞 DTMF COMMAND RECEIVED: {command}")
        print(f"="*60)
        
        # Check if command is mapped
        if command not in self.dtmf_commands:
            print(f"⚠️ Unknown DTMF command: {command}")
            print(f"="*60 + "\n")
            return
        
        action = self.dtmf_commands[command]
        print(f"🎯 Action: {action.upper()}")
        
        # Generate appropriate announcement
        text = None
        
        if action == "weather":
            if self.weather.enabled:
                text = self.weather.get_weather_announcement()
                print(f"🌤️ Weather: Fetching current conditions...")
            else:
                text = "Weather service is not enabled"
                print(f"⚠️ Weather service not enabled")
        
        elif action == "time":
            now = datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            text = f"The current time is {time_str}. Today is {date_str}"
            print(f"🕐 Time: {time_str}, {date_str}")
        
        elif action.startswith("custom"):
            # Custom message
            text = self.dtmf_messages.get(action, f"Custom message {action}")
            print(f"📝 Custom message: {text[:50]}...")
        
        # Queue the announcement
        if text:
            print(f"\n📢 Response Text: {text}")
            print(f"\n⏱️  TIMING:")
            print(f"   ▶️ Response queued NOW")
            print(f"   ⏳ Un-key your radio")
            print(f"   ⏳ Wait for VOX to drop (0.5-1s)")
            print(f"   ⏳ TTS generation in progress...")
            print(f"   🔊 Announcement will play in 1-3 seconds")
            print(f"="*60 + "\n")
            self.announcement_queue.put(text)
    
    def set_delay(self, delay_seconds):
        """Update delay time for continuous mode"""
        self.DELAY_SECONDS = delay_seconds
        new_buffer_size = int(self.RATE / self.CHUNK * self.DELAY_SECONDS)
        
        old_buffer = list(self.audio_buffer)
        self.audio_buffer = deque(maxlen=new_buffer_size)
        
        silence = np.zeros(self.CHUNK, dtype=np.int16).tobytes()
        for _ in range(new_buffer_size):
            if old_buffer:
                self.audio_buffer.append(old_buffer.pop(0))
            else:
                self.audio_buffer.append(silence)
    
    def cleanup(self):
        """Clean up resources"""
        self.stop()
        self.ptt_controller.disconnect()
        self.audio.terminate()


class ParrotBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Soft Repeater Box v1.01 - by NHscan")
        self.root.geometry("950x900")
        self.root.resizable(True, True)  # Allow resizing
        
        # Set minimum window size
        self.root.minsize(750, 600)
        
        # Configuration manager
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        
        self.parrot = ParrotBox()
        self.parrot.on_recording_complete = self.on_recording_complete
        self.parrot.on_vox_state_change = self.on_vox_state_change
        
        self.update_job = None
        self.recordings_history = []

        # Recordings directory
        self.recordings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
        try:
            os.makedirs(self.recordings_dir, exist_ok=True)
        except Exception:
            # If the folder can't be created (rare), fall back to CWD
            self.recordings_dir = os.path.join(os.getcwd(), "recordings")
            os.makedirs(self.recordings_dir, exist_ok=True)
        
        self.setup_gui()
        self.load_settings_from_config()
        self.refresh_serial_ports()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_scrollable_frame(self, parent):
        """Create a scrollable frame for tab content"""
        # Create canvas
        canvas = tk.Canvas(parent, bg='#f0f0f0')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        return scrollable_frame
    
    def setup_gui(self):
        """Create the GUI interface"""
        
        # Create menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Configuration", command=self.save_config_menu)
        file_menu.add_command(label="Reload Configuration", command=self.reload_config_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tabs with scrollable content
        main_tab_container = ttk.Frame(notebook)
        notebook.add(main_tab_container, text="Main Control")
        main_tab = self.create_scrollable_frame(main_tab_container)
        self.setup_main_tab(main_tab)
        
        audio_tab_container = ttk.Frame(notebook)
        notebook.add(audio_tab_container, text="Audio Devices")
        audio_tab = self.create_scrollable_frame(audio_tab_container)
        self.setup_audio_tab(audio_tab)
        
        repeater_tab_container = ttk.Frame(notebook)
        notebook.add(repeater_tab_container, text="Repeater Settings")
        repeater_tab = self.create_scrollable_frame(repeater_tab_container)
        self.setup_repeater_tab(repeater_tab)
        
        mode_settings_tab_container = ttk.Frame(notebook)
        notebook.add(mode_settings_tab_container, text="Mode Settings")
        mode_settings_tab = self.create_scrollable_frame(mode_settings_tab_container)
        self.setup_mode_settings_tab(mode_settings_tab)
        
        settings_tab_container = ttk.Frame(notebook)
        notebook.add(settings_tab_container, text="VOX/PTT Settings")
        settings_tab = self.create_scrollable_frame(settings_tab_container)
        self.setup_settings_tab(settings_tab)
        
        recordings_tab_container = ttk.Frame(notebook)
        notebook.add(recordings_tab_container, text="Recordings")
        recordings_tab = self.create_scrollable_frame(recordings_tab_container)
        self.setup_recordings_tab(recordings_tab)
        
        # DTMF/Weather Commands Tab
        commands_tab_container = ttk.Frame(notebook)
        notebook.add(commands_tab_container, text="DTMF Commands")
        commands_tab = self.create_scrollable_frame(commands_tab_container)
        self.setup_commands_tab(commands_tab)
    
    def setup_main_tab(self, parent):
        """Setup main control tab"""
        
        title_label = ttk.Label(parent, text="Soft Repeater Box v1.01", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # Author info
        author_label = ttk.Label(parent, text="by NHscan | host@nhscan.com", 
                                font=('Arial', 9), foreground='gray')
        author_label.pack(pady=2)
        title_label.pack(pady=10)
        
        # Status
        status_frame = ttk.LabelFrame(parent, text="Status", padding="10")
        status_frame.pack(fill='x', padx=10, pady=5)
        
        status_grid = ttk.Frame(status_frame)
        status_grid.pack()
        
        ttk.Label(status_grid, text="System:").grid(row=0, column=0, sticky='w', padx=5)
        self.status_label = ttk.Label(status_grid, text="● STOPPED", 
                                     font=('Arial', 11, 'bold'),
                                     foreground='red')
        self.status_label.grid(row=0, column=1, sticky='w', padx=5)
        
        ttk.Label(status_grid, text="VOX/Activity:").grid(row=1, column=0, sticky='w', padx=5)
        self.vox_status_label = ttk.Label(status_grid, text="○ Inactive", 
                                         font=('Arial', 10))
        self.vox_status_label.grid(row=1, column=1, sticky='w', padx=5)
        
        ttk.Label(status_grid, text="PTT:").grid(row=2, column=0, sticky='w', padx=5)
        self.ptt_status_label = ttk.Label(status_grid, text="○ Inactive", 
                                         font=('Arial', 10))
        self.ptt_status_label.grid(row=2, column=1, sticky='w', padx=5)
        
        # Controls
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.pack(fill='x', padx=10, pady=5)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack()
        
        self.start_button = ttk.Button(btn_frame, text="START SYSTEM", 
                                      command=self.start_parrot,
                                      width=20)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)
        
        self.stop_button = ttk.Button(btn_frame, text="STOP SYSTEM", 
                                     command=self.stop_parrot,
                                     width=20,
                                     state='disabled')
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)
        
        # Manual ID button
        self.manual_id_button = ttk.Button(btn_frame, text="SEND ID NOW",
                                          command=self.manual_id,
                                          width=20, state='disabled')
        self.manual_id_button.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Test audio output button
        self.test_audio_button = ttk.Button(btn_frame, text="TEST AUDIO OUTPUT",
                                           command=self.test_audio_output,
                                           width=20)
        self.test_audio_button.grid(row=2, column=0, columnspan=2, pady=5)
        
        # Save recording button (for parrot mode)
        self.save_recording_button = ttk.Button(btn_frame, text="SAVE RECORDING",
                                               command=self.manual_save_recording,
                                               width=20, state='disabled')
        self.save_recording_button.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Recording control buttons (for parrot/manual modes)
        self.start_rec_button = ttk.Button(btn_frame, text="START RECORDING",
                                          command=self.start_recording_clicked,
                                          width=20, state='disabled')
        self.start_rec_button.grid(row=4, column=0, padx=5, pady=5)
        
        self.stop_rec_button = ttk.Button(btn_frame, text="STOP RECORDING",
                                         command=self.stop_recording_clicked,
                                         width=20, state='disabled')
        self.stop_rec_button.grid(row=4, column=1, padx=5, pady=5)
        
        # Mode selection
        mode_frame = ttk.LabelFrame(parent, text="Operating Mode", padding="10")
        mode_frame.pack(fill='x', padx=10, pady=5)
        
        self.mode_var = tk.StringVar(value=RecordingMode.REPEATER.value)
        
        for mode in RecordingMode:
            desc = mode.value
            if mode == RecordingMode.REPEATER:
                desc += " (Real-time pass-through)"
            ttk.Radiobutton(mode_frame, text=desc, 
                           variable=self.mode_var,
                           value=mode.value,
                           command=self.change_mode).pack(anchor='w', pady=2)
        
        # Audio levels
        levels_frame = ttk.LabelFrame(parent, text="Audio Levels", padding="10")
        levels_frame.pack(fill='x', padx=10, pady=5)
        
        input_frame = ttk.Frame(levels_frame)
        input_frame.pack(fill='x', pady=2)
        ttk.Label(input_frame, text="Input:", width=8).pack(side='left')
        self.input_level_bar = ttk.Progressbar(input_frame, length=500, mode='determinate')
        self.input_level_bar.pack(side='left', padx=5)
        self.input_level_label = ttk.Label(input_frame, text="0%", width=5)
        self.input_level_label.pack(side='left')
        
        output_frame = ttk.Frame(levels_frame)
        output_frame.pack(fill='x', pady=2)
        ttk.Label(output_frame, text="Output:", width=8).pack(side='left')
        self.output_level_bar = ttk.Progressbar(output_frame, length=500, mode='determinate')
        self.output_level_bar.pack(side='left', padx=5)
        self.output_level_label = ttk.Label(output_frame, text="0%", width=5)
        self.output_level_label.pack(side='left')
        
        # Config status
        config_info = ttk.Label(parent, text="💾 Settings auto-save", 
                               font=('Arial', 8), foreground='gray')
        config_info.pack(pady=5)
    
    def setup_audio_tab(self, parent):
        """Setup audio devices configuration tab"""
        
        ttk.Label(parent, text="Audio Device Configuration", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Input device
        input_frame = ttk.LabelFrame(parent, text="Input Device (Microphone/Line-In)", padding="10")
        input_frame.pack(fill='x', padx=10, pady=10)
        
        input_select_frame = ttk.Frame(input_frame)
        input_select_frame.pack(fill='x', pady=5)
        
        ttk.Label(input_select_frame, text="Device:").pack(side='left', padx=5)
        
        self.input_device_var = tk.StringVar(value="Default")
        self.input_device_combo = ttk.Combobox(input_select_frame, 
                                               textvariable=self.input_device_var,
                                               width=40, state='readonly')
        self.input_device_combo.pack(side='left', padx=5)
        
        ttk.Button(input_select_frame, text="Refresh Devices",
                  command=self.refresh_audio_devices).pack(side='left', padx=5)
        
        # Input level with canvas for waveform
        input_monitor_frame = ttk.Frame(input_frame)
        input_monitor_frame.pack(fill='x', pady=5)
        
        ttk.Label(input_monitor_frame, text="Level:").pack(side='left', padx=5)
        self.input_device_level_bar = ttk.Progressbar(input_monitor_frame, length=300, mode='determinate')
        self.input_device_level_bar.pack(side='left', padx=5)
        self.input_device_level_label = ttk.Label(input_monitor_frame, text="0%", width=5)
        self.input_device_level_label.pack(side='left')
        
        # Input waveform
        input_wave_frame = ttk.Frame(input_frame)
        input_wave_frame.pack(fill='x', pady=5)
        
        ttk.Label(input_wave_frame, text="Waveform:").pack(anchor='w', padx=5)
        self.input_waveform = tk.Canvas(input_wave_frame, height=60, bg='black')
        self.input_waveform.pack(fill='x', padx=5, pady=5)
        
        # Output device
        output_frame = ttk.LabelFrame(parent, text="Output Device (Speaker/Line-Out)", padding="10")
        output_frame.pack(fill='x', padx=10, pady=10)
        
        output_select_frame = ttk.Frame(output_frame)
        output_select_frame.pack(fill='x', pady=5)
        
        ttk.Label(output_select_frame, text="Device:").pack(side='left', padx=5)
        
        self.output_device_var = tk.StringVar(value="Default")
        self.output_device_combo = ttk.Combobox(output_select_frame, 
                                                textvariable=self.output_device_var,
                                                width=40, state='readonly')
        self.output_device_combo.pack(side='left', padx=5)
        
        # Output level
        output_monitor_frame = ttk.Frame(output_frame)
        output_monitor_frame.pack(fill='x', pady=5)
        
        ttk.Label(output_monitor_frame, text="Level:").pack(side='left', padx=5)
        self.output_device_level_bar = ttk.Progressbar(output_monitor_frame, length=300, mode='determinate')
        self.output_device_level_bar.pack(side='left', padx=5)
        self.output_device_level_label = ttk.Label(output_monitor_frame, text="0%", width=5)
        self.output_device_level_label.pack(side='left')
        
        # Output waveform
        output_wave_frame = ttk.Frame(output_frame)
        output_wave_frame.pack(fill='x', pady=5)
        
        ttk.Label(output_wave_frame, text="Waveform:").pack(anchor='w', padx=5)
        self.output_waveform = tk.Canvas(output_wave_frame, height=60, bg='black')
        self.output_waveform.pack(fill='x', padx=5, pady=5)
        
        # Live Volume Controls
        volume_frame = ttk.LabelFrame(parent, text="Live Volume Controls", padding="10")
        volume_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(volume_frame, text="Adjust input and output gain in real-time:", 
                 wraplength=600).pack(anchor='w', pady=5)
        
        # Input gain
        input_gain_frame = ttk.Frame(volume_frame)
        input_gain_frame.pack(fill='x', pady=5)
        
        ttk.Label(input_gain_frame, text="Input Gain:").pack(side='left', padx=5)
        
        self.input_gain_var = tk.DoubleVar(value=1.0)
        ttk.Scale(input_gain_frame, from_=0.0, to=2.0,
                 variable=self.input_gain_var,
                 orient=tk.HORIZONTAL,
                 length=300,
                 command=self.update_input_gain).pack(side='left', padx=5)
        
        self.input_gain_label = ttk.Label(input_gain_frame, text="100%")
        self.input_gain_label.pack(side='left', padx=5)
        
        # Output gain
        output_gain_frame = ttk.Frame(volume_frame)
        output_gain_frame.pack(fill='x', pady=5)
        
        ttk.Label(output_gain_frame, text="Output Gain:").pack(side='left', padx=5)
        
        self.output_gain_var = tk.DoubleVar(value=1.0)
        ttk.Scale(output_gain_frame, from_=0.0, to=2.0,
                 variable=self.output_gain_var,
                 orient=tk.HORIZONTAL,
                 length=300,
                 command=self.update_output_gain).pack(side='left', padx=5)
        
        self.output_gain_label = ttk.Label(output_gain_frame, text="100%")
        self.output_gain_label.pack(side='left', padx=5)
        
        # Apply button
        apply_frame = ttk.Frame(parent)
        apply_frame.pack(pady=10)
        
        ttk.Button(apply_frame, text="Apply Device Changes (Requires Restart)",
                  command=self.apply_audio_devices,
                  width=40).pack()
        
        # Waveform buffers
        self.input_waveform_data = deque(maxlen=300)
        self.output_waveform_data = deque(maxlen=300)
        
        # Initialize
        self.refresh_audio_devices()
    
    def refresh_audio_devices(self):
        """Refresh available audio devices"""
        try:
            audio = pyaudio.PyAudio()
            
            input_devices = ["Default"]
            output_devices = ["Default"]
            
            for i in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(i)
                name = f"{i}: {info['name']}"
                
                if info['maxInputChannels'] > 0:
                    input_devices.append(name)
                if info['maxOutputChannels'] > 0:
                    output_devices.append(name)
            
            audio.terminate()
            
            self.input_device_combo['values'] = input_devices
            self.output_device_combo['values'] = output_devices
            
            print(f"Found {len(input_devices)-1} input devices, {len(output_devices)-1} output devices")
            
        except Exception as e:
            print(f"Error refreshing audio devices: {e}")
            messagebox.showerror("Error", f"Failed to list audio devices:\n{e}")
    
    def apply_audio_devices(self):
        """Apply audio device changes"""
        input_dev = self.input_device_var.get()
        output_dev = self.output_device_var.get()
        
        # Parse device indices from selection strings
        # Format is: "4: CABLE Input (VB-Audio Virtual C"
        # Extract the number before the colon
        
        try:
            if input_dev and input_dev != "Default":
                input_index = int(input_dev.split(':')[0])
                self.parrot.input_device_index = input_index
                print(f"Set input device index to: {input_index}")
            else:
                self.parrot.input_device_index = None
                print("Set input device to default")
        except (ValueError, IndexError):
            print(f"Could not parse input device index from: {input_dev}")
            self.parrot.input_device_index = None
        
        try:
            if output_dev and output_dev != "Default":
                output_index = int(output_dev.split(':')[0])
                self.parrot.output_device_index = output_index
                print(f"Set output device index to: {output_index}")
            else:
                self.parrot.output_device_index = None
                print("Set output device to default")
        except (ValueError, IndexError):
            print(f"Could not parse output device index from: {output_dev}")
            self.parrot.output_device_index = None
        
        # Save to config
        self.config["input_device"] = input_dev
        self.config["output_device"] = output_dev
        self.save_config()
        
        messagebox.showinfo("Device Changes", 
                           f"Audio devices configured:\nInput: {input_dev}\nOutput: {output_dev}\n\n" +
                           "Please STOP and START the system to apply changes.")
    
    def update_waveforms(self):
        """Update waveform displays"""
        if not self.parrot.is_running:
            return
        
        # Get current audio levels (already calculated in audio callback)
        input_level = self.parrot.input_level
        output_level = self.parrot.output_level
        
        # Add to waveform buffers
        self.input_waveform_data.append(input_level)
        self.output_waveform_data.append(output_level)
        
        # Draw input waveform
        self.draw_waveform(self.input_waveform, self.input_waveform_data, 'green')
        
        # Draw output waveform
        self.draw_waveform(self.output_waveform, self.output_waveform_data, 'yellow')
    
    def draw_waveform(self, canvas, data, color):
        """Draw waveform on canvas"""
        canvas.delete("all")
        
        if len(data) < 2:
            return
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        if width <= 1:
            width = 600
        
        # Draw grid
        for i in range(0, 101, 25):
            y = height - (i / 100.0 * height)
            canvas.create_line(0, y, width, y, fill='gray20', dash=(2, 2))
        
        # Draw waveform
        points = []
        data_list = list(data)
        for i, level in enumerate(data_list):
            x = (i / len(data_list)) * width
            y = height - (min(level, 100) / 100.0 * height)
            points.append((x, y))
        
        if len(points) > 1:
            for i in range(len(points) - 1):
                canvas.create_line(points[i][0], points[i][1],
                                 points[i+1][0], points[i+1][1],
                                 fill=color, width=2)
    
    def setup_repeater_tab(self, parent):
        """Setup repeater configuration tab"""
        """Setup repeater configuration tab"""
        
        ttk.Label(parent, text="Repeater Configuration", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Callsign
        callsign_frame = ttk.LabelFrame(parent, text="Station Identification", padding="10")
        callsign_frame.pack(fill='x', padx=10, pady=10)
        
        cs_entry_frame = ttk.Frame(callsign_frame)
        cs_entry_frame.pack(fill='x', pady=5)
        
        ttk.Label(cs_entry_frame, text="Callsign:").pack(side='left', padx=5)
        self.callsign_var = tk.StringVar(value="WRKC123")
        ttk.Entry(cs_entry_frame, textvariable=self.callsign_var, width=20).pack(side='left', padx=5)
        ttk.Button(cs_entry_frame, text="Update", command=self.update_callsign).pack(side='left', padx=5)
        
        # Auto ID enable checkbox
        self.auto_id_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(callsign_frame, text="Enable Automatic ID Announcements",
                       variable=self.auto_id_var,
                       command=self.toggle_auto_id).pack(anchor='w', pady=5)
        
        # ID interval
        interval_frame = ttk.Frame(callsign_frame)
        interval_frame.pack(fill='x', pady=5)
        
        ttk.Label(interval_frame, text="ID Interval (minutes):").pack(side='left', padx=5)
        
        self.id_interval_var = tk.DoubleVar(value=10.0)
        ttk.Scale(interval_frame, from_=5.0, to=15.0,
                 variable=self.id_interval_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_id_interval).pack(side='left', padx=5)
        
        self.id_interval_label = ttk.Label(interval_frame, text="10 min")
        self.id_interval_label.pack(side='left', padx=5)
        
        # Courtesy tone
        tone_frame = ttk.LabelFrame(parent, text="Courtesy Tone", padding="10")
        tone_frame.pack(fill='x', padx=10, pady=10)
        
        self.courtesy_tone_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(tone_frame, text="Enable Courtesy Tone (beep after transmission)",
                       variable=self.courtesy_tone_var,
                       command=self.toggle_courtesy_tone).pack(anchor='w', pady=5)
        
        tone_freq_frame = ttk.Frame(tone_frame)
        tone_freq_frame.pack(fill='x', pady=5)
        
        ttk.Label(tone_freq_frame, text="Tone Frequency (Hz):").pack(side='left', padx=5)
        
        self.tone_freq_var = tk.DoubleVar(value=1000)
        ttk.Scale(tone_freq_frame, from_=500, to=2000,
                 variable=self.tone_freq_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_tone_freq).pack(side='left', padx=5)
        
        self.tone_freq_label = ttk.Label(tone_freq_frame, text="1000 Hz")
        self.tone_freq_label.pack(side='left', padx=5)
        
        # Courtesy tone volume
        tone_vol_frame = ttk.Frame(tone_frame)
        tone_vol_frame.pack(fill='x', pady=5)
        
        ttk.Label(tone_vol_frame, text="Tone Volume:").pack(side='left', padx=5)
        
        self.tone_volume_var = tk.DoubleVar(value=0.5)
        ttk.Scale(tone_vol_frame, from_=0.0, to=1.0,
                 variable=self.tone_volume_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_tone_volume).pack(side='left', padx=5)
        
        self.tone_volume_label = ttk.Label(tone_vol_frame, text="50%")
        self.tone_volume_label.pack(side='left', padx=5)
        
        # Courtesy tone duration
        tone_dur_frame = ttk.Frame(tone_frame)
        tone_dur_frame.pack(fill='x', pady=5)
        
        ttk.Label(tone_dur_frame, text="Tone Duration (seconds):").pack(side='left', padx=5)
        
        self.tone_duration_var = tk.DoubleVar(value=0.5)
        ttk.Scale(tone_dur_frame, from_=0.1, to=2.0,
                 variable=self.tone_duration_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_tone_duration).pack(side='left', padx=5)
        
        self.tone_duration_label = ttk.Label(tone_dur_frame, text="0.5 sec")
        self.tone_duration_label.pack(side='left', padx=5)
        
        # Timeout timer
        timeout_frame = ttk.LabelFrame(parent, text="Timeout Timer", padding="10")
        timeout_frame.pack(fill='x', padx=10, pady=10)
        
        timeout_entry_frame = ttk.Frame(timeout_frame)
        timeout_entry_frame.pack(fill='x', pady=5)
        
        ttk.Label(timeout_entry_frame, text="Max TX Time (seconds):").pack(side='left', padx=5)
        
        self.timeout_var = tk.DoubleVar(value=180)
        ttk.Scale(timeout_entry_frame, from_=60, to=300,
                 variable=self.timeout_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_timeout).pack(side='left', padx=5)
        
        self.timeout_label = ttk.Label(timeout_entry_frame, text="180 sec")
        self.timeout_label.pack(side='left', padx=5)
        
        # PTT Pre-delay
        ptt_delay_frame = ttk.LabelFrame(parent, text="PTT Pre-Delay", padding="10")
        ptt_delay_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(ptt_delay_frame, text="Delay before speaking (allows PTT to key up):", 
                 wraplength=400).pack(anchor='w', pady=5)
        
        delay_control_frame = ttk.Frame(ptt_delay_frame)
        delay_control_frame.pack(fill='x', pady=5)
        
        ttk.Label(delay_control_frame, text="Pre-delay (seconds):").pack(side='left', padx=5)
        
        self.ptt_predelay_var = tk.DoubleVar(value=1.0)
        ttk.Scale(delay_control_frame, from_=0.0, to=3.0,
                 variable=self.ptt_predelay_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_ptt_predelay).pack(side='left', padx=5)
        
        self.ptt_predelay_label = ttk.Label(delay_control_frame, text="1.0 sec")
        self.ptt_predelay_label.pack(side='left', padx=5)
        
        # Tail Silence (VOX Drop Time)
        tail_frame = ttk.LabelFrame(parent, text="Tail Silence (VOX Drop)", padding="10")
        tail_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(tail_frame, text="Silence after transmission to drop radio VOX cleanly:", 
                 wraplength=400).pack(anchor='w', pady=5)
        
        tail_control_frame = ttk.Frame(tail_frame)
        tail_control_frame.pack(fill='x', pady=5)
        
        ttk.Label(tail_control_frame, text="Tail silence (seconds):").pack(side='left', padx=5)
        
        self.tail_silence_var = tk.DoubleVar(value=0.5)
        ttk.Scale(tail_control_frame, from_=0.0, to=2.0,
                 variable=self.tail_silence_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_tail_silence).pack(side='left', padx=5)
        
        self.tail_silence_label = ttk.Label(tail_control_frame, text="0.5 sec")
        self.tail_silence_label.pack(side='left', padx=5)
        
        # Custom announcement
        announce_frame = ttk.LabelFrame(parent, text="Custom Announcement", padding="10")
        announce_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(announce_frame, text="Enter text to announce:").pack(anchor='w', pady=5)
        
        self.custom_announce_var = tk.StringVar()
        ttk.Entry(announce_frame, textvariable=self.custom_announce_var, width=60).pack(fill='x', pady=5)
        
        ttk.Button(announce_frame, text="Send Announcement Now",
                  command=self.send_custom_announcement).pack(pady=5)
    
    def setup_mode_settings_tab(self, parent):
        """Setup mode-specific settings tab"""
        
        ttk.Label(parent, text="Recording Mode Settings",
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        # Timed Replay Mode Settings
        timed_frame = ttk.LabelFrame(parent, text="Timed Replay Mode", padding="10")
        timed_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(timed_frame, text="Maximum record time before auto-playback:").pack(anchor='w', pady=5)
        
        timer_control = ttk.Frame(timed_frame)
        timer_control.pack(fill='x', pady=5)
        
        self.timer_var = tk.DoubleVar(value=30.0)
        timer_slider = ttk.Scale(timer_control, from_=5, to=300,
                                variable=self.timer_var,
                                orient='horizontal',
                                command=self.update_timer_label)
        timer_slider.pack(side='left', fill='x', expand=True, padx=5)
        
        self.timer_value_label = ttk.Label(timer_control, text="30s", width=8)
        self.timer_value_label.pack(side='left', padx=5)
        
        # Continuous Delay Mode Settings
        delay_frame = ttk.LabelFrame(parent, text="Continuous Delay Line Mode", padding="10")
        delay_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(delay_frame, text="Delay time (seconds):").pack(anchor='w', pady=5)
        
        delay_control = ttk.Frame(delay_frame)
        delay_control.pack(fill='x', pady=5)
        
        self.delay_var = tk.DoubleVar(value=2.0)
        delay_slider = ttk.Scale(delay_control, from_=0.5, to=10.0,
                                variable=self.delay_var,
                                orient='horizontal',
                                command=self.update_delay_label)
        delay_slider.pack(side='left', fill='x', expand=True, padx=5)
        
        self.delay_value_label = ttk.Label(delay_control, text="2.0s", width=8)
        self.delay_value_label.pack(side='left', padx=5)
        
        # PTT Pre-key time for delay mode
        ttk.Label(delay_frame, text="PTT Pre-Key Time (seconds):").pack(anchor='w', pady=5)
        
        ptt_prekey_control = ttk.Frame(delay_frame)
        ptt_prekey_control.pack(fill='x', pady=5)
        
        self.ptt_prekey_delay_var = tk.DoubleVar(value=0.5)
        ptt_prekey_slider = ttk.Scale(ptt_prekey_control, from_=0.0, to=2.0,
                                variable=self.ptt_prekey_delay_var,
                                orient='horizontal',
                                command=self.update_ptt_prekey_label)
        ptt_prekey_slider.pack(side='left', fill='x', expand=True, padx=5)
        
        self.ptt_prekey_delay_label = ttk.Label(ptt_prekey_control, text="0.5s", width=8)
        self.ptt_prekey_delay_label.pack(side='left', padx=5)
        
        ttk.Label(delay_frame, text="PTT activates this many seconds BEFORE audio transmits.\n" +
                 "Prevents radio from cutting off first word (0.3-1.0s recommended).",
                 font=('Arial', 8), foreground='gray', wraplength=600).pack(anchor='w', pady=2)
        
        # Info
        info_text = ("These settings only apply when using their respective modes.\n"
                    "Repeater Mode has no configurable delays as it operates in real-time.")
        ttk.Label(parent, text=info_text, font=('Arial', 9), 
                 foreground='gray', wraplength=700).pack(pady=10)
    
    def update_timer_label(self, value):
        """Update timer label"""
        val = int(float(value))
        self.timer_value_label.config(text=f"{val}s")
        self.parrot.max_record_time = val
        self.save_config()
    
    def update_delay_label(self, value):
        """Update delay label"""
        val = float(value)
        self.delay_value_label.config(text=f"{val:.1f}s")
        self.parrot.DELAY_SECONDS = val
        self.save_config()
    
    def update_ptt_prekey_label(self, value):
        """Update PTT pre-key label"""
        val = float(value)
        self.ptt_prekey_delay_label.config(text=f"{val:.1f}s")
        self.parrot.ptt_prekey_time = val
        self.save_config()
    
    def setup_settings_tab(self, parent):
        """Setup VOX and PTT settings tab"""
        
        # VOX Settings
        vox_frame = ttk.LabelFrame(parent, text="VOX Settings", padding="10")
        vox_frame.pack(fill='x', padx=10, pady=10)
        
        info_label = ttk.Label(vox_frame, 
                              text="⚠️ For Repeater Mode: Only enable if detecting INCOMING audio to repeat.\n" +
                                   "If using radio's VOX for output, keep this DISABLED.",
                              foreground='blue', wraplength=500, justify='left')
        info_label.pack(anchor='w', pady=5)
        
        self.vox_enable_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(vox_frame, text="Enable Software VOX Detection", 
                       variable=self.vox_enable_var,
                       command=self.toggle_vox).pack(anchor='w', pady=5)
        
        # Feedback Protection Section
        feedback_frame = ttk.LabelFrame(parent, text="🔁 Feedback Protection (Web SDR / Stereo Mix)", padding="10")
        feedback_frame.pack(fill='x', padx=10, pady=10)
        
        feedback_info = ttk.Label(feedback_frame,
                                 text="Prevents feedback loops when using web-based SDR (OpenWebRX) or Stereo Mix.\n" +
                                      "Mutes input after transmission to avoid capturing own output.\n" +
                                      "⚠️ ENABLE THIS if you're getting audio feedback loops!",
                                 foreground='darkgreen', wraplength=500, justify='left',
                                 font=('Arial', 9, 'bold'))
        feedback_info.pack(anchor='w', pady=5)
        
        self.feedback_protection_var = tk.BooleanVar(value=True)
        feedback_check = ttk.Checkbutton(feedback_frame, 
                                        text="✓ Enable Feedback Protection (RECOMMENDED for Web SDR)", 
                                        variable=self.feedback_protection_var,
                                        command=self.toggle_feedback_protection)
        feedback_check.pack(anchor='w', pady=5)
        
        # Holdoff time slider
        holdoff_control = ttk.Frame(feedback_frame)
        holdoff_control.pack(fill='x', pady=5)
        
        ttk.Label(holdoff_control, text="Holdoff Time (mute input after output):").pack(anchor='w', padx=5)
        
        holdoff_slider_frame = ttk.Frame(holdoff_control)
        holdoff_slider_frame.pack(fill='x', padx=5, pady=2)
        
        self.feedback_holdoff_var = tk.DoubleVar(value=1.5)
        ttk.Scale(holdoff_slider_frame, from_=0.5, to=5.0,
                 variable=self.feedback_holdoff_var,
                 orient=tk.HORIZONTAL,
                 length=300,
                 command=self.update_feedback_holdoff).pack(side='left', padx=5)
        
        self.feedback_holdoff_label = ttk.Label(holdoff_slider_frame, text="1.5s", width=6)
        self.feedback_holdoff_label.pack(side='left', padx=5)
        
        ttk.Label(feedback_frame, 
                 text="💡 Lower = faster response but may allow feedback  |  Higher = prevents feedback but adds delay",
                 font=('Arial', 8), foreground='gray', wraplength=500).pack(anchor='w', pady=2, padx=5)
        
        # Status indicator
        self.feedback_status_frame = ttk.Frame(feedback_frame)
        self.feedback_status_frame.pack(fill='x', pady=5, padx=5)
        
        ttk.Label(self.feedback_status_frame, text="Status:").pack(side='left', padx=5)
        self.feedback_status_label = ttk.Label(self.feedback_status_frame, text="● Active", foreground='green')
        self.feedback_status_label.pack(side='left')
        
        thresh_frame = ttk.Frame(vox_frame)
        thresh_frame.pack(fill='x', pady=5)
        ttk.Label(thresh_frame, text="VOX Threshold:").pack(side='left', padx=5)
        self.vox_threshold_var = tk.DoubleVar(value=5.0)
        ttk.Scale(thresh_frame, from_=1.0, to=20.0,
                 variable=self.vox_threshold_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_vox_threshold).pack(side='left', padx=5)
        self.vox_threshold_label = ttk.Label(thresh_frame, text="5.0%")
        self.vox_threshold_label.pack(side='left', padx=5)
        
        attack_frame = ttk.Frame(vox_frame)
        attack_frame.pack(fill='x', pady=5)
        ttk.Label(attack_frame, text="Attack Time:").pack(side='left', padx=5)
        self.vox_attack_var = tk.DoubleVar(value=0.1)
        ttk.Scale(attack_frame, from_=0.05, to=1.0,
                 variable=self.vox_attack_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_vox_attack).pack(side='left', padx=5)
        self.vox_attack_label = ttk.Label(attack_frame, text="0.1s")
        self.vox_attack_label.pack(side='left', padx=5)
        
        release_frame = ttk.Frame(vox_frame)
        release_frame.pack(fill='x', pady=5)
        ttk.Label(release_frame, text="Release Time:").pack(side='left', padx=5)
        self.vox_release_var = tk.DoubleVar(value=0.5)
        ttk.Scale(release_frame, from_=0.1, to=3.0,
                 variable=self.vox_release_var,
                 orient=tk.HORIZONTAL,
                 length=200,
                 command=self.update_vox_release).pack(side='left', padx=5)
        self.vox_release_label = ttk.Label(release_frame, text="0.5s")
        self.vox_release_label.pack(side='left', padx=5)
        
        # PTT Control
        ptt_frame = ttk.LabelFrame(parent, text="PTT Control", padding="10")
        ptt_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(ptt_frame, text="PTT Mode:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)
        
        self.ptt_mode_var = tk.StringVar(value=PTTMode.VOX.value)
        
        ttk.Radiobutton(ptt_frame, text="VOX (Radio handles PTT via audio)", 
                       variable=self.ptt_mode_var,
                       value=PTTMode.VOX.value,
                       command=self.change_ptt_mode).pack(anchor='w', pady=2)
        
        ttk.Radiobutton(ptt_frame, text="USB/Serial (Software controls PTT)", 
                       variable=self.ptt_mode_var,
                       value=PTTMode.USB.value,
                       command=self.change_ptt_mode).pack(anchor='w', pady=2)
        
        serial_frame = ttk.Frame(ptt_frame)
        serial_frame.pack(fill='x', pady=10)
        
        ttk.Label(serial_frame, text="Serial Port:").pack(side='left', padx=5)
        
        self.serial_port_var = tk.StringVar()
        self.serial_combo = ttk.Combobox(serial_frame, 
                                        textvariable=self.serial_port_var,
                                        width=20, state='readonly')
        self.serial_combo.pack(side='left', padx=5)
        
        ttk.Button(serial_frame, text="Refresh", 
                  command=self.refresh_serial_ports).pack(side='left', padx=5)
        
        self.connect_button = ttk.Button(serial_frame, text="Connect",
                                        command=self.connect_serial)
        self.connect_button.pack(side='left', padx=5)
        
        self.serial_status_label = ttk.Label(ptt_frame, text="○ Not connected")
        self.serial_status_label.pack(anchor='w', pady=5)
        
        # Relay Type Selection
        relay_type_frame = ttk.Frame(ptt_frame)
        relay_type_frame.pack(fill='x', pady=5)
        
        ttk.Label(relay_type_frame, text="Relay Type:", font=('Arial', 9, 'bold')).pack(side='left', padx=5)
        
        self.relay_type_var = tk.StringVar(value="COMMAND")
        
        ttk.Radiobutton(relay_type_frame, text="Command-based (x003qjjrql, Chinese modules)", 
                       variable=self.relay_type_var,
                       value="COMMAND",
                       command=self.change_relay_type).pack(side='left', padx=5)
        
        ttk.Radiobutton(relay_type_frame, text="RTS/DTR (Standard serial)", 
                       variable=self.relay_type_var,
                       value="RTS",
                       command=self.change_relay_type).pack(side='left', padx=5)
        
        ttk.Button(ptt_frame, text="Test PTT ON", 
                  command=lambda: self.test_ptt(True)).pack(side='left', padx=5, pady=5)
        ttk.Button(ptt_frame, text="Test PTT OFF", 
                  command=lambda: self.test_ptt(False)).pack(side='left', padx=5, pady=5)
        
        # Audio devices info
        audio_info_frame = ttk.Frame(parent)
        audio_info_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(audio_info_frame, text="Audio Troubleshooting:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)
        ttk.Button(audio_info_frame, text="Show Audio Devices",
                  command=self.show_audio_devices).pack(anchor='w', pady=5)
        
        # Debug Mode
        debug_frame = ttk.LabelFrame(parent, text="🔧 Debug Mode", padding="10")
        debug_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(debug_frame, 
                 text="Enable to see detailed console output for troubleshooting.\n" +
                      "Disable for cleaner output (recommended for .exe distribution).",
                 font=('Arial', 9), foreground='gray').pack(anchor='w', pady=5)
        
        self.debug_mode_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(debug_frame, text="Enable Debug Mode (Verbose Console Output)", 
                       variable=self.debug_mode_var,
                       command=self.toggle_debug_mode).pack(anchor='w', pady=5)
    
    def setup_recordings_tab(self, parent):
        """Setup recordings tab"""
        
        ttk.Label(parent, text="Saved Recordings", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.recordings_listbox = tk.Listbox(list_frame, 
                                             yscrollcommand=scrollbar.set,
                                             height=20)
        self.recordings_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.recordings_listbox.yview)
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Open Folder",
                  command=self.open_recordings_folder).pack(side='left', padx=5)
    
    def setup_commands_tab(self, parent):
        """Setup DTMF commands and weather configuration tab"""
        
        ttk.Label(parent, text="DTMF Commands & Weather", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Weather Configuration
        weather_frame = ttk.LabelFrame(parent, text="Weather Service (Weather.gov - US Only)", padding="10")
        weather_frame.pack(fill='x', padx=10, pady=10)
        
        self.weather_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(weather_frame, text="Enable Weather Service", 
                       variable=self.weather_enabled_var,
                       command=self.toggle_weather).pack(anchor='w', pady=5)
        
        zip_frame = ttk.Frame(weather_frame)
        zip_frame.pack(fill='x', pady=5)
        ttk.Label(zip_frame, text="ZIP Code:").pack(side='left', padx=5)
        self.weather_zip_var = tk.StringVar(value="03894")
        zip_entry = ttk.Entry(zip_frame, textvariable=self.weather_zip_var, width=10)
        zip_entry.pack(side='left', padx=5)
        ttk.Button(zip_frame, text="Update Weather", 
                  command=self.update_weather_zip).pack(side='left', padx=5)
        ttk.Button(zip_frame, text="Test Connection", 
                  command=self.test_weather_connection).pack(side='left', padx=5)
        
        # Manual coordinates (advanced)
        coord_frame = ttk.LabelFrame(weather_frame, text="Manual Coordinates (Advanced - Skip ZIP lookup)", padding="5")
        coord_frame.pack(fill='x', pady=5)
        
        coord_entry_frame = ttk.Frame(coord_frame)
        coord_entry_frame.pack(fill='x', pady=2)
        
        ttk.Label(coord_entry_frame, text="Latitude:").pack(side='left', padx=5)
        self.weather_lat_var = tk.StringVar(value="")
        lat_entry = ttk.Entry(coord_entry_frame, textvariable=self.weather_lat_var, width=12)
        lat_entry.pack(side='left', padx=5)
        
        ttk.Label(coord_entry_frame, text="Longitude:").pack(side='left', padx=5)
        self.weather_lon_var = tk.StringVar(value="")
        lon_entry = ttk.Entry(coord_entry_frame, textvariable=self.weather_lon_var, width=12)
        lon_entry.pack(side='left', padx=5)
        
        ttk.Button(coord_entry_frame, text="Set Coordinates", 
                  command=self.set_manual_coords).pack(side='left', padx=5)
        
        ttk.Label(coord_frame, text="Find your coordinates at: https://www.latlong.net/", 
                 font=('Arial', 8), foreground='blue', cursor='hand2').pack(anchor='w')
        
        self.weather_include_id_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(weather_frame, text="Include Temperature in Station ID", 
                       variable=self.weather_include_id_var,
                       command=self.toggle_weather_in_id).pack(anchor='w', pady=5)
        
        self.weather_status_label = ttk.Label(weather_frame, text="Weather: Not configured", 
                                             foreground='gray')
        self.weather_status_label.pack(anchor='w', pady=5)
        
        ttk.Label(weather_frame, text="Note: Weather updates every 30 minutes automatically.\n" +
                 "DTMF 0001 will play full weather report.",
                 font=('Arial', 8), foreground='gray').pack(anchor='w', pady=2)
        
        # DTMF Detection
        dtmf_frame = ttk.LabelFrame(parent, text="DTMF Detection", padding="10")
        dtmf_frame.pack(fill='x', padx=10, pady=10)
        
        self.dtmf_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(dtmf_frame, text="Enable DTMF Detection (Repeater Mode Only)", 
                       variable=self.dtmf_enabled_var,
                       command=self.toggle_dtmf).pack(anchor='w', pady=5)
        
        ttk.Label(dtmf_frame, text="DTMF commands are 4-digit codes (e.g., 0001, 0002)\n" +
                 "Key up, dial the code, and the repeater will respond.",
                 font=('Arial', 9), foreground='gray').pack(anchor='w', pady=5)
        
        # DTMF Command Mapping
        commands_frame = ttk.LabelFrame(parent, text="DTMF Command Configuration", padding="10")
        commands_frame.pack(fill='x', padx=10, pady=10)
        
        # Fixed commands
        ttk.Label(commands_frame, text="Fixed Commands:", font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)
        ttk.Label(commands_frame, text="0001 → Weather Report (full weather information)",
                 font=('Arial', 9)).pack(anchor='w', padx=20)
        ttk.Label(commands_frame, text="0002 → Time & Date (current time and date)",
                 font=('Arial', 9)).pack(anchor='w', padx=20)
        
        # Custom messages
        ttk.Label(commands_frame, text="\nCustom Message Commands:", 
                 font=('Arial', 10, 'bold')).pack(anchor='w', pady=5)
        
        # Create entry fields for custom commands
        self.dtmf_custom_vars = {}
        for i in range(3, 11):  # 0003 through 0010
            code = f"000{i}" if i < 10 else f"00{i}"
            custom_key = f"custom{i-2}"
            
            cmd_frame = ttk.Frame(commands_frame)
            cmd_frame.pack(fill='x', pady=2)
            
            ttk.Label(cmd_frame, text=f"{code} →", width=8).pack(side='left', padx=5)
            
            var = tk.StringVar(value=f"Custom message {i-2}")
            self.dtmf_custom_vars[custom_key] = var
            entry = ttk.Entry(cmd_frame, textvariable=var, width=60)
            entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Test DTMF
        test_frame = ttk.Frame(commands_frame)
        test_frame.pack(fill='x', pady=10)
        
        ttk.Label(test_frame, text="Test Command:").pack(side='left', padx=5)
        self.test_dtmf_var = tk.StringVar(value="0001")
        test_entry = ttk.Entry(test_frame, textvariable=self.test_dtmf_var, width=10)
        test_entry.pack(side='left', padx=5)
        ttk.Button(test_frame, text="Test DTMF Command", 
                  command=self.test_dtmf_command).pack(side='left', padx=5)
        
        # Save button
        ttk.Button(commands_frame, text="Save All DTMF Settings", 
                  command=self.save_dtmf_settings).pack(pady=10)
        
        # Info
        info_text = ("📟 How to use DTMF Commands:\n"
                    "1. Enable DTMF Detection above\n"
                    "2. Start the system in Repeater Mode\n"
                    "3. Key up your radio\n"
                    "4. Dial a 4-digit code (e.g., 0-0-0-1)\n"
                    "5. Un-key and listen for the response\n\n"
                    "💡 Tips:\n"
                    "• Use slow, deliberate DTMF tones\n"
                    "• Wait for complete response before sending another command\n"
                    "• Commands work only in Repeater Mode (pass-through)")
        ttk.Label(parent, text=info_text, font=('Arial', 9), 
                 foreground='#666', wraplength=700, justify='left').pack(pady=10, padx=20)
    
    def toggle_weather(self):
        """Toggle weather service"""
        enabled = self.weather_enabled_var.get()
        self.parrot.weather.enabled = enabled
        if enabled:
            self.weather_status_label.config(text="Weather: Enabled", foreground='green')
            # Fetch weather immediately
            threading.Thread(target=self.fetch_weather_background, daemon=True).start()
        else:
            self.weather_status_label.config(text="Weather: Disabled", foreground='gray')
        self.save_config()
    
    def toggle_weather_in_id(self):
        """Toggle weather in ID"""
        self.parrot.include_weather_in_id = self.weather_include_id_var.get()
        self.save_config()
    
    def update_weather_zip(self):
        """Update weather ZIP code"""
        zip_code = self.weather_zip_var.get()
        self.parrot.weather.zip_code = zip_code
        self.parrot.weather.use_manual_coords = False  # Use ZIP lookup
        self.parrot.weather.latitude = None
        self.parrot.weather.longitude = None
        self.weather_status_label.config(text="Weather: Updating...", foreground='orange')
        threading.Thread(target=self.fetch_weather_background, daemon=True).start()
        self.save_config()
    
    def set_manual_coords(self):
        """Set manual coordinates"""
        try:
            lat = float(self.weather_lat_var.get())
            lon = float(self.weather_lon_var.get())
            
            if not (-90 <= lat <= 90):
                messagebox.showerror("Error", "Latitude must be between -90 and 90")
                return
            if not (-180 <= lon <= 180):
                messagebox.showerror("Error", "Longitude must be between -180 and 180")
                return
            
            self.parrot.weather.set_coordinates(lat, lon)
            self.weather_status_label.config(text=f"Coordinates set: {lat:.4f}, {lon:.4f}", foreground='blue')
            
            # Fetch weather with these coordinates
            threading.Thread(target=self.fetch_weather_background, daemon=True).start()
            self.save_config()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid decimal coordinates\nExample: Lat 43.6039, Lon -71.2356")
    
    def test_weather_connection(self):
        """Test weather API connectivity"""
        self.weather_status_label.config(text="Testing connection...", foreground='orange')
        threading.Thread(target=self._test_weather_thread, daemon=True).start()
    
    def _test_weather_thread(self):
        """Background thread for testing weather connection"""
        try:
            import requests
            
            # Test 1: Can we reach the internet?
            print("\n🧪 WEATHER CONNECTION TEST")
            print("="*60)
            print("Test 1: Internet connectivity...")
            try:
                response = requests.get("https://www.google.com", timeout=5)
                print(f"✅ Internet: OK (Status {response.status_code})")
            except:
                print("❌ Internet: FAILED - No internet connection")
                self.weather_status_label.config(text="Test: No internet connection", foreground='red')
                return
            
            # Test 2: Can we reach weather.gov?
            print("Test 2: Weather.gov API...")
            try:
                headers = {"User-Agent": "HamRadioRepeater/1.0 (Python-requests)"}
                response = requests.get("https://api.weather.gov/", headers=headers, timeout=10)
                print(f"✅ Weather.gov: OK (Status {response.status_code})")
            except Exception as e:
                print(f"❌ Weather.gov: FAILED - {e}")
                self.weather_status_label.config(text=f"Test: Cannot reach weather.gov", foreground='red')
                return
            
            # Test 3: Can we geocode?
            print("Test 3: Geocoding API...")
            zip_code = self.weather_zip_var.get()
            try:
                url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"
                params = {"address": zip_code, "benchmark": "2020", "format": "json"}
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("result", {}).get("addressMatches"):
                        print(f"✅ Geocoding: OK (found ZIP {zip_code})")
                    else:
                        print(f"⚠️ Geocoding: ZIP not found - try different ZIP or use manual coordinates")
                        self.weather_status_label.config(text=f"Test: ZIP {zip_code} not found", foreground='orange')
                        return
                else:
                    print(f"❌ Geocoding: HTTP {response.status_code}")
            except Exception as e:
                print(f"⚠️ Geocoding: FAILED - {e}")
                print("   You can use manual coordinates instead")
                self.weather_status_label.config(text="Test: Use manual coordinates", foreground='orange')
                return
            
            # Test 4: Full weather fetch
            print("Test 4: Full weather fetch...")
            weather = self.parrot.weather.fetch_weather()
            if weather:
                print(f"✅ ALL TESTS PASSED!")
                print(f"   Temperature: {weather['temperature']}°{weather['unit']}")
                print(f"   Conditions: {weather['conditions']}")
                print("="*60 + "\n")
                self.weather_status_label.config(
                    text=f"Test: SUCCESS! {weather['temperature']}°{weather['unit']}", 
                    foreground='green')
            else:
                print(f"❌ Weather fetch failed - check console for details")
                print("="*60 + "\n")
                self.weather_status_label.config(text="Test: Failed - check console", foreground='red')
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            import traceback
            traceback.print_exc()
            self.weather_status_label.config(text=f"Test: Error - {str(e)[:30]}", foreground='red')
    
    def fetch_weather_background(self):
        """Fetch weather in background thread"""
        try:
            weather = self.parrot.weather.fetch_weather()
            if weather:
                self.weather_status_label.config(
                    text=f"Weather: {weather['temperature']}°{weather['unit']}, {weather['conditions']}", 
                    foreground='green')
            else:
                self.weather_status_label.config(text="Weather: Failed to fetch", foreground='red')
        except Exception as e:
            self.weather_status_label.config(text=f"Weather: Error - {e}", foreground='red')
    
    def toggle_dtmf(self):
        """Toggle DTMF detection"""
        self.parrot.dtmf.enabled = self.dtmf_enabled_var.get()
        self.save_config()
    
    def test_dtmf_command(self):
        """Test a DTMF command"""
        command = self.test_dtmf_var.get()
        if len(command) != 4 or not command.isdigit():
            messagebox.showerror("Error", "Command must be exactly 4 digits (e.g., 0001)")
            return
        
        if not self.parrot.is_running:
            messagebox.showwarning("Warning", "Start the system first to test commands")
            return
        
        print(f"🧪 Testing DTMF command: {command}")
        self.parrot.handle_dtmf_command(command)
        messagebox.showinfo("Test", f"DTMF command {command} queued!\nListen for the announcement.")
    
    def save_dtmf_settings(self):
        """Save all DTMF custom messages"""
        # Update custom messages
        for key, var in self.dtmf_custom_vars.items():
            self.parrot.dtmf_messages[key] = var.get()
        
        self.save_config()
        messagebox.showinfo("Saved", "DTMF settings saved!")
    
    def load_settings_from_config(self):
        """Load all settings from config and apply to GUI"""
        try:
            # Repeater settings
            if hasattr(self, 'callsign_var'):
                self.callsign_var.set(self.config.get("callsign", "WRKC123"))
                self.parrot.repeater.callsign = self.callsign_var.get()
            
            if hasattr(self, 'id_interval_var'):
                id_interval = self.config.get("id_interval", 10.0)
                self.id_interval_var.set(id_interval)
                self.parrot.repeater.id_interval = id_interval * 60
                self.id_interval_label.config(text=f"{int(id_interval)} min")
            
            if hasattr(self, 'courtesy_tone_var'):
                courtesy_enabled = self.config.get("courtesy_tone_enabled", True)
                self.courtesy_tone_var.set(courtesy_enabled)
                self.parrot.repeater.enable_courtesy_tone = courtesy_enabled
            
            if hasattr(self, 'tone_freq_var'):
                tone_freq = self.config.get("courtesy_tone_freq", 1000)
                self.tone_freq_var.set(tone_freq)
                self.parrot.repeater.courtesy_tone_freq = tone_freq
                self.tone_freq_label.config(text=f"{int(tone_freq)} Hz")
            
            if hasattr(self, 'tone_volume_var'):
                tone_volume = self.config.get("courtesy_tone_volume", 0.5)
                self.tone_volume_var.set(tone_volume)
                self.parrot.repeater.courtesy_tone_volume = tone_volume
                self.tone_volume_label.config(text=f"{int(tone_volume*100)}%")
            
            if hasattr(self, 'tone_duration_var'):
                tone_duration = self.config.get("courtesy_tone_duration", 0.5)
                self.tone_duration_var.set(tone_duration)
                self.parrot.repeater.courtesy_tone_duration = tone_duration
                self.tone_duration_label.config(text=f"{tone_duration:.1f} sec")
            
            if hasattr(self, 'auto_id_var'):
                auto_id_enabled = self.config.get("auto_id_enabled", True)
                self.auto_id_var.set(auto_id_enabled)
                self.parrot.repeater.auto_id_enabled = auto_id_enabled
            
            # Audio gain settings
            if hasattr(self, 'input_gain_var'):
                input_gain = self.config.get("input_gain", 1.0)
                self.input_gain_var.set(input_gain)
                self.parrot.input_gain = input_gain
                self.input_gain_label.config(text=f"{int(input_gain*100)}%")
            
            if hasattr(self, 'output_gain_var'):
                output_gain = self.config.get("output_gain", 1.0)
                self.output_gain_var.set(output_gain)
                self.parrot.output_gain = output_gain
                self.output_gain_label.config(text=f"{int(output_gain*100)}%")
            
            if hasattr(self, 'timeout_var'):
                timeout = self.config.get("timeout_duration", 180)
                self.timeout_var.set(timeout)
                self.parrot.repeater.timeout_duration = timeout
                self.timeout_label.config(text=f"{int(timeout)} sec")
            
            if hasattr(self, 'ptt_predelay_var'):
                ptt_delay = self.config.get("ptt_pre_delay", 1.0)
                self.ptt_predelay_var.set(ptt_delay)
                self.parrot.ptt_pre_delay = ptt_delay
                self.ptt_predelay_label.config(text=f"{ptt_delay:.1f} sec")
            
            if hasattr(self, 'tail_silence_var'):
                tail_silence = self.config.get("tail_silence", 0.5)
                self.tail_silence_var.set(tail_silence)
                self.parrot.repeater.tail_silence_duration = tail_silence
                self.tail_silence_label.config(text=f"{tail_silence:.1f} sec")
            
            # VOX settings
            if hasattr(self, 'vox_enable_var'):
                vox_enabled = self.config.get("vox_enabled", False)
                self.vox_enable_var.set(vox_enabled)
                self.parrot.vox_enabled = vox_enabled
            
            if hasattr(self, 'vox_threshold_var'):
                vox_threshold = self.config.get("vox_threshold", 5.0)
                self.vox_threshold_var.set(vox_threshold)
                self.parrot.vox.threshold = vox_threshold
                self.vox_threshold_label.config(text=f"{vox_threshold:.1f}%")
            
            if hasattr(self, 'vox_attack_var'):
                vox_attack = self.config.get("vox_attack", 0.1)
                self.vox_attack_var.set(vox_attack)
                self.parrot.vox.attack_time = vox_attack
                self.parrot.vox.attack_samples = int(self.parrot.RATE * vox_attack / 1024)
                self.vox_attack_label.config(text=f"{vox_attack:.2f}s")
            
            if hasattr(self, 'vox_release_var'):
                vox_release = self.config.get("vox_release", 0.5)
                self.vox_release_var.set(vox_release)
                self.parrot.vox.release_time = vox_release
                self.parrot.vox.release_samples = int(self.parrot.RATE * vox_release / 1024)
                self.vox_release_label.config(text=f"{vox_release:.2f}s")
            
            # Feedback protection settings
            if hasattr(self, 'feedback_protection_var'):
                feedback_enabled = self.config.get("feedback_protection_enabled", True)
                self.feedback_protection_var.set(feedback_enabled)
                self.parrot.feedback_protection_enabled = feedback_enabled
                if feedback_enabled:
                    self.feedback_status_label.config(text="● Active", foreground='green')
                else:
                    self.feedback_status_label.config(text="○ Disabled", foreground='red')
            
            if hasattr(self, 'feedback_holdoff_var'):
                holdoff_time = self.config.get("feedback_holdoff_time", 1.5)
                self.feedback_holdoff_var.set(holdoff_time)
                self.parrot.feedback_holdoff_time = holdoff_time
                self.feedback_holdoff_label.config(text=f"{holdoff_time:.1f}s")
            
            # PTT settings
            if hasattr(self, 'ptt_mode_var'):
                ptt_mode = self.config.get("ptt_mode", "VOX")
                self.ptt_mode_var.set(ptt_mode)
                for mode in PTTMode:
                    if mode.value == ptt_mode:
                        self.parrot.ptt_mode = mode
                        break
            
            if hasattr(self, 'serial_port_var') and hasattr(self, 'serial_combo'):
                serial_port = self.config.get("serial_port", "")
                if serial_port and serial_port in self.serial_combo['values']:
                    self.serial_port_var.set(serial_port)
            
            # Mode settings
            if hasattr(self, 'mode_var'):
                recording_mode = self.config.get("recording_mode", "Repeater Mode")
                self.mode_var.set(recording_mode)
                for mode in RecordingMode:
                    if mode.value == recording_mode:
                        self.parrot.recording_mode = mode
                        break
            
            if hasattr(self, 'timer_var'):
                max_time = self.config.get("max_record_time", 30.0)
                self.timer_var.set(max_time)
                self.parrot.max_record_time = max_time
                self.timer_value_label.config(text=f"{int(max_time)}s")
            
            if hasattr(self, 'delay_var'):
                delay_time = self.config.get("delay_time", 2.0)
                self.delay_var.set(delay_time)
                self.parrot.DELAY_SECONDS = delay_time
                self.delay_value_label.config(text=f"{delay_time:.1f}s")
            
            if hasattr(self, 'ptt_prekey_delay_var'):
                ptt_prekey = self.config.get("ptt_prekey_time", 0.5)
                self.ptt_prekey_delay_var.set(ptt_prekey)
                self.parrot.ptt_prekey_time = ptt_prekey
                self.ptt_prekey_delay_label.config(text=f"{ptt_prekey:.1f}s")
            
            # Audio devices - parse and set device indices
            input_dev = self.config.get("input_device", "Default")
            output_dev = self.config.get("output_device", "Default")
            
            if input_dev and input_dev != "Default":
                try:
                    input_index = int(input_dev.split(':')[0])
                    self.parrot.input_device_index = input_index
                    print(f"Loaded input device index: {input_index}")
                    # Also update GUI dropdown
                    if hasattr(self, 'input_device_var'):
                        self.input_device_var.set(input_dev)
                except (ValueError, IndexError):
                    pass
            
            if output_dev and output_dev != "Default":
                try:
                    output_index = int(output_dev.split(':')[0])
                    self.parrot.output_device_index = output_index
                    print(f"Loaded output device index: {output_index}")
                    # Also update GUI dropdown
                    if hasattr(self, 'output_device_var'):
                        self.output_device_var.set(output_dev)
                except (ValueError, IndexError):
                    pass
            
            # Weather settings
            if hasattr(self, 'weather_enabled_var'):
                weather_enabled = self.config.get("weather_enabled", False)
                self.weather_enabled_var.set(weather_enabled)
                self.parrot.weather.enabled = weather_enabled
                if weather_enabled:
                    self.weather_status_label.config(text="Weather: Enabled", foreground='green')
            
            if hasattr(self, 'weather_zip_var'):
                weather_zip = self.config.get("weather_zip", "03894")
                self.weather_zip_var.set(weather_zip)
                self.parrot.weather.zip_code = weather_zip
            
            if hasattr(self, 'weather_include_id_var'):
                weather_in_id = self.config.get("weather_include_in_id", False)
                self.weather_include_id_var.set(weather_in_id)
                self.parrot.include_weather_in_id = weather_in_id
            
            # Manual coordinates
            if hasattr(self, 'weather_lat_var'):
                weather_lat = self.config.get("weather_manual_lat", "")
                weather_lon = self.config.get("weather_manual_lon", "")
                if weather_lat and weather_lon:
                    self.weather_lat_var.set(weather_lat)
                    self.weather_lon_var.set(weather_lon)
                    try:
                        lat = float(weather_lat)
                        lon = float(weather_lon)
                        self.parrot.weather.set_coordinates(lat, lon)
                    except:
                        pass
            
            # DTMF settings
            if hasattr(self, 'dtmf_enabled_var'):
                dtmf_enabled = self.config.get("dtmf_enabled", False)
                self.dtmf_enabled_var.set(dtmf_enabled)
                self.parrot.dtmf.enabled = dtmf_enabled
            
            # Debug mode
            if hasattr(self, 'debug_mode_var'):
                debug_mode = self.config.get("debug_mode", False)
                self.debug_mode_var.set(debug_mode)
                self.parrot.debug_mode = debug_mode
                self.parrot.weather.debug_mode = debug_mode
                self.parrot.dtmf.debug_mode = debug_mode
            
            # DTMF custom messages
            if hasattr(self, 'dtmf_custom_vars'):
                for key, var in self.dtmf_custom_vars.items():
                    msg = self.config.get(f"dtmf_message_{key}", f"Custom message {key[-1]}")
                    var.set(msg)
                    self.parrot.dtmf_messages[key] = msg
            
            print("Settings loaded from config")
        except Exception as e:
            print(f"Error loading some settings: {e}")
    
    def save_config(self):
        """Save current settings to config - with safe hasattr checks"""
        try:
            # Core settings - these should always exist
            if hasattr(self, 'callsign_var'):
                self.config["callsign"] = self.callsign_var.get()
            if hasattr(self, 'id_interval_var'):
                self.config["id_interval"] = self.id_interval_var.get()
            if hasattr(self, 'courtesy_tone_var'):
                self.config["courtesy_tone_enabled"] = self.courtesy_tone_var.get()
            if hasattr(self, 'tone_freq_var'):
                self.config["courtesy_tone_freq"] = self.tone_freq_var.get()
            if hasattr(self, 'tone_volume_var'):
                self.config["courtesy_tone_volume"] = self.tone_volume_var.get()
            if hasattr(self, 'tone_duration_var'):
                self.config["courtesy_tone_duration"] = self.tone_duration_var.get()
            if hasattr(self, 'auto_id_var'):
                self.config["auto_id_enabled"] = self.auto_id_var.get()
            if hasattr(self, 'input_gain_var'):
                self.config["input_gain"] = self.input_gain_var.get()
            if hasattr(self, 'output_gain_var'):
                self.config["output_gain"] = self.output_gain_var.get()
            if hasattr(self, 'timeout_var'):
                self.config["timeout_duration"] = self.timeout_var.get()
            if hasattr(self, 'ptt_predelay_var'):
                self.config["ptt_pre_delay"] = self.ptt_predelay_var.get()
            if hasattr(self, 'tail_silence_var'):
                self.config["tail_silence"] = self.tail_silence_var.get()
            
            # VOX settings
            if hasattr(self, 'vox_enable_var'):
                self.config["vox_enabled"] = self.vox_enable_var.get()
            if hasattr(self, 'vox_threshold_var'):
                self.config["vox_threshold"] = self.vox_threshold_var.get()
            if hasattr(self, 'vox_attack_var'):
                self.config["vox_attack"] = self.vox_attack_var.get()
            if hasattr(self, 'vox_release_var'):
                self.config["vox_release"] = self.vox_release_var.get()
            
            # Feedback protection settings
            if hasattr(self, 'feedback_protection_var'):
                self.config["feedback_protection_enabled"] = self.feedback_protection_var.get()
            if hasattr(self, 'feedback_holdoff_var'):
                self.config["feedback_holdoff_time"] = self.feedback_holdoff_var.get()
            
            # PTT settings
            if hasattr(self, 'ptt_mode_var'):
                self.config["ptt_mode"] = self.ptt_mode_var.get()
            if hasattr(self, 'serial_port_var'):
                self.config["serial_port"] = self.serial_port_var.get()
            
            # Mode settings
            if hasattr(self, 'mode_var'):
                self.config["recording_mode"] = self.mode_var.get()
            
            # Optional mode-specific settings
            if hasattr(self, 'timer_var'):
                self.config["max_record_time"] = self.timer_var.get()
            
            if hasattr(self, 'delay_var'):
                self.config["delay_time"] = self.delay_var.get()
            
            if hasattr(self, 'ptt_prekey_delay_var'):
                self.config["ptt_prekey_time"] = self.ptt_prekey_delay_var.get()
            
            # Weather settings
            if hasattr(self, 'weather_enabled_var'):
                self.config["weather_enabled"] = self.weather_enabled_var.get()
            if hasattr(self, 'weather_zip_var'):
                self.config["weather_zip"] = self.weather_zip_var.get()
            if hasattr(self, 'weather_include_id_var'):
                self.config["weather_include_in_id"] = self.weather_include_id_var.get()
            if hasattr(self, 'weather_lat_var'):
                self.config["weather_manual_lat"] = self.weather_lat_var.get()
            if hasattr(self, 'weather_lon_var'):
                self.config["weather_manual_lon"] = self.weather_lon_var.get()
            
            # DTMF settings
            if hasattr(self, 'dtmf_enabled_var'):
                self.config["dtmf_enabled"] = self.dtmf_enabled_var.get()
            
            # Debug mode
            if hasattr(self, 'debug_mode_var'):
                self.config["debug_mode"] = self.debug_mode_var.get()
            
            # DTMF custom messages
            if hasattr(self, 'dtmf_custom_vars'):
                for key, var in self.dtmf_custom_vars.items():
                    self.config[f"dtmf_message_{key}"] = var.get()
            
            # Save to file
            self.config_manager.save_config(self.config)
        except Exception as e:
            print(f"Warning: Error saving config: {e}")
            # Don't crash if save fails
    
    def save_config_menu(self):
        """Save configuration from File menu"""
        self.save_config()
        messagebox.showinfo("Configuration Saved", 
                          "Settings have been saved to repeater_config.json")
    
    def reload_config_menu(self):
        """Reload configuration from file"""
        try:
            self.config = self.config_manager.load_config()
            self.load_settings_from_config()
            messagebox.showinfo("Configuration Reloaded", 
                              "Settings have been reloaded from repeater_config.json")
        except Exception as e:
            messagebox.showerror("Reload Error", 
                               f"Error reloading config: {e}")
    
    # Event handlers
    def start_parrot(self):
        """Start the system"""
        try:
            self.parrot.start()
            self.status_label.config(text="● RUNNING", foreground='green')
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.manual_id_button.config(state='normal')
            self.save_recording_button.config(state='normal')
            
            # Enable recording controls for parrot and manual modes
            if self.parrot.recording_mode in [RecordingMode.CONTINUOUS_DELAY, RecordingMode.MANUAL]:
                self.start_rec_button.config(state='normal')
            
            self.update_levels()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start:\n{e}")
    
    def stop_parrot(self):
        """Stop the system"""
        self.parrot.stop()
        self.status_label.config(text="● STOPPED", foreground='red')
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.manual_id_button.config(state='disabled')
        self.save_recording_button.config(state='disabled')
        self.start_rec_button.config(state='disabled')
        self.stop_rec_button.config(state='disabled')
        
        if self.update_job:
            self.root.after_cancel(self.update_job)
            self.update_job = None
        
        self.reset_levels()
    
    def change_mode(self):
        """Change recording mode"""
        mode_name = self.mode_var.get()
        for mode in RecordingMode:
            if mode.value == mode_name:
                # Reset any in-progress record/play when switching modes
                self.parrot.is_recording = False
                self.parrot.is_playing_back = False
                self.parrot.playback_index = 0
                self.parrot.record_start_time = 0
                self.parrot.recorded_audio = []

                self.parrot.recording_mode = mode
                print(f"Mode changed to: {mode.value}")

                # If system is running and we switched into Timed Auto-Replay,
                # begin the loop immediately.
                if self.parrot.is_running and mode == RecordingMode.TIMED_REPLAY:
                    self.parrot.start_recording()
                break
        self.save_config()
    
    def manual_id(self):
        """Manually trigger station ID"""
        if self.parrot.is_running:
            self.parrot.queue_announcement(self.parrot.repeater.generate_id_announcement())
    
    def test_audio_output(self):
        """Test audio output with a beep"""
        if not self.parrot.is_running:
            messagebox.showinfo("Info", "Start the system first, then test audio")
            return
        
        # Generate a test beep
        print("Generating test beep...")
        test_audio = self.parrot.repeater.generate_courtesy_tone(self.parrot.RATE)
        print(f"Test beep generated: {len(test_audio)} samples, peak: {np.abs(test_audio).max()}")
        
        # Queue it for playback
        self.parrot.announcement_ready_queue.put(test_audio)
        messagebox.showinfo("Test", "Test beep queued! You should hear a tone.\nCheck your speakers/output device if you don't hear anything.")
    
    def manual_save_recording(self):
        """Manually save current recording buffer"""
        if not self.parrot.is_running:
            messagebox.showwarning("Warning", "System must be running to save recordings")
            return
        
        # Check if there's any recorded audio
        if not self.parrot.recorded_audio or len(self.parrot.recorded_audio) == 0:
            messagebox.showinfo("Info", 
                               "No recording to save.\n\n" +
                               "For Parrot Mode (Continuous Delay):\n" +
                               "• Press START RECORDING to begin capturing\n" +
                               "• Press STOP RECORDING when done\n" +
                               "• Then click SAVE RECORDING\n\n" +
                               "Recording is also automatic in other modes.")
            return
        
        # Ask for filename
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        mode = self.parrot.recording_mode.value.replace(" ", "_")
        default_filename = f"recording_{mode}_{ts}.wav"
        
        filename = filedialog.asksaveasfilename(
            initialdir=self.recordings_dir,
            initialfile=default_filename,
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav"), ("All files", "*.*")]
        )
        
        if filename:
            if self.parrot.save_recording(filename):
                # Add to list
                self.recordings_history.append(filename)
                if hasattr(self, 'recordings_listbox'):
                    basename = os.path.basename(filename)
                    self.recordings_listbox.insert(0, basename)
                messagebox.showinfo("Success", f"Recording saved!\n{filename}")
            else:
                messagebox.showerror("Error", "Failed to save recording")
    
    def start_recording_clicked(self):
        """Start recording button clicked"""
        if not self.parrot.is_running:
            messagebox.showwarning("Warning", "Start the system first")
            return
        
        # Clear previous recording
        self.parrot.recorded_audio = []
        self.parrot.start_recording()
        
        # Update button states
        self.start_rec_button.config(state='disabled')
        self.stop_rec_button.config(state='normal')
        
        print("🔴 Recording started by user")
    
    def stop_recording_clicked(self):
        """Stop recording button clicked"""
        if not self.parrot.is_running:
            return
        
        self.parrot.stop_recording()
        
        # Update button states
        self.start_rec_button.config(state='normal')
        self.stop_rec_button.config(state='disabled')
        
        chunks = len(self.parrot.recorded_audio)
        duration = chunks * self.parrot.CHUNK / self.parrot.RATE
        print(f"⏹️ Recording stopped by user - {chunks} chunks ({duration:.1f} seconds)")
        
        if chunks > 0:
            messagebox.showinfo("Recording Complete", 
                               f"Recorded {duration:.1f} seconds of audio\n\n" +
                               "Click SAVE RECORDING to save it to a file")
    
    def show_audio_devices(self):
        """Show available audio devices"""
        devices_info = "Available Audio Devices:\n\n"
        
        try:
            audio = pyaudio.PyAudio()
            for i in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(i)
                devices_info += f"Device {i}: {info['name']}\n"
                devices_info += f"  Inputs: {info['maxInputChannels']}, Outputs: {info['maxOutputChannels']}\n"
                devices_info += f"  Default Rate: {info['defaultSampleRate']}\n\n"
            audio.terminate()
            
            # Create a scrollable text window
            window = tk.Toplevel(self.root)
            window.title("Audio Devices")
            window.geometry("600x400")
            
            text = tk.Text(window, wrap='word')
            text.pack(fill='both', expand=True, padx=10, pady=10)
            text.insert('1.0', devices_info)
            text.config(state='disabled')
            
            ttk.Button(window, text="Close", command=window.destroy).pack(pady=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get audio devices:\n{e}")
    
    def update_callsign(self):
        """Update repeater callsign"""
        callsign = self.callsign_var.get().strip().upper()
        self.parrot.repeater.callsign = callsign
        self.save_config()
        print(f"Callsign updated to: {callsign}")
    
    def update_id_interval(self, value):
        """Update ID interval"""
        interval = float(value)
        self.id_interval_label.config(text=f"{int(interval)} min")
        self.parrot.repeater.id_interval = interval * 60  # Convert to seconds
        self.save_config()
    
    def toggle_courtesy_tone(self):
        """Toggle courtesy tone"""
        self.parrot.repeater.enable_courtesy_tone = self.courtesy_tone_var.get()
        self.save_config()
    
    def update_tone_freq(self, value):
        """Update courtesy tone frequency"""
        freq = float(value)
        self.tone_freq_label.config(text=f"{int(freq)} Hz")
        self.parrot.repeater.courtesy_tone_freq = freq
        self.save_config()
    
    def update_tone_volume(self, value):
        """Update courtesy tone volume"""
        volume = float(value)
        self.tone_volume_label.config(text=f"{int(volume*100)}%")
        self.parrot.repeater.courtesy_tone_volume = volume
        self.save_config()
    
    def update_tone_duration(self, value):
        """Update courtesy tone duration"""
        duration = float(value)
        self.tone_duration_label.config(text=f"{duration:.1f} sec")
        self.parrot.repeater.courtesy_tone_duration = duration
        self.save_config()
    
    def toggle_auto_id(self):
        """Toggle automatic ID announcements"""
        self.parrot.repeater.auto_id_enabled = self.auto_id_var.get()
        self.save_config()
        if self.auto_id_var.get():
            print("Automatic ID announcements enabled")
        else:
            print("Automatic ID announcements disabled")
    
    def update_input_gain(self, value):
        """Update input gain"""
        gain = float(value)
        self.input_gain_label.config(text=f"{int(gain*100)}%")
        self.parrot.input_gain = gain
        self.save_config()
    
    def update_output_gain(self, value):
        """Update output gain"""
        gain = float(value)
        self.output_gain_label.config(text=f"{int(gain*100)}%")
        self.parrot.output_gain = gain
        self.save_config()
    
    def update_timeout(self, value):
        """Update timeout timer"""
        timeout = float(value)
        self.timeout_label.config(text=f"{int(timeout)} sec")
        self.parrot.repeater.timeout_duration = timeout
        self.save_config()
    
    def update_ptt_predelay(self, value):
        """Update PTT pre-delay"""
        delay = float(value)
        self.ptt_predelay_label.config(text=f"{delay:.1f} sec")
        self.parrot.ptt_pre_delay = delay
        self.save_config()
    
    def update_tail_silence(self, value):
        """Update tail silence duration"""
        duration = float(value)
        self.tail_silence_label.config(text=f"{duration:.1f} sec")
        self.parrot.repeater.tail_silence_duration = duration
        self.save_config()
    
    def toggle_feedback_protection(self):
        """Toggle feedback protection"""
        enabled = self.feedback_protection_var.get()
        self.parrot.feedback_protection_enabled = enabled
        
        if enabled:
            self.feedback_status_label.config(text="● Active", foreground='green')
            print("Feedback protection ENABLED")
        else:
            self.feedback_status_label.config(text="○ Disabled", foreground='red')
            print("Feedback protection DISABLED")
        
        self.save_config()
    
    def update_feedback_holdoff(self, value):
        """Update feedback protection holdoff time"""
        holdoff = float(value)
        self.feedback_holdoff_label.config(text=f"{holdoff:.1f}s")
        self.parrot.feedback_holdoff_time = holdoff
        self.save_config()
    
    def update_delay(self, value):
        """Update delay value for continuous mode"""
        delay = float(value)
        self.delay_value_label.config(text=f"{delay:.1f}s")
        if self.parrot.is_running:
            self.parrot.set_delay(delay)
        self.save_config()
    
    def update_timer(self, value):
        """Update max record time"""
        timer = float(value)
        self.timer_value_label.config(text=f"{int(timer)}s")
        self.parrot.max_record_time = timer
        self.save_config()
    
    def send_custom_announcement(self):
        """Send custom announcement"""
        text = self.custom_announce_var.get().strip()
        if text and self.parrot.is_running:
            self.parrot.queue_announcement(text)
            self.custom_announce_var.set("")
            messagebox.showinfo("Queued", "Announcement queued and will play when channel is clear")
    
    def toggle_vox(self):
        """Toggle VOX"""
        self.parrot.vox_enabled = self.vox_enable_var.get()
        self.save_config()
    
    def toggle_debug_mode(self):
        """Toggle debug mode"""
        debug_enabled = self.debug_mode_var.get()
        self.parrot.debug_mode = debug_enabled
        self.parrot.weather.debug_mode = debug_enabled
        self.parrot.dtmf.debug_mode = debug_enabled
        self.save_config()
        if debug_enabled:
            print("🔧 Debug mode ENABLED - Verbose console output active")
        else:
            print("🔧 Debug mode DISABLED - Minimal console output")
    
    def update_vox_threshold(self, value):
        """Update VOX threshold"""
        threshold = float(value)
        self.vox_threshold_label.config(text=f"{threshold:.1f}%")
        self.parrot.vox.threshold = threshold
        self.save_config()
    
    def update_vox_attack(self, value):
        """Update VOX attack time"""
        attack = float(value)
        self.vox_attack_label.config(text=f"{attack:.2f}s")
        self.parrot.vox.attack_time = attack
        self.parrot.vox.attack_samples = int(self.parrot.RATE * attack / 1024)
        self.save_config()
    
    def update_vox_release(self, value):
        """Update VOX release time"""
        release = float(value)
        self.vox_release_label.config(text=f"{release:.2f}s")
        self.parrot.vox.release_time = release
        self.parrot.vox.release_samples = int(self.parrot.RATE * release / 1024)
        self.save_config()
    
    def change_ptt_mode(self):
        """Change PTT mode"""
        mode_name = self.ptt_mode_var.get()
        for mode in PTTMode:
            if mode.value == mode_name:
                self.parrot.ptt_mode = mode
                print(f"PTT mode changed to: {mode.value}")
                break
        self.save_config()
    
    def refresh_serial_ports(self):
        """Refresh serial ports"""
        ports = PTTController.get_available_ports()
        self.serial_combo['values'] = ports
        if ports:
            self.serial_combo.current(0)
    
    def connect_serial(self):
        """Connect to serial port"""
        port = self.serial_port_var.get()
        if not port:
            messagebox.showwarning("Warning", "Please select a serial port")
            return
        
        if self.parrot.ptt_controller.is_connected:
            self.parrot.ptt_controller.disconnect()
            self.connect_button.config(text="Connect")
            self.serial_status_label.config(text="○ Not connected")
        else:
            # Set relay type before connecting
            relay_type = self.relay_type_var.get()
            self.parrot.ptt_controller.set_relay_type(relay_type)
            
            if self.parrot.ptt_controller.connect(port):
                self.connect_button.config(text="Disconnect")
                self.serial_status_label.config(text=f"● Connected to {port} ({relay_type})", 
                                              foreground='green')
                self.save_config()  # Save the port
            else:
                messagebox.showerror("Error", f"Failed to connect to {port}")
    
    def change_relay_type(self):
        """Change relay type"""
        relay_type = self.relay_type_var.get()
        self.parrot.ptt_controller.set_relay_type(relay_type)
        self.save_config()
        print(f"Relay type changed to: {relay_type}")
        
        # If already connected, reconnect with new type
        if self.parrot.ptt_controller.is_connected:
            port = self.parrot.ptt_controller.port_name
            self.parrot.ptt_controller.disconnect()
            self.parrot.ptt_controller.connect(port)
            self.serial_status_label.config(text=f"● Connected to {port} ({relay_type})", 
                                          foreground='green')
    
    def test_ptt(self, state):
        """Test PTT"""
        if not self.parrot.ptt_controller.is_connected:
            messagebox.showwarning("Warning", "Serial port not connected")
            return
        
        if state:
            self.parrot.ptt_controller.ptt_on()
            self.ptt_status_label.config(text="● PTT ON", foreground='red')
        else:
            self.parrot.ptt_controller.ptt_off()
            self.ptt_status_label.config(text="○ PTT OFF", foreground='black')
    
    def update_levels(self):
        """Update audio levels"""
        if self.parrot.is_running:
            input_level = min(100, self.parrot.input_level)
            self.input_level_bar['value'] = input_level
            self.input_level_label.config(text=f"{int(input_level)}%")
            
            output_level = min(100, self.parrot.output_level)
            self.output_level_bar['value'] = output_level
            self.output_level_label.config(text=f"{int(output_level)}%")
            
            # Update audio device tab levels
            if hasattr(self, 'input_device_level_bar'):
                self.input_device_level_bar['value'] = input_level
                self.input_device_level_label.config(text=f"{int(input_level)}%")
            
            if hasattr(self, 'output_device_level_bar'):
                self.output_device_level_bar['value'] = output_level
                self.output_device_level_label.config(text=f"{int(output_level)}%")
            
            # Update waveforms
            if hasattr(self, 'update_waveforms'):
                self.update_waveforms()
            
            # VOX status
            if self.parrot.vox.is_active:
                self.vox_status_label.config(text="● Active", foreground='green')
            else:
                self.vox_status_label.config(text="○ Inactive", foreground='black')
            
            # PTT status
            if self.parrot.ptt_controller.ptt_active or self.parrot.is_announcing:
                self.ptt_status_label.config(text="● PTT ON", foreground='red')
            else:
                self.ptt_status_label.config(text="○ PTT OFF", foreground='black')
            
            # Feedback protection status
            if hasattr(self, 'feedback_status_label') and self.parrot.feedback_protection_enabled:
                if self.parrot.is_in_holdoff:
                    self.feedback_status_label.config(text="● Muting Input", foreground='orange')
                else:
                    self.feedback_status_label.config(text="● Active", foreground='green')
            
            self.update_job = self.root.after(50, self.update_levels)
    
    def reset_levels(self):
        """Reset levels"""
        self.input_level_bar['value'] = 0
        self.output_level_bar['value'] = 0
        self.input_level_label.config(text="0%")
        self.output_level_label.config(text="0%")
        self.vox_status_label.config(text="○ Inactive", foreground='black')
        self.ptt_status_label.config(text="○ PTT OFF", foreground='black')
    
    def on_recording_complete(self):
        """Recording complete callback"""
        # Auto-save the most recent recording to the recordings folder and update the list.
        try:
            if not self.parrot.recorded_audio:
                return

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            mode = self.parrot.recording_mode.value.replace(" ", "_")
            filename = f"recording_{mode}_{ts}.wav"
            path = os.path.join(self.recordings_dir, filename)

            if self.parrot.save_recording(path):
                # Keep a simple history list and UI listbox
                self.recordings_history.append(path)
                if hasattr(self, 'recordings_listbox'):
                    # Show newest at top
                    self.recordings_listbox.insert(0, filename)
            else:
                print("Recording complete but failed to save WAV")
        except Exception as e:
            print(f"Error saving recording: {e}")
    
    def on_vox_state_change(self, active):
        """VOX state change callback"""
        if active:
            self.vox_status_label.config(text="● Active", foreground='green')
        else:
            self.vox_status_label.config(text="○ Inactive", foreground='black')
    
    def open_recordings_folder(self):
        """Open recordings folder"""
        try:
            folder = self.recordings_dir
            if not os.path.isdir(folder):
                os.makedirs(folder, exist_ok=True)

            # Cross-platform open
            if os.name == 'nt':
                os.startfile(folder)  # type: ignore[attr-defined]
            elif sys.platform == 'darwin':
                import subprocess
                subprocess.Popen(['open', folder])
            else:
                import subprocess
                subprocess.Popen(['xdg-open', folder])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open recordings folder:\n{e}")
    
    def on_closing(self):
        """Handle window close"""
        if self.parrot.is_running:
            self.stop_parrot()
        self.save_config()  # Save config on exit
        self.parrot.cleanup()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ParrotBoxGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
