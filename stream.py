from tweepy import StreamListener, TweepError
import os
import tweepy
import keys
from time import sleep
from numpy.random import choice
from tools import Classifier
from datetime import datetime
from argparse import ArgumentParser


def main():

    parser = ArgumentParser(description='Script for analyzing the content users sees on the Twitter.')
    parser.add_argument('-p','--pages', help="List of page names.", required=True)
    parser.add_argument('-k','--keyword', help="Keyword we are looking for.",required=True)
    parser.add_argument('-n', '--num_of_studied_people', help="Number of studied people", required=False, default=50, type=int)
    parser.add_argument('-api', '--api', help='The index of API authentication', required=False, default=1, type=int)
    args = parser.parse_args()

    myTwitterStreamer = TwitterStreamer(args.api)

    pages = args.pages.split(',')

    print('Looking for followers of the pages...')
    for page in pages:
        page_followers_path = './Data/people/' + page + '.txt'
        if not(os.path.isfile(page_followers_path)):
            myTwitterStreamer.collect_followers(person=page, n=args.num_of_studied_people, out_path=page_followers_path)

    print('Looking for people followed by studied people...')
    for page in pages:
        followed_path = './Data/followed/' + page + '-followed.txt'
        if not(os.path.isfile(followed_path)):
            f = open('./Data/people/{}.txt'.format(page), 'r')
            following_people = f.read().split(',')[:-1]
            f.close()
            myTwitterStreamer.save_followed(people=following_people, file_path=followed_path)

    followed = dict()
    for page in pages:
        f = open('./Data/followed/{}-followed.txt'.format(page), 'r')
        followed_people = f.read().split(',')[:-1]
        f.close()
        followed[page] = followed_people

    print('Streaming...')
    myTwitterStreamer.stream(followed=followed, keyword=args.keyword)



class MyStreamListener(StreamListener, TweepError):
    def __init__(self, followed, keyword):
        StreamListener.__init__(self)
        self.TwitterClassifier = Classifier('./classifier/HugeTwitter-classifier.h5', './classifier/HugeTwitter-vocabulary.pickle')

        self.followed = followed
        self.pages = list(followed.keys())
        self.keyword = keyword

    def on_status(self, status):
        """
        Wraps default on_status method to measure sentiment and write to file.
        Prints errors.
        """
        sent = self.TwitterClassifier.sentiment(status.text)[0,0]
        for page in self.pages:
            if str(status.user.id) in self.followed[page]:
                with open('./Data/sentiment/{}-{}.csv'.format(self.keyword, page), 'a') as out_file:
                    out_file.write(str(datetime.now()) + ',' + str(sent) + '\n')
                with open('./Data/sentiment/{}-{}.txt'.format(self.keyword, page), 'a') as out_file:
                    out_file.write(status.text + '\n')


    def on_error(self, status_code):
        print('Error: ' + str(status_code))
        if status_code == 420:
            print('Sleeping for 1 min.')
            sleep(1*60)
        return False




class TwitterStreamer:
    def __init__(self, api):
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
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def load_people(self, page):
        try:
            f = open(file='./Data/people/{}.txt'.format(page), mode='r')
            people = f.read().split(',')[:-1] # [:-1] (vse az na posledni prvek) je to tu proto, ze posledni prvek je prazdny string
            f.close()
        except Exception as e:
            print("Can't load file with people to follow:", e)
        return people

    def save_followed(self, people, file_path):
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
                sleep(30)
            except TweepError:
                print('Error while loading friends.')
                pass
        ids = [str(_id) for _id in ids]
        f = open(file=file_path, mode='w')
        for node_id in ids:
            f.write(str(node_id)+',')
        f.close()
        print('Successfully saved to:', file_path)

    def collect_followers(self, person, n, out_path):
        """
        Collects followers of the person, randomly samples n of them and saves the sampled.
        Parameters:
            person: ID or name of person to sample followers from
            n: number of people to sample from person's followers
            out_path: file to save followers
        """
        followers = self.api.followers_ids(person)
        sampled_followers = choice(a=followers, size=n, replace=False)
        try:
            f = open(file=out_path, mode='w')
            for s in sampled_followers:
                f.write(str(s)+',')
            print('Successfully saved to:', out_path)
        except Exception as e:
            print("Can't write followers to file:", e)

    def _log(self, error, log_file):
        """
        Writes errors to the specified file.
        Parameters:
            error: key of the error
            log_file:
        """
        try:
            with open(log_file, 'a') as log_file:
                log_file.write(str(datetime.now()) + ',' + str(error)+'\n')
        except Exception as e:
            print('Exception while writing log:', e)

    def stream(self, followed, keyword):

        myStreamListener = MyStreamListener(followed=followed, keyword=keyword)
        myStream = tweepy.Stream(auth=self.api.auth, listener=myStreamListener)

        try:
            while True:
                try:
                    myStream.filter(track=[keyword])
                except Exception as e:
                    self._log(error=e, log_file='./Data/sentiment/{}.log'.format(keyword))
                    pass
        except KeyboardInterrupt:
            print('Disconnecting...')
            pass


if __name__ == '__main__':
    main()
