import argparse
import tweepy
import keys
from numpy.random import choice

def main():

    parser = argparse.ArgumentParser(description='This script collects all followers of the given person and randoly samples given number of them and writes to the file with given name.')
    parser.add_argument('-p','--person',
                        help="The main person. We are sampling from it's followers.",
                        required=True)
    parser.add_argument('-n','--number_of_people',
                        help="The number of people to sample from the 'person's followers.",
                        required=True, type=int)
    parser.add_argument('-o','--output_file',
                        help='File we are writing people IDs to.',
                        required=True)
    args = parser.parse_args()

    collectFollowers = CollectFollowers()
    collectFollowers.collect_and_save(person=args.person, n=args.number_of_people, out_path=args.output_file)


class CollectFollowers:
    def __init__(self):
        """Authenticate the Twitter API"""
        # authentication
        consumer_key = keys.consumer_key
        consumer_secret = keys.consumer_secret
        access_token = keys.access_token
        access_token_secret = keys.access_token_secret
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def collect_followers(self, person, n):
        """
        Collects followers of the person and randomly samples n of them
        Parameters:
            person: ID or name of person to sample followers from
            n: number of people to sample from person's followers
        Return:
            sampled_followers: list of followers ids
        """
        followers = self.api.followers_ids(person)
        sampled_followers = choice(a=followers, size=n, replace=False)
        return sampled_followers

    def save_to_txt(self, list_of_followers, file_path):
        """
        Writes list o followers to file.
        Parameters:
            list_of_followers: list of followers to write to file
            file_path: path to output file
        """
        try:
            f = open(file=file_path, mode='w')
            for s in list_of_followers:
                f.write(str(s)+',')
            print('Successfully saved to:', file_path)
        except Exception as e:
            print("Can't write followers to file:", e)

    def collect_and_save(self, person, n, out_path):
        """
        Collects followers of given person, randomly samples \'n\' of them and
        saves their IDs to given output file.
        Parameters:
            person: ID or name of person to sample followers from
            n: number of followers to sample
            out_path: file to write followers
        """
        followers = collectFollowers.collect_followers(person=person, n=n)
        collectFollowers.save_to_txt(list_of_followers=followers, file_path=out_path)


if __name__ == '__main__':
    main()
