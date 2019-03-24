import os
import logging
from .interface import Interface
from .hidapi_backend import HIDApi
from .pywinusb_backend import PyWinUSB


if HIDApi.isAvailable:
    USB_BACKEND = HIDApi
elif PyWinUSB.isAvailable:
    USB_BACKEND = PyWinUSB
else:
    USB_BACKEND = Interface
