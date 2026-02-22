"""
C-BOM App Launcher
Starts the web server and opens the browser automatically.
Bundled as a Windows desktop application via PyInstaller.
"""
import sys
import os

# When frozen by PyInstaller, add the bundle dir to path
if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS  # type: ignore[attr-defined]
    sys.path.insert(0, bundle_dir)
    os.chdir(bundle_dir)

PORT = 5000


def main():
    from cbom.web_ui import create_web_ui
    create_web_ui(port=PORT)


if __name__ == "__main__":
    main()
