


import core.entities as E

import enum

class Kicad:
    class Pin:
        class Type(enum.Enum):
            INPUT = 'input'
            OUTPUT = 'output'
            BIDIRECTIONAL = 'bidirectional'
            POWER_IN = 'power_in'
            POWER_OUT = 'power_out'
            TRISTATE = 'tristate'
            PASSIVE = 'passive'
            UNSPECIFIED = 'unspecified'
            NO_CONNECT = 'no_connect'

            @staticmethod
            def fromPin(value: E.Pin.Type):
                return {
                    E.Pin.Type.INPUT.value: Kicad.Pin.Type.INPUT,
                    E.Pin.Type.OUTPUT.value: Kicad.Pin.Type.OUTPUT,
                    E.Pin.Type.BIDIRECTIONAL.value: Kicad.Pin.Type.BIDIRECTIONAL,
                    E.Pin.Type.POWER_IN.value: Kicad.Pin.Type.POWER_IN,
                    E.Pin.Type.POWER_OUT.value: Kicad.Pin.Type.POWER_OUT,
                    E.Pin.Type.TRISTATE.value: Kicad.Pin.Type.TRISTATE,
                    E.Pin.Type.PASSIVE.value: Kicad.Pin.Type.PASSIVE,
                    E.Pin.Type.UNSPECIFIED.value: Kicad.Pin.Type.UNSPECIFIED,
                    E.Pin.Type.NO_CONNECT.value: Kicad.Pin.Type.NO_CONNECT
                }[value]


        @staticmethod
        def validate(pin: E.Pin):
            if not pin.number:
                raise ValueError("Pin number cannot be empty")
            if not pin.name:
                raise ValueError("Pin name cannot be empty")
            if not pin.type:
                raise ValueError("Pin type cannot be empty")
            if not pin.style:
                raise ValueError("Pin style cannot be empty")
            return pin

        @staticmethod
        def format(pin: E.Pin, x, y, orientation):
            res = ''
            res += f'(pin {Kicad.Pin.Type.fromPin(pin.type).value} {pin.style}\n'
            res += f'\t(at {x:.02f} {y:.02f} {orientation:.02f})\n'
            res += f'\t(length 5.08){' hide' if pin.hidden else ''}\n'
            res += f'\t(name "{pin.name}"\n'
            res += f'\t\t(effects\n'
            res += f'\t\t\t(font\n'
            res += f'\t\t\t\t(size 1.27 127)\n'
            res += f'\t\t\t)\n'
            res += f'\t\t)\n'
            res += f'\t)\n'
            res += f'\t(number "{pin.number}"\n'
            res += f'\t\t(effects\n'
            res += f'\t\t\t(font\n'
            res += f'\t\t\t\t(size 1.27 127)\n'
            res += f'\t\t\t)\n'
            res += f'\t\t)\n'
            res += f'\t)\n'
            res += f')\n'
            return res