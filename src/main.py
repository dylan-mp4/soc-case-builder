"""
SOC Case Builder - Main Entry Point
Entry point for the Flet-based UI application.
"""

import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.insert(0, root_dir)

from src.ui_flet.app import app
from src.resources.get_version import get_version
from src.utils.check_updates import prompt_and_update_if_needed


def main():
    """Main entry point."""
    # Check for updates and prompt if needed
    if prompt_and_update_if_needed(get_version()):
        sys.exit(0)  # Exit if update was triggered
        return  # not reached, but for clarity

    # Start Flet application
    app()


if __name__ == "__main__":
    main()