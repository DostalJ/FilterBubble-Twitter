# FilterBubble-Twitter
Software to study effects of filter bubble on Twitter.

### keys.py
To be able to use Twitter API, you have to make authentication (on this page). To be able to stream more than one stream at the time, you should make more than one authentication. The file has to have name ```keys.py``` and structure like this:
```
consumer_key = {1: 'XxXxXxXxXxXxXxXxXx',
                2: 'XxXxXxXxXxXxXxXxXx'}

consumer_secret = {1: 'XxXxXxXxXxXxXxXxXxXxXxXxXx',
                   2: 'XxXxXxXxXxXxXxXxXxXxXxXxXx'}

access_token = {1:'XxXxXxX-XxXxXxXxXxXxXxXxXxXxXxXxXx',
                2: 'XxXxXxX-XxXxXxXxXxXxXxXxXxXxXxXxXx'}

access_token_secret = {1: 'XxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx',
                       2: 'XxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx'}

```


### Streaming
Script ```stream.py``` helps with streaming tweets, measuring their sentiment and saving the data to file.
```
usage: stream.py [-h] -p PAGES -k KEYWORD [-n NUM_OF_STUDIED_PEOPLE]
                 [-api API]

Script for analyzing the content users sees on the Twitter.

optional arguments:
  -h, --help            show this help message and exit
  -p PAGES, --pages PAGES
                        List of page names.
  -k KEYWORD, --keyword KEYWORD
                        Keyword we are looking for.
  -n NUM_OF_STUDIED_PEOPLE, --num_of_studied_people NUM_OF_STUDIED_PEOPLE
                        Number of studied people
  -api API, --api API   The index of API authentication
```
