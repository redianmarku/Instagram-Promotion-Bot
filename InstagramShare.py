from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.keys import Keys
import time

options = UiAutomator2Options().load_capabilities({
    "platformName": "Android",
    "platformVersion": "13",  #put your platform version here
    "deviceName": "emulator-5554", #put your device name here
    "appPackage": "com.instagram.android",
    "appActivity": "com.instagram.mainactivity.LauncherActivity",
    "autoGrantPermissions": True,
    "noReset": True,
    "fullReset": False,
    "disableIdLocatorAutocompletion": True,
})

# Prompt the user for the username to promote
username_to_promote = input("Enter the username to promote: ")

# Read usernames to deliver from a text file
with open("usernames.txt", "r") as file:
    usernames_to_deliver = file.read().splitlines()

# Read the message to be sent from a text file
with open("message.txt", "r") as file:
    message_to_send = file.read()

def click_element(driver, element_id, by_type=AppiumBy.ID):
    element = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((by_type, element_id))
    )
    element.click()

def type_element(driver, element_id, text, type=AppiumBy.ID):
    element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((type, element_id))
    )
    element.click()
    for char in text:
        if char == " ":
            driver.press_keycode(62)
        elif char == "_":
            driver.set_clipboard_text("_")
            driver.press_keycode(279)
        elif char == ".":
            driver.press_keycode(56)
        else:
            key_code = int(ord(char)) - 68 
            driver.press_keycode(key_code)

def write_element(driver, element_id, text, type=AppiumBy.ID):
    element = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((type, element_id))
    )
    element.click()
    element.send_keys(text)

def remove_username_from_file(username):
    # Read the existing usernames
    with open("usernames.txt", "r") as file:
        usernames = file.read().splitlines()

    # Remove the processed username
    usernames.remove(username)

    # Write the updated usernames back to the file
    with open("usernames.txt", "w") as file:
        file.write("\n".join(usernames))

driver = webdriver.Remote("http://127.0.0.1:4723", options=options)

click_element(driver, "com.instagram.android:id/search_tab")
type_element(driver, "com.instagram.android:id/action_bar_search_edit_text", username_to_promote)
click_element(driver, f'//android.widget.TextView[@resource-id="com.instagram.android:id/row_search_user_username" and @text="{username_to_promote}"]', AppiumBy.XPATH)

for user in usernames_to_deliver:
    try:
        click_element(driver, 'com.instagram.android:id/action_bar_overflow_icon')
        click_element(driver, '//android.widget.Button[@resource-id="com.instagram.android:id/action_sheet_row_text_view" and @text="Share this profile"]', AppiumBy.XPATH)
        type_element(driver, 'com.instagram.android:id/search_row', user)
        click_element(driver, '(//android.widget.CompoundButton[@resource-id="com.instagram.android:id/recipient_toggle"])[1]', AppiumBy.XPATH)
        write_element(driver, 'com.instagram.android:id/direct_private_share_message_box', message_to_send)
        time.sleep(1)
        click_element(driver, 'com.instagram.android:id/direct_send_button_multi_select')
        time.sleep(3)
    except TimeoutException:
        # Handle the case where the element is not found
        driver.press_keycode(4)  # Press "Back" once
        driver.press_keycode(4)
        print(f"Skipping user {user} as the recipient doesnt exist.")

    finally:
        # Remove the processed username from the file
        remove_username_from_file(user)

driver.quit()
