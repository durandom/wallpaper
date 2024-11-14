#!/usr/bin/env python3

import sys
import argparse
from io import BytesIO
import requests
from PIL import Image
import os
import re
from google_images_search import GoogleImagesSearch
from time import sleep

# You'll need to set these environment variables:
# GOOGLE_SEARCH_API_KEY - from Google Cloud Console
# GOOGLE_SEARCH_CX - from Google Programmable Search Engine
GCS_DEVELOPER_KEY = os.getenv('GCS_DEVELOPER_KEY')
GCS_CX = os.getenv('GCS_CX')

def sanitize_filename(filename):
    """Remove invalid characters from filename"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def download_image(url, folder, index):
    """Download image from URL and save to folder"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            # Get file extension from content-type or fallback to .jpg
            content_type = response.headers.get('content-type', '')
            ext = '.jpg'
            if 'png' in content_type.lower():
                ext = '.png'
            elif 'jpeg' in content_type.lower() or 'jpg' in content_type.lower():
                ext = '.jpg'

            filename = f"image_{index + 1}{ext}"
            filepath = os.path.join(folder, filename)

            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"Error downloading image: {str(e)}", file=sys.stderr)
    return False

def check_image_resolution(url, min_width, min_height):
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        width, height = img.size
        return width >= min_width and height >= min_height
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description='Search for Google images with minimum resolution')
    parser.add_argument('search_term', help='The search term to look for')
    parser.add_argument('--resolution', default='1920x1080',
                      help='Minimum resolution in format WIDTHxHEIGHT (default: 1920x1080)')
    parser.add_argument('--max-results', type=int, default=1,
                      help='Maximum number of results to return (default: 1)')

    args = parser.parse_args()

    if not GCS_DEVELOPER_KEY or not GCS_CX:
        print("Error: Please set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX environment variables")
        sys.exit(1)

    try:
        min_width, min_height = map(int, args.resolution.lower().split('x'))
    except ValueError:
        print("Error: Resolution must be in format WIDTHxHEIGHT (e.g., 1920x1080)")
        sys.exit(1)

    gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)

    # Define search params
    search_params = {
        'q': args.search_term,
        'num': args.max_results * 2,  # Get more results than needed to allow for filtering
        'imgType': 'photo',
        'safe': 'high',
    }

    max_retries = 3
    retry_delay = 2  # seconds

    for attempt in range(max_retries):
        try:
            # Search for images
            gis.search(search_params)

            # Create folder for saving images
            folder_name = sanitize_filename(args.search_term)
            os.makedirs(folder_name, exist_ok=True)

            # Filter and save results
            results_found = 0
            for image in gis.results():
                if results_found >= args.max_results:
                    break

                url = image.url
                if check_image_resolution(url, min_width, min_height):
                    print(f"Downloading: {url}")
                    if download_image(url, folder_name, results_found):
                        results_found += 1

            if results_found > 0:
                print(f"\nSaved {results_found} images to folder: {folder_name}")
                break
            elif attempt < max_retries - 1:
                print(f"No suitable images found, retrying... (attempt {attempt + 1}/{max_retries})",
                      file=sys.stderr)
                sleep(retry_delay)
            else:
                print("No images found matching the resolution criteria", file=sys.stderr)

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Error occurred, retrying... (attempt {attempt + 1}/{max_retries}): {str(e)}",
                      file=sys.stderr)
                sleep(retry_delay)
            else:
                print(f"Error: {str(e)}", file=sys.stderr)
                sys.exit(1)

if __name__ == '__main__':
    main()
