from typing import List
import pyautogui
import pygetwindow
from PIL import Image
from pytesseract import image_to_string, pytesseract
import numpy as np
from decimal import Decimal
import re
from config import Config


LOOT_RE = r"([a-zA-Z\(\) ]+) [\(\{\[](\d+[\.\,]\d+) PED[\)\]\}]"


pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def change_contrast(img, level):
    factor = (259 * (level + 255)) / (255 * (259 - level))

    def contrast(c):
        return 128 + factor * (c - 128)

    return img.point(contrast)


def get_loot_instances_from_screen():
    loots = []

    img, width, height = screenshot_window()
    if img is None:
        return loots

    try:
        img = img.convert('LA')
        data = np.array(img)
        img_contrast = change_contrast(img, 150)

        # Greyscale and try and isolate text
        converted = np.where((data // 39) == 215 // 39, 0, 255)

        processed_img = Image.fromarray(converted.astype('uint8'))

        text = image_to_string(processed_img)
        lines = text.split("\n")
        for s in lines:
            match = re.match(LOOT_RE, s)
            print(s)
            if match:
                name, value = match.groups()
                value = Decimal(value.replace(",", "."))
                loots.append((name, value))
    finally:
        # Clean up PIL images and numpy arrays
        if hasattr(img, 'close'):
            img.close()
        if 'img_contrast' in locals() and hasattr(img_contrast, 'close'):
            img_contrast.close()
        if 'processed_img' in locals() and hasattr(processed_img, 'close'):
            processed_img.close()
        # Explicitly delete numpy arrays to free memory
        if 'data' in locals():
            del data
        if 'converted' in locals():
            del converted
        
    return loots


def capture_target(contrast=0, banding=35, filter=225):
    im = pyautogui.screenshot()

    try:
        width, height = im.size

        sides = width / 3
        bottom = height / 3

        print((0, 0, sides, bottom))
        im1 = im.crop((sides, 0, width - sides, bottom))

        im1 = im1.convert('LA')
        data = np.array(im1)
        im1_contrast = change_contrast(im1, contrast)

        # Greyscale and try and isolate text
        converted = np.where((data // banding) == filter // banding, 0, 255)

        processed_img = Image.fromarray(converted.astype('uint8'))
        text = image_to_string(processed_img)
        lines = text.split("\n")
        results = []
        for s in lines:
            if s:
                print(s)
                results.append(s)
        return results
    finally:
        # Clean up PIL images and numpy arrays
        if hasattr(im, 'close'):
            im.close()
        if hasattr(im1, 'close'):
            im1.close()
        if 'im1_contrast' in locals() and hasattr(im1_contrast, 'close'):
            im1_contrast.close()
        if 'processed_img' in locals() and hasattr(processed_img, 'close'):
            processed_img.close()
        # Explicitly delete numpy arrays to free memory
        if 'data' in locals():
            del data
        if 'converted' in locals():
            del converted


def screenshot_window():
    """Take a screenshot of the Entropia Universe window."""
    window_name = None

    for window_name in pygetwindow.getAllTitles():
        if window_name.startswith("Entropia Universe Client"):
            found_window = window_name
            break

    if not window_name:
        return None, 0, 0

    window = pygetwindow.getWindowsWithTitle(window_name)[0]
    try:
        window.activate()
    except:
        pass  # ignore for now

    im = pyautogui.screenshot()

    top_left = window.topleft
    width = window.width
    height = window.height

    im1 = im.crop((top_left.x, top_left.y, top_left.x + width, top_left.y + height))
    
    # Close the original screenshot to free memory
    if hasattr(im, 'close'):
        im.close()
    
    return im1, width, height