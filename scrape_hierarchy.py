# Script to download GPX files for all activities in mountains_hierarchy.json
# with hierarchical folder structure: mountain_name/model-course_name/activity_title.gpx
#
# Usage:
#   1. Activate conda environment: conda activate sindy
#   2. Run script: python scrape_hierarchy.py
#
# Requirements:
#   - conda environment 'sindy' with selenium and beautifulsoup4
#   - yamap_cookies.json in Desktop folder
#   - mountains_hierarchy.json in Desktop folder

import os
import time
import re
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Cookie file path
COOKIE_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "yamap_cookies.json")
HIERARCHY_FILE = os.path.join(os.path.expanduser("~"), "Desktop", "mountains_hierarchy.json")


def load_cookies_from_json(driver, filepath):
    """Load cookies from JSON file"""
    if not os.path.exists(filepath):
        print(f"  ✗ Cookie file not found: {filepath}")
        return False
    
    try:
        with open(filepath, 'r') as f:
            cookies = json.load(f)
        
        # First navigate to the domain
        print(f"  Loading cookies from {filepath}...")
        driver.get("https://yamap.com")
        time.sleep(2)
        
        # Add each cookie
        added = 0
        for cookie in cookies:
            try:
                # Convert browser cookie format to Selenium format
                cookie_dict = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie['domain'],
                    'path': cookie['path'],
                    'secure': cookie.get('secure', False),
                }
                
                # Add expiry if present
                if 'expirationDate' in cookie:
                    cookie_dict['expiry'] = int(cookie['expirationDate'])
                
                # Add httpOnly if present
                if 'httpOnly' in cookie:
                    cookie_dict['httpOnly'] = cookie['httpOnly']
                
                # Add sameSite if present
                if 'sameSite' in cookie and cookie['sameSite'] != 'unspecified':
                    cookie_dict['sameSite'] = cookie['sameSite']
                
                driver.add_cookie(cookie_dict)
                added += 1
            except Exception as e:
                # Some cookies might fail, that's okay
                pass
        
        print(f"  ✓ Loaded {added}/{len(cookies)} cookies")
        return True
    except Exception as e:
        print(f"  ✗ Failed to load cookies: {e}")
        return False


def verify_login(driver):
    """Check if user is logged in"""
    try:
        # Check cookies directly
        cookies = driver.get_cookies()
        cookie_names = [c['name'] for c in cookies]
        
        # Check for yamap_token which is the authentication cookie
        if 'yamap_token' in cookie_names and 'user_id' in cookie_names:
            print("  ✓ Found authentication cookies (yamap_token, user_id)")
            return True
        
        print("  ✗ Missing authentication cookies")
        return False
    except Exception as e:
        print(f"  ✗ Error verifying login: {e}")
        return False


def login_with_cookies(driver):
    """
    Login to YAMAP using cookies from JSON file
    Returns True if successful
    """
    # Load cookies from JSON file
    if not load_cookies_from_json(driver, COOKIE_FILE):
        print("✗ Failed to load cookies")
        return False
    
    # Verify login by refreshing and checking
    print("  Verifying login...")
    driver.get("https://yamap.com")
    time.sleep(3)
    
    if verify_login(driver):
        print("✓ Successfully logged in with cookies!\n")
        return True
    else:
        print("✗ Cookies didn't work, login verification failed")
        print("  Please update your cookies in yamap_cookies.json")
        return False


def sanitize_filename(filename):
    """
    Sanitize filename to be filesystem-safe
    """
    # Replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Replace multiple spaces with single space
    filename = re.sub(r'\s+', ' ', filename)
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 150:
        filename = filename[:150]
    return filename


def get_activity_title(driver, activity_id):
    """
    Extract the activity title from the page
    """
    try:
        # Wait for page to load
        time.sleep(2)

        # Get page source
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Try to get title from <title> tag
        title_tag = soup.find('title')
        if title_tag:
            full_title = title_tag.get_text().strip()
            # Extract the main title before the " / " separator
            match = re.match(r'^([^/]+)', full_title)
            if match:
                title = match.group(1).strip()
                return title

        # Fallback: try to find h1 or main title on page
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text().strip()
            return title

        return f"activity_{activity_id}"

    except Exception as e:
        print(f"  Error extracting title: {e}")
        return f"activity_{activity_id}"


def download_gpx_for_activity(driver, activity_id, output_dir, activity_title=None):
    """
    Download GPX for a single activity using an existing browser session
    Returns (success, filename) tuple
    """
    try:
        # Navigate to activity page
        print(f"    Navigating to activity page...")
        driver.get(f"https://yamap.com/activities/{activity_id}")
        
        # Random delay to avoid rate limiting (2-5 seconds)
        delay = random.uniform(2, 5)
        time.sleep(delay)
        
        # Check if we got redirected to login page
        current_url = driver.current_url
        if "login" in current_url.lower():
            print(f"    ⚠ Session expired, need to re-login")
            return (False, None)

        # Get title - use provided title or scrape from page
        if activity_title:
            title = activity_title
        else:
            title = get_activity_title(driver, activity_id)
        
        safe_title = sanitize_filename(title)
        output_filename = f"{safe_title}.gpx"

        # Check if file already exists
        final_path = os.path.join(output_dir, output_filename)
        if os.path.exists(final_path):
            print(f"    ⊘ File already exists, skipping...")
            return (True, output_filename)

        # Find and click export button
        print(f"    Looking for export button...")
        possible_selectors = [
            "//button[contains(text(), 'エクスポート')]",
            "//button[contains(@class, 'DownloadButton')]",
            "//a[contains(text(), 'エクスポート')]",
        ]

        export_button = None
        for selector in possible_selectors:
            try:
                export_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
                if export_button:
                    break
            except:
                continue

        if export_button:
            existing_gpx_files = set([f for f in os.listdir(output_dir) if f.endswith('.gpx')])

            driver.execute_script("arguments[0].scrollIntoView(true);", export_button)
            time.sleep(1)
            export_button.click()

            # Wait for download
            print(f"    Waiting for download...")
            for i in range(15):
                time.sleep(1)
                current_gpx_files = set([f for f in os.listdir(output_dir) if f.endswith('.gpx')])
                new_files = current_gpx_files - existing_gpx_files

                if new_files:
                    new_file = list(new_files)[0]
                    downloaded_path = os.path.join(output_dir, new_file)

                    if downloaded_path != final_path:
                        if os.path.exists(final_path):
                            os.remove(final_path)
                        os.rename(downloaded_path, final_path)
                    else:
                        final_path = downloaded_path

                    return (True, output_filename)

            print(f"    ✗ Download timeout")
            return (False, None)
        else:
            print("    ✗ Could not find export button")
            return (False, None)

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return (False, None)


def load_hierarchy_json(filepath):
    """Load the mountains hierarchy JSON file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"✗ Error loading hierarchy file: {e}")
        return None


def count_total_activities(data):
    """Count total number of activities in the hierarchy"""
    total = 0
    for mountain in data.get('mountains', []):
        for model_course in mountain.get('model_courses', []):
            total += len(model_course.get('activities', []))
    return total


def main():
    print("=" * 80)
    print("YAMAP GPX Hierarchical Downloader")
    print("=" * 80)
    print(f"Hierarchy file: {HIERARCHY_FILE}")
    print(f"Cookie file: {COOKIE_FILE}")
    print()

    # Load hierarchy data
    print("Loading mountains hierarchy...")
    hierarchy_data = load_hierarchy_json(HIERARCHY_FILE)
    if not hierarchy_data:
        print("✗ Failed to load hierarchy data")
        return

    total_mountains = len(hierarchy_data.get('mountains', []))
    total_activities = count_total_activities(hierarchy_data)
    print(f"✓ Loaded {total_mountains} mountains with {total_activities} total activities")
    print()

    # Base download directory
    base_download_dir = os.path.join(os.path.expanduser("~"), "Desktop", "yamap_gpx_hierarchy")
    os.makedirs(base_download_dir, exist_ok=True)
    print(f"Base download directory: {base_download_dir}")
    print()

    # Setup Chrome with download preferences
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Login with cookies
        print("Logging in to YAMAP...")
        if not login_with_cookies(driver):
            print("✗ Failed to login")
            return
        
        # Statistics
        total_processed = 0
        successful = 0
        failed = 0
        skipped = 0

        # Iterate through mountains
        for mountain_idx, mountain in enumerate(hierarchy_data.get('mountains', []), 1):
            mountain_name = mountain.get('name', f"mountain_{mountain.get('id')}")
            safe_mountain_name = sanitize_filename(mountain_name)
            
            print(f"\n{'='*80}")
            print(f"[{mountain_idx}/{total_mountains}] Mountain: {mountain_name}")
            print(f"{'='*80}")
            
            # Create mountain directory
            mountain_dir = os.path.join(base_download_dir, safe_mountain_name)
            os.makedirs(mountain_dir, exist_ok=True)
            
            # Iterate through model courses
            model_courses = mountain.get('model_courses', [])
            for course_idx, model_course in enumerate(model_courses, 1):
                course_name = model_course.get('name', f"course_{model_course.get('id')}")
                # Clean up the course name (remove extra whitespace and newlines)
                course_name = ' '.join(course_name.split())
                safe_course_name = sanitize_filename(course_name)
                
                activities = model_course.get('activities', [])
                if not activities:
                    print(f"  [{course_idx}/{len(model_courses)}] {course_name}: No activities")
                    continue
                
                print(f"\n  [{course_idx}/{len(model_courses)}] Model Course: {course_name}")
                print(f"  Activities: {len(activities)}")
                
                # Create model course directory
                course_dir = os.path.join(mountain_dir, safe_course_name)
                os.makedirs(course_dir, exist_ok=True)
                
                # Set download directory for this course
                prefs = {
                    "download.default_directory": course_dir,
                    "download.prompt_for_download": False,
                    "download.directory_upgrade": True,
                    "safebrowsing.enabled": True
                }
                driver.execute_cdp_cmd('Page.setDownloadBehavior', {
                    'behavior': 'allow',
                    'downloadPath': course_dir
                })
                
                # Iterate through activities
                for activity_idx, activity in enumerate(activities, 1):
                    activity_id = activity.get('id')
                    activity_title = activity.get('title', f"activity_{activity_id}")
                    
                    total_processed += 1
                    print(f"\n    [{activity_idx}/{len(activities)}] Activity {activity_id}: {activity_title}")
                    
                    success, filename = download_gpx_for_activity(
                        driver, 
                        activity_id, 
                        course_dir,
                        activity_title
                    )
                    
                    if success:
                        if "already exists" in str(filename):
                            skipped += 1
                        else:
                            successful += 1
                        print(f"    ✓ {filename}")
                    else:
                        failed += 1
                        print(f"    ✗ Failed")
                    
                    # Random delay between activities
                    if activity_idx < len(activities):  # Don't delay after last activity
                        delay = random.uniform(2, 4)
                        time.sleep(delay)
                
                # Longer delay between courses
                if course_idx < len(model_courses):
                    delay = random.uniform(3, 5)
                    time.sleep(delay)
            
            # Even longer delay between mountains
            if mountain_idx < total_mountains:
                delay = random.uniform(5, 8)
                print(f"\n  Waiting {delay:.1f}s before next mountain...")
                time.sleep(delay)

    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n\nClosing browser...")
        driver.quit()

    # Summary
    print()
    print("=" * 80)
    print("DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"Total activities processed: {total_processed}")
    print(f"✓ Successfully downloaded:  {successful}")
    print(f"⊘ Skipped (already exists): {skipped}")
    print(f"✗ Failed:                   {failed}")
    print(f"Download directory: {base_download_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()

