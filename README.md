# Picopad

Code to turn my Raspberry Pi Pico into a macropad. Intended to send keycodes that don't already correspond to existing keys on standard US keyboards to allow for additional buttons for uses like keybinds without needing to worry about multi-button macros.

Uses the Keyboard, HID, and Core components of [micropython-lib](https://github.com/micropython/micropython-lib)'s USB set.
