import unittest
import argparse
import logging


# Declare arguments
parser = argparse.ArgumentParser(description='Unit tests for the entire project')
# Log level arg with value check

def logLevelValidator(value):
    logLevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if not value.upper() in logLevels:
        raise argparse.ArgumentTypeError(f'Invalid log level, must be one of:\n\t{logLevels}')
    return value

parser.add_argument('-l', '--loglevel', type=logLevelValidator, default='INFO', help='Set the log level')
parser.add_argument('-v', '--verbose', action='store_true', help='Set log level to DEBUG')


# Parse arguments
args = parser.parse_args()


# Set up logging
loggingFormat = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
# ignore loglevel if verbose is set
loggingLevel = logging.getLevelName(args.loglevel)
if args.verbose:
    loggingLevel = logging.DEBUG
logging.basicConfig(format=loggingFormat, level=loggingLevel)






# Run tests
unittest.main()