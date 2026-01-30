# Contributing to Soft Repeater Box

First off, **thank you** for considering contributing to Soft Repeater Box! 🎉

The amateur radio community thrives on collaboration, and your contributions help make this project better for everyone.

---

## 🤝 **How to Contribute**

### Reporting Bugs 🐛

Found a bug? Help us squash it!

1. **Check existing issues** first to avoid duplicates
2. **Open a new issue** with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (OS, Python version, radio model)
   - Console output (with Debug Mode enabled!)
   - Screenshots if relevant

**Template**:
```
**Bug Description**: 
Brief description of the problem

**Steps to Reproduce**:
1. Step one
2. Step two
3. See error

**Expected Behavior**:
What should happen

**Actual Behavior**:
What actually happens

**Environment**:
- OS: Windows 11
- Python: 3.11.0
- Radio: Baofeng UV-5R
- Relay: x003qjjrql USB module

**Console Output**:
```
[Paste console output here with Debug Mode ON]
```

**Screenshots**:
[If applicable]
```

### Suggesting Features 💡

Have an idea? We'd love to hear it!

1. **Check the roadmap** in README.md
2. **Search existing issues** for similar requests
3. **Open a feature request** with:
   - Clear use case
   - Expected behavior
   - Why it would benefit users
   - Potential implementation ideas (optional)

### Pull Requests 🔀

Want to contribute code? Awesome!

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**: `git commit -m "Add amazing feature"`
6. **Push to your fork**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

**PR Guidelines**:
- Keep changes focused (one feature per PR)
- Follow existing code style
- Add comments for complex logic
- Update documentation if needed
- Test on your actual hardware if possible

---

## 🎯 **Good First Issues**

New to the project? Start here:

- 📝 Documentation improvements
- 🐛 Simple bug fixes
- 🧪 Testing on different platforms
- 📊 Adding error messages
- 🎨 GUI improvements
- 📖 Expanding WIRING.md with more radios

Look for issues tagged `good first issue` on GitHub!

---

## 💻 **Development Setup**

### Prerequisites
- Python 3.8+
- Git
- Your radio equipment (for testing)

### Setup Steps
```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/soft-repeater-box.git
cd soft-repeater-box

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python soft_repeater_box.py

# 5. Make your changes

# 6. Test thoroughly!
```

### Testing Checklist
- [ ] All 4 modes work
- [ ] VOX triggers correctly
- [ ] PTT activates relay
- [ ] DTMF commands detect properly
- [ ] Weather fetches successfully
- [ ] Configuration saves/loads
- [ ] No console errors
- [ ] Debug mode works
- [ ] Test on actual radio (if possible)

---

## 📋 **Code Style**

### Python Style
- Follow PEP 8 (mostly)
- Use descriptive variable names
- Add docstrings for functions
- Comment complex logic
- Keep functions focused and small

**Example**:
```python
def calculate_audio_level(audio_data, sample_rate):
    """
    Calculate RMS audio level from raw audio data.
    
    Args:
        audio_data: Raw audio bytes
        sample_rate: Sample rate in Hz
        
    Returns:
        float: Audio level as percentage (0-100)
    """
    # Convert bytes to numpy array
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    
    # Calculate RMS level
    rms = np.sqrt(np.mean(audio_array**2))
    
    # Convert to percentage
    return (rms / 32768.0) * 100
```

### Git Commit Messages
- Use present tense: "Add feature" not "Added feature"
- Be descriptive but concise
- Reference issues: "Fix #42: Resolve DTMF detection bug"

**Good**:
```
Add weather caching to reduce API calls

- Cache weather for 30 minutes
- Add timestamp to weather data
- Show cache age in status
```

**Not so good**:
```
fixed stuff
```

---

## 🧪 **Testing**

### Manual Testing
- Test all operating modes
- Verify PTT control
- Test DTMF detection
- Check weather fetching
- Verify configuration save/load
- Test with actual radio equipment

### Platform Testing
If you can test on different platforms, please do!
- Windows 10/11
- Linux (Ubuntu, Debian, etc.)
- macOS
- Raspberry Pi

### Radio Testing
Have a different radio? Test and document!
- Document any special wiring needs
- Note any compatibility issues
- Share your working configuration

---

## 📝 **Documentation**

Good documentation is crucial!

### What Needs Documentation
- New features
- Changed behavior
- New DTMF commands
- Radio-specific wiring
- Troubleshooting tips
- Configuration options

### Where to Document
- **README.md**: Main features, quick start
- **WIRING.md**: Hardware connections, pinouts
- **CHANGELOG.md**: Version changes
- **Code comments**: Complex logic
- **GitHub Wiki**: Extended guides (future)

---

## 🏆 **Recognition**

Contributors will be:
- Listed in CONTRIBUTORS.md (create this!)
- Mentioned in release notes
- Credited in commit messages
- Thanked profusely! 🙏

---

## 🐛 **Bug Priority**

### Critical (Fix ASAP)
- Crashes
- Data loss
- Security issues
- Complete feature breakage

### High
- Major functionality broken
- Incorrect behavior
- Performance issues

### Medium
- Minor bugs
- Cosmetic issues
- Enhancement requests

### Low
- Nice-to-haves
- Future features
- Documentation typos

---

## 💬 **Communication**

### Where to Discuss
- **GitHub Issues**: Bug reports, features
- **GitHub Discussions**: General questions, ideas
- **Email**: host@nhscan.com (direct contact)

### Response Time
- **Bugs**: Within 48 hours
- **PRs**: Within 1 week
- **Features**: Within 2 weeks
- **General**: When possible!

*Note: This is a hobby project - response times may vary!*

---

## 🎓 **Learning Resources**

New to contributing? Check these out:

- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)
- [How to Write Good Git Commits](https://chris.beams.io/posts/git-commit/)
- [Python Style Guide (PEP 8)](https://www.python.org/dev/peps/pep-0008/)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/docs/)

---

## ⚖️ **Code of Conduct**

### Be Respectful
- Treat everyone with respect
- Be patient with beginners
- Provide constructive feedback
- Focus on the code, not the person

### Be Professional
- No harassment or discrimination
- No spam or off-topic content
- No personal attacks
- Keep discussions civil

### Amateur Radio Spirit
- Help fellow hams
- Share knowledge freely
- Promote experimentation
- Support the community

**73!** 📻

---

## 📞 **Questions?**

Not sure about something? Just ask!

- **Email**: host@nhscan.com
- **GitHub Discussions**: [Ask a Question](https://github.com/nhscan/soft-repeater-box/discussions)
- **Issues**: [Open an Issue](https://github.com/nhscan/soft-repeater-box/issues)

---

## 💝 **Thank You!**

Every contribution, no matter how small, makes a difference!

Whether you:
- Fix a typo
- Report a bug
- Add a feature
- Share feedback
- Star the project
- Tell a friend

**You're helping make Soft Repeater Box better for everyone!**

**73 and thanks for contributing!** 📻

---

**Author**: NHscan  
**Donate**: CashApp [$NHlife](https://cash.app/$NHlife)
