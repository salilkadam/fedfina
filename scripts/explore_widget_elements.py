#!/usr/bin/env python3
"""
Explore ElevenLabs Widget Elements
Find text chat interfaces and interactive elements
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def explore_widget_elements():
    print("🔍 Exploring ElevenLabs Widget Elements")
    print("=" * 50)
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Load the page
        print("🌐 Loading page...")
        driver.get("http://localhost:3000?emailId=salil.kadam@vectrax.ai&accountId=Acc1234")
        time.sleep(5)
        print(f"📄 Page title: {driver.title}")
        
        # Wait for widget
        try:
            widget_element = driver.find_element(By.TAG_NAME, "elevenlabs-convai")
            print("✅ Widget element found")
            
            agent_id = widget_element.get_attribute("agent-id")
            print(f"🤖 Agent ID: {agent_id}")
            
        except:
            print("❌ Widget element not found")
            return
        
        # Wait longer for widget to fully load
        print("⏳ Waiting for widget to fully load...")
        time.sleep(15)
        
        # Get all elements on the page
        print("\n🔍 ALL ELEMENTS ON PAGE:")
        all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
        print(f"Total elements: {len(all_elements)}")
        
        # Categorize elements by type
        element_types = {}
        for element in all_elements:
            try:
                tag_name = element.tag_name.lower()
                if tag_name not in element_types:
                    element_types[tag_name] = []
                element_types[tag_name].append(element)
            except:
                continue
        
        # Print element counts by type
        print("\n📊 ELEMENT COUNTS BY TYPE:")
        for tag_name, elements in sorted(element_types.items()):
            print(f"  {tag_name}: {len(elements)}")
        
        # Look for specific interactive elements
        print("\n🎯 INTERACTIVE ELEMENTS:")
        
        # Input fields
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Input fields: {len(inputs)}")
        for i, input_elem in enumerate(inputs[:5]):
            try:
                input_type = input_elem.get_attribute("type") or "text"
                placeholder = input_elem.get_attribute("placeholder") or ""
                class_name = input_elem.get_attribute("class") or ""
                print(f"  Input {i+1}: type={input_type}, placeholder='{placeholder[:30]}', class='{class_name[:30]}'")
            except:
                pass
        
        # Textareas
        textareas = driver.find_elements(By.TAG_NAME, "textarea")
        print(f"Textareas: {len(textareas)}")
        for i, textarea in enumerate(textareas[:5]):
            try:
                placeholder = textarea.get_attribute("placeholder") or ""
                class_name = textarea.get_attribute("class") or ""
                print(f"  Textarea {i+1}: placeholder='{placeholder[:30]}', class='{class_name[:30]}'")
            except:
                pass
        
        # Buttons
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Buttons: {len(buttons)}")
        for i, button in enumerate(buttons[:10]):
            try:
                text = button.text or ""
                class_name = button.get_attribute("class") or ""
                onclick = button.get_attribute("onclick") or ""
                print(f"  Button {i+1}: text='{text[:30]}', class='{class_name[:30]}', onclick='{onclick[:30]}'")
            except:
                pass
        
        # Look for elements with specific classes
        print("\n🎨 ELEMENTS WITH SPECIFIC CLASSES:")
        
        class_patterns = [
            "chat", "message", "conversation", "input", "send", "text", "typing",
            "voice", "audio", "mic", "record", "play", "stop", "start"
        ]
        
        for pattern in class_patterns:
            elements = driver.find_elements(By.CSS_SELECTOR, f"[class*='{pattern}']")
            if elements:
                print(f"  Elements with '{pattern}' in class: {len(elements)}")
                for i, elem in enumerate(elements[:3]):
                    try:
                        tag_name = elem.tag_name
                        class_name = elem.get_attribute("class") or ""
                        text = elem.text or ""
                        print(f"    {i+1}. {tag_name}: class='{class_name[:50]}', text='{text[:30]}'")
                    except:
                        pass
        
        # Look for contenteditable elements
        print("\n✏️ CONTENTEDITABLE ELEMENTS:")
        contenteditable = driver.find_elements(By.CSS_SELECTOR, "[contenteditable='true']")
        print(f"Contenteditable elements: {len(contenteditable)}")
        for i, elem in enumerate(contenteditable):
            try:
                tag_name = elem.tag_name
                class_name = elem.get_attribute("class") or ""
                text = elem.text or ""
                print(f"  {i+1}. {tag_name}: class='{class_name[:50]}', text='{text[:30]}'")
            except:
                pass
        
        # Look for role attributes
        print("\n🎭 ELEMENTS WITH ROLE ATTRIBUTES:")
        roles = ["button", "textbox", "textbox", "dialog", "form", "input"]
        for role in roles:
            elements = driver.find_elements(By.CSS_SELECTOR, f"[role='{role}']")
            if elements:
                print(f"  Elements with role='{role}': {len(elements)}")
                for i, elem in enumerate(elements[:3]):
                    try:
                        tag_name = elem.tag_name
                        class_name = elem.get_attribute("class") or ""
                        text = elem.text or ""
                        print(f"    {i+1}. {tag_name}: class='{class_name[:50]}', text='{text[:30]}'")
                    except:
                        pass
        
        # Look for iframes (widget might be in iframe)
        print("\n🖼️ IFRAMES:")
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        print(f"Iframes: {len(iframes)}")
        for i, iframe in enumerate(iframes):
            try:
                src = iframe.get_attribute("src") or ""
                print(f"  Iframe {i+1}: src='{src[:50]}'")
                
                # Try to switch to iframe and explore
                try:
                    driver.switch_to.frame(iframe)
                    iframe_elements = driver.find_elements(By.CSS_SELECTOR, "*")
                    print(f"    Elements in iframe: {len(iframe_elements)}")
                    
                    # Look for input fields in iframe
                    iframe_inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea, button")
                    print(f"    Interactive elements in iframe: {len(iframe_inputs)}")
                    
                    for j, elem in enumerate(iframe_inputs[:5]):
                        try:
                            tag_name = elem.tag_name
                            class_name = elem.get_attribute("class") or ""
                            placeholder = elem.get_attribute("placeholder") or ""
                            print(f"      {j+1}. {tag_name}: class='{class_name[:30]}', placeholder='{placeholder[:20]}'")
                        except:
                            pass
                    
                    driver.switch_to.default_content()
                except Exception as e:
                    print(f"    Error exploring iframe: {e}")
                    driver.switch_to.default_content()
                    
            except:
                pass
        
        # Take screenshot for visual inspection
        screenshot_path = "/tmp/widget_exploration.png"
        driver.save_screenshot(screenshot_path)
        print(f"\n📸 Screenshot saved to: {screenshot_path}")
        
        # Get page source for manual inspection
        page_source = driver.page_source
        print(f"\n📄 Page source length: {len(page_source)} characters")
        
        # Look for specific patterns in page source
        patterns = ["chat", "message", "input", "send", "text", "voice", "audio"]
        for pattern in patterns:
            count = page_source.lower().count(pattern)
            if count > 0:
                print(f"  '{pattern}' appears {count} times in page source")
        
    except Exception as e:
        print(f"❌ Exploration failed: {e}")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    explore_widget_elements() 