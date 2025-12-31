import time
import os
import sys
from selenium.common.exceptions import WebDriverException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from config import OUTPUT_DIR, AUDIO_DEVICE_NAME
from utils.email_parser import fetch_latest_meeting_email
from utils.recorder import AudioRecorder

# Import Bots
from bots.google_meet import join_google_meet
from bots.zoom_bot import join_zoom
from bots.zoho_bot import join_zoho

def save_metadata(details):
    filename = os.path.join(OUTPUT_DIR, f"meeting_{int(time.time())}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Subject: {details['subject']}\n")
        f.write(f"Link: {details['link']}\n")
        f.write(f"From: {details['from']}\n")
        f.write(f"To: {details['to']}\n")
        f.write(f"CC: {details['cc']}\n")
        f.write(f"Platform: {details['platform']}\n")
    return filename

def check_if_meeting_ended(driver):
    """
    Checks if specific 'Meeting Ended' text is VISIBLE on screen.
    Returns True if meeting has ended, False otherwise.
    """
    try:
        # ZOOM: Check for the specific popup text
        # We use a list of common end phrases
        end_phrases = [
            "No one else is in this meeting",
            "This meeting has been ended by host",
            "The host has ended this meeting",
            "The host has removed you from the meeting",
            "The host has left the meeting",
            "You have been removed",
            "Thanks for Participating! The host has ended this meeting.",
            "You left the meeting"
        ]
        
        for phrase in end_phrases:
            # Find elements containing the text
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{phrase}')]")
            
            for elem in elements:
                # CRITICAL: Only count it if the user can actually see it
                if elem.is_displayed():
                    print(f">>> DETECTED END SCREEN: '{phrase}'")
                    return True

    except (NoSuchElementException, StaleElementReferenceException):
        # Element might have disappeared or DOM changed, assume meeting active
        pass
    except Exception as e:
        print(f"Status Check Error: {e}")
        
    return False

def main():
    print("--- Continuous Meeting Bot Started ---")
    print("1. Ensure System Output is set to 'CABLE Input'.")
    print("2. Close Chrome windows.")
    print("3. Press Ctrl+C to stop the bot safely.\n")

    processed_links = []

    try:
        while True:
            print(f"[{time.strftime('%H:%M:%S')}] Checking inbox...")
            
            try:
                details = fetch_latest_meeting_email()
            except Exception as e:
                print(f"Error checking email: {e}")
                details = None

            if details and details['link'] not in processed_links:
                
                print(f"\n>>> NEW MEETING FOUND: {details['subject']}")
                print(f">>> Platform: {details['platform']}")
                processed_links.append(details['link'])

                # 1. Start Recording
                audio_file = os.path.join(OUTPUT_DIR, f"meeting_{int(time.time())}.wav")
                recorder = AudioRecorder(audio_file, AUDIO_DEVICE_NAME)
                recorder.start()

                # 2. Save Metadata
                save_metadata(details)

                # 3. Join Meeting
                driver = None
                try:
                    if details['platform'] == 'google_meet':
                        driver = join_google_meet(details['link'])
                    elif details['platform'] == 'zoom':
                        driver = join_zoom(details['link'])
                    elif details['platform'] == 'zoho':
                        driver = join_zoho(details['link'])
                    
                    if driver:
                        print(">>> In Meeting. Monitoring status...")
                        
                        # --- MONITORING LOOP ---
                        meeting_active = True
                        while meeting_active:
                            time.sleep(5) # Check every 5 seconds
                            
                            # 1. Check if browser is still open
                            try:
                                _ = driver.title
                            except WebDriverException:
                                print(">>> Browser closed manually.")
                                meeting_active = False
                                break

                            # 2. Check for "Ended" Popups (Visible only)
                            if check_if_meeting_ended(driver):
                                meeting_active = False
                                break

                except Exception as e:
                    print(f"Error during meeting process: {e}")
                
                finally:
                    print(">>> Meeting Ended. Cleaning up...")
                    recorder.stop()
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                    print(">>> Waiting for next meeting (30s)...")
                    print("-" * 30)

            else:
                time.sleep(30)

    except KeyboardInterrupt:
        print("\nStopping Bot manually. Goodbye!")
        sys.exit()

if __name__ == "__main__":
    main()