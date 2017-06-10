import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.style import use

# use('seaborn-dark')  #
# use('seaborn-bright')
# use('seaborn-paper')
# use('seaborn-pastel')  #
# use('grayscale')
# use('fivethirtyeight')  #
# use('seaborn-dark-palette')
# use('seaborn-whitegrid')
# use('seaborn-ticks')
# use('seaborn-colorblind')
# use('bmh')  #
# use('classic')
# use('seaborn-white')  #
# use('seaborn-talk')
# use('ggplot')  #
# use('seaborn-muted')
# use('dark_background')
# use('seaborn-notebook')
# use('seaborn-poster')
# use('seaborn-deep')
# use('seaborn-darkgrid')


NAME = 'test01'
path = './Data/{}/sentiment/custom_filtered/'.format(NAME)


class HistogramVisualizer:

    def __init__(self, path):
        files = [f for f in os.listdir(path=path) if f[-3:] == 'csv']
        names = np.array([f[:-4].split('-') for f in files])
        keywords = list(set(names[:, 0]))
        groups = list(set(names[:, 1]))
        self.path = path
        self.keywords = keywords
        self.groups = groups

        # self.COLORS =

    def load_data(self, keyword, group):
        path = self.path + '{}-{}.csv'.format(keyword, group)
        with open(file=path, mode='r') as f:
            data = [d.rstrip() for d in f.readlines()]
        df = pd.DataFrame([d.split(',') for d in data])
        df.columns = ['date', 'num_tweets', 'sent']
        df['date'] = pd.to_datetime(df['date'])
        df['num_tweets'] = pd.to_numeric(df['num_tweets'])
        df['sent'] = pd.to_numeric(df['sent'])
        return df

    def make_hist(self, keyword, num_bins=10, save_path=None):
        plt.clf()
        groups_sentiment = [
            self.load_data(keyword=keyword, group=group)['sent'].values
            for group in self.groups
        ]
        groups_weights = [np.ones_like(array) / array.shape[0]
                          for array in groups_sentiment]
        plt.hist(x=groups_sentiment,
                 bins=num_bins,
                 weights=groups_weights,
                 label=self.groups)
        plt.title(r"Keyword: {:s}".format(keyword),)# size=17)
        plt.ylabel(r"Proportion of tweets",)# size=17)
        plt.xlabel(r"Sentiment",)# size=17)
        plt.legend(loc=2,)# prop={'size': 13})
        if save_path:
            plt.savefig(filename=save_path)
        else:
            plt.show()


myHistogramVisualizer = HistogramVisualizer(path=path)
# myHistogramVisualizer.make_hist('trump', 6)


for style in plt.style.available:
    use(style)
    myHistogramVisualizer.make_hist(
        'clinton', 6, save_path='./style_examples/{:s}'.format(style))
