#!/usr/bin/env python3
"""
config.py -- Vaultpass configuration manager

- Ensures config file exists in ~/.vaultpass/system/vaultpassconfig
- Loads config settings into a dictionary
- Writes config with comments if not present
- Provides read/update/save functions for settings

Config format: key=value, with comments for each setting.
"""

import os

HOME = os.path.expanduser("~")
SYSTEM_DIR = os.path.join(HOME, ".vaultpass", "system")
CONFIG_PATH = os.path.join(SYSTEM_DIR, "vaultpassconfig")

# Default config with comments for clarity
DEFAULT_CONFIG = """\
# Vaultpass Configuration File
# This file controls optional features and output behavior.
# To enable/disable a feature, change the value and save.

# Enable colored output (true/false)
color=true

# Check for updates every N days (default: 3)
update_days=3

# Maximum lines to show in changelog box (default: 20)
changelog_max=20

# Reserved for future settings...

"""

def ensure_config():
    """
    Ensures the config file exists; writes default if not present.
    """
    if not os.path.exists(SYSTEM_DIR):
        os.makedirs(SYSTEM_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w") as f:
            f.write(DEFAULT_CONFIG)

def load_config():
    """
    Loads the config into a dict. Ensures defaults for missing keys.
    Ignores comments and blank lines.
    """
    ensure_config()
    config = {}
    with open(CONFIG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip()
    # Fill in defaults if missing
    for line in DEFAULT_CONFIG.splitlines():
        if "=" in line:
            key, val = line.split("=", 1)
            if key.strip() not in config:
                config[key.strip()] = val.strip()
    return config

def save_config(config):
    """
    Saves the config dict to file, preserving comments & order.
    """
    # Read the template to preserve comments and order
    lines_out = []
    existing = {}
    for line in DEFAULT_CONFIG.splitlines():
        if "=" in line:
            key, _ = line.split("=", 1)
            val = config.get(key.strip(), None)
            if val is not None:
                lines_out.append(f"{key.strip()}={val}")
            else:
                lines_out.append(line)
        else:
            lines_out.append(line)
    # Add any custom keys (not in default)
    for k, v in config.items():
        if f"{k}=" not in DEFAULT_CONFIG:
            lines_out.append(f"{k}={v}")
    # Write it out
    with open(CONFIG_PATH, "w") as f:
        f.write("\n".join(lines_out) + "\n")

def get_config_value(key, default=None):
    """
    Returns the value for a key, or default if not present.
    """
    config = load_config()
    return config.get(key, default)

def set_config_value(key, value):
    """
    Updates a single config value and saves to disk.
    """
    config = load_config()
    config[key] = value
    save_config(config)

# Example usage
if __name__ == "__main__":
    ensure_config()
    config = load_config()
    print("Vaultpass config loaded:")
    for k, v in config.items():
        print(f"  {k} = {v}")
    print("\nTry set_config_value('color', 'false') to disable color.")