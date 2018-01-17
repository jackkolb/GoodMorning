# GoodMorning


GoodMorning is a nice display of the time, date, weather, and stock data,
featuring greetings and backgrounds for morning, evening, and night. I
made this as a hobby project, it is running on a Raspberry Pi Zero
mounted to a small display on my mirror!


Made in Python 3.6


Package Requirements:
- pytz
- PIL
- tkinter


Install Guide:
1. clone the repository or unzip the files somewhere
2. edit the settings.cfg file to your preferred name/timezome/stocks/etc
3. for weather data I use openweathermap's API -- make a free account for the API key
4. for stock data I use alphavantage's API -- make a free account for the API key
5. run the main.py file to run the display


Notes:
- The backgrounds scale to the window size, so they are not restricted to specific dimensions
- To exit the display, press "e"
- The code is pretty straightforward, so feel free to modify it :)
- There are screenshots in the screenshots folder!


Settings:
- name: the display name ("Good Morning _____")
- timezone: your timezone as per pytz's formats ("US/Eastern", "US/Western", etc)
- temperature: "F" - Fahrenheit, "R" - Rankine, "C" - Celsius, "K" - Kelvin
- 24hour: "True" to display as 24-hour (military) time ("15:30"), "False" to display as 12-hour time ("3:30 pm")
- weather_api_key: your openweathermap api key
- zip_code: your zip code, for the weather api
- stock_api_key: your alphavantage api key
- stocks: the stocks you want listed on the ticker feed, in the example format: "stocks=MSFT,AAPL,AMZN,AMD"
- cryptos: the cryptocurrencies you want listed on the ticker feed, in the example format: "cryptos=BTC,ETH,USDT"


Troubleshooting:

"My Raspberry Pi says 'cannot import name ImageTk'!"
sudo apt-get install python3-pil.imagetk

"Weather and/or stock data is unavailable"
Several possible sources:
- you haven't yet setup the api key in the settings.cfg file (assume this first)
- you aren't connected to the internet (assume this second)
- something is up with the API server
- the API changed and I have not updated this package

If you've checked your internet, the API site, your key, and the package is
at the latest version, leave an issue! Be as descriptive as possible.

"It says 'Good Afternoon Jack!', how can I make it my own name?"
Change the name in settings.cfg

"How do I manage the stock/crypto data displayed?"
The program splits the tickers by commas, no spaces (Ex: AAPL,GOOG,TSLA,MSFT,AMZN)

"What is jack_settings.cfg?"
My development settings (with my API keys), as I use GitHub to get the code onto
my Raspberry Pi, and don't feel like retyping the keys when I change the settings file!
It should not get in the way

Enjoy! If you make any significant improvements, let me know so we can add them to the main branch!
