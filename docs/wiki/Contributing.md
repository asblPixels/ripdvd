# Contributing

Thank you for considering contributing to ripdvd! 🎉

## How to contribute

1. **Fork** the repository on GitHub.
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ripdvd.git
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature
   ```
4. **Make your changes** and test them on your system.
5. **Commit** with a clear message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```bash
   git commit -m "feat: add your feature"
   ```
6. **Push** and open a **Pull Request**.

## Commit message convention

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `refactor:` — code refactor
- `style:` — formatting
- `test:` — tests
- `chore:` — maintenance

## Code style

### Python

- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use 4-space indentation.
- Maximum line length: 120 characters.
- Use type hints where appropriate.
- Document public methods with docstrings.

### Shell scripts

- Use `shellcheck`-clean bash.
- Use `set -e` for error handling.
- Quote variables properly.

### Thread safety

**Critical**: Never touch GTK widgets from worker threads. Always use `GLib.idle_add()`:

```python
# WRONG — will cause segfault
def worker(self):
    self.status.set_label("Done")  # GTK access from worker thread

# CORRECT
def worker(self):
    GLib.idle_add(self._update_status, "Done")

def _update_status(self, text):
    self.status.set_label(text)
```

## Reporting bugs

Use the [Bug Report template](https://github.com/asblPixels/ripdvd/issues/new?template=bug_report.md).

Include:
- Your OS and version
- HandBrake version (`HandBrakeCLI --version`)
- The content of `~/.ripdvd-debug.log`
- Steps to reproduce
- Expected vs. actual behavior

## Feature requests

Use the [Feature Request template](https://github.com/asblPixels/ripdvd/issues/new?template=feature_request.md).

## Development setup

### Linux (Fedora)

```bash
git clone https://github.com/asblPixels/ripdvd.git
cd ripdvd
sudo dnf install python3 python3-gobject gtk4 libadwaita zenity HandBrake HandBrake-cli
python3 src/ripdvd.py
```

### Windows

```powershell
git clone -b windows https://github.com/asblPixels/ripdvd.git
cd ripdvd
python src/ripdvd-win.py
```

## Testing

Currently, ripdvd does not have automated tests. Contributions adding tests are welcome!

Manual testing checklist:
- [ ] App launches without errors
- [ ] DVD scan detects the correct main title
- [ ] Audio tracks are listed with correct languages
- [ ] Subtitle tracks are listed
- [ ] Encoding produces a valid MKV file
- [ ] Progress bar updates during encoding
- [ ] Stop button cancels encoding
- [ ] Resume button re-encodes successfully
- [ ] Quit button closes the app cleanly
- [ ] Output file plays correctly in VLC/Jellyfin

## Pull request process

1. Ensure your code follows the style guidelines.
2. Update the README if you add new features.
3. Update the CHANGELOG.
4. Test on at least one supported platform.
5. Submit the PR with a clear description.

## Questions?

Open a [Discussion](https://github.com/asblPixels/ripdvd/discussions) or contact the maintainer.
