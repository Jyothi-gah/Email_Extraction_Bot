import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def join_google_meet(meeting_link):
    print("Initializing Google Meet Bot (Guest Mode)...")
    
    # 1. Setup Options
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-notifications")
    
    # Block Mic and Camera Permissions (Value 2 = Block)
    # This prevents the browser from asking "Allow Microphone?"
    options.add_experimental_option("prefs", { 
        "profile.default_content_setting_values.media_stream_mic": 2, 
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.notifications": 2
    })
    
    # Initialize Driver
    driver = uc.Chrome(options=options)
    wait = WebDriverWait(driver, 20)
    
    try:
        driver.get(meeting_link)
        time.sleep(5)

        # --- PHASE 1: HANDLE GUEST NAME ---
        # Since we are guests, Google asks "What's your name?"
        try:
            # Look for the input field
            # Common selectors: placeholder text or standard input types
            name_input = None
            inputs = driver.find_elements(By.TAG_NAME, "input")
            
            for inp in inputs:
                # Check visible text inputs
                if inp.is_displayed() and inp.get_attribute("type") == "text":
                    placeholder = inp.get_attribute("placeholder")
                    if placeholder and ("name" in placeholder.lower()):
                        name_input = inp
                        break
            
            if name_input:
                name_input.clear()
                name_input.send_keys("Meeting Bot")
                print("Entered Guest Name.")
                
                # Sometimes a 'Next' button appears, or we just click Ask to Join
                time.sleep(1)
        except Exception as e:
            print(f"Name input check skipped: {e}")

        # --- PHASE 2: DISMISS POPUPS ---
        # (Mic/Cam are blocked by prefs, so fewer popups, but checking anyway)
        try:
            driver.find_element(By.XPATH, "//span[contains(text(), 'Dismiss')]").click()
        except: pass
        
        try:
            # Sometimes "Continue without microphone" appears because we blocked it
            driver.find_element(By.XPATH, "//span[contains(text(), 'Continue without microphone')]").click()
        except: pass

        # --- PHASE 3: CLICK JOIN ---
        print("Clicking Join...")
        try:
            # Look for "Ask to join"
            xpath = "//span[contains(text(), 'Ask to join') or contains(text(), 'Join now')]/ancestor::button"
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            btn.click()
            print("Clicked 'Ask to join'. WAITING FOR HOST TO ADMIT.")
        except:
            # Fallback generic click
            try:
                driver.find_element(By.XPATH, "//span[contains(text(), 'Join')]").click()
            except:
                print("Could not find Join button.")

    except Exception as e:
        print(f"Google Meet Error: {e}")

    return driver