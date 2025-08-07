#!/usr/bin/env python3
"""
Test ElevenLabs widget in visible browser mode
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def test_visible_widget():
    print("👁️ Testing ElevenLabs Widget in Visible Browser")
    print("=" * 50)
    
    # Setup Chrome webdriver in visible mode
    chrome_options = Options()
    # Remove headless mode to see what's happening
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
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
        
        # Wait much longer for widget to fully load
        print("⏳ Waiting 30 seconds for widget to fully load...")
        time.sleep(30)
        
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
            "[placeholder*='type']",
            "iframe"  # Widget might be in an iframe
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
        
        # Check if there are any iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Found {len(iframes)} iframes")
        
        # If there are iframes, try switching to them
        for i, iframe in enumerate(iframes):
            try:
                print(f"Switching to iframe {i+1}...")
                driver.switch_to.frame(iframe)
                
                # Look for elements in iframe
                iframe_elements = driver.find_elements(By.CSS_SELECTOR, "input, textarea, button")
                print(f"Found {len(iframe_elements)} elements in iframe {i+1}")
                
                for j, element in enumerate(iframe_elements[:3]):
                    try:
                        tag_name = element.tag_name
                        class_name = element.get_attribute("class") or ""
                        placeholder = element.get_attribute("placeholder") or ""
                        print(f"  Iframe element {j+1}: {tag_name} (class: {class_name[:30]}, placeholder: {placeholder[:30]})")
                    except:
                        pass
                
                # Switch back to main content
                driver.switch_to.default_content()
                
            except Exception as e:
                print(f"Error with iframe {i+1}: {e}")
                driver.switch_to.default_content()
        
        # Try to interact with the widget
        print("🎯 Attempting to interact with widget...")
        
        # Try clicking on the widget first
        try:
            print("Clicking on widget element...")
            driver.execute_script("arguments[0].click();", widget_element)
            time.sleep(5)
            print("Widget clicked")
        except Exception as e:
            print(f"Failed to click widget: {e}")
        
        # Wait more time after clicking
        print("⏳ Waiting 10 seconds after clicking...")
        time.sleep(10)
        
        # Look for input field again after clicking
        print("🔍 Looking for input field after clicking...")
        input_field = None
        
        # Try to find input field
        try:
            input_field = driver.find_element(By.CSS_SELECTOR, "input, textarea")
            print("Found input field")
        except:
            print("No input field found")
        
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
                
                return True
                
            except Exception as e:
                print(f"❌ Failed to send message: {e}")
                return False
        else:
            print("❌ No input field found for conversation")
            
            # Take screenshot for debugging
            screenshot_path = "/tmp/visible_widget_test.png"
            driver.save_screenshot(screenshot_path)
            print(f"📸 Screenshot saved to: {screenshot_path}")
            
            return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_visible_widget()
    if success:
        print("\n🎉 Visible widget test SUCCESSFUL!")
    else:
        print("\n❌ Visible widget test FAILED!") 