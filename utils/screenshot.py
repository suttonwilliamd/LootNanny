import win32gui
import win32ui
import win32con
from PIL import Image
import numpy as np
import cv2
import re
import json
import os
from typing import Tuple, Optional


def screenshot_window() -> Tuple[Optional[Image.Image], Optional[int], Optional[int]]:
    """
    Take a screenshot of the Entropia Universe window.
    
    Returns:
        Tuple of (PIL Image, width, height) or (None, None, None) if window not found
    """
    hwnd = win32gui.FindWindow(None, "Entropia Universe")
    if not hwnd:
        return None, None, None

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = right - left
    height = bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    result = saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

    return im, width, height