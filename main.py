import tkinter as tk
from PIL import Image, ImageTk
import datetime
import time
import threading
import urllib.request
import json
import pytz

settings = {}


def get_settings():
    with open('jack_settings.cfg', 'r') as settings_file:
        lines = settings_file.readlines()

        for line in lines:
            if line == '\n':
                continue
            variable = line[:line.find('=')]
            value = line[line.find('=')+1:-1]

            settings[variable] = value


def get_date():
    # majority 'borrowed' from StackOverflow (user: gsteff )
    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    def custom_strftime(time_format, t):
        return t.strftime(time_format).replace('{S}', str(t.day) + suffix(t.day))

    date_string = custom_strftime('%A, %B {S}', datetime.datetime.now(pytz.timezone(settings['timezone'])))
    return "Today is " + date_string


def get_time():
    current_time = datetime.datetime.now(pytz.timezone(settings['timezone']))
    hour = current_time.hour
    ampm = "am"
    if hour >= 12:
        ampm = "pm"

    if hour > 12:
        hour -= 12

    if hour == 0:
        hour += 12

    minute = current_time.minute
    if minute < 10:
        minute = "0" + str(minute)

    return str(hour) + ":" + str(minute) + " " + ampm


def convert_kelvin_to_fahrenheit(kelvin):
    return int((kelvin - 273) * 1.8 + 32)


def convert_kelvin_to_celsius(kelvin):
    return int((kelvin - 273))


def get_stocks():
    ticker_line = []

    if settings['stock_api_key'] == "ALPHAVANTAGE_API_KEY_GOES_HERE":
        return "read the ReadMe!"
    try:
        stocks = settings['stocks'].split(',')
        cryptos = settings['cryptos'].split(',')

        for stock in stocks:
            url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=" + stock\
                  + "&interval=60min&outputsize=compact&apikey=" + settings['stock_api_key']
            title = "Time Series (60min)"
            header = "4. close"
            interval = 23

            http_data = urllib.request.urlopen(url)
            json_data = json.loads(http_data.read().decode())
            times = list(json_data[title].keys())
            times.sort()
            current_price = float(json_data[title][times[0]][header])
            previous_price = float(json_data[title][times[interval]][header])
            gain = current_price - previous_price
            percent = 100 * gain / previous_price
            gain = round(gain, 2)
            if gain > 0:
                gain = "+" + str(gain)
            ticker_line.append(stock + ": " + "$" + str(round(current_price, 2)) + " " + str(gain)
                               + " (" + str(round(percent, 2)) + "%)")

        for crypto in cryptos:
            url = "https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_INTRADAY&symbol=" + crypto\
                  + "&market=USD&apikey=" + settings['stock_api_key']
            title = "Time Series (Digital Currency Intraday)"
            header = "1a. price (USD)"
            interval = 288

            http_data = urllib.request.urlopen(url)
            json_data = json.loads(http_data.read().decode())
            times = list(json_data[title].keys())
            times.sort()
            current_price = float(json_data[title][times[0]][header])
            previous_price = float(json_data[title][times[interval]][header])
            gain = current_price - previous_price
            percent = gain/previous_price
            gain = round(gain, 2)
            if gain > 0:
                gain = "+" + str(gain)
            ticker_line.append(crypto + ": " + "$" + str(round(current_price, 2)) + " " + str(gain)
                               + " (" + str(round(percent, 2)) + "%)")

    except KeyboardInterrupt as e:
        ticker_line.append("Stocks Unavailable")

    stock_line = ""
    for line in ticker_line:
        stock_line += line + "  "

    return stock_line


def get_weather():
    if settings['weather_api_key'] == "OPENWEATHERMAP_API_KEY_GOES_HERE":
        return "read the ReadMe!"
    try:
        http_data = urllib.request.urlopen("http://api.openweathermap.org/data/2.5/weather?zip=" + settings['zip_code']
                                           + ",us&appid=" + settings['weather_api_key'])
        json_data = json.loads(http_data.read().decode())
        weather_data = json_data['main']

        prefix = ""
        temp = ""
        temp_max = ""
        temp_min = ""

        if settings['temperature'] == "F":
            prefix = "F" + u'\N{DEGREE SIGN}'
            temp = str(convert_kelvin_to_fahrenheit(weather_data['temp']))
            temp_max = str(convert_kelvin_to_fahrenheit(weather_data['temp_max']))
            temp_min = str(convert_kelvin_to_fahrenheit(weather_data['temp_min']))

        elif settings['temperature'] == "C":
            prefix = "C" + u'\N{DEGREE SIGN}'
            temp = str(convert_kelvin_to_celsius(weather_data['temp']))
            temp_max = str(convert_kelvin_to_celsius(weather_data['temp_max']))
            temp_min = str(convert_kelvin_to_celsius(weather_data['temp_min']))

        elif settings['temperature'] == "K":
            prefix = "K"
            temp = str(int(weather_data['temp']))
            temp_max = str(int(weather_data['temp_max']))
            temp_min = str(int(weather_data['temp_min']))

        weather = prefix + " " + temp + " (" + temp_max + "/" + temp_min + ")" + '\n'

        weather += json_data['weather'][0]['main']
        for i in json_data['weather'][1:]:
            weather += ", " + i['main']
    except Exception:
        weather = "Weather Unavailable"
    return weather


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
    root.title('Good Morning')
#    root.geometry('800x600')
    root.bind("e", lambda event: root.destroy())

    root.grid()

#    root.overrideredirect(True)
    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()

    get_settings()

    initial_background = Image.open("img/morning_background.png").copy().resize((width, height))
    initial_background_image = ImageTk.PhotoImage(initial_background)

    background = tk.Canvas(width=width, height=height, bg='black', highlightthickness=0, relief='ridge')
    background.grid(row=0, column=0, rowspan=20, columnspan=20)

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

    class TickerBar:
        delay = 250  # milliseconds of delay per character
        stock_text = "Loading Stocks..."

    def shif():
        TickerBar.stock_text = TickerBar.stock_text[1:] + TickerBar.stock_text[0]
        background.itemconfig(stock_scroll, text=TickerBar.stock_text)
        root.after(TickerBar.delay, shif)
    shif()

    def update_thread():
        date_flag = -1
        weather_flag = -1
        time_flag = -1
        environment_flag = ""
        stock_flag = -1

        while True:
            now = datetime.datetime.now(pytz.timezone(settings['timezone']))

            if now.day != date_flag:
                background.itemconfig(date_text, text=get_date())
                date_flag = now.day

            if now.hour != weather_flag:
                weather = get_weather()
                background.itemconfig(weather_text, text=weather)
                weather = weather.split('\n')[-1]
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
                weather_foreground = Image.open(weather_image).copy().resize((width, height))
                weather_foreground_image = ImageTk.PhotoImage(weather_foreground)
                background.itemconfig(foreground_image, image=weather_foreground_image)
                weather_flag = now.hour

            if now.minute != time_flag:
                background.itemconfig(time_text, text=get_time())
                time_flag = now.minute

            if 12 > now.hour >= 6 and environment_flag != "morning":
                environment_flag = "morning"
                morning_background = Image.open("img/morning_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            if 17 > now.hour >= 12 and environment_flag != "afternoon":
                environment_flag = "afternoon"
                morning_background = Image.open("img/morning_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            if 20 > now.hour >= 17 and environment_flag != "evening":
                environment_flag = "evening"
                morning_background = Image.open("img/evening_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            if (now.hour >= 20 or now.hour < 6) and environment_flag != "night":
                environment_flag = "night"
                morning_background = Image.open("img/night_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            if now.hour != stock_flag:
                TickerBar.stock_text = get_stocks()
                stock_flag = now.hour

            time.sleep(3)

    update = threading.Thread(target=update_thread)
    update.start()

    root.mainloop()


if __name__ == "__main__":
    main()
