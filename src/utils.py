from pathlib import Path
import logging
import argparse
import json
import sys
from typing import Tuple, Union, List, Dict, Optional

def setup_logging(main_log_file=None, scenario_log_file=None, log_dir: Union[str, Path] = "logs", log_level: Union[str, int] = logging.INFO):
    """
    Sets up logging for both console and file handlers.

    :param main_log_file: Name of the main log file (default is None).
    :param scenario_log_file: Name of the scenario-specific log file (default is None).
    :param log_dir: Directory where logs are stored (accepts str or Path).
    :param log_level: Logging level (default INFO).
    """
    # Convert log_dir to Path if it's not already a Path object
    if not isinstance(log_dir, Path):
        log_dir = Path(log_dir)
    
    log_dir.mkdir(parents=True, exist_ok=True)  # Create the log directory if it doesn't exist
    
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)  # Default to INFO if not found
    
    logger = logging.getLogger()
    logger.setLevel(log_level)
    log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    # Main Log File Handler (append mode, only if provided)
    if main_log_file:
        main_log_path = log_dir / main_log_file  # Construct the path using log_dir
        main_file_handler = logging.FileHandler(main_log_path, mode='a')
        main_file_handler.setLevel(log_level)
        main_file_handler.setFormatter(log_formatter)
        logger.addHandler(main_file_handler)

    # Scenario Log File Handler (overwrite mode, only if provided)
    if scenario_log_file:
        scenario_log_path = log_dir / scenario_log_file  # Construct the path using log_dir
        scenario_file_handler = logging.FileHandler(scenario_log_path, mode='w')
        scenario_file_handler.setLevel(log_level)
        scenario_file_handler.setFormatter(log_formatter)
        logger.addHandler(scenario_file_handler)

    logger.info("Logging is set up.")

def log_data(data: Union[Dict, List], title: Optional[str] = None, format_as_currency: bool = False) -> None:
    """
    Logs a dictionary or list in a structured format.

    :param data: The data to log (dict or list).
    :param title: Optional title to be logged before the data.
    :param format_as_currency: If True, formats numbers in the data as currency.
    :return: None
    """
    if title:
        logging.info(f"--- {title} ---")

    if isinstance(data, dict):
        if format_as_currency:
            # Format each value as currency if it is a number
            formatted_data = {k: format_currency(v) if isinstance(v, (int, float)) else v for k, v in data.items()}
            logging.info(formatted_data)
        else:
            logging.info(data)

    elif isinstance(data, list):
        # If data is a list, log each item
        if format_as_currency:
            formatted_list = [format_currency(item) if isinstance(item, (int, float)) else item for item in data]
            logging.info(formatted_list)
        else:
            logging.info(data)

    else:
        logging.warning("Unsupported data type provided to log_data.")


def handle_arguments():
    try:
        args = parse_arguments()
        log_data(vars(args), title="Arguments Received")
        return args

    # Handle argument-related errors
    except argparse.ArgumentError as e:
        logging.error(f"Argument parsing error: {e}")
        sys.exit(1)
    
    # Handle incorrect types or values in the arguments
    except ValueError as e:
        logging.error(f"Invalid argument value: {e}")
        sys.exit(1)
    
    # Handle any other potential issues (keeping a catch-all for unforeseen exceptions)
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
        sys.exit(1)

def parse_arguments():
    """
    Parses command-line arguments for the financial configuration script.

    Returns:
        argparse.Namespace: Parsed arguments containing the configuration file path.
    """
    logging.debug("Entering parse_arguments function")

    # Define the argument parser
    parser = argparse.ArgumentParser(description='Process financial configuration.')
    parser.add_argument('config_file_path', nargs='?', default='config.finance.json', help='Path to the configuration file')

    args = parser.parse_args()

    # Log the parsed arguments
    logging.info(f"Parsed arguments: {args}")
    
    # Check if the configuration file exists
    config_path = Path(args.config_file_path)
    if not config_path.exists():
        logging.error(f"Configuration file {config_path} does not exist.")
        sys.exit(1)  # Exits the program if the config file is not found
    
    return args

LOGS_DIR = Path('../logs').resolve()

def format_currency(value):
    return f"${value:,.2f}"

def load_logging_level():
    # Assuming the config file is in the src directory
    config_path = Path(__file__).parent / 'config.json'  # Using __file__ to get the current script's directory
    with config_path.open('r') as f:
        config_data = json.load(f)
        return config_data.get('logging_level', 'INFO')  # Default to 'INFO' if not found
