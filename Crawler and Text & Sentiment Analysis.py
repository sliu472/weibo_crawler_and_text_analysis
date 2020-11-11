import jieba
import requests
from pyquery import PyQuery as pq
import time
from urllib.parse import quote
import csv
import random
import numpy as np
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import matplotlib.pyplot as plt
from collections import Counter
from snownlp import SnowNLP


def get_page(page):

    # quote() to encode and pass the chinese character to url

    url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D' + quote(
        m) + '&page_type=searchall&page=' + str(page)

    headers = {
        'Host': 'm.weibo.cn',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            if page%10 == 0:
                print('%dth page fetched' % page)
            return response.json()
    except requests.ConnectionError as e:
        print('Error', e.args)


def parse_group(json):
    groups = json.get('card_group')
    count = 0
    if groups is None:
        items = json.get('mblog')
        count += 1
        return items
    else:
        for group in groups:
            items = group.get('mblog')
            count += 1
            return items


def parse_page(json):
    if json:
        items = json.get('data').get('cards')
        for i in items:
            item = parse_group(i)
            if item is None:
                # print('none')
                continue

            # longText to be explored
            # print(weibo['longText'])

            weibo = {}
            weibo['id'] = item.get('id')
            weibo['text'] = pq(item.get('text')).text()
            weibo['name'] = item.get('user').get('screen_name')
            weibo['attitudes'] = item.get('attitudes_count')
            weibo['comments'] = item.get('comments_count')
            weibo['reposts'] = item.get('reposts_count')
            weibo['time'] = item.get('created_at')
            yield weibo


def save_csv(filepath, results, page):

    # without encoding='utf-8-sig' chinese character won't display correctly
    with open(filepath, 'a', encoding='utf-8-sig', newline='') as f:
        fieldnames = ['id', 'text', 'name', 'attitudes', 'comments', 'reposts', 'time']
        writer = csv.writer(f, delimiter=',')
        if page == 1:
            writer.writerow(fieldnames)
        csvdatas = []
        for result in results:
            csvdata = [result['id'], result['text'], result['name'],
                       result['attitudes'], result['comments'], result['reposts'],
                       result['time']]
            csvdatas.append(csvdata)

        writer.writerows(csvdatas)


def read_csv(filepath):
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        comments = [row[1] for row in reader]
        return comments


def word_cloud(comments):
    comment_text = jieba.cut(''.join(comments[1:]))
    comment_text = ' '.join(comment_text)

    # set stopwords
    stopwords = set(STOPWORDS)
    stopwords.add('全文')
    stopwords.add('微博')
    stopwords.add('视频')

    # count frequent words
    c = Counter()  # produce a tuple (value: count)
    for x in comment_text.split():  # to count word freq, must split the text
        if len(x)>1 and x != '\r\n':
            c[x] += 1
    print('word freq: ')
    for (k, v) in c.most_common(20):
        print('%s: %d' % (k, v))

    # make wordcloud
    mask = np.array(Image.open('1.jpeg'))
    wc = WordCloud(font_path='/Applications/anaconda3/lib/python3.7/site-packages/wordcloud/simhei.ttf',
                   background_color='white', max_words=200, stopwords=stopwords,
                   width=561, height=800, mask=mask).generate(comment_text)

    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.show()
    plt.pause(.2)
    plt.close()
    wc.to_file('worcloud_%s.png' % m)


def sentiment_analyze(text):
    sentiments_list = []
    for i in text:
        try:
            s = SnowNLP(i)
            sentiments_list.append(s.sentiments)
        except:
            print('something wrong with the %dth comment' % len(sentiments_list))

    # turn sentiment coef to [-0.5, 0.5] for visualization
    res = []
    for i in range(0, len(sentiments_list)):
        res.append(sentiments_list[i]-0.5)

    # visualize sentiments
    fig = plt.figure()
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)

    ax1.hist(res, bins=np.arange(-0.5, 0.5, 0.01))
    ax1.set_xlabel('sentiments probability')
    ax1.set_ylabel('quantity')

    ax2.plot(np.arange(0, len(sentiments_list), 1), res, 'k-')
    ax2.set_xlabel('number of comment')
    ax2.set_ylabel('sentiment coefficient')
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    m = input('关键字/keyword：')  # keyword
    n = int(input('需要查找多少页/how many pages you want to check：'))  # page
    start = time.time()

    # m = '拜登'
    # n = 100

    filepath = 'weibo_%s.csv' % m

    for page in range(1, n + 1):
        time.sleep(random.randint(1, 4))
        json = get_page(page)
        if not json:
            print('no more page available')
            break
        results = parse_page(json)
        save_csv(filepath, results, page)
    comments = read_csv(filepath)
    print('total comments count: %d' % len(comments))
    word_cloud(comments)
    sentiment_analyze(comments)
    end = time.time()
    print('program runs for %f seconds' % (end-start))
