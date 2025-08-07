#!/usr/bin/env python3
"""
Simple test to automate conversation with the working ElevenLabs widget from main branch
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def test_main_branch_widget():
    print("🧪 Testing Main Branch ElevenLabs Widget")
    print("=" * 50)
    
    # Setup Chrome webdriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
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
            
            # Check if widget is visible
            is_displayed = widget_element.is_displayed()
            print(f"Widget displayed: {is_displayed}")
            
            # Get widget dimensions
            size = widget_element.size
            location = widget_element.location
            print(f"Widget size: {size}")
            print(f"Widget location: {location}")
            
        except NoSuchElementException:
            print("❌ Widget element not found")
            return False
        
        # Wait for widget to fully load
        print("⏳ Waiting for widget to fully load...")
        time.sleep(10)
        
        # Look for conversation elements
        print("🔍 Looking for conversation elements...")
        
        # Try different selectors to find conversation interface
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
        
        conversation_elements = []
        for selector in selectors_to_try:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector '{selector}'")
                    for i, element in enumerate(elements[:3]):  # Log first 3
                        try:
                            tag_name = element.tag_name
                            class_name = element.get_attribute("class") or ""
                            placeholder = element.get_attribute("placeholder") or ""
                            print(f"  Element {i+1}: {tag_name} (class: {class_name[:30]}, placeholder: {placeholder[:30]})")
                            conversation_elements.append(element)
                        except:
                            pass
            except:
                continue
        
        print(f"Total conversation elements found: {len(conversation_elements)}")
        
        # Try to interact with the widget
        print("🎯 Attempting to interact with widget...")
        
        # Try clicking on the widget first
        try:
            print("Clicking on widget element...")
            driver.execute_script("arguments[0].click();", widget_element)
            time.sleep(3)
            print("Widget clicked")
        except Exception as e:
            print(f"Failed to click widget: {e}")
        
        # Look for input field again after clicking
        print("🔍 Looking for input field after clicking...")
        input_field = None
        
        for element in conversation_elements:
            try:
                tag_name = element.tag_name.lower()
                class_name = element.get_attribute("class") or ""
                placeholder = element.get_attribute("placeholder") or ""
                
                if tag_name in ["input", "textarea"]:
                    print(f"Found input element: {tag_name} (class: {class_name[:30]}, placeholder: {placeholder[:30]})")
                    input_field = element
                    break
                    
            except Exception as e:
                continue
        
        # If no input field found, try to find it again
        if not input_field:
            print("No input field found, searching again...")
            try:
                input_field = driver.find_element(By.CSS_SELECTOR, "input, textarea")
                print("Found input field on second search")
            except:
                print("Still no input field found")
        
        # Try to send a message if input field is found
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
                    # Try different methods to get transcript
                    transcript_script = """
                    if (window.ElevenLabsConvaiWidget && window.ElevenLabsConvaiWidget.getTranscript) {
                        return window.ElevenLabsConvaiWidget.getTranscript();
                    }
                    return null;
                    """
                    transcript = driver.execute_script(transcript_script)
                    if transcript:
                        print(f"✅ Transcript extracted: {len(transcript)} messages")
                        for msg in transcript[:3]:  # Show first 3 messages
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
            print("❌ No input field found for conversation")
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        # Take screenshot for debugging
        try:
            screenshot_path = "/tmp/main_branch_test.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved to: {screenshot_path}")
        except:
            pass
        
        driver.quit()

if __name__ == "__main__":
    success = test_main_branch_widget()
    if success:
        print("\n🎉 Main branch widget test SUCCESSFUL!")
    else:
        print("\n❌ Main branch widget test FAILED!") 