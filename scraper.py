import argparse
import os
import random
import time
import datetime

from selenium import webdriver
from shutil import copyfile
import json


parser = argparse.ArgumentParser()
parser.add_argument('--begin_d', default=None, type=str)
parser.add_argument('--end_d', default=None, type=str)
parser.add_argument('--test', default=False, type=bool)
parser.add_argument('--filedir', default='./out/naver_news', type=str)



def get_date_list(begin_d=None, end_d=None):
    if begin_d is None:
        begin_d = (datetime.datetime.now()+datetime.timedelta(-2)).strftime('%Y-%m-%d')

    if end_d is None:
        end_d = (datetime.datetime.now()+datetime.timedelta(1)).strftime('%Y-%m-%d')

    days_range = []

    start = datetime.datetime.strptime(begin_d, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_d, "%Y-%m-%d") # 범위 + 1
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days)]

    for date in date_generated:
        if date.weekday() in [5, 6]: # weekend
            continue

        days_range.append(date.strftime("%Y%m%d"))

    return days_range


def get_oid():
    return {'032': '경향신문',
             '005': '국민일보',
             '020': '동아일보',
             '021': '문화일보',
             '081': '서울신문',
             '022': '세계일보',
             '023': '조선일보',
             '025': '중앙일보',
             '028': '한겨레',
             '469': '한국일보',
             '009': '매일경제',
             '008': '머니투데이',
             '011': '서울경제',
             '277': '아시아경제',
             '018': '이데일리',
             '014': '파이낸셜뉴스',
             '015': '한국경제',
             '016': '헤럴드경제',
             '029': '디지털타임스',
             '030': '전자신문'}


def get_url(base_url, mode, mid, oid, listType, date_):
    return "{base_url}?mode={mode}&mid={mid}&oid={oid}&listType={listType}&date={date_}".format(
        base_url=base_url, mode=mode, mid=mid, oid=oid, listType=listType, date_=date_)


def get_articles_meta(cdriver, begin_d=None, end_d=None, test=False):

    """
    base url:
    mode: LPOD=언론사뉴스 / LSD=분야별뉴스
    mid: sec=페이지나눔 / shm= paper한정 전부다나옴 (잘 모르겠지만 listType=paper일경우 shm good)
    oid: 언론사 코드
    listType: paper=신문게재기사만 title=제목형 summary=요약형 photo=포토만

    """
    base_url = "https://news.naver.com/main/list.nhn"
    mode = 'LPOD'
    mid = 'shm'
    oid_dict = get_oid()
    listType = 'paper'
    date_list = get_date_list(begin_d, end_d)
    articles_meta = dict()

    for date_ in date_list:
        s_t = time.time()
        time.sleep((0.2 + random.random()) * 3)
        for oid, name in oid_dict.items():
            print("{}: {} start".format(date_, name))
            url = get_url(base_url, mode, mid, oid, listType, date_)

            cdriver.get(url)
            cdriver.implicitly_wait(3)

            pages = cdriver.find_elements_by_class_name('firstlist')
            for page in pages:
                a_list = page.find_elements_by_tag_name('a')
                for a in a_list:
                    url = a.get_attribute('href')
                    id = url.split('aid=')[1]
                    title = a.text
                    if id in articles_meta.keys():
                        continue

                    articles_meta[id] = {'title':title,
                                        'url': url,
                                        'date': date_,
                                        'from': name}

                    # 작동 테스트
                    if test and len(articles_meta) >= 2:
                        return articles_meta

            print("{}: {} end".format(date_, name))
        print("{} time spent: {} sec".format(date_, time.time() - s_t))

    return articles_meta


def scrap_news(cdriver, articles_meta, filedir='./out/naver_news', test=False):

    if not os.path.exists(filedir):
        os.makedirs(filedir)

    filename = 'news.json'
    backup = 'news_backup.json'
    log = 'log.log'

    file_path = os.path.join(filedir, filename)
    backup_path = os.path.join(filedir, backup)
    log_path = os.path.join(filedir, log)

    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            articles = json.load(f)
    else:
        articles = dict()

    st = time.time()
    for i, (id, article_meta) in enumerate(articles_meta.items()):
        if test and i == 2:
            break

        if id in articles.keys():
            continue

        cdriver.get(article_meta['url'])
        cdriver.implicitly_wait(3)
        try:
            article_meta['content'] = cdriver.find_element_by_id('articleBodyContents').text
            article_meta['class'] = cdriver.find_element_by_class_name('guide_categorization_item').text
        except:
            with open(log_path, 'a') as f:
                str_ = '[failed] id: {} {} {}\n'.format(id, article_meta['title'], article_meta['url'])
                f.write(str_)

            continue

        articles[id] = article_meta
        with open(file_path, 'wb') as f:
            s = json.dumps(articles, indent=4, ensure_ascii=False).encode('utf-8')
            f.write(s)

        copyfile(file_path, backup_path)
        time.sleep((0.2 + random.random()) * 5)
        elapsed_time = time.time() - st
        print("progress: {}/{} ({}%, expected {} sec)".format(i+1, len(articles_meta), (i+1)/len(articles_meta) * 100, elapsed_time * len(articles_meta) / (i+1)))
    print('done')

def main(args):

    cdriver = webdriver.Chrome('d:/chromedriver_win32/chromedriver.exe')
    time.sleep(2)

    # dictionary: key=news_id | value=[title, link]
    # articles_meta = get_articles_meta(cdriver, begin_d='2020-11-02', end_d='2020-11-25')
    articles_meta = get_articles_meta(cdriver, begin_d=args.begin_d, end_d=args.end_d, test=args.test)
    with open(os.path.join(args.filedir, 'meta.json'), 'w') as f:
        json.dump(articles_meta, f, indent=4)

    time.sleep(2)
    scrap_news(cdriver, articles_meta, filedir=args.filedir, test=args.test)
    print('done')

    cdriver.close()


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)