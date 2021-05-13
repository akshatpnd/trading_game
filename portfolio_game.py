import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import datetime as dt
from datetime import datetime
from dateutil.relativedelta import *
import warnings
warnings.filterwarnings('ignore')

# Read in data to make model
df = pd.read_csv('dogecoin_may.csv', index_col='Date', parse_dates=True)

# Create model based on findings from Time Series Analysis
model = SARIMAX(df['Open'].diff().diff().dropna(), order=(3,0,2))
result = model.fit()

# Define class to handle Portfolio interactions
class Portfolio:
    
    def __init__(self, name, start_date=dt.datetime(2020, 6, 30)):
        """
        Constructor to initialize portfolio with a given name
        and a default start date of June 30th, 2020
        """
        self.name = name
        # Always start with $100
        self.money = 100
        self.coin = 0
        self.curr_date = start_date
        self.price = 0
        
    def buy(self, money, date):
        """
        Method to buy 'money' dollars worth of dogecoin
        on a given date
        """
        if money > self.money:
            return('You do not have enough money!')
        if date < df.index[0]:
            return('Dogecoin did not exist yet')
                        
        self.money = self.money - money
        self.coin = self.coin + (money/self.price)
        return('You successfully bought {} dogecoins at a price of ${} per coin'.format(money/self.price, self.price))
        
    def curr_price(self, date):
        """
        Method to determine the price of dogecoin on
        a given date
        """
        if date < df.index[0]:
            return('Dogecoin did not exist yet')
        elif date < df.index[-1]:
            self.price = df.loc[date]['Open']
            return('Current price of dogecoin is ${}'.format(self.price))
            
        days_ahead = (date - df.index[-1]).days
        forecast = result.get_forecast(steps=days_ahead).predicted_mean
        fore_to_price = np.cumsum(forecast) + df['Open'].iloc[-1]
        curr_val = fore_to_price.values[-1]
        self.price = curr_val
        return('Current price of dogecoin is ${}'.format(curr_val))
        
    def sell(self, date, amt):
        """
        Method to sell 'amt' dogecoins on a certain date
        """
        if amt > self.coin:
            return('You do not have that many coins!')
            
        self.coin = self.coin - amt
        self.money = self.money + amt * self.price
        return('You earned {} and now have {} coins.'.format(amt * self.price, self.coin))
        
    def overview(self):
        """
        Method to provide an overview of your portfolio
        """
        print('On {}, {}\'s portfolio owns {} dogecoins with a monetary value of ${}'.format(self.curr_date.date(), self.name, self.coin, self.coin*self.price))
        
    def advance(self, amt):
        """
        Method to advance one unit of time
        based on chosen metric out of
        day, month, or year
        """
        if amt.lower() == 'day':
            x = dt.timedelta(days=1)
            self.curr_date = self.curr_date + x
        elif amt.lower() == 'month':
            x = relativedelta(months=1)
            self.curr_date = self.curr_date + x
        else:
            x = relativedelta(years=1)
            self.curr_date = self.curr_date + x


# Method to track game state  
continue_game = True

# Introduction and set-up of Portfolio
print('Welcome to a virtual trading game where you can go back in time and trade dogecoin')
name = input('What will you name your portfolio?')
print('You will start with $100 and on 30th June, 2020')
other_date = input('Do you wish to start at another date?')

if other_date.lower() == 'yes':
    try:
        date = input('Please enter a date in the format year-month-day:')
        start_date = datetime.strptime(date, '%Y-%m-%d')
        port = Portfolio(name, start_date)
    except ValueError:
        print('Please follow the format for the date')
else:
    port = Portfolio(name)

# Begin game
print('')
print('Let the game begin!')
while continue_game:
    port.overview()
    print(port.curr_price(port.curr_date))
    
    buy = input('You currently have ${}, do you wish to buy some dogecoin?'.format(port.money))
    if buy.lower() == 'yes':
        print('How much money would you like to spend?')
        amt = int(input())
        print(port.buy(amt, port.curr_date))
    else:
        sell_or_not = input('You currently have {} coins, do you wish to sell some dogecoin?'.format(port.coin))
        if sell_or_not.lower() == 'yes':
            print('How much would you like to sell?')
            amt = int(input())
            print(port.sell(port.curr_date, amt))
    
    adv = input('Do you wish to continue?')
    if adv.lower() == 'yes':
        how_long = input('Enter day, month, or year to advance by one unit of chosen time:')
        port.advance(how_long)
    else:
        continue_game = False
print('Thank you for playing, hope you enjoyed your time!')