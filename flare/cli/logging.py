import logging
import logging.config
import os


class MyInterfaceLogging:
    """Custom logging for my application, inspired by Luigi's InterfaceLogging"""

    _configured = False  # Ensures logging is only set up once

    @classmethod
    def setup(cls, opts=None):
        """Setup logging based on provided options (config file or defaults)"""
        if cls._configured:
            return  # Prevent reconfiguration

        if opts and getattr(opts, "logging_conf_file", None):
            cls._conf(opts)
        else:
            cls._default(opts)

        cls._configured = True  # Mark as configured

    @classmethod
    def _conf(cls, opts):
        """Setup logging from an external config file (INI format)"""
        if not os.path.exists(opts.logging_conf_file):
            raise OSError(
                f"Error: Cannot find logging configuration file: {opts.logging_conf_file}"
            )

        logging.config.fileConfig(
            opts.logging_conf_file, disable_existing_loggers=False
        )

    @classmethod
    def _default(cls, opts):
        """Setup default logging if no config file is provided"""
        log_level = getattr(
            logging, getattr(opts, "log_level", "DEBUG").upper(), logging.DEBUG
        )

        logger = logging.getLogger("my-interface")  # Change this name for your project
        logger.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)

        # Define log format
        formatter = logging.Formatter("~FLARE~ [%(levelname)s]: %(message)s")
        console_handler.setFormatter(formatter)

        # Attach handler to logger
        logger.addHandler(console_handler)

    @staticmethod
    def get_logger():
        """Return the configured logger"""
        return logging.getLogger("my-interface")


class Opts:
    logging_conf_file = None  # Set to a path if using a config file
    log_level = "INFO"  # Set log level


opts = Opts()

# Initialize logging
MyInterfaceLogging.setup(opts)

# Use the logger
logger = MyInterfaceLogging.get_logger()
