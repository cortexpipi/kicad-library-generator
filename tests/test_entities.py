import unittest

from core.entities import Pin,Row

import logging
logging.basicConfig(level=logging.DEBUG)


class TestPin(unittest.TestCase):

    def testConstructor(self):
        pin = Pin()
        for prop in ['number', 'name', 'type', 'style', 'hidden']:
            self.assertIsNone(pin.__dict__.get(f'{prop}'))

        pin.hidden = True
        self.assertTrue(pin.hidden)

        with self.assertRaises(ValueError):
            for prop in ['number', 'name', 'type', 'style']:
                setattr(pin, prop, 'invalid')

        for prop in ['number', 'name', 'type', 'style']:
            setattr(pin, prop, None)
            self.assertEqual(getattr(pin, prop), None)

        for style in Pin.KNOWN_STYLES:
            pin.style = style
            self.assertEqual(pin.style, style)

        for type in Pin.KNOWN_TYPES:
            pin.type = type
            self.assertEqual(pin.type, type)

