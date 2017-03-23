from tweepy import StreamListener, TweepError
from http.client import IncompleteRead
import tensorflow as tf
import tweepy
import keys
from keras.models import load_model
from tools import Vocabulary
from pickle import load
from keras.preprocessing import sequence
import argparse
import time
from datetime import datetime


def main():

    parser = argparse.ArgumentParser(description='This script streams content that given users see and saves sentiment for every post with one of given keywords that given users might see.')
    parser.add_argument('-k','--keywords',
                        help="Keywords the script will look for in the stream.",
                        required=True)
    parser.add_argument('-o','--output_file',
                        help='File we are writing sentiment to.',
                        required=True)
    parser.add_argument('-p','--people',
                        help="Path to file with ids (delimited by comma). The script will stream what everything these users might see. If not given, whole Twitter is streamed.",
                        required=False)
    parser.add_argument('-l', '--log',
                        help='Type of logging. 0 for no logging, 1 for logging to terminal, path/to/log/file to write logs to file',
                        required=False, type=str, default='1')
    parser.add_argument('-api', '--api',
                        help='The index of API authentication',
                        required=False, type=int, default=1)
    parser.add_argument('-f', '--filter_level',
                        help="Level of filtering the tweets from stream according to their popularity (the preferential algorithms measures the popularity of tweets). For more tweets use \'low\', for stricter filtering (default) use \'medium\'.",
                        required=False, type=str, default='medium')
    parser.add_argument('-lang', '--languages',
                        help="Possible languages of the tweets. Default is \'en\'.",
                        required=False, type=str, default='en')
    args = parser.parse_args()

    if args.people == None:
        people = None
    else:
        try:
            f = open(file=args.people, mode='r')
            people = f.read().split(',')[:-1] # [:-1] (vse az na posledni prvek) je to tu proto, ze posledni prvek je prazdny string
            f.close()
        except Exception as e:
            print("Can't load file with people to follow:", e)

    keywords = args.keywords.split(',')
    languages = args.languages.split(',')

    print('Preparing streaming...')
    TA = TwitterAnalyzer(people=people, keywords=keywords, api=args.api, log=args.log, filter_level=args.filter_level, languages=languages)
    TA.stream_analyze_save(out_path=args.output_file)


class Classifier:
    def __init__(self, classifier_path, vocabulary_path):
        """
        Class that uses saved keras classifier to measure sentiment of tweets.
        Parameters:
            classifier_path: path to saved classifier in .h5 keras format
            vocabulary_path: path to vocabulary saved in .pickle format
        """
        try:
            self.classifier = load_model(filepath=classifier_path)
            self.graph = tf.get_default_graph()
            print('Classifier successfuly loaded.')
        except Exception as e:
            print('-'*30)
            raise Exception('Failed in loading classifier:', e)
            print('-'*30)

        self.Vocabulary = Vocabulary(vocabulary_file=vocabulary_path)
    def sentiment(self, sentence):
        num_sent = self.Vocabulary.to_num(sentence)
        num_sent = sequence.pad_sequences([num_sent], maxlen=140) # doplnit, nebo ustrihnout
        global graph
        with self.graph.as_default():
            sentiment = self.classifier.predict(num_sent)
        return sentiment


class MyStreamListener(StreamListener, TweepError):
    def __init__(self, out_path):
        """
        Wraps default tweepy\'s StreamListener and uses it to measure sentiment
        of and save tweets
        Parameters:
            out_path: path to save sentiment and time to
        """
        StreamListener.__init__(self)
        self.out_path = out_path
        self.TwitterClassifier = Classifier('./classifier/HugeTwitter-classifier.h5', './classifier/HugeTwitter-vocabulary.pickle')

    def on_status(self, status):
        """
        Wraps default on_status method to measure sentiment and write to file.
        Prints errors.
        """
        try:
            sent = self.TwitterClassifier.sentiment(status.text)[0,0]
            with open(self.out_path, 'a') as out_file:
                out_file.write(str(datetime.now()) + ',' + str(sent)+'\n')
        except TweepError:
            print('Error: ' + str(status_code) + '\n')
            return False

    def on_error(self, status_code):
        """
        Handles 420 error. Sleeps for 5 minutes to avoid restrictions from
        Twitter API servise.
        """
        print('Error: ' + str(status_code) + '\n')
        if status_code == 420:
            time.sleep(5*60)
            print('Retrying...')
        return False

class TwitterAnalyzer:
    def __init__(self, people, keywords, api, log, filter_level, languages):
        """
        Streams and analyzes data from twitter.
        Parameters:
            people: file with people we are studying
            keywords: keywords to look for
            api: (int) keys of API codes saved in file keys.py
            log: type of logging. 0 for no logging, 1 for logging to terminal,
                 path/to/log/file to write logs to file
            filter_level: Level of filtering the tweets from stream according to
                          their popularity (the preferential algorithms measures
                          the popularity of tweets). For more tweets use \'low\',
                          for stricter filtering use \'medium\'.
            languages: List of possible languages of the tweets.

        """
        # authentication
        consumer_key = keys.consumer_key[api]
        consumer_secret = keys.consumer_secret[api]
        access_token = keys.access_token[api]
        access_token_secret = keys.access_token_secret[api]

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

        if people == None:
            self.ids = None
        else:
            self.ids = self._filter_by_friends(people)

        self.keywords = keywords
        self.log = log
        self.filter_level = filter_level
        self.languages = languages


    def _filter_by_friends(self, people):
        """
        Takes file with people and returns union of people they are following.
        Parameters:
            people: file with people
        """
        ids = set()
        for node in people:
            try: # some users are protected
                friends_of_node = self.api.friends_ids(node)
                ids = ids.union(friends_of_node)
            except TweepError:
                pass
        ids = [str(_id) for _id in ids]
        return ids

    def _log(self, e, log):
        """
        Logs errors.
        Parameters:
            e: key of the error
            log: type of logging
        """
        if log == '0':
            pass
        elif log == '1':
            print('Exception:', e)
            print('Retrying...')
        else:
            try:
                with open(log, 'a') as log_file:
                    log_file.write(str(datetime.now()) + ',' + str(e)+'\n')
            except Exception as e:
                print('Exception while writing log:', e)

    def stream_analyze_save(self, out_path):
        """
        Streams the tweets and saves its sentiment with time to file.
        Parameters:
            out_path: file to write sentiment
        """
        myStreamListener = MyStreamListener(out_path)
        myStream = tweepy.Stream(auth=self.api.auth, listener=myStreamListener)
        print('Streaming...')
        stop = False
        while True:
            try:
                if self.ids == None:
                    myStream.filter(track=self.keywords, languages=self.languages, filter_level=self.filter_level)
                else:
                    myStream.filter(track=self.keywords, follow=self.ids, languages=self.languages, filter_level=self.filter_level)
            except KeyboardInterrupt:
                stop = True
            except Exception as e:
                self._log(e=e, log=self.log)
                pass
            if stop:
                print('Disconnecting.')
                myStream.disconnect()
                break

if __name__ == '__main__':
    main()
