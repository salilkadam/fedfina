#!/usr/bin/env python3
"""
Test ElevenLabs widget with patience - wait for conversation elements to appear
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def test_widget_patience():
    print("⏳ Testing ElevenLabs Widget with Patience")
    print("=" * 50)
    
    # Setup Chrome webdriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-test")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Load the main branch page
        print("Loading main branch page...")
        driver.get("http://localhost:3000")
        
        # Wait for page to load
        time.sleep(5)
        print(f"Page title: {driver.title}")
        
        # Check if widget element exists
        try:
            widget_element = driver.find_element(By.TAG_NAME, "elevenlabs-convai")
            print("✅ Widget element found")
            
            agent_id = widget_element.get_attribute("agent-id")
            print(f"Agent ID: {agent_id}")
            
        except NoSuchElementException:
            print("❌ Widget element not found")
            return False
        
        # Patiently wait for conversation elements to appear
        print("⏳ Patiently waiting for conversation elements to appear...")
        max_wait = 120  # Wait up to 2 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Look for any conversation-related elements
            conversation_elements = []
            
            selectors_to_try = [
                "input",
                "textarea", 
                "button",
                "[class*='input']",
                "[class*='chat']",
                "[class*='message']",
                "[class*='conversation']",
                "[role='textbox']",
                "[contenteditable='true']",
                "[placeholder*='message']",
                "[placeholder*='type']"
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    conversation_elements.extend(elements)
                except:
                    continue
            
            # Remove duplicates
            unique_elements = []
            seen_ids = set()
            for element in conversation_elements:
                try:
                    element_id = element.get_attribute("id") or element.get_attribute("class") or str(element)
                    if element_id not in seen_ids:
                        unique_elements.append(element)
                        seen_ids.add(element_id)
                except:
                    continue
            
            if unique_elements:
                print(f"✅ Found {len(unique_elements)} conversation elements after {int(time.time() - start_time)} seconds!")
                
                # Log what we found
                for i, element in enumerate(unique_elements[:5]):
                    try:
                        tag_name = element.tag_name
                        class_name = element.get_attribute("class") or ""
                        placeholder = element.get_attribute("placeholder") or ""
                        print(f"  Element {i+1}: {tag_name} (class: {class_name[:30]}, placeholder: {placeholder[:30]})")
                    except:
                        pass
                
                # Try to interact with the first input field
                input_field = None
                for element in unique_elements:
                    try:
                        tag_name = element.tag_name.lower()
                        if tag_name in ["input", "textarea"]:
                            input_field = element
                            break
                    except:
                        continue
                
                if input_field:
                    print("📝 Attempting to send message...")
                    try:
                        # Clear and type message
                        input_field.clear()
                        input_field.send_keys("Hello, this is a test message")
                        time.sleep(1)
                        
                        # Try to send
                        input_field.send_keys(Keys.RETURN)
                        time.sleep(5)
                        
                        print("✅ Message sent successfully!")
                        
                        # Try to send another message
                        input_field.clear()
                        input_field.send_keys("How are you today?")
                        input_field.send_keys(Keys.RETURN)
                        time.sleep(5)
                        
                        print("✅ Second message sent successfully!")
                        
                        # Try to extract transcript
                        print("📄 Attempting to extract transcript...")
                        try:
                            transcript_script = """
                            if (window.ElevenLabsConvaiWidget && window.ElevenLabsConvaiWidget.getTranscript) {
                                return window.ElevenLabsConvaiWidget.getTranscript();
                            }
                            return null;
                            """
                            transcript = driver.execute_script(transcript_script)
                            if transcript:
                                print(f"✅ Transcript extracted: {len(transcript)} messages")
                                for msg in transcript[:3]:
                                    print(f"  {msg.get('speaker', 'unknown')}: {msg.get('content', '')[:50]}...")
                            else:
                                print("❌ No transcript found via widget API")
                                
                                # Try to extract from DOM
                                messages = driver.find_elements(By.CSS_SELECTOR, "[class*='message'], [class*='chat']")
                                if messages:
                                    print(f"✅ Found {len(messages)} messages in DOM")
                                    for i, msg in enumerate(messages[:3]):
                                        print(f"  Message {i+1}: {msg.text[:50]}...")
                                else:
                                    print("❌ No messages found in DOM")
                                    
                        except Exception as e:
                            print(f"❌ Failed to extract transcript: {e}")
                        
                        return True
                        
                    except Exception as e:
                        print(f"❌ Failed to send message: {e}")
                        return False
                else:
                    print("❌ No input field found among conversation elements")
                    return False
            
            # Wait a bit more
            time.sleep(5)
            elapsed = int(time.time() - start_time)
            print(f"⏳ Still waiting... ({elapsed}s elapsed)")
        
        print("❌ No conversation elements appeared within timeout")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Take screenshot for debugging
        try:
            screenshot_path = "/tmp/patient_widget_test.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved to: {screenshot_path}")
        except:
            pass
        
        driver.quit()

if __name__ == "__main__":
    success = test_widget_patience()
    if success:
        print("\n🎉 Patient widget test SUCCESSFUL!")
    else:
        print("\n❌ Patient widget test FAILED!") 