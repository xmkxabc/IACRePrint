#!/usr/bin/env python

import requests

from tweet import tweet
from storage import Storage
from config import HTTP_HEADERS
from paperscraper import PaperScraper
from datetime import datetime

# @sentry_client.capture_exceptions
def main():
#    now = datetime.now()
#    print("the time: ", now)
    resp = requests.get(
        'https://eprint.iacr.org/rss/atom.xml',
        headers=HTTP_HEADERS
    )

    if resp.status_code != 200:
        msg = 'request failed: ' + str(resp.status_code) \
            + '\n\n' + resp.text
        raise Exception(msg)
        
    # my_parser = EPrintParser()
    # curr_list = my_parser.feed(resp.text)

    scraper = PaperScraper('https://eprint.iacr.org/rss/atom.xml')
    curr_list = scraper.parse_data()
#    now = datetime.now()
#    print("the time: ", now)
    if curr_list is None \
            or not isinstance(curr_list, list) \
            or len(curr_list) < 20:
        # in case the crawled page has problems
        return

    my_storage = Storage()
    prev_list = my_storage.retrieve()
    if prev_list is None \
            or not isinstance(prev_list, list) \
            or len(prev_list) == 0:
        my_storage.save(curr_list)
#        now = datetime.now()
#        print("the time: ", now)
    else:
        # sentry_client.user_context({
        #     'prev_list': prev_list,
        #     'curr_list': curr_list,
        # })
        list_updated = [i for i in curr_list if i not in prev_list]
        if len(list_updated):
            list_untweeted = tweet(list_updated)
            list_to_save = [i for i in curr_list if i not in list_untweeted]
            my_storage.save(list_to_save)
    now = datetime.now()
    print("the time: ", now.strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == '__main__':
    main()
