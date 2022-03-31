"""Identify images with text to assess localization impact
   See https://ssp.ptc.com/jira/browse/L10NPROD-120 for more details.
"""
# pylint: disable = import-error
import argparse
import os
import re
import sys
import numpy as np
import cv2
import pytesseract

# To fix issue - tesseract is not installed or it's not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
# +------------------------------------------------------
def post_process_tree(source_root, log_dir):
    """Post process image files"""
    # pylint: disable=unused-variable
    for parent_dir, subdirs, file_names in os.walk(source_root):
        for file_name in file_names:
            full_path = os.path.join(parent_dir, file_name)
            rel_path = os.path.relpath(full_path, source_root)
            if re.search("\\.(png|jpeg|jpg)$", rel_path):
                image = cv2.imread(full_path)
                image_text = ocr_core(image)
                result = check(file_name, image_text)
                create_log(log_dir, result)
    print(rf"Log file with details: {os.path.abspath(log_dir)}\log.txt")
# +------------------------------------------------------
def get_grayscale(image):
    """Get image from the BGR color space to gray"""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# +------------------------------------------------------
def sharpen(image):
    """Creating sharpening filter"""
    # Using 3x3 dimensional kernels to sharpen the images
    kernel = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])

    # Filter2D operation convolves an image with the kernel
    return cv2.filter2D(image, -1, kernel)
# +------------------------------------------------------
def ocr_core(image):
    """Preprocessing the images by calling the core logic of pytesseract"""
    grayscale_image = get_grayscale(image)
    sharpen_image = sharpen(grayscale_image)
    text = pytesseract.image_to_string(sharpen_image)
    return text
# +------------------------------------------------------
def check(image_name, image_text):
    """If the alphabets are lesser or equal to one then image has no localization impact"""
    if count_letters(image_text) >= 2:
        result = f"{image_name} : Loc Impact - YES\n"
        print(result)
    else:
        result = f"{image_name} : Loc Impact - NO\n"
        print(result)
    return result
# +------------------------------------------------------
def count_letters(image_text):
    """Counter to store the number of alphabets in the string"""
    letter = 0
    # Every character in the string is iterated
    for i, _ in enumerate(image_text):
        # To check if the character is an alphabet or not
        if image_text[i].isalpha():
            letter += 1
    return letter
# +------------------------------------------------------
def create_log(log_dir, result):
    """Creates log file with result details"""
    os.makedirs(os.path.abspath(log_dir), exist_ok=True)
    log_file_name = 'log.txt'
    log = os.path.join(os.path.abspath(log_dir), log_file_name)

    with open(log, "a", encoding="utf-8") as log_file:
        log_file.write(result)
# +------------------------------------------------------
def main():
    """Identify images with text to assess localization impact"""
    parser = argparse.ArgumentParser(
        description='Identify images with text to assess localization impact')
    parser.add_argument(
        'source_root',
        metavar='<source_root>',
        help='Source path containing images')
    parser.add_argument(
        '--logdir',
        dest='log_dir',
        metavar='<dir>',
        help='Log directory')
    args = parser.parse_args(sys.argv[1:])

    post_process_tree(args.source_root, args.log_dir)
# +------------------------------------------------------
if __name__ == "__main__":
    main()
