# Script to scrape mountains, model courses, and activities from YAMAP
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


def scrape_mountains_list(driver, base_url):
    """
    Scrape the list of mountains from the 100 famous mountains page (paginated)
    Returns list of dicts with mountain name, ID, and URL
    """
    mountains = []
    seen_ids = set()

    # The list is paginated across 10 pages
    for page in range(1, 11):
        page_url = f"{base_url}?page={page}"
        print(f"\nScraping mountains page {page}/10: {page_url}")

        driver.get(page_url)
        time.sleep(random.uniform(2, 4))

        # Scroll down to ensure all content loads
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all mountain links (format: /mountains/{id})
        # Use more flexible regex pattern
        mountain_links = soup.find_all('a', href=re.compile(r'/mountains/\d+'))

        print(f"  Found {len(mountain_links)} potential mountain links")

        page_count = 0
        for link in mountain_links:
            href = link.get('href')

            # Only match direct mountain links, not sub-paths
            match = re.match(r'^/mountains/(\d+)$', href)
            if match:
                mountain_id = match.group(1)
                if mountain_id not in seen_ids:
                    seen_ids.add(mountain_id)

                    # Get mountain name - try multiple approaches
                    name = link.get_text().strip()

                    # If link text is empty or too short, try parent element
                    if not name or len(name) < 2:
                        parent = link.parent
                        if parent:
                            # Look for heading tags that might contain the name
                            heading = parent.find(['h1', 'h2', 'h3', 'h4'])
                            if heading:
                                name = heading.get_text().strip()

                            # If still no name, get all text from parent
                            if not name or len(name) < 2:
                                parent_text = parent.get_text().strip()
                                # Get first line or first few words
                                lines = parent_text.split('\n')
                                if lines:
                                    name = lines[0].strip()

                    # Clean up the name (remove extra whitespace)
                    if name:
                        name = ' '.join(name.split())

                    if name and len(name) >= 2:
                        mountains.append({
                            'id': mountain_id,
                            'name': name,
                            'url': f"https://yamap.com/mountains/{mountain_id}"
                        })
                        page_count += 1

        print(f"  Found {page_count} new mountains on page {page} (Total: {len(mountains)})")

        # Debug: save HTML if first page has very few results
        if page == 1 and page_count < 3:
            debug_file = os.path.join(os.path.expanduser("~"), "Desktop", "debug_mountains_page.html")
            with open(debug_file, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"  ⚠ Warning: Only found {page_count} mountains on first page")
            print(f"  Saved page HTML to: {debug_file}")

        # If no mountains found on this page, maybe we've reached the end
        if page_count == 0:
            print(f"  No new mountains found, stopping pagination")
            break

    print(f"\n✓ Total unique mountains found: {len(mountains)}")
    return mountains


def scrape_model_courses(driver, mountain_url, mountain_id):
    """
    Scrape model courses from a mountain page
    Returns list of dicts with course name, ID, and URL
    """
    print(f"  Scraping model courses from: {mountain_url}")
    driver.get(mountain_url)
    time.sleep(random.uniform(2, 4))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    courses = []

    # Find all model course links (format: /model-courses/{id})
    course_links = soup.find_all('a', href=re.compile(r'/model-courses/\d+'))

    seen_ids = set()
    for link in course_links:
        href = link.get('href')
        match = re.search(r'/model-courses/(\d+)', href)
        if match:
            course_id = match.group(1)
            if course_id not in seen_ids:
                seen_ids.add(course_id)

                # Get course name from link text or nearby elements
                name = link.get_text().strip()
                if not name:
                    # Try to get name from parent or sibling elements
                    parent = link.parent
                    if parent:
                        name = parent.get_text().strip()

                if name:
                    courses.append({
                        'id': course_id,
                        'name': name,
                        'url': f"https://yamap.com/model-courses/{course_id}"
                    })

    print(f"    Found {len(courses)} model courses")
    return courses


def scrape_activities_from_course(driver, course_url, course_id):
    """
    Scrape activities from a model course page
    Returns list of dicts with activity title, ID, and URL
    """
    print(f"    Scraping activities from: {course_url}")
    driver.get(course_url)
    time.sleep(random.uniform(2, 4))

    # Scroll down to load more content
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    activities = []

    # Find all activity links (format: /activities/{id})
    activity_links = soup.find_all('a', href=re.compile(r'/activities/\d+'))

    seen_ids = set()
    for link in activity_links:
        href = link.get('href')
        match = re.search(r'/activities/(\d+)', href)
        if match:
            activity_id = match.group(1)
            if activity_id not in seen_ids:
                seen_ids.add(activity_id)

                # Get activity title from link text or nearby elements
                title = link.get_text().strip()
                if not title or len(title) < 3:
                    # Try to get title from parent or sibling elements
                    parent = link.parent
                    if parent:
                        text = parent.get_text().strip()
                        if len(text) > len(title):
                            title = text

                activities.append({
                    'id': activity_id,
                    'title': title if title else f"Activity {activity_id}",
                    'url': f"https://yamap.com/activities/{activity_id}"
                })

    print(f"      Found {len(activities)} activities")
    return activities


def get_activity_title_from_page(driver, activity_url, activity_id):
    """
    Get the actual title from an activity page
    """
    try:
        driver.get(activity_url)
        time.sleep(random.uniform(1, 2))

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

        return f"Activity {activity_id}"

    except Exception as e:
        print(f"      Error getting title: {e}")
        return f"Activity {activity_id}"


def scrape_mountains_hierarchy(driver, mountains_list_url, limit_mountains=None):
    """
    Main function to scrape the entire hierarchy:
    Mountains -> Model Courses -> Activities (last 2)
    
    Args:
        driver: Selenium WebDriver instance
        mountains_list_url: URL of the mountains list page
        limit_mountains: Optional limit on number of mountains to process (for testing)
    
    Returns:
        Dict containing the hierarchy
    """
    # Step 1: Get mountains list
    mountains = scrape_mountains_list(driver, mountains_list_url)

    if limit_mountains:
        mountains = mountains[:limit_mountains]
        print(f"\n⚠ Limiting to first {limit_mountains} mountains for testing\n")

    result = {
        'source_url': mountains_list_url,
        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_mountains': len(mountains),
        'mountains': []
    }

    # Step 2: For each mountain, get model courses
    for idx, mountain in enumerate(mountains, 1):
        print(f"\n[{idx}/{len(mountains)}] Processing mountain: {mountain['name']} (ID: {mountain['id']})")

        mountain_data = {
            'id': mountain['id'],
            'name': mountain['name'],
            'url': mountain['url'],
            'model_courses': []
        }

        try:
            # Get model courses for this mountain
            courses = scrape_model_courses(driver, mountain['url'], mountain['id'])

            # Step 3: For each model course, get activities
            for course_idx, course in enumerate(courses, 1):
                print(f"  [{course_idx}/{len(courses)}] Processing course: {course['name']} (ID: {course['id']})")

                course_data = {
                    'id': course['id'],
                    'name': course['name'],
                    'url': course['url'],
                    'activities': []
                }

                try:
                    # Get activities for this course
                    activities = scrape_activities_from_course(driver, course['url'], course['id'])

                    # Step 4: Get last 2 activities (or fewer if there aren't 2)
                    last_activities = activities[-2:] if len(activities) >= 2 else activities

                    for activity in last_activities:
                        print(f"      Getting title for activity {activity['id']}...")

                        # Get proper title from activity page
                        title = get_activity_title_from_page(driver, activity['url'], activity['id'])

                        activity_data = {
                            'id': activity['id'],
                            'title': title,
                            'url': activity['url']
                        }
                        course_data['activities'].append(activity_data)

                        print(f"      ✓ {title}")

                        # Small delay between activity page requests
                        time.sleep(random.uniform(1, 2))

                except Exception as e:
                    print(f"      ✗ Error processing course {course['id']}: {e}")

                mountain_data['model_courses'].append(course_data)

                # Delay between courses
                time.sleep(random.uniform(2, 3))

        except Exception as e:
            print(f"  ✗ Error processing mountain {mountain['id']}: {e}")

        result['mountains'].append(mountain_data)

        # Delay between mountains
        time.sleep(random.uniform(3, 5))

    return result


if __name__ == "__main__":
    print("=" * 80)
    print("YAMAP Mountains -> Model Courses -> Activities Scraper")
    print("=" * 80)
    print(f"Using cookies from: {COOKIE_FILE}\n")

    # URL for 都道府県最高峰
    # mountains_list_url = "https://yamap.com/mountains/famous/252321"

    # # URL for 日本百名山
    # mountains_list_url = "https://yamap.com/mountains/famous/27504"

    # # URL for 日本二百名山
    # mountains_list_url = "https://yamap.com/mountains/famous/27505"

    # # URL for 日本百高山
    # mountains_list_url = "https://yamap.com/mountains/famous/559740"

    # # URL for 3000m峰
    mountains_list_url = "https://yamap.com/mountains/famous/265338"

    # Output file
    output_file = os.path.join(os.path.expanduser("~"), "Desktop",
                               "mountains_hierarchy.json")

    # Limit for testing (set to None to scrape all mountains)
    LIMIT_MOUNTAINS = None  # Set to a small number like 3 for testing

    # Setup Chrome
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Login with cookies
        print("Logging in to YAMAP...")
        if not login_with_cookies(driver):
            print("✗ Failed to login")
            driver.quit()
            exit(1)

        # Scrape the hierarchy
        print("\nStarting scraping process...")
        print("-" * 80)

        result = scrape_mountains_hierarchy(driver,
                                            mountains_list_url,
                                            limit_mountains=LIMIT_MOUNTAINS)

        # Save to JSON file
        print("\n" + "=" * 80)
        print("Saving results to JSON...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"✓ Results saved to: {output_file}")

        # Print summary
        print("\n" + "=" * 80)
        print("SCRAPING SUMMARY")
        print("=" * 80)
        print(f"Total mountains:     {result['total_mountains']}")

        total_courses = sum(
            len(m['model_courses']) for m in result['mountains'])
        print(f"Total model courses: {total_courses}")

        total_activities = sum(
            len(c['activities']) for m in result['mountains']
            for c in m['model_courses'])
        print(f"Total activities:    {total_activities}")
        print(f"Output file:         {output_file}")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("\nClosing browser...")
        driver.quit()
        print("Done!")
