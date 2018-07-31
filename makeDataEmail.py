# This code written in Python 3

import json, requests                     # for BTC price
from pandas.io.json import json_normalize # for BTC price
import quandl, numpy                      # for treasury yield
import datetime, pandas as pd             # for 538 Trump approve
from astral import Astral                 # For moon phase
import fitbit, urllib, base64             # For weight data
import sqlite3                            # For weight database connection

# Constants and file locations
LOG_FILE = '/home/pi/logging/data_email_log.txt'
KEYS_FILE = '/home/pi/keys/fitbit_api_keys.json'
DB_DIR = '/home/pi/health.db'

def main(log_bool=True):
    
    updateWeightDatabase()
    
    b = getBTCprice()
    a, a2 = get538trumpapprove()
    t, t2 = get10yeartreas()
    w = getWeightData()
    m = getMoonPhaseMessage()
    
    if m != "":
        m = '\n' + m 
    
    email = (b + '\n' + 
            '538 Trump Approval: ' + a + " (last wk avg: " + a2 + ')\n' + 
            '10 Yr UST Yield: ' + t + " (last yr avg: " + t2 + ')' + '\n' + 
             w + # \n included in m
             m)
    
    if log_bool:
        email_log = open(LOG_FILE, "a")
        email_log.write('\n' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M') + '\n' + email + '\n')
        email_log.close()
    
    return email

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
    conn = sqlite3.connect(DB_DIR)
    cur = conn.cursor()
    interp_days = 365
    
    yearago = datetime.date.today() + datetime.timedelta(days=-interp_days)
    yearago_string = yearago.strftime("%Y-%m-%d")
    
    cur.execute("SELECT * FROM weight WHERE julianday(date)>=julianday('%s');" % (yearago_string))
    weightdata = cur.fetchall()
    weight_tuple = list(zip(*weightdata))[1]
    
    cur.close()
    conn.close()
    
    weights = []
    datelist = [j[0] for j in weightdata]

    for i in range(interp_days):
        dt = (datetime.date.today()-datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        if dt in datelist:
            k = datelist.index(dt)
            wt = weightdata[k][1]
            bf = weightdata[k][2]
            interp = 0
        else:
            wt = None
            bf = None
            interp = 1
        weights.append((dt,wt,bf,interp))
    # Weights now is an array with the last 30 days and with the known weights filled in
    # Insert code here to do the interpolation and make graphs
    
    # weight_avg = round(sum(weight_tuple)/len(weight_tuple),1)
    # weight_message = "30 day mvg avg weight: " + str(weight_avg)
    
    return weights


def updateWeightDatabase():
    # This code refreshes the access token
    refresh_err = refreshFitbitTokens(KEYS_FILE)
    
    # If the refresh failed, return an error message
    if refresh_err: 
        return "Error with weight data."
    
    # Load the updated API information
    fitbit_api_keys = json.load(open(KEYS_FILE))
    client_id = fitbit_api_keys['client_id']
    client_secret = fitbit_api_keys['client_secret']
    access_token = fitbit_api_keys['access_token']
    refresh_token = fitbit_api_keys['refresh_token']
    
    # next bit will declare the client, and get data
    # get_bodyweight returns weight and body fat data
    auth_client = fitbit.Fitbit(client_id, client_secret, access_token=access_token, refresh_token=refresh_token)
    weight_data = auth_client.get_bodyweight(period='30d')['weight']
    
    # UPDATE THE WEIGHT DATABASE
    conn = sqlite3.connect(DB_DIR)
    cur = conn.cursor()
    
    for i in range(len(weight_data)):
       dt = weight_data[i]['date']
       if 'weight' not in weight_data[i]:
          wt = 'NULL'
       else:
          wt = round(weight_data[i]['weight'],1)

       if 'fat' not in weight_data[i]:
          bf = 'NULL'
       else:
          bf = round(weight_data[i]['fat'],1)

       cur.execute("UPDATE weight SET weight=%s, bf_pcnt=%s WHERE date='%s';" % (wt,bf,dt))

    conn.commit()
    cur.close()
    conn.close()

def refreshFitbitTokens(json_keys_file):
    # Open the json file with the API keys, and load the data that we need
    fitbit_api_keys = json.load(open(json_keys_file))
    client_id = fitbit_api_keys['client_id']
    client_secret = fitbit_api_keys['client_secret']
    refresh_token = fitbit_api_keys['refresh_token']
    
    # Set up the body of the http request
    TokenURL = 'https://api.fitbit.com/oauth2/token'
    BodyText = {'grant_type':'refresh_token',
                'refresh_token':refresh_token}
    BodyURLEncoded = urllib.parse.urlencode(BodyText).encode('utf-8')
    
    # Create a http request with the given URL, and that data package
    tokenreq = urllib.request.Request(TokenURL,BodyURLEncoded)
    
    # Add headers to the http request 
    tokenreq.add_header('Authorization', 'Basic ' + base64.b64encode(bytes(client_id + ":" + client_secret, 'utf-8')).decode('utf-8'))
    tokenreq.add_header('Content-Type', 'application/x-www-form-urlencoded')
    
    try:
        # Fire off the http request
        tokenresponse = urllib.request.urlopen(tokenreq)
        
        # See what we got back.  If it's this part of  the code it was OK
        FullResponse = tokenresponse.read()
        
        # Need to pick out the tokens and return them
        ResponseJSON = json.loads(FullResponse.decode('utf-8'))
        
        # Put the keys into the json file
        fitbit_api_keys['access_token'] = str(ResponseJSON['access_token'])
        fitbit_api_keys['refresh_token'] = str(ResponseJSON['refresh_token'])
        fitbit_api_keys['last-refreshed'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Update the actual file 
        with open(KEYS_FILE, 'w') as outfile:
            json.dump(fitbit_api_keys, outfile)
        
        refresh_err = False
    except urllib.error.URLError as e:
        # Getting to this part of the code means we got an error
        # print(e.code)
        # print(e.read())
        # print('Error in getting new Fitbit access tokens.')
        refresh_err = True
        
    return refresh_err
