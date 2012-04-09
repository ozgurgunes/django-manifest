#!/usr/bin/env python
import sys
from django.core.management import execute_from_command_line

try:
    import manifest
except ImportError:
    sys.stderr.write("Error: Can't import manifest. Make sure you are in a "
        "virtual environment that has\Django Manifest installed.\n")
    sys.exit(1)
else:
    import manifest.env

manifest.env.setup_environ(__file__)

if __name__ == "__main__":
    execute_from_command_line()
