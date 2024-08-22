# Dexscreener Automation Script

## Overview

The `dexscreener_auto.py` script is an automation script that interacts with the Dexscreener website to perform specific actions. It uses the Playwright library to launch a browser instance, navigate to the website, locate elements on the page, and interact with them. The script also uses PyAutoGUI to simulate mouse clicks on C
cloudfare's reCAPTCHA checkbox and fetches the backend data from the website. The script is designed to intercept network requests made by the website and extract the required data for further processing. and export the data to a Google Sheet.

## Purpose

The purpose of this script is to automate the process of fetching data from the Dexscreener website and exporting it to a Google Sheet. By automating this process, users can save time and effort by avoiding manual data entry and extraction. The script can be customized to fetch specific data dev tools and export it to a Google Sheet for further analysis and processing.

## Requirements

- Python 3.7+
- Playwright
- PyAutoGUI
- asyncio

## Installation

1. **Clone the repository:**
   ```sh
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install the required packages:**
   ```sh
   pip install playwright pyautogui
   ```

3. **Install Playwright browsers:**
   ```sh
   playwright install
   ```

## Usage

1. **Setup Google Sheets:**
   Before running the script, ensure that the `setup_GoogleSheet` method is properly configured to set up your Google Sheets integration.

2. **Run the script:**
   ```sh
   python dexscreener_auto.py
   ```

## How It Works

1. **Initialization:**
   The script initializes an instance of the `Dexscreener` class and sets up Google Sheets integration.

2. **Main Function:**
   The `main` function is the entry point of the script. It uses the [`asyncio` library to run the `run` method asynchronously.

3. **Run Method:**
   The `run` method performs the following steps:
   - Launches a browser instance using Playwright.
   - Navigates to the Dexscreener website.
   - Locates specific elements on the page and performs actions such as clicking on them using PyAutoGUI.
   - Handles exceptions and saves the browser's storage state to a JSON file.
   - Pauses the page for debugging purposes.
   - Closes the browser.

4. **Element Interaction:**
   The script calculates the position of elements on the page and uses PyAutoGUI to click on them. It handles exceptions and logs errors if any occur.

## Code Explanation

Here is a brief explanation of the key parts of the code:

```python
element_width = element_position["width"] * 10 / 100
center_y = element_position["y"] + element_position["height"] / 2
pyautogui.click(element_position["x"] + element_width, center_y)
time.sleep(5)
```
- **element_width:** Calculates 10% of the element's width.
- **center_y:** Calculates the vertical center of the element.
- **pyautogui.click:** Clicks on the calculated position of the element.
- **time.sleep(5):** Waits for 5 seconds.

```python
except Exception as e:
    print(f"Error: {e}")
    await page.context.storage_state(path=os.path.join(self.current_path, "CREDENTIALS", "storage_state.json"))
    break
```
- **Exception Handling:** Catches any exceptions, logs the error, saves the browser's storage state, and breaks the loop.

```python
await page.pause()
await browser.close()
```
- **page.pause():** Pauses the page for debugging, and allows you to intercepting network requests, inspect elements, etc.
- **browser.close():** Closes the browser instance.

## Conclusion

The `dexscreener_auto.py` script is a powerful automation tool that can interact with the Dexscreener website, extract data, and export it to a Google Sheet. By automating this process, users can save time and effort, and perform data analysis more efficiently. The script can be customized to fetch specific data and perform additional actions based on user requirements. It demonstrates the capabilities of Playwright and PyAutoGUI libraries for web automation and interaction.