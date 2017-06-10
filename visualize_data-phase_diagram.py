import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.style import use
use('ggplot')


class NumTweetsMetric:

    def __init__(self, custom_filtered_path, base):
        custom_filtered_files = [f for f in os.listdir(
            path=custom_filtered_path) if f[-3:] == 'csv']
        names = np.array([f[:-4].split('-') for f in custom_filtered_files])
        keywords = list(set(names[:, 0]))
        groups = list(set(names[:, 1]))
        groups.pop(groups.index(base))
        self.custom_filtered_path = custom_filtered_path
        self.keywords = keywords
        self.groups = groups
        self.base = base

    def load_data(self, keyword, group):
        path = self.custom_filtered_path + '{}-{}.csv'.format(keyword, group)
        with open(file=path, mode='r') as f:
            data = [d.rstrip() for d in f.readlines()]
        df = pd.DataFrame([d.split(',') for d in data])
        df.columns = ['date', 'num_tweets', 'sent']
        df['date'] = pd.to_datetime(df['date'])
        df['num_tweets'] = pd.to_numeric(df['num_tweets'])
        df['sent'] = pd.to_numeric(df['sent'])
        return df

    def proportion(self, keyword, group):
        data = self.load_data(keyword=keyword, group=group)
        num_tweets_with_keyword = len(data)
        num_tweets = data['num_tweets'].iloc[-1]
        prop = num_tweets_with_keyword / num_tweets
        return prop

    def _l2(self, base, y):
        # assert len(x) == len(y), 'Distribuce musi mit stejnou velikost.'
        return np.sqrt(np.square((base - y))) / base

    def _conserve_sign(self, base, y):
        # return (base - y) / base
        # TODO: Jakym smerem?
        return (y - base) / base


    def _aitchison(self, base, y):
        # assert len(x) == len(y), 'Distribuce musi mit stejnou velikost.'
        return np.sqrt(np.square(np.log(base * (1 - y)) - np.log(y * (1 - base))))

    def measure(self, metric):
        if metric == 'L2':
            metric = self._l2
        elif metric == 'Aitchison':
            metric = self._aitchison
        elif metric == 'ConserveSign':
            metric = self._conserve_sign

        base = {key: self.proportion(keyword=key, group=self.base)
                for key in self.keywords}
        distances = {group: {key: 0 for key in self.keywords}
                     for group in self.groups}
        for group in self.groups:
            for key in self.keywords:
                prop = self.proportion(keyword=key, group=group)
                distances[group][key] = metric(base=base[key], y=prop)
                # TODO: tady predpokladam, ze metrika bude mit vzdy totozne
                #       argumenty
        return distances


class HistogramMetric:

    def __init__(self, twitter_filtered_path, base):
        twitter_filtered_files = [f for f in os.listdir(
            path=twitter_filtered_path) if f[-3:] == 'csv']
        names = np.array([f[:-4].split('-') for f in twitter_filtered_files])
        keywords = list(set(names[:, 0]))
        groups = list(set(names[:, 1]))
        groups.pop(groups.index(base))
        self.twitter_filtered_path = twitter_filtered_path
        self.keywords = keywords
        self.groups = groups
        self.base = base

    def load_data(self, keyword, group):
        path = self.twitter_filtered_path + '{}-{}.csv'.format(keyword, group)
        with open(file=path, mode='r') as f:
            data = [d.rstrip() for d in f.readlines()]
        df = pd.DataFrame([d.split(',') for d in data])
        df.columns = ['date', 'num_tweets', 'sent']
        df['date'] = pd.to_datetime(df['date'])
        df['num_tweets'] = pd.to_numeric(df['num_tweets'])
        df['sent'] = pd.to_numeric(df['sent'])
        return df

    def make_hist(self, keyword, group, num_bins=20):
        bins = [(1/num_bins) * i for i in range(1, num_bins+1)]
        df = self.load_data(keyword=keyword, group=group)
        weights = [1 / len(df) for _ in range(len(df))]
        hist_vals, _ = np.histogram(a=df['sent'], bins=bins, weights=weights)
        return hist_vals

    def _l2(self, base, y):
        assert len(base) == len(y), 'Distribuce musi mit stejnou velikost.'
        return np.linalg.norm(base - y)

    def _conserve_sign(self, base, y):
        assert len(base) == len(y), 'Distribuce musi mit stejnou velikost.'
        # TODO: Dava to smysl?
        # avg_base = np.average(a=np.linspace(start=0, stop=1, num=19), weights=base)
        # avg_y = np.average(a=np.linspace(start=0, stop=1, num=19), weights=y)
        # print(avg_base)
        # print(avg_y)
        # if avg_base > avg_y:
        #     sign = -1
        # else:
        #     sign = 1
        # return sign*np.sum(abs(base - y))
        return np.sum(y - base) / max(base)

    def _aitchison(self, base, y):
        assert len(base) == len(y), 'Distribuce musi mit stejnou velikost.'
        d = len(base)
        dist_sq = sum([(np.log(base[i] / base[j]) - np.log(y[i] / y[j]))**2
                       for i in range(d) for j in range(d)])
        dist = np.sqrt((1/(2*d))*dist_sq)
        return dist

    def measure(self, metric, num_bins=20):
        if metric == 'L2':
            metric = self._l2
        elif metric == 'Aitchison':
            metric = self._aitchison
        elif metric == 'ConserveSign':
            metric = self._conserve_sign

        base = {key: self.make_hist(keyword=key, group=self.base, num_bins=num_bins)
                for key in self.keywords}
        distances = {group: {key: 0 for key in self.keywords}
                     for group in self.groups}
        for group in self.groups:
            for key in self.keywords:
                hist = self.make_hist(keyword=key,
                                      group=group,
                                      num_bins=num_bins)
                distances[group][key] = metric(base=base[key], y=hist)
        return distances


def plot(num_tweets_dist, hist_dist, name, show=True):
    groups = list(num_tweets_dist.keys())
    keywords = list(num_tweets_dist[groups[0]].keys())
    for group in groups:
        for key in keywords:
            x1 = hist_dist[group][key]
            x2 = num_tweets_dist[group][key]
            plt.scatter([x1], [x2], marker='x', s=200, color='r', linewidth=5)
            plt.annotate('{}-{}'.format(key, group), (x1, x2), size=10)
    plt.ylabel('Proportion difference', size=20)
    plt.xlabel('Histogram difference', size=20)
    plt.xlim(0)
    plt.ylim(0)
    plt.title(name)
    if show:
        plt.show()


def visualize(name, base):
    curr_dir = os.getcwd()
    custom_filtered_path = '{}/Data/{}/sentiment/custom_filtered/'.format(curr_dir, name)
    twitter_filtered_path = '{}/Data/{}/sentiment/twitter_filtered/'.format(curr_dir, name)

    myNumTweetsMetric = NumTweetsMetric(custom_filtered_path=custom_filtered_path,
                                        base=base)
    num_tweets_dist_l = myNumTweetsMetric.measure('L2')
    num_tweets_dist_a = myNumTweetsMetric.measure('Aitchison')

    myHistogramMetric = HistogramMetric(twitter_filtered_path=twitter_filtered_path,
                                        base=base)
    hist_dist_l = myHistogramMetric.measure('L2', num_bins=20)
    hist_dist_a = myHistogramMetric.measure('Aitchison', num_bins=10)

    plt.subplot(1, 2, 1)
    plot(num_tweets_dist_l, hist_dist_l, name='L2 distance', show=False)
    plt.axis('equal')
    # plt.xlim(0)
    # plt.ylim(0)
    plt.subplot(1, 2, 2)
    plot(num_tweets_dist_a, hist_dist_a, name='Aitchison distance', show=False)
    plt.axis('equal')
    # plt.xlim(0)
    # plt.ylim(0)
    plt.tight_layout()
    plt.show()


def visualize2(name, base):
    curr_dir = os.getcwd()
    custom_filtered_path = '{}/Data/{}/sentiment/custom_filtered/'.format(curr_dir, name)
    twitter_filtered_path = '{}/Data/{}/sentiment/twitter_filtered/'.format(curr_dir, name)

    myNumTweetsMetric = NumTweetsMetric(custom_filtered_path=custom_filtered_path,
                                        base=base)
    num_tweets_dist = myNumTweetsMetric.measure('ConserveSign')

    myHistogramMetric = HistogramMetric(twitter_filtered_path=twitter_filtered_path,
                                        base=base)
    hist_dist = myHistogramMetric.measure('ConserveSign', num_bins=20)

    plt.axhline(y=0, color='k', linewidth=1.5)
    plt.axvline(x=0, color='k', linewidth=1.5)

    plot(num_tweets_dist, hist_dist, name='Conserve Sign', show=False)
    # plt.axis('equal')
    plt.tight_layout()
    plt.show()

BASE = 'Twitter'
NAME = 'test01'
# visualize(name=NAME, base=BASE)
visualize2(name=NAME, base=BASE)
