import random, pandas

def getRandomLexiMessage():
    messages = pandas.read_csv(messages.csv)
    rand_message = messages['morning'].values(random.randint(0,len(messages)))
    return rand_message
