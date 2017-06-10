from tweepy import StreamListener, TweepError
import threading

import os
from os import environ
import tweepy
import keys
from time import sleep
from numpy.random import choice
from tools import Classifier, Filter
from datetime import datetime
from argparse import ArgumentParser

environ['TF_CPP_MIN_LOG_LEVEL'] = '2'



def main():

    parser = ArgumentParser(description=('Script for analyzing the content'
                                         + 'users sees on the Twitter.'))
    parser.add_argument('-g', '--groups',
                        help="List of group names.",
                        required=True)
    parser.add_argument('-k', '--keywords',
                        help="Keywords we are looking for.",
                        required=True)
    parser.add_argument('-l', '--language',
                        help='Language',
                        required=False,
                        default='en', type=str)
    parser.add_argument('-d', '--data_dir',
                        help='Directory with data.',
                        required=True)
    parser.add_argument('-api', '--api',
                        help='The index of API authentication',
                        required=False,
                        default=1, type=int)
    args = parser.parse_args()

    groups = args.groups.split(',')
    keywords = [key.replace('_', ' ')
                for key in args.keywords.split(',')]

    save_dirs = ['twitter_filtered', 'custom_filtered']
    for dir_ in save_dirs:
        if not(os.path.isdir('{}/sentiment/{}'.format(args.data_dir, dir_))):
            os.makedirs('{}/sentiment/{}'.format(args.data_dir, dir_))

    myTwitterStreamer_twitterFiltered = TwitterStreamer(api=args.api,
                                                        groups=groups,
                                                        keywords=keywords,
                                                        lang=args.language,
                                                        data_dir=args.data_dir,
                                                        save_dir=save_dirs[0])
    myTwitterStreamer_customFiltered = TwitterStreamer(api=args.api,
                                                       groups=groups,
                                                       keywords=keywords,
                                                       lang=args.language,
                                                       data_dir=args.data_dir,
                                                       save_dir=save_dirs[1])

    thread1 = threading.Thread(
        target=myTwitterStreamer_twitterFiltered.filter_stream_save)
    thread1.start()

    thread2 = threading.Thread(
        target=myTwitterStreamer_customFiltered.stream_filter_save)
    thread2.start()


class TwitterStreamer:
    def __init__(self, api, groups, keywords, lang, data_dir, save_dir):
        """
        Streames data from Twitter, analyzes them and saves them.
        """

        # authentication
        consumer_key = keys.consumer_key[api]
        consumer_secret = keys.consumer_secret[api]
        access_token = keys.access_token[api]
        access_token_secret = keys.access_token_secret[api]
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth,
                              wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True)
        self.keywords = keywords
        self.lang = lang
        self.data_dir = data_dir
        self.save_dir = save_dir

        people = dict()
        for group in groups:
            f = open('{}/followed/{}-followed.txt'.format(data_dir, group),
                     'r')
            followed_people = f.read().split(',')[:-1]
            f.close()
            people[group] = followed_people

        self.myStreamListener = MyStreamListener(people=people,
                                                 keywords=keywords,
                                                 data_dir=self.data_dir,
                                                 save_dir=self.save_dir)

    def _log(self, error, log_file):
        """
        Writes errors to the specified file.
        Parameters:
            error: key of the error
            log_file:
        """
        try:
            with open(log_file, 'a') as log_file:
                log_file.write(str(datetime.now()) + ': ' + str(error)+'\n')
        except Exception as e:
            print('Exception while writing log:', e)

    def stream_filter_save(self):
        myStream = tweepy.Stream(auth=self.api.auth,
                                 listener=self.myStreamListener)

        try:
            print('Streaming...')
            while True:
                try:
                    myStream.filter(track=['a'],
                                    languages=[self.lang],
                                    stall_warnings=True)
                except Exception as e:
                    self._log(error=e,
                              log_file='{}/sentiment/{}/log.log'.format(self.data_dir,
                                                                        self.save_dir))
                    pass
        except KeyboardInterrupt:
            print('\nDisconnecting...')
            pass

    def filter_stream_save(self):
        myStream = tweepy.Stream(auth=self.api.auth,
                                 listener=self.myStreamListener)

        try:
            print('Streaming...')
            while True:
                try:
                    myStream.filter(track=self.keywords,
                                    languages=[self.lang],
                                    stall_warnings=True)
                except Exception as e:
                    self._log(error=e,
                              log_file='{}/sentiment/{}/log.log'.format(self.data_dir,
                                                                        self.save_dir))
                    pass
        except KeyboardInterrupt:
            print('\nDisconnecting...')
            pass


class MyStreamListener(StreamListener, TweepError):
    def __init__(self, people, keywords, data_dir, save_dir):
        StreamListener.__init__(self)
        self.TwitterClassifier = Classifier('./classifier/HugeTwitter-classifier.h5',
                                            './classifier/HugeTwitter-vocabulary.pickle')
        self.myFilter = Filter(keywords=keywords, people=people)

        self.data_dir = data_dir
        self.save_dir = save_dir

        self.tweets_in_group = {group: 0 for group in people.keys()}

    def on_status(self, status):
        """
        Wraps default on_status method to measure sentiment and write to file.
        Prints errors.
        """
        in_groups, with_keywords = self.myFilter.filter(tweet=status)
        sent = self.TwitterClassifier.sentiment(status.text)[0, 0]
        for group in in_groups.keys():
            if in_groups[group]:
                self.tweets_in_group[group] += 1
                for keyword in with_keywords.keys():
                    if with_keywords[keyword]:
                        with open('{}/sentiment/{}/{}-{}.csv'.format(self.data_dir, self.save_dir, keyword, group), 'a') as out_file:
                            out_file.write(str(datetime.now()) + ',' + str(self.tweets_in_group[group]) + ',' + str(sent) + '\n')
                        with open('{}/sentiment/{}/{}-{}.txt'.format(self.data_dir, self.save_dir, keyword, group), 'a') as out_file:
                            out_file.write(status.text + '\n')

    def on_error(self, status_code):
        print('Error: ' + str(status_code))
        if status_code == 420:
            print('Sleeping for 1 min.')
            sleep(1*60)
        return False


if __name__ == '__main__':
    main()
