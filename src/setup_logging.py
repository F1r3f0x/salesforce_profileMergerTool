import logging

def setup_logging(logfile_name, title='Logging ready...'):
    """
    Setups the script logging to a File and the console simultaneously
    """
    # Setup Logging
    root_logger = logging.getLogger()

    # Log File Config
    file_handler = logging.FileHandler(
        filename=f'{logfile_name}.log',
        mode='w',
        encoding='utf-8'
    )

    file_handler_formatter = logging.Formatter(
        fmt='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_handler_formatter)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(logging.DEBUG)


    # Console Log Config
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.INFO)
    console_logger.setFormatter(
        logging.Formatter(
            fmt='%(asctime)s %(name)-12s: %(levelname)-8s %(message)s',
            datefmt='%H:%M:%S'
        )
    )
    root_logger.addHandler(console_logger)

    logging.info(title)
