# This code written in Python3

import json, requests         # for BTC price
import quandl                 # for treasury yield
import datetime, pandas as pd # for 538 Trump approve
from astral import Astral     # For moon phase
import random                 # For Lexi Messages

def getBTCprice():
    url = requests.get('https://api.coindesk.com/v1/bpi/currentprice/USD.json')
    price = json.loads(url.text)
    BTCprice = float(price['bpi']['USD']['rate'].replace(',',''))
    BTCpriceformatted = '${:,.2f}'.format(BTCprice)
    return BTCpriceformatted

def get538trumpapprove():
    data = pd.read_csv('https://projects.fivethirtyeight.com/trump-approval-data/approval_topline.csv')
    today = datetime.date.today().strftime('%m%d%Y')
    data = data[data.subgroup == 'All polls']
    trumpapprove = data['approve_estimate'].values[0].round(1)
    # moving average currently not used
    mvgavg = data['approve_estimate'].values[0:5]
    trumpapprove5day = (sum(mvgavg)/len(mvgavg)).round(1)
    return str(trumpapprove) + "%"

def get10yeartreas():
    treasury = quandl.get("USTREASURY/YIELD")
    tenyeartreas = treasury['10 YR'][len(treasury)-1]
    return str(tenyeartreas) + "%"

def getMoonPhaseMessage():
    phasenum = Astral.moon_phase(Astral(),datetime.date.today())
    messages = {13:"Full moon tomorrow!",
                14:"Full moon today!",
                15:"Make waxing gibbous message."}
    return messages.get(phasenum,"")

def main():
    email = ('Bitcoin/USD: ' + getBTCprice() + '\n' + 
            '538 Trump Approval: ' + get538trumpapprove() + '\n' + 
            '10 Year US Treasury Yield: ' + get10yeartreas() + '\n' +
            getMoonPhaseMessage())
    print(email)
    
def getRandomLexiMessage():
    messages = {1:"I love you!",
                2:"You are my sunshine!",
                3:"Message 3"}
    message = messages.get(random.randint(1,len(messages)))
    return message
