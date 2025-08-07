#!/usr/bin/env python3
"""
Test ElevenLabs Widget in Visible Browser
See what actually happens when clicking the widget
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_visible_widget():
    print("👁️ Testing ElevenLabs Widget in Visible Browser")
    print("=" * 50)
    
    # Setup Chrome driver in visible mode
    chrome_options = Options()
    # Remove headless mode to see what's happening
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_argument("--allow-running-insecure-content")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-visible-test")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Load the page
        print("🌐 Loading page...")
        driver.get("http://localhost:3000?emailId=salil.kadam@vectrax.ai&accountId=Acc1234")
        
        # Wait for page to load
        time.sleep(5)
        print(f"📄 Page title: {driver.title}")
        
        # Wait for widget
        try:
            widget_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "elevenlabs-convai"))
            )
            print("✅ Widget element found")
            
            agent_id = widget_element.get_attribute("agent-id")
            print(f"🤖 Agent ID: {agent_id}")
            
        except:
            print("❌ Widget element not found")
            return False
        
        # Wait longer for widget to fully load
        print("⏳ Waiting for widget to fully load...")
        time.sleep(10)
        
        # Check elements before clicking
        print("\n📊 Elements before clicking:")
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        print(f"Total elements: {len(all_elements)}")
        
        # Look for the widget element
        widget_element = driver.find_element(By.TAG_NAME, "elevenlabs-convai")
        print(f"Widget element: {widget_element}")
        
        # Check if widget is clickable
        is_displayed = widget_element.is_displayed()
        is_enabled = widget_element.is_enabled()
        print(f"Widget displayed: {is_displayed}, enabled: {is_enabled}")
        
        # Get widget dimensions and location
        size = widget_element.size
        location = widget_element.location
        print(f"Widget size: {size}, location: {location}")
        
        # Take screenshot before clicking
        screenshot_path = "/tmp/before_click.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot before clicking: {screenshot_path}")
        
        # Wait for user to see the widget
        print("\n👀 Widget should be visible now. Waiting 10 seconds for you to see it...")
        time.sleep(10)
        
        # Try to click the widget
        print("🖱️ Attempting to click widget...")
        try:
            # Use JavaScript click
            driver.execute_script("arguments[0].click();", widget_element)
            print("✅ JavaScript click successful")
        except Exception as e:
            print(f"❌ JavaScript click failed: {e}")
            return False
        
        # Wait for conversation interface to appear
        print("⏳ Waiting for conversation interface to appear...")
        time.sleep(10)
        
        # Take screenshot after clicking
        screenshot_path = "/tmp/after_click.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 Screenshot after clicking: {screenshot_path}")
        
        # Check for conversation elements
        print("\n🔍 Checking for conversation elements...")
        selectors = [
            "input", "textarea", "button", 
            "[class*='chat']", "[class*='message']", "[class*='conversation']",
            "[class*='input']", "[class*='send']", "[class*='text']",
            "[role='textbox']", "[contenteditable='true']"
        ]
        
        conversation_elements = []
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  Found {len(elements)} elements with selector '{selector}'")
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
        
        print(f"📊 Total unique conversation elements: {len(unique_elements)}")
        
        # Log details of found elements
        for i, element in enumerate(unique_elements[:10]):
            try:
                tag_name = element.tag_name
                class_name = element.get_attribute("class") or ""
                placeholder = element.get_attribute("placeholder") or ""
                text = element.text or ""
                print(f"  Element {i+1}: {tag_name} (class: {class_name[:30]}, placeholder: {placeholder[:20]}, text: {text[:20]})")
            except:
                pass
        
        # Check if we found input fields
        input_fields = [elem for elem in unique_elements if elem.tag_name.lower() in ['input', 'textarea']]
        print(f"🎯 Input fields found: {len(input_fields)}")
        
        if len(input_fields) > 0:
            print("✅ Conversation interface appeared!")
            return True
        else:
            print("❌ Conversation interface did not appear")
            return False
        
    except Exception as e:
        print(f"❌ Visible widget test failed: {e}")
        return False
        
    finally:
        # Wait a bit before closing so user can see the result
        print("\n⏳ Waiting 5 seconds before closing browser...")
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    success = test_visible_widget()
    if success:
        print("\n🎉 VISIBLE WIDGET TEST PASSED!")
        exit(0)
    else:
        print("\n❌ VISIBLE WIDGET TEST FAILED!")
        exit(1) 