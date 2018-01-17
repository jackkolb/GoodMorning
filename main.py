# GoodMorning -- (C) Jack Kolb, 2018

# External Libraries
from PIL import Image, ImageTk
import pytz

# Internal Libraries
import tkinter as tk
import datetime
import time
import threading
import urllib.request
import json
import os.path
import sys


settings = {}  # settings dictionary used in various functions


# retrieves settings from the settings file
def get_settings():
    settings_file_path = 'settings.cfg'  # the default file path
    if os.path.exists('jack_settings.cfg'):  # changes the path if it finds my dev settings file (not on GitHub)
        settings_file_path = 'jack_settings.cfg'

    # reads the settings file into the settings dictionary, everything before'=' is variable, after '=' is value
    with open(settings_file_path, 'r') as settings_file:
        file_lines = settings_file.readlines()
        for line in file_lines:
            if line == '\n' or line == '':  # rejects blank lines
                continue
            variable = line[:line.find('=')]
            value = line[line.find('=')+1:-1]

            settings[variable] = value


# uses datetime to get the local date, formats as the displayed string ("Today is January 26th")
def get_date():
    # majority 'borrowed' from StackOverflow (user: gsteff ) -- gets the day suffix ("th", "rd", "nd")
    def suffix(day):
        return 'th' if 11 <= day <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')

    def custom_strftime(time_format, t):
        return t.strftime(time_format).replace('{S}', str(t.day) + suffix(t.day))

    date_string = custom_strftime('%A, %B {S}', datetime.datetime.now(pytz.timezone(settings['timezone'])))
    return "Today is " + date_string


# uses datetime to get the local time, formats as the displayed string ("9:30 pm" or "15:20")
def get_time():
    current_time = datetime.datetime.now(pytz.timezone(settings['timezone']))
    hour = current_time.hour

    if settings['24hour'] == "True":  # If using 24-hour time, don't change the hour
        hour = hour
        ampm = ""

    else:  # if using 12-hour time, format and append am/pm
        ampm = " am"
        if hour >= 12:
            ampm = " pm"
        if hour > 12:  # turns 15:30pm into 3:30pm
            hour -= 12
        if hour == 0:  # turns 0:45am into 12:45am
            hour += 12

    minute = current_time.minute
    if minute < 10:  # turns 4:9am into 4:09am
        minute = "0" + str(minute)

    return str(hour) + ":" + str(minute) + ampm


# converts kelvin (default temperature from the weather API) to fahrenheit
def convert_kelvin_to_fahrenheit(kelvin):
    return int((kelvin - 273) * 1.8 + 32)


# converts kelvin (default temperature from the weather API) to celsius
def convert_kelvin_to_celsius(kelvin):
    return int((kelvin - 273))


# converts kelvin (default temperature from the weather API) to celsius
def convert_kelvin_to_rankine(kelvin):
    return int(convert_kelvin_to_fahrenheit(kelvin) - 460.67)


# uses the AlphaVantage API to get stock data, formats as the ticker information string ("TICK: price gain (gain%)")
def get_stocks():
    ticker_line = []  # list of ticker information lines

    # if the API key was not changed, or is blank, just don't have a ticker line (two empty spaces)
    if settings['stock_api_key'] == "ALPHAVANTAGE_API_KEY_GOES_HERE" or settings['stock_api_key'] == "":
        return "  "

    try:
        stocks = settings['stocks'].split(',')  # transforms the raw settings data into a stock ticker list
        cryptos = settings['cryptos'].split(',')  # transforms the raw settings data into a crypto ticker list

        for stock in stocks:
            # the api returns a json file
            url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=" + stock\
                  + "&interval=60min&outputsize=compact&apikey=" + settings['stock_api_key']
            title = "Time Series (60min)"
            header = "4. close"
            interval = 23

            http_data = urllib.request.urlopen(url)  # gets data from the url
            json_data = json.loads(http_data.read().decode())  # turns raw data into json format
            times = list(json_data[title].keys())  # gets list of data points (by time)
            times.sort()  # sorts the data points by time

            current_price = float(json_data[title][times[0]][header])  # fetches current price from data
            previous_price = float(json_data[title][times[interval]][header])  # fetches 24-hour price from data
            gain = current_price - previous_price  # calculates the difference in prices
            percent = 100 * gain / previous_price  # calculates the percent change
            gain = round(gain, 2)  # rounds the difference to two decimal places
            if gain > 0:  # prepends a '+' if the difference is >0 ('-' is prepended by the number format if <0)
                gain = "+" + str(gain)
            ticker_line.append(stock + ": " + "$" + str(round(current_price, 2)) + " " + str(gain)
                               + " (" + str(round(percent, 2)) + "%)")  # formats as a pretty string, adds to the list

        for crypto in cryptos:
            url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&symbol=" + crypto\
                  + "&market=USD&apikey=" + settings['stock_api_key']
            title = "Time Series (Digital Currency Intraday)"
            header = "1a. price (USD)"
            interval = 288

            http_data = urllib.request.urlopen(url)  # gets data from the url
            json_data = json.loads(http_data.read().decode())  # turns raw data into json format
            times = list(json_data[title].keys())  # gets list of data points (by time)
            times.sort()  # sorts the data points by time

            current_price = float(json_data[title][times[0]][header])  # fetches current price from data
            previous_price = float(json_data[title][times[interval]][header])  # fetches 24-hour price from data
            gain = current_price - previous_price  # calculates the difference in prices
            percent = 100 * gain/previous_price  # calculates the percent change
            gain = round(gain, 2)  # rounds the difference to two decimal places
            if gain > 0:  # prepends a '+' if the difference is >0 ('-' is prepended by the number format if <0)
                gain = "+" + str(gain)
            ticker_line.append(crypto + ": " + "$" + str(round(current_price, 2)) + " " + str(gain)
                               + " (" + str(round(percent, 2)) + "%)")  # formats as a pretty string, adds to the list

    except urllib.request.URLError:  # usually means your internet is down
        ticker_line.append("Stocks Unavailable")

    stock_line = ""
    for line in ticker_line:  # consolidates all the ticker lines into one big line
        stock_line += line + "  "

    return stock_line


# uses the OpenWeathermap API to get weather data, formats as a weather string
def get_weather():
    # if the API key was not changed, or is blank, just don't have a weather display (two empty spaces)
    if settings['weather_api_key'] == "OPENWEATHERMAP_API_KEY_GOES_HERE" or settings['weather_api_key'] == "":
        return "  "

    try:
        http_data = urllib.request.urlopen("http://api.openweathermap.org/data/2.5/weather?zip=" + settings['zip_code']
                                           + ",us&appid=" + settings['weather_api_key'])
        json_data = json.loads(http_data.read().decode())  # gets data from the url
        weather_data = json_data['main']  # turns raw data into json format

        # variables used in the weather string
        prefix = ""  # 'F', 'R', 'C', 'K'
        temperature = weather_data['temp']  # current temperature (default in Kelvin)
        temperature_max = weather_data['temp_max']  # daily max temperature (default in Kelvin)
        temperature_min = weather_data['temp_min']  # daily min temperature (default in Kelvin)

        # If Fahrenheit is specified in settings, convert the temperatures to Fahrenheit
        if settings['temperature'] == "F":
            prefix = u'\N{DEGREE SIGN}' + "F"
            temperature = str(convert_kelvin_to_fahrenheit(temperature))
            temperature_max = str(convert_kelvin_to_fahrenheit(temperature_max))
            temperature_min = str(convert_kelvin_to_fahrenheit(temperature_min))

        # If Rankine is specified in settings, convert the temperatures to Rankine
        elif settings['temperature'] == "R":
            prefix = u'\N{DEGREE SIGN}' + "R"
            temperature = str(convert_kelvin_to_rankine(temperature))
            temperature_max = str(convert_kelvin_to_rankine(temperature_max))
            temperature_min = str(convert_kelvin_to_rankine(temperature_min))

        # If Celsius is specified in settings, convert the temperatures to Celsius
        elif settings['temperature'] == "C":
            prefix = u'\N{DEGREE SIGN}' + "C"
            temperature = str(convert_kelvin_to_celsius(temperature))
            temperature_max = str(convert_kelvin_to_celsius(temperature_max))
            temperature_min = str(convert_kelvin_to_celsius(temperature_min))

        # If Kelvin is specified in settings, keep the temperatures as Kelvin
        elif settings['temperature'] == "K":
            prefix = "K"
            temperature = temperature
            temperature_max = temperature_max
            temperature_min = temperature_min

        # consolidates the information into a string
        weather = prefix + " " + temperature + " (" + temperature_max + "/" + temperature_min + ")" + '\n'

        # gets the weather status ('Rain', 'Snow', 'Clouds', etc) from the json data, consolidates to weather string
        weather += json_data['weather'][0]['main']
        for i in json_data['weather'][1:]:
            weather += ", " + i['main']  # sometimes there are multiple statuses

    except urllib.request.URLError:  # usually means your internet is down
        weather = "Weather\nUnavailable"

    return weather


# uses the environment (morning, afternoon, evening, night) and name (from settings) to make a greeting
def get_greeting(environment):
    salutation = ""
    if environment == "morning":
        salutation = "Good Morning"
    elif environment == "afternoon":
        salutation = "Good Afternoon"
    elif environment == "evening":
        salutation = "Good Evening"
    elif environment == "night":
        salutation = "Good Night"
    return salutation + " " + settings['name'] + "!"


def main():
    root = tk.Tk()
    root.title('GoodMorning')  # sets window title to 'GoodMorning'

    root.bind("e", lambda event: root.destroy())  # if you press 'e', the display will exit

    root.grid()  # the display uses a grid layout

#    root.overrideredirect(True)  # this makes the display full screen, but I have trouble exiting it on a Raspberry Pi
#    root.geometry('800x600')  # nice small standard size for testing
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))  # uses the screen size

    width = root.winfo_screenwidth()  # used for positioning widgets
    height = root.winfo_screenheight()  # used for positioning widgets

    get_settings()  # loads the settings

    # the default background is the morning background
    initial_background = Image.open("img/morning_background.png").copy().resize((width, height))
    initial_background_image = ImageTk.PhotoImage(initial_background)

    # creates canvas that spans the entire frame
    background = tk.Canvas(width=width, height=height, bg='black', highlightthickness=0, relief='ridge')
    background.grid(row=0, column=0, rowspan=1, columnspan=1)

    background_image = background.create_image(width, height, image=initial_background_image, anchor=tk.SE)

    foreground_image = background.create_image(width, height, anchor=tk.SE)

    greeting_text = background.create_text(width*.5, height*.3,
                                           font="AvantGarde " + str(int(height*.08)) + " normal",
                                           text="",
                                           fill="white")

    date_text = background.create_text(width*.5, height*.4,
                                       font="AvantGarde " + str(int(height*.03)) + " normal",
                                       text="",
                                       fill="white")

    weather_text = background.create_text(width*.2, height*.67,
                                          font="AvantGarde " + str(int(height*.03)) + " normal",
                                          text="",
                                          fill="white",
                                          anchor="ne")

    time_text = background.create_text(width*.5, height*.07,
                                       font="AvantGarde " + str(int(height*.03)) + " normal",
                                       text="",
                                       fill="white")

    stock_scroll = background.create_text(width * .5, height * .95,
                                          font="Courier " + str(int(height*.03)) + " bold",
                                          text="  ",
                                          fill="white")

    # class for holding the stock ticker scroll bar information
    class TickerBar:
        delay = 250  # delay (ms) per shift
        stock_text = "Loading Stocks..."  # initial ticker text

    # The scroll-bar itself: recursively calls itself, and shifts the ticker text one digit to the left
    def ticker_bar_animation():
        TickerBar.stock_text = TickerBar.stock_text[1:] + TickerBar.stock_text[0]  # shifts the ticker text
        background.itemconfig(stock_scroll, text=TickerBar.stock_text)  # updates the text on the GUI
        root.after(TickerBar.delay, ticker_bar_animation)  # waits before updating again

    ticker_bar_animation()  # begins the ticker scroll bar

    update_flag = True  # flag for the update thread, is set to "False" when the program ends

    # thread function, updates information periodically
    def update_thread():
        # set initial update flags to -1/"", so they all fire on the first pass
        date_flag = -1
        weather_flag = -1
        time_flag = -1
        environment_flag = ""
        stock_flag = -1

        # will loop infinitely until the program exits (and turns update_flag to False)
        while update_flag is True:
            now = datetime.datetime.now(pytz.timezone(settings['timezone']))  # get current date/time

            # update the date
            if now.day != date_flag:
                background.itemconfig(date_text, text=get_date())
                date_flag = now.day

            # update the weather
            if now.hour != weather_flag:
                weather = get_weather()  # retrieves the weather as the text displayed
                background.itemconfig(weather_text, text=weather)
                weather = weather.split('\n')[-1]  # gets the last line of the weather (the environment)
                # choose a foreground image based on the environment, defaults to "light_clouds"
                if "clear" in weather.lower():
                    weather_image = "img/clear_skies.png"
                elif "overcast" in weather.lower():
                    weather_image = "img/heavy_clouds.png"
                elif "clouds" in weather.lower():
                    weather_image = "img/light_clouds.png"
                elif "mist" in weather.lower():
                    weather_image = "img/heavy_clouds.png"
                elif "snow" in weather.lower():
                    weather_image = "img/storm_clouds.png"
                elif "rain" in weather.lower():
                    weather_image = "img/storm_clouds.png"
                elif "drizzle" in weather.lower():
                    weather_image = "img/storm_clouds.png"
                elif "fog" in weather.lower():
                    weather_image = "img/fog_clouds.png"
                else:
                    weather_image = "img/light_clouds.png"
                weather_overlay = Image.open(weather_image).copy().resize((width, height))  # format image
                weather_overlay_image = ImageTk.PhotoImage(weather_overlay)
                background.itemconfig(foreground_image, image=weather_overlay_image)  # set image to foreground
                weather_flag = now.hour  # updates weather_flag

            # updates the clock
            if now.minute != time_flag:
                background.itemconfig(time_text, text=get_time())
                time_flag = now.minute

            # updates the environment to morning: changes background image and greeting text accordingly
            if 12 > now.hour >= 6 and environment_flag != "morning":
                environment_flag = "morning"
                morning_background = Image.open("img/morning_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            # updates the environment to afternoon: changes background image and greeting text accordingly
            if 17 > now.hour >= 12 and environment_flag != "afternoon":
                environment_flag = "afternoon"
                morning_background = Image.open("img/morning_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            # updates the environment to evening: changes background image and greeting text accordingly
            if 20 > now.hour >= 17 and environment_flag != "evening":
                environment_flag = "evening"
                morning_background = Image.open("img/evening_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            # updates the environment to nighttime: changes background image and greeting text accordingly
            if (now.hour >= 20 or now.hour < 6) and environment_flag != "night":
                environment_flag = "night"
                morning_background = Image.open("img/night_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            # updates the stock ticker bar text hourly
            if now.hour != stock_flag:
                TickerBar.stock_text = get_stocks()
                stock_flag = now.hour

            time.sleep(3)  # waits three seconds before looping again

    update = threading.Thread(target=update_thread)  # ready the thread
    update.start()  # run the thread

    root.mainloop()  # run the main loop
    update_flag = False  # sets the update flag to False, which will stop the thread


if __name__ == "__main__":
    main()
