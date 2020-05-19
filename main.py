from selenium import webdriver
from selenium.webdriver.chrome.options import Options 
import schedule
import time
import requests

class Wallmart_Crawler:
  def __init__(self):
    # main loop
    try:
      with open('zip_codes.txt') as file:
        self.zip_codes = [ x.replace('\n','') for x in file.readlines()]
      with open('links.txt') as file:
        self.links = [ link.replace('\n','') for link in file.readlines()]
    except:
      print("Couldnt read zip_codes.txt or links.txt files properly, please check.")
    chrome_options = Options()  
    #chrome_options.add_argument("--headless") 
    #chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    chrome_options.add_argument("--window-size=1920,1080")
    #chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--proxy-server='direct://'")
    chrome_options.add_argument("--proxy-bypass-list=*")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    #chrome_options.add_argument('--disable-dev-shm-usage')
    #chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--ignore-certificate-errors')
    self.browser = webdriver.Chrome(chrome_options=chrome_options)
        
  def change_zip(self,zip_code,link):
    fetch ="""
        console.log(arguments)
        let get_data = async ()=>{
        let x = await fetch("https://www.walmart.com/account/api/location", {
      "headers": {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
      },
      "body": "{\\"postalCode\\":\\""+arguments[0]+"\\",\\"storeMeta\\":false,\\"plus\\":false,\\"clientName\\":\\"Web-Header-LocationMenu\\",\\"persistLocation\\":true}",
      "method": "PUT",
      "mode": "cors",
      "credentials": "include"
    });
        return x.json()
        }
        get_data().then(dt=>{arguments[2](dt)})
    """
    dt = self.browser.execute_async_script(fetch,str(zip_code),'function(dt){return dt}')
    self.browser.get('https://www.walmart.com/')
    self.browser.get(link)
    return dt
  
  def change_zip_alt(self,zip_code):
    self.browser.find_element_by_css_selector('button[data-tl-id=header-Header-sparkButton]').click()
    time.sleep(1)
    self.browser.find_element_by_css_selector('button[data-tl-id=header-GlobalHeaderSparkMenu-locationButton]').click()
    time.sleep(1)
    self.browser.execute_script('document.querySelector("input#zip-code-input").value="'+str(zip_code)+'"')
    value = self.browser.execute_script('return document.querySelector("input#zip-code-input").value')
    print(value)
    time.sleep(1)
    self.browser.find_element_by_css_selector('button#zipcode-form-submit-button').click()
    time.sleep(6)
  
  def check_availability(self):
    els = self.browser.find_elements_by_css_selector('div.prod-fulfillment')
    if els:
      for el in els:
        print(el.text.lower())
        if 'pickup' in el.text.lower():
          if 'not available' in el.text.lower():
            return None
          else:
            return el.text
    else:
      return None
  
  def telegram_bot_sendtext(self,bot_message):
    bot_token = 'XXXXXXXXXXXXXXXXXXXXXXXXXXX'
    bot_chatID = 'XXXXXXXXXX'
    payload = {'text':bot_message,'chat_id':bot_chatID}
    response = requests.post('https://api.telegram.org/bot' + bot_token + '/sendMessage',data=payload)
    
    return response.json()
  
  def get_message(self,zip_code,store_info):
    product_name = self.browser.find_element_by_css_selector('h1.prod-ProductTitle').text
    price = self.browser.find_element_by_css_selector('span[itemprop=price]').get_attribute('content')
    return 'Item available for pickup WITH THE ZIP CODE='+str(zip_code)+' on: '+self.browser.current_url+'.\n Product name: '+product_name+',\n Price: '+str(price)+',\n Store Info: '+str(store_info)
  
  def run(self):
    for link in self.links:
      for zip_code in self.zip_codes:
        try:
          print('Wandering link',link)
          self.browser.get(link)
          print('Page loaded')
          time.sleep(2)
          self.change_zip_alt(zip_code)
          print('Changed zip successfully')
          time.sleep(2)
          available = self.check_availability()
          if available:
            print('Item available')
            msg = self.get_message(zip_code,available.split('\n')[-1])
            print('Prepared message',msg)
            self.telegram_bot_sendtext(msg)
            print('Message sent.')
        except Exception as e:
          print(e)
          print('Something went wrong while wandering links, passing')
    self.browser.quit()
  
  def kill(self):
    self.browser.quit()


if __name__ == "__main__":
  #def run():
  crawler=Wallmart_Crawler()
  crawler.run()
  
  # schedule the run every one minutes
  #schedule.every(1).minutes.do(run)

  #while True:
    #schedule.run_pending()
    #time.sleep(1)