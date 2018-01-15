GoodMorning ReadMe:

GoodMorning is a nice display of the time, date, weather, and stock data,
featuring greetings and backgrounds for morning, evening, and night. I
made this as a hobby project, it is running on a Raspberry Pi Zero
mounted to a small display on my mirror!

Made in Python 3.6

Package Requirements:
- pytz
- PIL

Install Guide:
1. clone the repository or unzip the files somewhere
2. edit the settings.cfg file to your preferred name/timezome/stocks/etc
3. for weather data I use openweathermap's API -- make a free account for the API key
4. for stock data I use alphavantage's API -- make a free account for the API key
5. run the main.py file to run the display

Notes:
- The backgrounds scale to the window size, so you can change them as per your preference
- To exit the display, press [Escape]
- The code is pretty straightforward, so feel free to modify it :)


Troubleshooting:

"My Raspberry Pi says 'cannot import name ImageTk'!"
sudo apt-get install python3-pil.imagetk

"It says 'read the ReadMe!'"
This means you haven't yet setup the api key in the settings.cfg file

"It says 'Good Afternoon Jack!', how can I make it my own name?"
Change the name in settings.cfg
