from argparse import ArgumentParser
from time import sleep

import tweepy
from numpy.random import randint, random
from tweepy import TweepError

import keys


def main():
    parser = ArgumentParser(
        description='Script for random sampling twitter users.')
    parser.add_argument('-n', '--num_of_sampled_people',
                        help="Number of sampled people",
                        required=False,
                        default=100, type=int)
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

    random_sample(api=api, out_file='{}/followers/Twitter.txt'.format(
        args.directory), num_samples=args.num_of_sampled_people)


def random_sample(api, out_file, num_samples=100,
                  lower_bound1=1, upper_bound1=5 * 10**9,
                  lower_bound2=7 * 10**17, upper_bound2=8.6 * 10**17):
    random_users = 0
    while (random_users < num_samples):
        if random() < 0.5:
            rnd_index = randint(low=lower_bound1, high=upper_bound1)
        else:
            rnd_index = randint(low=lower_bound2, high=upper_bound2)

        try:
            api.get_user(rnd_index)
            with open(out_file, 'a') as f:
                f.write(str(rnd_index) + ',')
            random_users += 1
        except TweepError:
            pass
        sleep(1)
    print('Successfully saved {:d} random users to: {}'.format(
        num_samples, out_file))


if __name__ == '__main__':
    main()
