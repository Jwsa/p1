"""Visualizing Twitter Sentiment Across America"""

from data import word_sentiments, load_tweets
from datetime import datetime
from doctest import run_docstring_examples
from geo import us_states, geo_distance, make_position, longitude, latitude
from maps import draw_state, draw_name, draw_dot, wait, message
from string import ascii_letters
from ucb import main, trace, interact, log_current_line


# Phase 1: The Feelings in Tweets

def make_tweet(text, time, lat, lon):
    """Return a tweet, represented as a python dictionary.

    text      -- A string; the text of the tweet, all in lowercase
    time      -- A datetime object; the time that the tweet was posted
    latitude  -- A number; the latitude of the tweet's location
    longitude -- A number; the longitude of the tweet's location

    >>> t = make_tweet("just ate lunch", datetime(2012, 9, 24, 13), 38, 74)
    >>> tweet_words(t)
    ['just', 'ate', 'lunch']
    >>> tweet_time(t)
    datetime.datetime(2012, 9, 24, 13, 0)
    >>> p = tweet_location(t)
    >>> latitude(p)
    38
    """
    return {'text': text, 'time': time, 'latitude': lat, 'longitude': lon}

def tweet_words(tweet):
    """Return a list of the words in the text of a tweet."""
    aux = tweet['text']
    result = extract_words(aux) 
    
    return result
    
def tweet_time(tweet):
    """Return the datetime that represents when the tweet was posted."""
    return tweet['time']

def tweet_location(tweet):
    """Return a position (see geo.py) that represents the tweet's location.
    #Usei a função make_position do arquivo geo.py"""
    
    return make_position(tweet['latitude'], tweet['longitude'])
                

def tweet_string(tweet):
    """Return a string representing the tweet."""
    return '"{0}" @ {1}'.format(tweet['text'], tweet_location(tweet))

def extract_words(text):
    """Return the words in a tweet, not including punctuation.

    >>> extract_words('anything else.....not my job')
    ['anything', 'else', 'not', 'my', 'job']
    >>> extract_words('i love my job. #winning')
    ['i', 'love', 'my', 'job', 'winning']
    >>> extract_words('make justin # 1 by tweeting #vma #justinbieber :)')
    ['make', 'justin', 'by', 'tweeting', 'vma', 'justinbieber']
    >>> extract_words("paperclips! they're so awesome, cool, & useful!")
    ['paperclips', 'they', 're', 'so', 'awesome', 'cool', 'useful']
    """
    #peguei uma variavél auxiliar coloquei um string vazio
    #concatenei o "text" com um caractere especial "!" no final para que a condição funcionasse por completo" 
    aux = ''
    aux2 = []
    for x in text + "!" :
        if x in ascii_letters:
            aux = aux+x
        else:
            if aux != '':
                aux2.append(aux)
                aux = ''
    return aux2
    
def make_sentiment(value):
    """Return a sentiment, which represents a value that may not exist.

    >>> s = make_sentiment(0.2)
    >>> t = make_sentiment(None)
    >>> has_sentiment(s)
    True
    >>> has_sentiment(t)
    False
    >>> sentiment_value(s)
    0.2
    """
    #só precisei retornar o " value".
    assert value is None or (value >= -1 and value <= 1), 'Illegal value'
    return value

def has_sentiment(s): 
    """Return whether sentiment s has a value."""
    #Essa função e uma "pergunta" ela é feita pra checar se o valor inserido existe no banco de dados de sentimentos do programa.
    if s != None:
        if s >= -1 and s <= 1 :
            return True
        else:
            return False
    else:
        return False 

def sentiment_value(s):
    """Return the value of a sentiment s."""
    #eu só precisei retornar o "s" que é o valor em float do sentimento
    assert has_sentiment(s), 'No sentiment value'
    return s

def get_word_sentiment(word):
    """Return a sentiment representing the degree of positive or negative
    feeling in the given word, if word is not in the sentiment dictionary.

    >>> sentiment_value(get_word_sentiment('good'))
    0.875
    >>> sentiment_value(get_word_sentiment('bad'))
    -0.625
    >>> sentiment_value(get_word_sentiment('winning'))
    0.5
    >>> has_sentiment(get_word_sentiment('Berkeley'))
    False
    """
    return make_sentiment(word_sentiments.get(word, None))

def analyze_tweet_sentiment(tweet):
    """ Return a sentiment representing the degree of positive or negative
    sentiment in the given tweet, averaging over all the words in the tweet
    that have a sentiment value.

    If no words in the tweet have a sentiment value, return
    make_sentiment(None).

    >>> positive = make_tweet('i love my job. #winning', None, 0, 0)
    >>> round(sentiment_value(analyze_tweet_sentiment(positive)), 5)
    0.29167
    >>> negative = make_tweet("Thinking, 'I hate my job'", None, 0, 0)
    >>> sentiment_value(analyze_tweet_sentiment(negative))
    -0.25
    >>> no_sentiment = make_tweet("Go bears!", None, 0, 0)
    >>> has_sentiment(analyze_tweet_sentiment(no_sentiment))
    False
    """
    average = make_sentiment(None)#padrão
    valores = 0 #valor de cada palavra
    contador = 0 
    words = tweet_words(tweet) 
    key = False #chave de acesso a condição para retornar a média(average) das palavras
    

    for n in words:
        if has_sentiment(get_word_sentiment(n)):# chamei a função get_word_sentiment dentro da has_sentiment pois ele devolverar o valor de cada palavra se houver valor
            auxiliar_valores = get_word_sentiment(n)# variavel que guarda o valor de cada palavra
            valores += auxiliar_valores 
            contador += 1
            key = True

    if key == True:
        average = (valores/contador)#média

        return average

    else:
        return average


# Phase 2: The Geometry of Maps

def find_centroid(polygon):
    """Find the centroid of a polygon.

    http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon

    polygon -- A list of positions, in which the first and last are the same

    Returns: 3 numbers; centroid latitude, centroid longitude, and polygon area

    Hint: If a polygon has 0 area, return its first position as its centroid

    >>> p1, p2, p3 = make_position(1, 2), make_position(3, 4), make_position(5, 0)
    >>> triangle = [p1, p2, p3, p1]  # First vertex is also the last vertex
    >>> find_centroid(triangle)
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p3, p2, p1])
    (3.0, 2.0, 6.0)
    >>> find_centroid([p1, p2, p1])
    (1, 2, 0)
    """
    latitude = 0    #Formula1 = Centroide_X = (Xi + Xi+1)* ( Xi*Yi+ 1 - Xi+1*Yi)/(6 * area)
    longitude = 0   #Formula2 = Centroide_Y = (Yi + Yi+1)* ( Xi*Yi+ 1 - Xi+1*Yi)/(6 * area)
    area = 0        #Formula da area A = ( Xi*Yi+ 1 - Xi+1*Yi)/2
    n = 0           # um "Contador"
    while n < len(polygon) - 1:
        aux = (polygon[n][0] * polygon[n+1][1] - polygon[n+1][0] * polygon[n][1]) #variavel auxiliar para area 
        latitude += (polygon[n][0] + polygon[n+1][0]) * aux #aplicação Formula1
        longitude += (polygon[n][1] + polygon[n+1][1]) * aux #aplicação Formula2
        area += aux
        n += 1
    area = (area/2) #Aplicando formula da area 

    if area != 0: # se isso for verdade , good for you!
        latitude = latitude /(6 * area)
        longitude = longitude/(6 * area)
        
    else: #caso contrario as coordenadas estão wrong !
        latitude = polygon[0][0]
        longitude = polygon[0][1]
        area = int(0)
         
    return (latitude, longitude, abs(area))

        

def find_center(polygons):
    """Compute the geographic center of a state, averaged over its polygons.

    The center is the average position of centroids of the polygons in polygons,
    weighted by the area of those polygons.

    Arguments:
    polygons -- a list of polygons

    >>> ca = find_center(us_states['CA'])  # California
    >>> round(latitude(ca), 5)
    37.25389
    >>> round(longitude(ca), 5)
    -119.61439

    >>> hi = find_center(us_states['HI'])  # Hawaii
    >>> round(latitude(hi), 5)
    20.1489
    >>> round(longitude(hi), 5)
    -156.21763
    """
    #"""No caso de dois polígonos: 
    #P1=[(1,2),(3,4),(5,0),(1,2)]
    #P2=[(5,6),(7,8),(9,0),(5,6)]
    #Seus centróides seriam:
    #CentroideP1=(3.0, 2.0, 6.0)
    #CentroideP2= (7.0, 4.6, 10.0)
    #A latitude e a longitude do seu centro seria:
    #LatCentro= ((3.0*6)+(7.0*10))/(6+10)=5.5
    #LongiCentro=((2.0*6)+(4.6*10))/(6+10)=3.6"""
    
    latitude = 0
    longitude = 0
    area = 0
    for n in polygons:
        aux = find_centroid(n) #vai devolver uma lista
        area += aux[2] 
        latitude += aux[0] * aux[2]
        longitude += aux[1] * aux[2]
    latitude = latitude / area
    longitude = longitude / area
    return (latitude, longitude)

# Phase 3: The Mood of the Nation

def find_closest_state(tweet, state_centers):
    """Return the name of the state closest to the given tweet's location.

    Use the geo_distance function (already provided) to calculate distance
    in miles between two latitude-longitude positions.

    Arguments:
    tweet -- a tweet abstract data type
    state_centers -- a dictionary from state names to positions.

    >>> us_centers = {n: find_center(s) for n, s in us_states.items()}
    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> find_closest_state(sf, us_centers)
    'CA'
    >>> find_closest_state(ny, us_centers)
    'NJ'
    """
    #vou usar a função "geo_distance(x,y)" Retorna a distância do círculo (em milhas) entre duas Posições geográficas. geo.py

    tweet = tweet_location(tweet) #devolver a posição do tweet
    key = True

    for state in state_centers:
        distancia = geo_distance(tweet, state_centers[state]) #calcula a distancia entre a posição do tweet e do estado percorrido na lista 
        if key == True:
            menor_distancia = distancia # assume que essa é a menor distancia 
            closest_state = state        # assume que esse é o estado mais próximo
            key = False                  
        else:
            if menor_distancia > distancia:
                menor_distancia = distancia
                closest_state = state

    return closest_state

def group_tweets_by_state(tweets):
    """Return a dictionary that aggregates tweets by their nearest state center.

    The keys of the returned dictionary are state names, and the values are
    lists of tweets that appear closer to that state center than any other.

    tweets -- a sequence of tweet abstract data types

    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122) 
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> ca_tweets = group_tweets_by_state([sf, ny])['CA']
    >>> tweet_string(ca_tweets[0])
    '"Welcome to San Francisco" @ (38, -122)'
    """
    tweets_by_state = {}
    "*** YOUR CODE HERE***"
    us_centers = {n: find_center(s) for n, s in us_states.items()} #cria um dicionario que liga a chave "N :" ao centro de S onde n e s estão em "us_states.items()"

    for state in us_states:
        tweets_by_state[state] = [] # ele cria uma lista para cada state .
        
    for position in tweets:
        closest_state = find_closest_state(position, us_centers)
        tweets_by_state[closest_state].append(position)
 
    return tweets_by_state

def most_talkative_state(term): # retorna a sigla do estado que mais falou esse termo
    """Return the state that has the largest number of tweets containing term.

    >>> most_talkative_state('texas')
    'TX'
    >>> most_talkative_state('sandwich')
    'NJ'
    """
    tweets = load_tweets(make_tweet, term)  # A list of tweets containing term
    "*** YOUR CODE HERE ***"
    
    Tweets = group_tweets_by_state(tweets) #term mais falado
    largest = 0
    aux = ''
    for i in Tweets:
        if len(Tweets[i]) > largest:
            largest = len(Tweets[i])
            aux = i
    return(aux)
def average_sentiments(tweets_by_state):
    """Calculate the average sentiment of the states by averaging over all
    the tweets from each state. Return the result as a dictionary from state
    names to average sentiment values (numbers).

    If a state has no tweets with sentiment values, leave it out of the
    dictionary entirely.  Do NOT include states with no tweets, or with tweets
    that have no sentiment, as 0.  0 represents neutral sentiment, not unknown
    sentiment.

    tweets_by_state -- A dictionary from state names to lists of tweets
    """
    averaged_state_sentiments = {}
    aux = ''
    for x in tweets_by_state:
        contador = 0
        sentiments = 0
        for y in tweets_by_state[x]:           
           aux = analyze_tweet_sentiment(y)
           if aux != None:
               contador = contador + 1
               sentiments = sentiments + aux
               
        if contador != 0:    
            averaged_state_sentiments[x] = (sentiments / contador)    
    return averaged_state_sentiments


# Phase 4: Into the Fourth Dimension

def group_tweets_by_hour(tweets):
    """Return a dictionary that groups tweets by the hour they were posted.

    The keys of the returned dictionary are the integers 0 through 23.

    The values are lists of tweets, where tweets_by_hour[i] is the list of all
    tweets that were posted between hour i and hour i + 1. Hour 0 refers to
    midnight, while hour 23 refers to 11:00PM.

    To get started, read the Python Library documentation for datetime objects:
    http://docs.python.org/py3k/library/datetime.html#datetime.datetime

    tweets -- A list of tweets to be grouped
    """
    tweets_by_hour = {}
    for x in range(24): #chaves do dicionário 
        tweets_by_hour[x] = []
    for t in tweets: #tweets horas
        hora = t['time']
        tweets_by_hour[hora.hour].append(t)       
    return tweets_by_hour
    


# Interaction.  You don't need to read this section of the program.

def print_sentiment(text='Are you virtuous or verminous?'):
    """Print the words in text, annotated by their sentiment scores."""
    words = extract_words(text.lower())
    assert words, 'No words extracted from "' + text + '"'
    layout = '{0:>' + str(len(max(words, key=len))) + '}: {1:+}'
    for word in extract_words(text.lower()):
        s = get_word_sentiment(word)
        if has_sentiment(s):
            print(layout.format(word, sentiment_value(s)))

def draw_centered_map(center_state='TX', n=10):
    """Draw the n states closest to center_state."""
    us_centers = {n: find_center(s) for n, s in us_states.items()}
    center = us_centers[center_state.upper()]
    dist_from_center = lambda name: geo_distance(center, us_centers[name])
    for name in sorted(us_states.keys(), key=dist_from_center)[:int(n)]:
        draw_state(us_states[name])
        draw_name(name, us_centers[name])
    draw_dot(center, 1, 10)  # Mark the center state with a red dot
    wait()

def draw_state_sentiments(state_sentiments={}):
    """Draw all U.S. states in colors corresponding to their sentiment value.

    Unknown state names are ignored; states without values are colored grey.

    state_sentiments -- A dictionary from state strings to sentiment values
    """
    for name, shapes in us_states.items():
        sentiment = state_sentiments.get(name, None)
        draw_state(shapes, sentiment)
    for name, shapes in us_states.items():
        center = find_center(shapes)
        if center is not None:
            draw_name(name, center)

def draw_map_for_term(term='my job'):
    """Draw the sentiment map corresponding to the tweets that contain term.

    Some term suggestions:
    New York, Texas, sandwich, my life, justinbieber
    """
    tweets = load_tweets(make_tweet, term)
    tweets_by_state = group_tweets_by_state(tweets)
    state_sentiments = average_sentiments(tweets_by_state)
    draw_state_sentiments(state_sentiments)
    for tweet in tweets:
        s = analyze_tweet_sentiment(tweet)
        if has_sentiment(s):
            draw_dot(tweet_location(tweet), sentiment_value(s))
    wait()

def draw_map_by_hour(term='my job', pause=0.5):
    """Draw the sentiment map for tweets that match term, for each hour."""
    tweets = load_tweets(make_tweet, term)
    tweets_by_hour = group_tweets_by_hour(tweets)

    for hour in range(24):
        current_tweets = tweets_by_hour.get(hour, [])
        tweets_by_state = group_tweets_by_state(current_tweets)
        state_sentiments = average_sentiments(tweets_by_state)
        draw_state_sentiments(state_sentiments)
        message("{0:02}:00-{0:02}:59".format(hour))
        wait(pause)

def run_doctests(names):
    """Run verbose doctests for all functions in space-separated names."""
    g = globals()
    errors = []
    for name in names.split():
        if name not in g:
            print("No function named " + name)
        else:
            if run_docstring_examples(g[name], g, True) is not None:
                errors.append(name)
    if len(errors) == 0:
        print("Test passed.")
    else:
        print("Error(s) found in: " + ', '.join(errors))

@main
def run(*args):
    """Read command-line arguments and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Run Trends")
    parser.add_argument('--print_sentiment', '-p', action='store_true')
    parser.add_argument('--run_doctests', '-t', action='store_true')
    parser.add_argument('--draw_centered_map', '-d', action='store_true')
    parser.add_argument('--draw_map_for_term', '-m', action='store_true')
    parser.add_argument('--draw_map_by_hour', '-b', action='store_true')
    parser.add_argument('text', metavar='T', type=str, nargs='*',
                        help='Text to process')
    args = parser.parse_args()
    for name, execute in args.__dict__.items():
        if name != 'text' and execute:
            globals()[name](' '.join(args.text))

