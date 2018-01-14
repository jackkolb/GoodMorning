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
    with open('settings.cfg', 'r') as settings_file:
        lines = settings_file.readlines()

        for line in lines:
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


def get_weather():
    if settings['weather_api_key'] == "OPENWEATHERMAP_API_KEY_GOES_HERE":
        return "read the ReadMe!"
    try:
        http_data = urllib.request.urlopen("http://api.openweathermap.org/data/2.5/weather?zip=92507,us&appid=" + settings['weather_api_key'])
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
    root.geometry('800x600')
    root.bind("<Escape>", lambda event: root.destroy())

    root.grid()

#    root.overrideredirect(True)
#    root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

    width = 800
    height = 600

    get_settings()

    morning_background = Image.open("img/morning_background.png").copy().resize((width, height))
    morning_background_image = ImageTk.PhotoImage(morning_background)

    background = tk.Canvas(width=width, height=height, bg='black', highlightthickness=0, relief='ridge')
    background.grid(row=0, column=0, rowspan=20, columnspan=20)

    background_image = background.create_image(width, height, image=morning_background_image, anchor=tk.SE)

    greeting_text = background.create_text(width*.5, height*.4,
                           font="AvantGarde 40 normal",
                           text=get_greeting("morning"),
                           fill="white")

    date_text = background.create_text(width*.5, height*.5,
                           font="AvantGarde 20 normal",
                           text=get_date(),
                           fill="white")

    weather_text = background.create_text(width*.2, height*.70,
                           font="AvantGarde 20 normal",
                           text=get_weather(),
                           fill="white",
                           justify="left")

    time_text = background.create_text(width*.5, height*.07,
                           font="AvantGarde 20 normal",
                           text=get_time(),
                           fill="white",
                           justify="left")




    def update_thread():
        date_flag = 0
        weather_flag = 0
        time_flag = 0
        environment_flag = "morning"

        while True:
            time.sleep(3)
            now = datetime.datetime.now(pytz.timezone(settings['timezone']))

            if now.day != date_flag:
                background.itemconfig(date_text, text=get_date())
                date_flag = now.day

            if now.hour != weather_flag:
                background.itemconfig(weather_text, text=get_weather())
                weather_flag = now.hour

            if now.minute != time_flag:
                background.itemconfig(time_text, text=get_time())
                time_flag = now.minute

            if now.hour >= 6 and now.hour < 12 and environment_flag != "morning":
                environment_flag = "morning"
                morning_background = Image.open("img/morning_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            if now.hour >= 12 and now.hour < 17 and environment_flag != "afternoon":
                environment_flag = "afternoon"
                morning_background = Image.open("img/morning_background.png").copy().resize((width, height))
                morning_background_image = ImageTk.PhotoImage(morning_background)
                background.itemconfig(background_image, image=morning_background_image)
                background.itemconfig(greeting_text, text=get_greeting(environment_flag))

            if now.hour >= 17 and now.hour < 20 and environment_flag != "evening":
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

            print("Update!")

    update = threading.Thread(target=update_thread)
    update.start()

    root.mainloop()


if __name__ == "__main__":
    main()
