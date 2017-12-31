# This code written in Python 3

import json, requests                     # for BTC price
from pandas.io.json import json_normalize # for BTC price
import quandl, numpy                      # for treasury yield
import datetime, pandas as pd             # for 538 Trump approve
from astral import Astral                 # For moon phase
import random                             # For Lexi Messages

def getBTCprice():
    # Get price as of this exact moment
    url = requests.get('https://api.coindesk.com/v1/bpi/currentprice/USD.json')
    price = json.loads(url.text)
    BTCprice = float(price['bpi']['USD']['rate'].replace(',',''))
    BTCpriceformatted = '${:,.2f}'.format(BTCprice)
    
    # Get historical close prices and average
    base_url = 'https://api.coindesk.com/v1/bpi/historical/close.json'
    today = str(datetime.date.today())
    monthago = str(datetime.date.today() + datetime.timedelta(-30))
    dateparam = "?start=" + monthago + "&end=" + today
    url = requests.get(base_url + dateparam)
    price = json.loads(url.text)
    data = numpy.transpose(json_normalize(price['bpi']))
    BTCmonthavg = sum(data.values[0:len(data)])/len(data)
    BTCmonthavgformatted = '${:,.2f}'.format(float(BTCmonthavg))
    return BTCpriceformatted, BTCmonthavgformatted

def get538trumpapprove():
    data = pd.read_csv('https://projects.fivethirtyeight.com/trump-approval-data/approval_topline.csv')
    today = datetime.date.today().strftime('%m%d%Y')
    data = data[data.subgroup == 'All polls']
    trumpapprove = data['approve_estimate'].values[0].round(1)
    
    # moving average
    mvgavg = data['approve_estimate'].values[0:7]
    trumpapproveweek = (sum(mvgavg)/len(mvgavg)).round(1)
    
    return str(trumpapprove) + "%", str(trumpapproveweek) + "%"

def get10yeartreas():
    treasury = quandl.get("USTREASURY/YIELD")
    tenyeartreas = treasury['10 YR'][len(treasury)-1]
    yearavg10YT = sum(treasury['10 YR'][-365:len(treasury)].values)/365
    return str(tenyeartreas) + "%", str(round(yearavg10YT,2)) + "%"

def getMoonPhaseMessage():
    phasenum = Astral.moon_phase(Astral(),datetime.date.today())
    # Moon phase numbers: 
    # 0 = New Moon
    # 7 = First Quarter
    # 14 = Full Moon
    # 21 = Last Quarter
    messages = {13:"This waxing gibbous is about to go FULL MOON!",
                14:"Full moon today!"}
    return messages.get(phasenum,"")

def main():
    b, b2 = getBTCprice()
    a, a2 = get538trumpapprove()
    t, t2 = get10yeartreas()
    m = getMoonPhaseMessage()
    
    if m != "":
        m = '\n' + m 
    
    email = ('BTC/USD: ' + b + ' (last mth avg: ' + b2 + ')\n' + 
            '538 Trump Approval: ' + a + " (last wk avg: " + a2 + ')\n' + 
            '10 Yr UST Yield: ' + t + " (last yr avg: " + t2 + ')' + # \n included in m
             m)
    
    print(email)
    
def getRandomLexiMessage():
    messages = {1:"I love you!",
                2:"You are my sunshine!",
                3:"Message 3"}
    message = messages.get(random.randint(1,len(messages)))
    return message
