
from playwright.async_api import Playwright, async_playwright, Request, Route
from playwright_stealth import stealth
import pandas as pd, os, sqlite3, pyautogui, asyncio, time, pygsheets, datetime

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
        self.gc = pygsheets.authorize(service_account_file=os.path.join(self.current_path,"pygsheets","red-operative-433318-p6-fc23505f7ac9.json"))
        self.sheet_key="1A9aHqXMdh6_CEbJR2IXiE1nzkBJR3mEz9F7EnmsqDs0"
        self.file_path = os.path.join(self.current_path,self.directory,self.sheet_key)
        self.current_url = "https://dexscreener.com/solana/bamgxrark2xrw7wmv6lmj3742d29j2sz8mpwx3ztephd"
        os.makedirs(self.file_path, exist_ok=True)
    
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
        while True:
            try:
                await page.get_by_role("heading", name="Verify you are human by").click()
                element_position = await page.locator('div[class="spacer"] >div').bounding_box()
                element_width = element_position["width"]*10/100
                center_y = element_position["y"] +element_position["height"]/2
                pyautogui.click(element_position["x"]+element_width,center_y)
                time.sleep(5)
            except Exception as e:
                print(f"Error: {e}")
                await page.context.storage_state(path=os.path.join(self.current_path, "CREDENTIALS", "storage_state.json"))
                break
                
        await page.pause()
        await browser.close()
    async def main(self) -> None:
        
        async with async_playwright() as playwright:
            await self.run(playwright)

if __name__ == "__main__":
    dexscreener = Dexscreener()
    dexscreener.setup_GoogleSheet()
    asyncio.run(dexscreener.main())


