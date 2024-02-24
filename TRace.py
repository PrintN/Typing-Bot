import threading
import keyboard as k
import wx
from selenium import webdriver
import re
import time
import random

class TyperacerBot:
    def __init__(self):
        self.driver = None
        self.typing_event = threading.Event()
        self.wpm = 0
        self.error_rate = 0

    def open_game_window(self):
        self.driver = webdriver.Chrome(executable_path=r"[PUT YOUR PATH TO THE DRIVER HERE]/chromedriver.exe")
        self.driver.get("https://monkeytype.com")

    def initialize_driver(self):
        # Do nothing here, as we'll open the game window explicitly
        pass

    def html(self):
        try:
            result = self.driver.page_source.partition("""class="word active""")[2].partition("""class="keymap hidden""")[0]
            result = re.sub("""class="word""", '> <', result)
            x = re.findall(r"\>([a-z ])\<", result)
            x.append(' ')
            return x
        except Exception as e:
            print("Error getting HTML:", e)
            return []

    def introduce_error(self, char):
        if char == ' ':
            return char  # Don't introduce errors for spaces
        if random.random() < self.error_rate / 100:
            return random.choice([c for c in 'abcdefghijklmnopqrstuvwxyz' if c != char])
        return char

    def type_text(self):
        while not self.typing_event.is_set():
            try:
                words = self.html()
                for word in words:
                    for char in word:
                        if self.typing_event.is_set():
                            return  # Exit the thread if the event is set
                        char = self.introduce_error(char)
                        start_time = time.time()
                        webdriver.ActionChains(self.driver).send_keys(char).perform()
                        end_time = time.time()
                        character_time = end_time - start_time
                        time.sleep(max(0, ((60 / (self.wpm * 5)) - character_time)))  # Adjusted delay based on actual character typing time
            except Exception as e:
                print("Error typing text:", e)
                break

    def start_typing(self):
        self.typing_event.clear()
        threading.Thread(target=self.type_text).start()

    def stop_typing(self):
        self.typing_event.set()  # Set the event to stop typing

class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(350, 400))

        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(26, 35, 43))  # Set background color

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.bot = TyperacerBot()

        open_game_btn = wx.Button(panel, label='Open Game', size=(150, 40))
        open_game_btn.SetBackgroundColour(wx.Colour(26, 35, 43))  # Set button background color
        open_game_btn.SetForegroundColour(wx.Colour(255, 255, 255))  # Set button text color
        open_game_btn.Bind(wx.EVT_BUTTON, self.on_open_game)
        open_game_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))  # Set button text font
        vbox.Add(open_game_btn, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 20)

        wpm_label = wx.StaticText(panel, label="Words per Minute (WPM):")
        wpm_label.SetForegroundColour(wx.Colour(255, 255, 255))  # Set text color
        wpm_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))  # Set text font
        vbox.Add(wpm_label, 0, wx.EXPAND | wx.ALL, 5)

        self.wpm_text = wx.TextCtrl(panel, size=(150, -1))
        self.wpm_text.SetBackgroundColour(wx.Colour(26, 35, 43))  # Set input field background color
        self.wpm_text.SetForegroundColour(wx.Colour(255, 255, 255))  # Set input field text color
        vbox.Add(self.wpm_text, 0, wx.EXPAND | wx.ALL, 5)

        error_label = wx.StaticText(panel, label="Human Error (%):")
        error_label.SetForegroundColour(wx.Colour(255, 255, 255))  # Set text color
        error_label.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))  # Set text font
        vbox.Add(error_label, 0, wx.EXPAND | wx.ALL, 5)

        self.error_text = wx.TextCtrl(panel, size=(150, -1))
        self.error_text.SetBackgroundColour(wx.Colour(26, 35, 43))  # Set input field background color
        self.error_text.SetForegroundColour(wx.Colour(255, 255, 255))  # Set input field text color
        vbox.Add(self.error_text, 0, wx.EXPAND | wx.ALL, 5)

        start_btn = wx.Button(panel, label='Start Typing', size=(150, 40))
        start_btn.SetBackgroundColour(wx.Colour(26, 35, 43))  # Set button background color
        start_btn.SetForegroundColour(wx.Colour(255, 255, 255))  # Set button text color
        start_btn.Bind(wx.EVT_BUTTON, self.on_start_typing)
        start_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))  # Set button text font
        vbox.Add(start_btn, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 20)

        stop_btn = wx.Button(panel, label='Stop Typing', size=(150, 40))
        stop_btn.SetBackgroundColour(wx.Colour(26, 35, 43))  # Set button background color
        stop_btn.SetForegroundColour(wx.Colour(255, 255, 255))  # Set button text color
        stop_btn.Bind(wx.EVT_BUTTON, self.on_stop_typing)
        stop_btn.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))  # Set button text font
        vbox.Add(stop_btn, 0, wx.CENTER | wx.TOP | wx.BOTTOM, 20)

        panel.SetSizer(vbox)

    def on_open_game(self, event):
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
frame.SetForegroundColour(wx.Colour(29, 206, 38))  # Set text color to #1dce26
frame.Show(True)
app.MainLoop()
