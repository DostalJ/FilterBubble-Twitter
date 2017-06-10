import os
from argparse import ArgumentParser
from time import sleep

import tweepy
from numpy.random import choice
from tweepy import TweepError

import keys


def main():
    parser = ArgumentParser(description=('Script for random sampling followers'
                                         + 'of given groups.'))
    parser.add_argument('-g', '--groups',
                        help="List of group names.",
                        required=True)
    parser.add_argument('-t', '--sleep_time',
                        help=("Time to sleep betweet retrieving people"
                              + "followed by a user. Higher the value the less"
                              + "probable is blocked api by Twitter."),
                        required=False,
                        default=60, type=int)
    parser.add_argument('-d', '--directory',
                        help='Directory with data.',
                        required=True)
    parser.add_argument('-api', '--api',
                        help='The index of API authentication',
                        required=False,
                        default=1, type=int)
    args = parser.parse_args()

    consumer_key = keys.consumer_key[args.api]
    consumer_secret = keys.consumer_secret[args.api]
    access_token = keys.access_token[args.api]
    access_token_secret = keys.access_token_secret[args.api]
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,
                     wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)

    groups = args.groups.split(',')

    save_folder = '{}/followed/'.format(args.directory)
    if not(os.path.exists(save_folder)):
        os.makedirs(name=save_folder)

    print('Looking for people followed by studied people...')
    for group in groups:
        followed_path = args.directory + '/followed/' + group + '-followed.txt'
        f = open('{}/followers/{}.txt'.format(args.directory, group), 'r')
        following_people = f.read().split(',')[:-1]
        f.close()
        save_followed(api=api,
                      people=following_people,
                      file_path=followed_path,
                      sleep_time=args.sleep_time)


def save_followed(api, people, file_path, sleep_time=30):
    """
    Takes file with people and returns union of people they are following.
    Parameters:
        people: file with people
    """
    ids = set()
    for node in people:
        try:  # some users are protected
            friends_of_node = api.friends_ids(node)
            ids = ids.union(friends_of_node)
            sleep(sleep_time)
        except TweepError:
            print('Error while loading friends.')
            pass
    ids = [str(_id) for _id in ids]
    f = open(file=file_path, mode='w')
    for node_id in ids:
        f.write(str(node_id) + ',')
    f.close()
    print('Successfully {:d} saved to:'.format(len(ids)), file_path)


if __name__ == '__main__':
    main()
