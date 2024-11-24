import logging
import os
import argparse
import re

from core.entities import Pin
from core.formatters import Kicad as KicadFormatter

logName = __name__
if __name__ == "__main__":
    logName = os.path.basename(__file__)
log = logging.getLogger(logName)

# Set up arguments


parser = argparse.ArgumentParser(description="Convert a list of pins to a kicad symbol")


# Log level arg with value check
def logLevel(value):
    logLevels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if not value.upper() in logLevels:
        raise argparse.ArgumentTypeError(
            f"Invalid log level, must be one of:\n\t{logLevels}"
        )
    return value


parser.add_argument(
    "-l", "--loglevel", type=logLevel, default="INFO", help="Set the log level"
)
# verbose flag
parser.add_argument(
    "-v", "--verbose", action="store_true", help="Set log level to DEBUG"
)
# input file with checks
parser.add_argument(
    "-i", "--input", type=argparse.FileType("r"), help="Input file containing pin list"
)
# output file with permission check
parser.add_argument(
    "-o",
    "--output",
    type=argparse.FileType("w"),
    default=None,
    help="Output file to write symbol to",
)

# autofix flag
parser.add_argument(
    "--autofix", action="store_true", help="Automatically fix issues in the input file"
)

# grouping flag
parser.add_argument(
    "-g", "--group", action="store_true", help="Group pins by type (separate subsymbols)"
)

# set loglevel
args = parser.parse_args()


# Set up logging

loggingFormat = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

# ignore loglevel if verbose is set
loggingLevel = logging.getLevelName(args.loglevel)
if args.verbose:
    loggingLevel = logging.DEBUG
logging.basicConfig(format=loggingFormat, level=loggingLevel)

log.debug("Pins to Symbol")
log.debug(f"Log level: {args.loglevel}")
log.debug(f"Verbose: {args.verbose}")
log.debug(f"Actual loglevel: {logging.getLevelName(loggingLevel)}")
log.debug(f"Input file: {args.input.name}")
log.debug(f"Output file: {args.output.name if args.output else None}")


def parseInputFile(f):

    log.debug("Parsing input file...")
    rows = []
    currentRow = []
    labels = []
    for line in f:
        if line.strip().startswith("#") or len(line.strip()) == 0:
            log.debug("Skipping line: {line}")
            continue
        if line.startswith(" "):
            currentRow.append(line.strip())
        else:
            if len(currentRow) > 0:
                rows.append(currentRow)
            currentRow = []
            labels.append(line.strip())
    if len(currentRow) > 0:
        rows.append(currentRow)

    gridWidth = 0
    gridHeight = len(rows)
    for row in rows:
        gridWidth = max(gridWidth, len(row))
    log.debug(f"Grid size: {gridWidth}x{gridHeight}")
    if len(rows) != len(labels):
        if args.autofix:
            log.warning("Number of labels does not match number of rows")
            log.warning("Autofixing...")
            # labels.extend([""] * (len(rows) - len(labels)))
            raise NotImplementedError("Autofix not implemented")
        else:
            raise ValueError(
                f"Number of labels ({len(rows)}) does not match number of rows ({len(labels)})"
            )
    grid = dict(zip(labels, rows))
    for i, (label, row) in zip(range(len(grid)), grid.items()):
        log.debug(f"{i:03d}\t{label}[{len(row)}]: {row}")
    for i, (label, row) in zip(range(len(grid)), grid.items()):
        if len(row) < gridWidth:
            if args.autofix:
                log.warning(f"Row is too short, autofixing...")
                # row.extend([""] * (gridWidth - len(row)))
                raise NotImplementedError("Autofix not implemented")
            else:
                raise ValueError(f"Row {label} ({i}) is too short: {row}\n\tExpected {gridWidth} columns, got {len(row)}")

    footprint = []
    for label, row in grid.items():
        for i, pin in zip(range(1, len(row) + 1), row):
            if pin:
                footprint.append(Pin(number=f'{label}{i}', name=pin, type="input", style="line"))
    return footprint

def guessPinType(pin):
    pinName = re.sub(r'\W', '', pin.name).upper()
    if any(pinName.startswith(prefix) for prefix in ['VCC', 'VDD', 'VSS', 'GND']):
        return Pin.Type.POWER_IN
    if pinName in ['NC', 'DNU']:
        return Pin.Type.NO_CONNECT
    return Pin.Type.BIDIRECTIONAL

def guessPinStyle(pin):
    return Pin.Style.LINE

def guessPinHidden(pin):
    namesOfHiddenPins = ['NC', 'DNU']
    pinName = re.sub(r'\W', '', pin.name).upper()
    if pinName in namesOfHiddenPins:
        return True
    return False

def fillPinParameters(pin):
    if not pin.type:
        pin.type = guessPinType(pin)
    if not pin.style:
        pin.style = guessPinStyle(pin)
    if not pin.hidden:
        pin.hidden = guessPinHidden(pin)
    return pin

def preprocessPins(pins):
    log.debug("Preprocessing pins...")
    return [fillPinParameters(pin) for pin in pins]

def groupPins(pins):
    log.debug("Grouping pins...")
    result = {}
    predefinedGroupFilters = {
        'power': ['VCC\\w+', 'GND\\w+', 'VDD\\w+', 'VSS\\w+'],
        'gpio': ['P[a-zA-Z][0-9]+', 'IO[0-9]+'],
    }

    groupFilters = [ (re.compile(f'^{filter}$'), group) for group, filters in predefinedGroupFilters.items() for filter in filters ]

    ignoreList = ['NB']

    for pin in pins:
        if pin.name in ignoreList:
            continue
        groupName = 'other'
        for filter, group in groupFilters:
            if filter.match(pin.name):
                groupName = group
                break
        if groupName not in result:
            result[groupName] = []
        result[groupName].append(pin)
    return result





pins = parseInputFile(args.input)
log.debug("Parsed.")

pins = [pin for pin in pins if pin.name != 'NB']

pins = preprocessPins(pins)
log.debug("Preprocessed.")

pins = sorted(pins, key=lambda pin: f'{pin.name}:{pin.number}')
log.debug("Sorted.")

if args.group:
    pins = groupPins(pins)
else:
    pins = {'': pins}
log.debug("Groupped.")
log.debug(pins)

def output(*fnargs, **fnkwargs):
    if args.output:
        print(*fnargs, **fnkwargs, file=args.output)
    else:
        print(*fnargs, **fnkwargs)

for group, pins in pins.items():
    log.debug(f"Processing group: {group}")
    x = 0
    y = 0
    orientation = 0
    prev = None
    for pin in pins:
        # Remove numeric suffix from name
        currentNamePrefix = re.sub(r'[0-9]+$', '', pin.name)
        prevNamePrefix = re.sub(r'[0-9]+$', '', prev.name) if prev else None
        if currentNamePrefix != prevNamePrefix and not pin.hidden:
            y += 254

        validated = KicadFormatter.Pin.validate(pin)
        xReal, yReal = x, y
        if (pin.hidden):
            xReal, yReal = 0, 0
            continue
        formatted = KicadFormatter.Pin.format(validated, xReal/100, yReal/100, orientation)
        output(formatted)
        if not pin.hidden:
            y += 254




