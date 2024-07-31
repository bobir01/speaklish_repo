import logging


logger = logging.getLogger('django')


def logged(logged_message: object, logged_type: str = "debug") -> None:
    """Use this function to logging.

    :param log_message: object -> log message
    :param _type: string -> log type choicesw ("info, error, warning, debug...")
        default: _type -> debug
    """
    if logged_type == 'info':
        logger.info(logged_message)
    elif logged_type == "warning":
        logger.warning(logged_message)
    elif logged_type == "debug":
        logger.debug(logged_message)
    elif logged_type == "error":
        logger.error(logged_message)
    elif logged_type == "critical":
        logger.critical(logged_message)

    elif logged_type not in ('warning', 'error', 'debug', 'critical'):
        logger.debug(logged_message)
