from pathlib import Path

# This can be loaded from a config file or set directly
LOGS_DIR = Path('../logs').resolve()

def format_currency(value):
    return f"${value:,.2f}"
