# This code written in Python 3

import json, requests                     # for BTC price
from pandas.io.json import json_normalize # for BTC price
import quandl, numpy                      # for treasury yield
import datetime, pandas as pd             # for 538 Trump approve
from astral import Astral                 # For moon phase
import fitbit, urllib, base64             # For weight data

def getBTCprice():
    try: 
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
        
        btcMessage = 'BTC/USD: ' + BTCpriceformatted + ' (last mth avg: ' + BTCmonthavgformatted + ')'
        
    except:
        btcMessage = 'Unable to retreive BTC information.'
    
    return btcMessage

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

def getWeightData():
    # Get the API keys from where I've stored them locally on the pi
    fitbit_api_keys = json.load(open("/home/pi/keys/fitbit_api_keys.json"))
    client_id = fitbit_api_keys['client_id']
    client_secret = fitbit_api_keys['client_secret']
    access_token = fitbit_api_keys['access_token']
    refresh_token = fitbit_api_keys['refresh_token']
    
    # This code refreshes the access token
    refresh_err, a, r = refreshFitbitTokens(client_id, client_secret, refresh_token)
    if not refresh_err:
        fitbit_api_keys['access_token'] = a
        fitbit_api_keys['refresh_token'] = r
        fitbit_api_keys['last-refreshed'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        access_token = a
        refresh_token = r
    else: 
        return
    
    # next bit will declare the client, and get data
    auth_client = fitbit.Fitbit(client_id, client_secret, access_token=access_token, refresh_token=refresh_token)
    weight_data = auth_client.get_bodyweight(period='30d')
    
    # last bit will do the moving average calculation and format the message
    no_obs = len(weight_data['weight'])
    weight_array = []
    for i in range(no_obs):
        weight_array.append(weight_data['weight'][i]['weight'])
    
    weight_avg = round(sum(weight_array)/len(weight_array),1)
    weight_array.clear()
    return weight_avg

def refreshFitbitTokens(client_id, client_secret, refresh_token):
    TokenURL = 'https://api.fitbit.com/oauth2/token'
    BodyText = {'grant_type':'refresh_token',
                'refresh_token':refresh_token}
    BodyURLEncoded = urllib.parse.urlencode(BodyText).encode('utf-8')
    tokenreq = urllib.request.Request(TokenURL,BodyURLEncoded)
    
    # IT WORKS NOW.  DEAR LORD YES
    tokenreq.add_header('Authorization', 'Basic ' + base64.b64encode(bytes(client_id + ":" + client_secret, 'utf-8')).decode('utf-8'))
    tokenreq.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        tokenresponse = urllib.request.urlopen(tokenreq)

        #See what we got back.  If it's this part of  the code it was OK
        FullResponse = tokenresponse.read()

        #Need to pick out the access token and write it to the config file.  Use a JSON manipluation module
        ResponseJSON = json.loads(FullResponse.decode('utf-8'))

        #Read the access token as a string
        NewAccessToken = str(ResponseJSON['access_token'])
        NewRefreshToken = str(ResponseJSON['refresh_token'])
        refresh_err = False

    except urllib.error.URLError as e:
        # Getting to this part of the code means we got an error
        # print(e.code)
        # print(e.read())
        print('Error in getting new Fitbit access tokens.')
        NewAccessToken = ''
        NewRefreshToken = ''
        refresh_err = True
        
    return refresh_err, NewAccessToken, NewRefreshToken
        
def main():
    b = getBTCprice()

    a, a2 = get538trumpapprove()
    t, t2 = get10yeartreas()
    m = getMoonPhaseMessage()
    
    if m != "":
        m = '\n' + m 
    

    email = (b + '\n' + 
            '538 Trump Approval: ' + a + " (last wk avg: " + a2 + ')\n' + 
            '10 Yr UST Yield: ' + t + " (last yr avg: " + t2 + ')' + # \n included in m
             m)
    
    print(email)

