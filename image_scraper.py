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


def main():
    parser = argparse.ArgumentParser(description='Search and download Google images')
    parser.add_argument('search_term', nargs='+', help='The search terms to look for')
    parser.add_argument('--max-results', type=int, default=2, help='Maximum number of images to download')

    args = parser.parse_args()

    # Combine search terms into a single string
    search_term = ' '.join(args.search_term)

    if not GCS_DEVELOPER_KEY or not GCS_CX:
        print("Error: Please set GOOGLE_SEARCH_API_KEY and GOOGLE_SEARCH_CX environment variables")
        sys.exit(1)

    gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)

    # Define search params
    search_params = {
        'q': search_term,
        'num': args.max_results,
        # 'imgType': 'photo',
        # 'safe': 'high',
        # 'imgSize': 'xxlarge',  # Filter for largest images
        'imgSize': 'HUGE',  # Filter for largest images
        # 'exactTerms': args.search_term,
        # 'rights': 'cc_publicdomain|cc_attribute|cc_sharealike',
        'aspectRatio': 'wide',  # Prefer wide aspect ratios
    }

    max_retries = 3
    retry_delay = 2  # seconds

    print(search_params)

    for attempt in range(max_retries):
        try:
            # Search for images
            gis.search(search_params)

            # Create folder for saving images
            folder_name = sanitize_filename(search_term)
            os.makedirs(folder_name, exist_ok=True)

            # Download results
            results_found = 0
            for image in gis.results():
                # if results_found >= args.max_results:
                #     break

                try:
                    print(f"Downloading: {image.url}")
                    image.download(folder_name)
                    results_found += 1
                except Exception as e:
                    print(f"Error downloading image: {str(e)}", file=sys.stderr)
                    continue

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
