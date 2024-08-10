import os
import threading
import wx
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import random
import re
from bs4 import BeautifulSoup

class Bot:
    def __init__(self):
        self.driver = None
        self.typing_event = threading.Event()
        self.wpm = 0
        self.error_rate = 0
        self.website = "https://monkeytype.com"

    def open_game_window(self):
        chrome_options = webdriver.ChromeOptions()
        chromedriver_path = ChromeDriverManager().install()
        
        service = ChromeService(executable_path=chromedriver_path)
        
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(self.website)

    def html(self):
        try:
            if "monkeytype" in self.website:
                result = self.driver.page_source.partition("""class="word active""")[2].partition("""class="keymap hidden""")[0]
                result = re.sub("""class="word""", '> <', result)
                x = re.findall(r"\>([a-zA-Z0-9,\. ])\<", result)
            elif "typeracer" in self.website:
                input_panel = self.driver.find_element(By.CLASS_NAME, "inputPanel")
                spans = input_panel.find_elements(By.TAG_NAME, "span")
                x = [span.text for span in spans if span.text.strip()]
                x.append(' ')
            else:
                return []
            
            return x
        except Exception as e:
            print("Error getting HTML:", e)
            return []

    def introduce_error(self, char):
        character_set = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789, .'
        if char == ' ':
            return char
        if random.random() < self.error_rate / 100:
            return random.choice([c for c in character_set if c != char])
        return char

    def type_text(self):
        while not self.typing_event.is_set():
            try:
                words = self.html()
                if "monkeytype" in self.website:
                    while not self.typing_event.is_set():
                        try:
                            words = self.html()
                            for word in words:
                                for char in word:
                                    if self.typing_event.is_set():
                                        return
                                    char = self.introduce_error(char)
                                    start_time = time.time()
                                    webdriver.ActionChains(self.driver).send_keys(char).perform()
                                    end_time = time.time()
                                    character_time = end_time - start_time
                                    time.sleep(max(0, ((60 / (self.wpm * 5)) - character_time)))
                        except Exception as e:
                            print("Error typing text:", e)
                            break

                elif "typeracer" in self.website:
                    input_box = self.driver.find_element(By.CSS_SELECTOR, "input.txtInput")
                    input_box.click()

                    table = self.driver.find_element(By.CSS_SELECTOR, "table.inputPanel")

                    inner_html = self.driver.execute_script("return arguments[0].innerHTML;", table)

                    soup = BeautifulSoup(inner_html, 'html.parser')

                    combined_text = ''

                    spans = soup.find_all('span')

                    for span in spans:
                        combined_text += span.get_text()

                    print(f"Combined text: '{combined_text}'")

                    for char in combined_text:
                        if self.typing_event.is_set():
                            return
                        char = self.introduce_error(char)
                        ActionChains(self.driver).send_keys(char).perform()
                        time.sleep(60 / (self.wpm * 5))

            except Exception as e:
                print("Error typing text:", e)
                break

    def start_typing(self):
        self.typing_event.clear()
        threading.Thread(target=self.type_text).start()

    def stop_typing(self):
        self.typing_event.set()

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(400, 500))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(26, 35, 43))

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.bot = Bot()

        open_game_btn = wx.Button(panel, label='Open Game', size=(150, 40))
        open_game_btn.SetBackgroundColour(wx.Colour(26, 35, 43))
        open_game_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        open_game_btn.Bind(wx.EVT_BUTTON, self.on_open_game)
        open_game_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(open_game_btn, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 20)

        self.website_choice = wx.Choice(panel, choices=["Monkeytype", "TypeRacer"], size=(150, -1))
        self.website_choice.SetSelection(0)
        vbox.Add(self.website_choice, 0, wx.EXPAND | wx.ALL, 5)

        wpm_label = wx.StaticText(panel, label="Words per Minute (WPM):")
        wpm_label.SetForegroundColour(wx.Colour(255, 255, 255))
        wpm_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(wpm_label, 0, wx.EXPAND | wx.ALL, 5)

        self.wpm_text = wx.TextCtrl(panel, size=(150, -1))
        self.wpm_text.SetBackgroundColour(wx.Colour(26, 35, 43))
        self.wpm_text.SetForegroundColour(wx.Colour(255, 255, 255))
        vbox.Add(self.wpm_text, 0, wx.EXPAND | wx.ALL, 5)

        error_label = wx.StaticText(panel, label="Human Error (%):")
        error_label.SetForegroundColour(wx.Colour(255, 255, 255))
        error_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(error_label, 0, wx.EXPAND | wx.ALL, 5)

        self.error_text = wx.TextCtrl(panel, size=(150, -1))
        self.error_text.SetBackgroundColour(wx.Colour(26, 35, 43))
        self.error_text.SetForegroundColour(wx.Colour(255, 255, 255))
        vbox.Add(self.error_text, 0, wx.EXPAND | wx.ALL, 5)

        start_btn = wx.Button(panel, label='Start Typing', size=(150, 40))
        start_btn.SetBackgroundColour(wx.Colour(26, 35, 43)) 
        start_btn.SetForegroundColour(wx.Colour(255, 255, 255)) 
        start_btn.Bind(wx.EVT_BUTTON, self.on_start_typing)
        start_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        vbox.Add(start_btn, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 20)

        stop_btn = wx.Button(panel, label='Stop Typing', size=(150, 40))
        stop_btn.SetBackgroundColour(wx.Colour(26, 35, 43)) 
        stop_btn.SetForegroundColour(wx.Colour(255, 255, 255))  
        stop_btn.Bind(wx.EVT_BUTTON, self.on_stop_typing)
        stop_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)) 
        vbox.Add(stop_btn, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 20)

        panel.SetSizer(vbox)

    def on_open_game(self, event):
        if self.website_choice.GetStringSelection() == "Monkeytype":
            self.bot.website = "https://monkeytype.com"
        elif self.website_choice.GetStringSelection() == "Typeracer":
            self.bot.website = "https://play.typeracer.com"
        
        self.bot.open_game_window()

    def on_start_typing(self, event):
        wpm = int(self.wpm_text.GetValue())
        error_rate = int(self.error_text.GetValue())
        self.bot.wpm = wpm
        self.bot.error_rate = error_rate
        self.bot.start_typing()

    def on_stop_typing(self, event):
        self.bot.stop_typing()

app = wx.App(False)
frame = MyFrame(None, 'Typing Bot')
frame.SetForegroundColour(wx.Colour(29, 206, 38)) 
frame.Show(True)
app.MainLoop()
