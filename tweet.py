#!/usr/bin/env python

# import urllib
import requests
from unidecode import unidecode
from requests_oauthlib import OAuth1
import time
import json

from config import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

def tweet_format(entry, t_co_len):
    ret = u'[' + unicode(entry['update_type']).capitalize() + u']'
    ret += u' ' + entry['title']
    ret += u' (' + entry['authors'] + u') '

    ret = unidecode(ret)  # the tweet package cannot input non-ascii msg
    ret = ret.replace('  ', ' ')  # what's wrong with the recent updates?
    ret = ret.replace('  ', ' ')

    if len(ret) > 280 - t_co_len - 2:  # -2 for extra space
        ret = ret[:(280 - t_co_len - 2 - 3)] + u'...'
    ret += u' https://ia.cr/' + unicode(entry['pub_id'])

    # assert len(ret) <= 280
    # assert len(ret) <= 280 + 31 - t_co_len
    # return urllib.quote(ret.replace('~', ' '))
    return ret.replace('~', ' ')
    # hope nobody uses ~ in his/her name and title
    # the twitter api will return 401 unautheroized error
    # if the string contains a ~ (even after URL encoding)

# def create_oauth_client():
#     new_client = OAuth1Session(
#         TWITTER_CONSUMER_KEY,
#         client_secret=TWITTER_CONSUMER_SECRET,
#         resource_owner_key=TWITTER_ACCESS_TOKEN,
#         resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET)

#     return new_client

def tweet(tweet_texts):
    consumer_key = CONSUMER_KEY
    consumer_secret = CONSUMER_SECRET
    access_token = ACCESS_TOKEN
    access_token_secret = ACCESS_TOKEN_SECRET
    short_url_length=23
    unfinished_entries = []
    
    auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)

    url = 'https://api.x.com/2/tweets'

    for tweet_text in reversed(tweet_texts):
	payload = {
            'text': tweet_format(tweet_text , short_url_length)
        }
        response = requests.post(url, auth=auth, json=payload, verify=False)
        if response.status_code == 401 and 'not authenticate' in response.text:
            # sometimes not stable (don't know why), just try it again
            print 1
            response = requests.post(url, auth=auth, json=payload)
        # if resp.status_code == 403 and 'duplicate' in resp.text:
        if response.status_code == 403:
            # report but continue to the next entry
            print('Failed to send tweet:', response.text)
            # sentry_client.captureMessage(
            #     'tweet err code ' + str(resp.status_code),
            #     extra={
            #         'status_code': resp.status_code,
            #         'error_text': resp.text,
            #         'current_entry': entry,
            #         'list_of_entries': list_entries
            #     }
            # )
            print 2
            continue

        if response.status_code == 201:
            print('Tweet sent successfully!',tweet_text)
            print('Tweet ID:', response.json()['data']['id'])
        else:
            # if it still doesn't work
            unfinished_entries.append(tweet_text)
            #print('Failed to send tweet:', response.text)
            #Be carefull ! print failed message, the response.headers have x-rate-limit-reset and so on.
            #print('Failed to send tweet:', response.text, response.headers, response.json())
            if response.status_code == 429:
                # Calculate retry time from `x-user-limit-24hour-reset` header
                retry_after = int(response.headers.get('x-user-limit-24hour-reset', 0)) - int(time.time())
                user_limit_24h = response.headers.get('x-user-limit-24hour-limit', 'Unknown')
                user_remaining_24h = response.headers.get('x-user-limit-24hour-remaining', 'Unknown')
                app_limit_24h = response.headers.get('x-app-limit-24hour-limit', 'Unknown')
                app_remaining_24h = response.headers.get('x-app-limit-24hour-remaining', 'Unknown')
                app_reset_24h = response.headers.get('x-app-limit-24hour-reset', 'Unknown')
                
                # Print details about the rate limit and retry timing
                print 'Failed to send tweet:', json.loads(response.text).get('detail', 'No detail provided')
                print '24-hour user limit:', user_limit_24h
                print 'Remaining requests in 24-hour window (user):', user_remaining_24h
                print '24-hour app limit:', app_limit_24h
                print 'Remaining requests in 24-hour window (app):', app_remaining_24h
                print 'App rate limit resets at:', app_reset_24h
                print 'Retry after {} seconds.'.format(retry_after)
                
                # Optionally, you can wait until the rate limit resets
                # time.sleep(retry_after)
            else:
                print 'Failed to send tweet:', response.text, response.status_code, response.reason
                #print(dir(response))
            print 3
        
    return unfinished_entries


if __name__ == '__main__':
    entries = [{
        'pub_id': '2013/562',
        'authors': u'Binglong Chen and Chang-An~Zhao',
        'update_type': 'new',
        'title': u'Self-pairings on supersingular elliptic curves'
                 + ' with embedding degree $three$'
    }#, {
     #   'authors': 'Pierre-Alain Fouque and Moon Sung Lee '
     #              + 'and Tancr\`ede Lepoint and Mehdi Tibouchi',
     #   'pub_id': u'2014/1024',
     #   'title': u'Cryptanalysis of the Co-ACD Assumption',
     #   'update_type': 'revised'
    #}
    ]
    tweet(entries)
