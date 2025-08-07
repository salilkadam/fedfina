#!/usr/bin/env python3
"""
Debug script to check ElevenLabs widget visibility and take screenshot
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def debug_widget():
    print("🔍 Debugging ElevenLabs Widget")
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
        # Load the page
        test_url = "http://localhost:3000?emailId=salil.kadam@vectrax.ai&accountId=Acc1234"
        print(f"Loading: {test_url}")
        driver.get(test_url)
        
        # Wait for page to load
        time.sleep(5)
        
        # Check page title
        print(f"Page title: {driver.title}")
        
        # Check if widget element exists
        try:
            widget_element = driver.find_element(By.TAG_NAME, "elevenlabs-convai")
            print("✅ Widget element found")
            
            # Check widget attributes
            agent_id = widget_element.get_attribute("agent-id")
            email_id = widget_element.get_attribute("data-email-id")
            account_id = widget_element.get_attribute("data-account-id")
            
            print(f"Agent ID: {agent_id}")
            print(f"Email ID: {email_id}")
            print(f"Account ID: {account_id}")
            
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
        
        # Check for all elements on the page
        print("\n🔍 All elements on page:")
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        print(f"Total elements: {len(all_elements)}")
        
        # Look for specific elements
        buttons = driver.find_elements(By.TAG_NAME, "button")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        
        print(f"Buttons: {len(buttons)}")
        print(f"Inputs: {len(inputs)}")
        print(f"Textareas: {len(textareas)}")
        
        # Check for elements with conversation-related classes
        conversation_elements = driver.find_elements(By.CSS_SELECTOR, 
            "[class*='conversation'], [class*='chat'], [class*='input'], [class*='message']")
        print(f"Conversation-related elements: {len(conversation_elements)}")
        
        # Log details of conversation elements
        for i, element in enumerate(conversation_elements[:10]):
            try:
                tag_name = element.tag_name
                class_name = element.get_attribute("class") or ""
                element_id = element.get_attribute("id") or ""
                print(f"  Element {i+1}: {tag_name} (class: {class_name[:50]}, id: {element_id[:20]})")
            except:
                pass
        
        # Take screenshot
        screenshot_path = "/tmp/widget_debug.png"
        driver.save_screenshot(screenshot_path)
        print(f"\n📸 Screenshot saved to: {screenshot_path}")
        
        # Get page source
        page_source = driver.page_source
        print(f"\n📄 Page source length: {len(page_source)} characters")
        
        # Check for ElevenLabs script in page source
        if "elevenlabs" in page_source.lower():
            print("✅ ElevenLabs script found in page source")
        else:
            print("❌ ElevenLabs script not found in page source")
        
        # Check for widget element in page source
        if "elevenlabs-convai" in page_source:
            print("✅ elevenlabs-convai element found in page source")
        else:
            print("❌ elevenlabs-convai element not found in page source")
        
        # Wait a bit more to see if widget loads
        print("\n⏳ Waiting 30 seconds to see if widget loads...")
        time.sleep(30)
        
        # Check again
        try:
            widget_element = driver.find_element(By.TAG_NAME, "elevenlabs-convai")
            print("✅ Widget element still found after waiting")
            
            # Check for conversation elements again
            conversation_elements = driver.find_elements(By.CSS_SELECTOR, 
                "[class*='conversation'], [class*='chat'], [class*='input'], [class*='message']")
            print(f"Conversation elements after waiting: {len(conversation_elements)}")
            
        except NoSuchElementException:
            print("❌ Widget element not found after waiting")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_widget() 