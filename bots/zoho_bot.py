import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def join_zoho(meeting_link):
    print("Initializing Zoho Bot (Guest Mode)...")
    
    opt = Options()
    opt.add_argument("--start-maximized")
    opt.add_argument("--disable-blink-features=AutomationControlled")
    
    # --- FAKE DEVICE SETTINGS ---
    opt.add_argument("--use-fake-ui-for-media-stream")
    opt.add_argument("--use-fake-device-for-media-stream")
    
    # Permissions: Allow (1)
    opt.add_experimental_option("prefs", { 
        "profile.default_content_setting_values.media_stream_mic": 1, 
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.notifications": 2
    })

    driver = webdriver.Chrome(options=opt)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get(meeting_link)
        
        # --- PHASE 1: ENTER NAME ---
        print("Waiting for Name Input...")
        try:
            name_input = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//input[@placeholder='Your name']")
            ))
            name_input.clear()
            name_input.send_keys("Meeting Bot")
            time.sleep(1)
        except:
            print("Name input check skipped (might be filled).")

        # --- PHASE 2: SMART JOIN LOOP (The Fix) ---
        print("Starting Smart Join Loop (Max 45s)...")
        
        start_time = time.time()
        while time.time() - start_time < 45:
            try:
                # 1. CHECK FOR "AUDIO DEVICE" POPUP
                try:
                    continue_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Continue Anyway')]")
                    if continue_btn.is_displayed():
                        continue_btn.click()
                        print(">>> POPUP HANDLED: Clicked 'Continue Anyway'.")
                        time.sleep(2)
                except:
                    pass

                # 2. FIND "JOIN MEETING" BUTTON
                join_btn = None
                try:
                    join_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Join meeting')]")
                except:
                    pass

                # 3. DECISION LOGIC
                if join_btn and join_btn.is_displayed():
                    # If button is VISIBLE, we are NOT joined yet. Click it.
                    if join_btn.is_enabled():
                        print("Clicking 'Join meeting' button...")
                        driver.execute_script("arguments[0].click();", join_btn)
                    else:
                        print("Join button disabled (loading)...")
                
                else:
                    # If button is GONE, check if we are truly in
                    page_source = driver.page_source.lower()
                    
                    if "waiting for the host" in page_source:
                        print(">>> STATUS: Waiting for Host to Admit...")
                        break
                    
                    # Check for indicators of an active meeting (e.g., Leave button, Share button)
                    # We avoid 'mic-icon' because it exists on the join screen too.
                    # We look for the "Leave" red phone icon or text usually found inside.
                    if "leave" in page_source or "end meeting" in page_source or "participants" in page_source:
                        print(">>> STATUS: Successfully Joined!")
                        break
                    
                    # If neither, we might be transitioning, just wait
                    print("Transitioning...")

            except Exception as e:
                print(f"Loop error: {e}")
            
            time.sleep(1)

    except Exception as e:
        print(f"Zoho Error: {e}")
        pass

    return driver