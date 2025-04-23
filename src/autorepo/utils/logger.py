import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """
    Sets up the logging configuration for the application.
    Logs to a file in the user's home directory.
    """
    log_dir = Path.home() / '.autorepo' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'autorepo.log'

    # Use a basic configuration for now
    logging.basicConfig(
        level=logging.INFO, # Default logging level
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='a'),
            logging.StreamHandler() # Also log to console
        ]
    )

# Call setup_logging when the module is imported
setup_logging()

# Provide a function to get a logger instance (optional, but good practice)
def get_logger(name):
    """Get a logger instance by name."""
    return logging.getLogger(name)

# Note: The original custom JSON/CSV logging format is not replicated here
# using standard logging. A custom formatter would be needed for that.
# For now, using a standard text format.
