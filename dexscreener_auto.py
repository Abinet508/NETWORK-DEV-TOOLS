
from playwright.async_api import Playwright, async_playwright, Request, Route
from playwright_stealth import stealth
import pandas as pd, os, sqlite3, pyautogui, asyncio, time, pygsheets, datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import dotenv
dotenv.load_dotenv(os.path.join(os.path.dirname(os.path.realpath(__file__)),"CREDENTIALS",".env"))

pyautogui.FAILSAFE = True

class Dexscreener:
    """
    Dexscreener is a class used to scrape the data from the website and save it in the google sheet
    """
    def __init__(self) -> None:
        self.current_path = os.path.abspath(os.path.dirname(__file__))
        self.success = None
        self.phone_number = None
        self.email = None
        self.trace_path = os.path.join(self.current_path, "TRACE", "register_user_trace.zip")
        os.makedirs(os.path.dirname(self.trace_path), exist_ok=True)
        self.worksheet = pd.DataFrame()
        self.drop_duplicates = True
        self.directory = "DEXSCREENER"
        self.file_name = "dexscreener_worksheet.xlsx"
        self.url_key = "dexscreener"
        self.email= os.getenv("EMAIL")
        self.email_password= os.getenv("EMAIL_PASSWORD")
        self.gc = pygsheets.authorize(service_account_file=os.path.join(self.current_path,"pygsheets","red-operative-433318-p6-fc23505f7ac9.json"))
        self.sheet_key="1A9aHqXMdh6_CEbJR2IXiE1nzkBJR3mEz9F7EnmsqDs0"
        self.file_path = os.path.join(self.current_path,self.directory,self.sheet_key)
        self.current_url = "https://dexscreener.com/solana/bamgxrark2xrw7wmv6lmj3742d29j2sz8mpwx3ztephd"
        os.makedirs(self.file_path, exist_ok=True)
        self.not_verified = True
        self.after_verification = False
    def setup_GoogleSheet(self):
        """ setup_google_sheet is a function that setup google sheet
        """
    
        while True:
            try:
                print("Setting up Google sheet")
                self.sh = self.gc.open_by_key(self.sheet_key)
                print("Google sheet opened successfully")
                self.wks = self.sh.sheet1
                self.all_rows=self.wks.rows
                self.columunName=self.wks.get_row(1)
                sheet_title = self.sh.title
                try:
                    sheet_title = sheet_title.split("-")[0]
                except Exception as e:
                    pass
                finally:
                    get_date = datetime.datetime.now().strftime("%Y/%m/%d %I:%M %p")
                    sheet_title = sheet_title + "-" + get_date
                    self.sh.title = sheet_title
                    print("Sheet title is: ", sheet_title, "Google sheet setup successfully")
                    print()
                    return True
            except Exception as e:
                print("Error in setup_GoogleSheet",e.__str__())
                time.sleep(5)
                continue
    
    async def send_email(self, file_path: str) -> None:
        """
        send_email is a function that send email
        """
        try:
            
            if  os.path.exists(file_path):
                msg = MIMEMultipart()
                msg['From'] = self.email
                msg['To'] = self.email
                msg['Subject'] = "Dexscreener"
                body = "Dexscreener"
                msg.attach(MIMEText(body, 'plain'))
                attachment = open(file_path, "rb")
                p = MIMEBase('application', 'octet-stream')
                p.set_payload((attachment).read())
                encoders.encode_base64(p)
                p.add_header('Content-Disposition', "attachment; filename= %s" % file_path)
                msg.attach(p)
                
            else:
                msg = MIMEMultipart()
                msg['From'] = self.email
                msg['To'] = self.email
                msg['Subject'] = "Dexscreener"
                body = "Dexscreener"
                msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.email, self.email_password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print("Error in send_email",e.__str__())
    
    async def intercept_network_request(self, route: Route, request: Request) -> None:
        """
        This function is used to intercept the network request and save the data in the worksheet

        Args:
            route (Route): The route object to intercept the network request
            request (Request): The request object made by the browser
        """
        await route.continue_()
       
        #try:
        print(request.resource_type)
        if self.url_key in request.url and (request.resource_type == "xhr" or request.resource_type == "fetch" or request.resource_type == "websocket" or request.resource_type == "document"):
            if self.worksheet.empty:
                self.worksheet = pd.DataFrame({"URL": [request.url], "Method": [request.method], "ResourceType": [request.resource_type], "PostData": [request.post_data]})
            else:
                self.worksheet = pd.concat([self.worksheet, pd.DataFrame({"URL": [request.url], "Method": [request.method], "ResourceType": [request.resource_type], "PostData": [request.post_data]})], ignore_index=True)
            if self.drop_duplicates:
                self.worksheet.drop_duplicates(inplace=True)
            if not os.path.exists(self.file_path):
                os.makedirs(self.file_path, exist_ok=True)
            self.wks.set_dataframe(self.worksheet, (1, 1))
       
            if "https://dexscreener.com/cdn-cgi/challenge-platform" in request.url and not self.after_verification and self.not_verified:
                self.not_verified = True
    async def run(self,playwright: Playwright) -> None:
       
        """
        This function is used to run the playwright browser

        Args:
            playwright (Playwright): Playwright object
        """
        
        browser = await playwright.firefox.launch(headless=False,
        ignore_default_args=[ "--no-startup-window"],
        args=["--kiosk"],)
        if os.path.exists(os.path.join(self.current_path, "CREDENTIALS", "storage_state.json")):
            context = await browser.new_context(storage_state=os.path.join(self.current_path, "CREDENTIALS", "storage_state.json"),
        no_viewport=True)
        else:
            context = await browser.new_context(
        no_viewport=True)
        
        script = """
Element.prototype._attachShadow = Element.prototype.attachShadow;
Element.prototype.attachShadow = function () {
    return this._attachShadow({ mode: "open" });
};
"""
        page = await context.new_page()
        #await page.add_init_script(script=script)
        await stealth.stealth_async(page)
        await context.route("**/*", self.intercept_network_request)
       
        
        await page.goto(self.current_url,wait_until="load",timeout=3000000)
        current_url = page.url 
        while current_url != self.current_url:
            try:
                
                print("Waiting for the verification")
                await page.get_by_role("heading", name="Verify you are human by").click(timeout=10000)
                element_position = await page.locator('div[class="spacer"] >div').bounding_box()
                window_position = await page.locator('html').bounding_box()
                element_width = element_position["width"]
                element_height = element_position["height"]
                element_x = element_position["x"]
                element_y = element_position["y"]
                screen_postion = pyautogui.size()
                screen_postion_width = screen_postion[0]
                screen_postion_height = screen_postion[1]
                if screen_postion_width != window_position["width"]:
                    element_x_diff = (window_position["width"])/screen_postion_width
            
                else:
                    element_x_diff = 1
                if screen_postion_height != window_position["height"]:
                    element_y_diff = (window_position["height"])/screen_postion_height
                else:
                    element_y_diff = 1
                element_x = (element_x+32)/element_x_diff
                element_y = (element_y+32)/element_y_diff
                print(f"Element_x_diff: {element_x_diff}", f"Element_y_diff: {element_y_diff}")
                #calculate the element position on the screen size
                pyauto_position = pyautogui.position()
                pyautogui.click(element_x, element_y)
                #pyautogui.moveTo(element_x, element_y, duration=1)
                print(f"Point(window_position): {window_position}")
                print(f"PLAYWRIGHT ELEMENT POSTION: {element_position}")
                print(f"PYAUTOGUI-Screen-Size: {screen_postion}")
                print(f"Point ON ELEMENT(x={element_x}, y={element_y})")
                print("PYAUTOGUI POINT: ",pyauto_position)
                self.not_verified = False
                time.sleep(5)
                current_url = page.url
            except Exception as e:
                print(f"Error: {e}")
                os.makedirs(os.path.join(self.current_path, "CREDENTIALS"), exist_ok=True)
                await page.context.storage_state(path=os.path.join(self.current_path, "CREDENTIALS", "storage_state.json"))
                if self.after_verification or not self.not_verified:
                    break
        self.after_verification = True
        await page.screenshot(path=os.path.join(self.current_path, "screenshot.png"))
        await self.send_email(os.path.join(self.current_path, "screenshot.png"))
        await page.pause()
        await browser.close()
    async def main(self) -> None:
        
        async with async_playwright() as playwright:
            await self.run(playwright)

if __name__ == "__main__":
    dexscreener = Dexscreener()
    dexscreener.setup_GoogleSheet()
    asyncio.run(dexscreener.main())


# Point(x=423, y=360)
# SCREEN-Size(width=1920, height=1080)
# PLAYWRIGHT ELEMENT POSTION: {'x': 312, 'y': 256, 'width': 912, 'height': 67.39999389648438}
# PYAUTOGUI-MOUSE-Point ON ELEMENT(x=423, y=360)