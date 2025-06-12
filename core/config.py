#!/usr/bin/env python3
import os

# =========================
# Vaultpass Config Handler
# =========================

HOME = os.path.expanduser("~")
SYSTEM_DIR = os.path.join(HOME, ".vaultpass", "system")
CONFIG_FILE = os.path.join(SYSTEM_DIR, "vaultpassconfig")

DEFAULT_CONFIG = """# Vaultpass Configuration File
# Toggle color output (true/false)
color = true

# Auto-update on launch (true/false)
auto_update = true

# Reserved for future settings...
"""

def ensure_config():
    """Create the config file with defaults if missing."""
    if not os.path.exists(SYSTEM_DIR):
        os.makedirs(SYSTEM_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            f.write(DEFAULT_CONFIG)
        return True
    return False

def load_config():
    """Load config file as a dict (simple format)."""
    ensure_config()
    config = {}
    with open(CONFIG_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue
            if "=" in line:
                k, v = line.split("=", 1)
                config[k.strip()] = v.strip().lower()
    return config

def update_config(key, value):
    """Update a single config key/value."""
    config = load_config()
    config[key] = str(value).lower()
    # Write back with comments preserved at top
    with open(CONFIG_FILE, "r") as f:
        lines = f.readlines()
    with open(CONFIG_FILE, "w") as f:
        for line in lines:
            if line.strip().startswith("#") or not line.strip():
                f.write(line)
            elif "=" in line:
                k = line.split("=")[0].strip()
                if k == key:
                    f.write(f"{key} = {value}\n")
                else:
                    f.write(line)
        # Append new key if not present
        if key not in [l.split("=")[0].strip() for l in lines if "=" in l]:
            f.write(f"{key} = {value}\n")

# Example usage
if __name__ == "__main__":
    ensure_config()
    conf = load_config()
    print("Config loaded:", conf)
    update_config("color", "false")
    print("Color setting updated to false.")