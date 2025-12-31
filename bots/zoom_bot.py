import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

def join_zoom(meeting_link):
    print("Initializing Zoom Bot...")

    # 1. FORCE WEB CLIENT URL
    try:
        meeting_id = re.search(r"/j/(\d+)", meeting_link).group(1)
    except AttributeError:
        meeting_id = None
        web_link = meeting_link.replace("/j/", "/wc/join/")

    if meeting_id:
        # We append ?prefer=1 to force web client
        web_link = f"https://zoom.us/wc/join/{meeting_id}?prefer=1"
        if "?pwd=" in meeting_link:
            pwd_segment = "&pwd=" + meeting_link.split("?pwd=")[1].split("&")[0]
            web_link += pwd_segment
    
    print(f"Target Link: {web_link}")

    # 2. CONFIG: BLOCK MIC/CAM (Forces 'Continue without mic')
    opt = Options()
    opt.add_argument("--start-maximized")
    opt.add_argument("--disable-blink-features=AutomationControlled")
    opt.add_experimental_option("prefs", { 
        "profile.default_content_setting_values.media_stream_mic": 2, 
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.notifications": 2
    })

    driver = webdriver.Chrome(options=opt)
    wait = WebDriverWait(driver, 10)

    try:
        driver.get(web_link)
        time.sleep(3) # Initial load wait

        # --- PHASE 1: CLEAR POPUPS (Critical for finding input) ---
        print("--- Clearing Popups ---")
        try:
            # Agree to Terms
            agree_btn = driver.find_element(By.ID, "wc_agree1")
            agree_btn.click()
            print("Clicked Terms Agree.")
            time.sleep(1)
        except:
            pass

        try:
            # Cookie Accept
            cookie_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
            cookie_btn.click()
            print("Clicked Cookie Accept.")
            time.sleep(1)
        except:
            pass

        # --- PHASE 2: ENTER NAME (Robust Search) ---
        print("--- Looking for Name Input ---")
        name_entered = False
        
        # List of possible selectors for the Name Input field
        name_selectors = [
            (By.ID, "inputname"),                                   # Standard
            (By.XPATH, "//input[@placeholder='Your Name']"),        # Placeholder
            (By.XPATH, "//input[@placeholder='Enter your name']"),  # Alt Placeholder
            (By.CSS_SELECTOR, "input[type='text']")                 # Generic Fallback
        ]

        for method, selector in name_selectors:
            try:
                input_field = driver.find_element(method, selector)
                if input_field.is_displayed():
                    input_field.clear()
                    input_field.send_keys("Meeting Bot")
                    print(f"Entered name using: {selector}")
                    name_entered = True
                    break
            except:
                continue
        
        if name_entered:
            time.sleep(1)
            # Click Join Button
            try:
                join_btn = driver.find_element(By.ID, "joinBtn")
                join_btn.click()
                print("Clicked 'Join' (ID: joinBtn)")
            except:
                try:
                    # Fallback by text
                    join_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Join')]")
                    join_btn.click()
                    print("Clicked 'Join' (By Text)")
                except Exception as e:
                    print(f"Could not find Join button: {e}")
            
            # Wait for meeting to transition
            time.sleep(5)
        else:
            print("Could not find any Name Input field. Assuming already logged in.")

        # --- PHASE 3: AUDIO CHOICE (Mic Blocked) ---
        print("--- Handling Audio ---")
        try:
            # Look for 'Continue without microphone' since mic is blocked
            no_mic_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continue without microphone')]"))
            )
            no_mic_btn.click()
            print("Selected: Continue without microphone.")
        except TimeoutException:
            print("Audio popup not found. Attempting fallback...")
            try:
                driver.find_element(By.XPATH, "//button[contains(text(), 'Join Audio by Computer')]").click()
            except:
                pass

        print(">>> SUCCESS: Setup Complete.")

    except Exception as e:
        print(f"Zoom Crash: {e}")
        # Keep window open for debugging
        pass

    return driver 