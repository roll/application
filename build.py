import PyInstaller.__main__
import subprocess


def build_application():
    """Build an executable file for the Application."""

    print("[server] Creating linux executable file for Open Data Editor")
    PyInstaller.__main__.run([
        'ode/main.py',
        '--collect-all', 'frictionless',  # Frictionless depends on data files
        '--collect-all', 'ode',  # Collect all assets from Open Data Editor
        '--log-level', 'WARN',
        '--name', 'opendataeditor',
        '--noconfirm',
    ])
    # Clean the spec file generated by PyInstaller
    subprocess.run(['rm', 'opendataeditor.spec'])


if __name__ == "__main__":
    build_application()
