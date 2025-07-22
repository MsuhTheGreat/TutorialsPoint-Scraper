import logging
from scrapy.utils.log import configure_logging

try:
    from colorlog import ColoredFormatter
    use_color = True
except ImportError:
    use_color = False

LOG_ENABLED = False
configure_logging(install_root_handler=False)

LOG_LEVEL = 'DEBUG'

console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)

if use_color:
    console_formatter = ColoredFormatter(
        '%(log_color)s[%(levelname)s] %(message)s',
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'bold_red',
        }
    )
else:
    console_formatter = logging.Formatter('[%(levelname)s] %(message)s')

console_handler.setFormatter(console_formatter)

file_handler = logging.FileHandler('scrapy_log.log', mode='w', encoding='utf-8')
file_handler.setLevel(LOG_LEVEL)
file_formatter = logging.Formatter('[%(levelname)s] %(message)s')
file_handler.setFormatter(file_formatter)

root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)
root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)
