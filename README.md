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

### Collecting followers
Script ```collect_followers.py``` helps with collecting followers of given user.
Usage:
```
usage: collect_followers.py [-h] -p PERSON -n NUMBER_OF_PEOPLE -o OUTPUT_FILE

This script collects all followers of the given person and randoly samples
given number of them and writes to the file with given name.

optional arguments:
  -h, --help            show this help message and exit
  -p PERSON, --person PERSON
                        The main person. We are sampling from it's followers.
  -n NUMBER_OF_PEOPLE, --number_of_people NUMBER_OF_PEOPLE
                        The number of people to sample from the 'person's
                        followers.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        File we are writing people IDs to.
```

### Streaming
Script ```stream.py``` helps with streaming tweets, measuring their sentiment and savig the data to file.
```
usage: stream.py [-h] -k KEYWORDS -o OUTPUT_FILE [-p PEOPLE] [-l LOG]
                 [-api API] [-f FILTER_LEVEL] [-lang LANGUAGES]

This script streams content that given users see and saves sentiment for every
post with one of given keywords that given users might see.

optional arguments:
  -h, --help            show this help message and exit
  -k KEYWORDS, --keywords KEYWORDS
                        Keywords the script will look for in the stream.
  -o OUTPUT_FILE, --output_file OUTPUT_FILE
                        File we are writing sentiment to.
  -p PEOPLE, --people PEOPLE
                        Path to file with ids (delimited by comma). The script
                        will stream what everything these users might see. If
                        not given, whole Twitter is streamed.
  -l LOG, --log LOG     Type of logging. 0 for no logging, 1 for logging to
                        terminal, path/to/log/file to write logs to file
  -api API, --api API   The index of API authentication
  -f FILTER_LEVEL, --filter_level FILTER_LEVEL
                        Level of filtering the tweets from stream according to
                        their popularity (the preferential algorithms measures
                        the popularity of tweets). For more tweets use 'low',
                        for stricter filtering (default) use 'medium'.
  -lang LANGUAGES, --languages LANGUAGES
                        Possible languages of the tweets. Default is 'en'.
```
