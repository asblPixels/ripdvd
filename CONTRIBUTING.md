# Contributing to ripdvd

Thank you for considering contributing! 🎉

## How to contribute

1. **Fork** the repository.
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/ripdvd.git`
3. **Create a branch**: `git checkout -b feature/your-feature`
4. **Make your changes** and test them on Fedora.
5. **Commit** with a clear message: `git commit -m "feat: describe your change"`
6. **Push** and open a **Pull Request**.

## Commit message convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation
- `refactor:` — code refactor
- `style:` — formatting
- `test:` — tests
- `chore:` — maintenance

## Code style

- Python: follow PEP 8, use 4-space indentation.
- Shell: use `shellcheck`-clean bash.
- Keep the GUI thread-safe: **never** touch GTK widgets from worker threads — use `GLib.idle_add`.

## Reporting bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md). Include:
- Fedora version (`cat /etc/fedora-release`)
- HandBrake version (`HandBrakeCLI --version`)
- The content of `~/.ripdvd-debug.log`
- Steps to reproduce

## Feature requests

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

## Development setup

```bash
git clone https://github.com/asblPixels/ripdvd.git
cd ripdvd
sudo dnf install python3 python3-gobject gtk4 libadwaita zenity HandBrake HandBrake-cli
python3 src/ripdvd.py
```
