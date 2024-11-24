import logging
import enum

log = logging.getLogger(__name__)


class __Entity(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"Unknown attribute: {key}")
            if key.startswith("__"):
                raise AttributeError(f"Cannot set private attribute: {key}")
            setattr(self, key, value)

    def __publicProps(self):
        return {k: v for k, v in vars(self).items() if not k.startswith("__")}

    def __str__(self):
        return f"{self.__class__.__name__} {self.__publicProps()}"

    __repr__ = __str__


def optionalString(func):
    def wrapper(self, value):
        if not isinstance(value, (type(None), str)):
            raise TypeError("Value must be a string or None")
        if type(value) is str and not len(value):
            raise ValueError("Value cannot be empty")
        return func(self, value)

    return wrapper


class Pin(__Entity):
    class Style(enum.Enum):
        LINE = "line"
        INVERTED = "inverted"
        CLOCK = "clock"
        INVERTED_CLOCK = "inverted_clock"
        NON_LOGIC = "non_logic"

    class Type(enum.Enum):
        INPUT = "input"
        OUTPUT = "output"
        BIDIRECTIONAL = "bidirectional"
        TRISTATE = "tristate"
        PASSIVE = "passive"
        POWER_IN = "power_in"
        POWER_OUT = "power_out"
        ANALOG = "analog"
        FREE = "free"
        UNSPECIFIED = "unspecified"
        NO_CONNECT = "no_connect"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def name(self):
        try:
            return self.__name
        except AttributeError:
            return None

    @name.setter
    @optionalString
    def name(self, value):
        self.__name = value

    @property
    def number(self):
        try:
            return self.__number
        except AttributeError:
            return None

    @number.setter
    @optionalString
    def number(self, value):
        self.__number = value

    @property
    def type(self):
        try:
            return self.__type
        except AttributeError:
            return None

    @type.setter
    @optionalString
    def type(self, value):
        if value is None:
            self.__type = None
            return
        if not value:
            raise ValueError("Type cannot be empty")
        if value not in Pin.Type:
            raise ValueError(
                f"Unknown type: {value}, must be one of:\n\t{set(Pin.Type)}"
            )
        self.__type = value

    @property
    def style(self):
        try:
            return self.__style
        except AttributeError:
            return None

    @style.setter
    @optionalString
    def style(self, value):
        if value is None:
            self.__style = None
            return
        if value not in Pin.Style:
            raise ValueError(
                f"Unknown style: {value}, must be one of:\n\t{set(Pin.Style)}"
            )
        self.__style = value

    @property
    def hidden(self):
        try:
            return self.__hidden
        except AttributeError:
            return None

    @hidden.setter
    def hidden(self, value):
        if not isinstance(value, (bool, type(None))):
            raise ValueError("Hidden must be a boolean or None")
        self.__hidden = value

    def __str__(self):
        return f"{self.__class__.__name__} (Name: {self.name}, Number: {self.number}, Type: {self.type}, Style: {self.style}, Hidden: {self.hidden})"

    # Repr is same as str
    __repr__ = __str__
