from argparse import ArgumentParser
from time import sleep
import os

import tweepy
from numpy.random import choice

import keys


def main():
    parser = ArgumentParser(description=('Script for random sampling followers'
                                         + 'of given groups.'))
    parser.add_argument('-g', '--groups',
                        help="List of group names.",
                        required=True)
    parser.add_argument('-d', '--directory',
                        help='Directory with data.',
                        required=True)
    parser.add_argument('-n', '--num_of_sampled_people',
                        help="Number of sampled people",
                        required=False,
                        default=50, type=int)
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

    save_folder = '{}/followers/'.format(args.directory)
    if not(os.path.exists(save_folder)):
        os.makedirs(name=save_folder)

    print('Looking for followers of the groups...')
    for group in groups:
        group_followers_path = '{}/followers/{}.txt'.format(
            args.directory, group)
        collect_followers(api=api,
                          person=group,
                          n=args.num_of_sampled_people,
                          out_path=group_followers_path)


def collect_followers(api, person, n, out_path):
    """
    Collects followers of the person, randomly samples n of them and saves
    the sampled.
    Parameters:
        api: authenticed twitter api
        person: ID or name of person to sample followers from
        n: number of people to sample from person's followers
        out_path: file to save followers
    """
    followers = api.followers_ids(person)
    sampled_followers = choice(a=followers, size=n, replace=False)
    try:
        f = open(file=out_path, mode='w')
        for s in sampled_followers:
            f.write(str(s) + ',')
        print('Successfully saved to:', out_path)
    except Exception as e:
        print("Can't write followers to file:", e)


if __name__ == '__main__':
    main()
