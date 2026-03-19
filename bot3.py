import pyautogui
import cv2
import numpy as np
import pytesseract
import time
import random
import os
import re

# ============================================
# CONFIGURATION
# ============================================
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
MESSAGE_BUTTON_TEMPLATE = 'message_button.png'

# ============================================
# PART 1: GOTO PAGE (Navigate to Profile)
# ============================================

def get_friends():
    """Read all friends from file"""
    filename = "friends.txt"
    
    if not os.path.exists(filename):
        print("❌ friends.txt not found")
        return []
    
    with open(filename, 'r') as f:
        friends = [line.strip() for line in f.read().splitlines() if line.strip()]
    
    return friends

def construct_url(username):
    """Build TikTok URL from username"""
    clean_name = username.lstrip('@')
    return f"https://www.tiktok.com/@{clean_name}"

def navigate_to_url(url):
    """Type URL in browser address bar and navigate"""
    print(f"  Navigating to: {url}")
    
    # Click address bar
    pyautogui.keyDown('ctrl')
    pyautogui.keyDown('l')
    pyautogui.keyUp('l')
    pyautogui.keyUp('ctrl')
    
    time.sleep(0.2)
    
    # Type URL
    pyautogui.typewrite(url, interval=0.01)
    time.sleep(0.2)
    
    # Press Enter
    pyautogui.keyDown('return')
    pyautogui.keyUp('return')
    
    print("  🚀 Page loading...")

# ============================================
# PART 2: TIKTOK CHAT (Click Message Button)
# ============================================

class TikTokMessageButton:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.template_path = MESSAGE_BUTTON_TEMPLATE

    def capture_screenshot(self):
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def find_message_button(self):
        """Find Message button by image matching"""
        print("🔍 Looking for 'Message' button...")
        
        if not os.path.exists(self.template_path):
            print(f"⚠️  Template not found, using fallback")
            return self.fallback_click()
        
        template = cv2.imread(self.template_path)
        if template is None:
            return self.fallback_click()
        
        template_h, template_w = template.shape[:2]
        screen = self.capture_screenshot()
        screen_h, screen_w = screen.shape[:2]
        
        search_region = screen[:int(screen_h*0.5), :]
        result = cv2.matchTemplate(search_region, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        print(f"  Match confidence: {max_val:.2f}")
        
        if max_val > 0.7:
            x, y = max_loc
            full_x = x + template_w // 2
            full_y = y + template_h // 2
            print(f"✅ Found button at ({full_x}, {full_y})")
            return (full_x, full_y)
        
        print("⚠️  Low confidence, using fallback")
        return self.fallback_click()

    def fallback_click(self):
        x = int(self.screen_width * 0.78)
        y = int(self.screen_height * 0.18)
        print(f"  Fallback: ({x}, {y})")
        return (x, y)

    def click_message(self):
        print("\n🚀 Clicking 'Message' button")
        
        x, y = self.find_message_button()
        pyautogui.moveTo(x, y, duration=0.5)
        time.sleep(0.3)
        pyautogui.click()
        
        print("✅ Clicked!")
        return True

# ============================================
# PART 3: TIKTOK REPLY (Send Message)
# ============================================

class TikTokAutoReply:
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()

    def capture_screenshot(self):
        screenshot = pyautogui.screenshot()
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def find_message_box_by_text(self):
        """Find 'Send a message...' text and click there"""
        print("🔍 Looking for message input...")
        
        screen = self.capture_screenshot()
        height, width = screen.shape[:2]
        
        bottom_region = screen[int(height*0.75):, :]
        data = pytesseract.image_to_data(bottom_region, output_type=pytesseract.Output.DICT)
        
        n_boxes = len(data['text'])
        target_box = None
        
        for i in range(n_boxes):
            text = data['text'][i].strip().lower()
            conf = int(data['conf'][i])
            
            if conf > 60 and any(keyword in text for keyword in ['send', 'message']):
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                full_y = int(height*0.75) + y
                
                print(f"  Found '{data['text'][i]}' at ({x}, {full_y})")
                
                if x < width * 0.7:
                    target_box = (x, full_y, w, h)
                    if 'send' in text and 'message' in text:
                        break
        
        if target_box:
            x, y, w, h = target_box
            click_x = x + w//2
            click_y = y + h//2 - 3  # Your adjustment
            print(f"✅ Clicking at ({click_x}, {click_y})")
            return (click_x, click_y)
        
        # Fallback
        fallback_x = int(self.screen_width * 0.33)
        fallback_y = int(self.screen_height * 0.88)
        return (fallback_x, fallback_y)

    def human_type(self, text):
        """Type with human variation"""
        for char in text:
            if random.random() < 0.03 and char != ' ':
                wrong = random.choice('abcdefghijklmnopqrstuvwxyz')
                pyautogui.typewrite(wrong, interval=random.uniform(0.05, 0.1))
                time.sleep(random.uniform(0.1, 0.3))
                pyautogui.keyDown('backspace')
                pyautogui.keyUp('backspace')
                time.sleep(random.uniform(0.05, 0.15))
            
            if char in 'asdfjkl; ':
                interval = random.gauss(0.06, 0.02)
            else:
                interval = random.gauss(0.12, 0.04)
            
            pyautogui.typewrite(char, interval=max(0.01, interval))

    def send_message(self, message):
        """Send message in DM"""
        print(f"\n💬 Sending: '{message}'")
        
        time.sleep(0.5)
        
        x, y = self.find_message_box_by_text()
        pyautogui.click(x, y)
        time.sleep(0.3)
        
        print("🤔 Thinking...")
        time.sleep(random.uniform(1.5, 3))
        
        print("⌨️  Typing...")
        self.human_type(message)
        
        time.sleep(random.uniform(0.8, 2))
        pyautogui.keyDown('return')
        pyautogui.keyUp('return')
        
        print("✅ Sent!")
        return True

# ============================================
# MAIN WORKFLOW
# ============================================

def process_friend(friend, message):
    """Full pipeline for one friend: goto -> click message -> reply"""
    print(f"\n{'='*50}")
    print(f"🎯 Processing: {friend}")
    print(f"{'='*50}")
    
    # Step 1: Navigate to profile
    url = construct_url(friend)
    navigate_to_url(url)
    time.sleep(4)  # Wait for profile load
    
    # Step 2: Click Message button
    button_clicker = TikTokMessageButton()
    button_clicker.click_message()
    time.sleep(3)  # Wait for DM to open
    
    # Step 3: Send message
    dm_bot = TikTokAutoReply()
    dm_bot.send_message(message)
    time.sleep(2)  # Brief pause after send

def main():
    # Settings
    message = "yeah that was hilarious lol"  # Your message here
    initial_delay = 5
    
    # Get friends
    friends = get_friends()
    
    if not friends:
        print("💨 No friends found in friends.txt")
        return
    
    print("🤖 TikTok Auto Messenger")
    print("=" * 50)
    print(f"Friends: {len(friends)}")
    print(f"Message: '{message}'")
    print("=" * 50)
    print(f"Starting in {initial_delay}s...")
    print("👉 Switch to browser now!")
    
    # Countdown
    for i in range(initial_delay, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    # Process each friend
    for friend in friends:
        process_friend(friend, message)
        time.sleep(3)  # Pause between friends
    
    print(f"\n{'='*50}")
    print(f"✨ Done! Messaged {len(friends)} friends")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()