
data_path = 'Sentiment_Analysis_Dataset.csv'

try:
    data_file = open(data_path, 'r', encoding='utf=8').readlines()
    print('Data file successfully loaded')
except Exception as e:
    print("Can't load data file:", e)

positive = []
negative = []


# ItemID, Sentiment, SentimentSource, SentimentText
for line in data_file:
    line = line.split(',')
    sentiment = line[1] # sentiment column

    # mohli jsme omylem rozdelit i text na nekolik casti (pokud v nem byla ',')
    text_list = line[3:]
    text = ""
    for part in text_list:
        text += part
    text = text.strip(" \'\"") # ocesame od zbytecnosti

    if sentiment == '1':
        positive.append(text)
    elif sentiment == '0':
        negative.append(text)

print('Positive samples:', len(positive))
print('Negative samples:', len(negative))

pos_path = 'positive.txt'
neg_path = 'negative.txt'

try:
    pos_file = open(pos_path, 'w')
    pos_file.write("".join(positive))
    pos_file.close()

    neg_file = open(neg_path, 'w')
    neg_file.write("".join(negative))
    neg_file.close()

    print("Data successfully saved.")
except Exception as e:
    print("Can't save the data:", e)
