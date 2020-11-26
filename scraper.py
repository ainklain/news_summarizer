# python scraper.py --begin_d=20201101 --end_d=20201126

import platform
import argparse
import os
import random
import time
import datetime
from collections import deque

from selenium import webdriver
from shutil import copyfile
import json
import re

parser = argparse.ArgumentParser()
parser.add_argument('--begin_d', default=None, type=str)
parser.add_argument('--end_d', default=None, type=str)
parser.add_argument('--test', default=False, type=bool)
parser.add_argument('--filedir', default='./out/naver_news', type=str)
parser.add_argument('--metadir', default='./out/naver_news/meta', type=str)
parser.add_argument('--source', default='press', type=str, choices=['press', 'category'])
parser.add_argument('--chrome_driver_path', default='d:/chromedriver_win32/chromedriver.exe', type=str)


class TestArgs:
    begin_d = None
    end_d = None
    test = True
    filedir = './out/naver_news'
    metadir = './out/naver_news/meta'
    chrome_driver_path = 'd:/chromedriver_win32/chromedriver.exe'
    source = 'press'


def get_date_list(begin_d=None, end_d=None):
    if begin_d is None:
        begin_d = (datetime.datetime.now()+datetime.timedelta(-2)).strftime('%Y%m%d')

    if end_d is None:
        end_d = (datetime.datetime.now()+datetime.timedelta(1)).strftime('%Y%m%d')

    days_range = []

    start = datetime.datetime.strptime(begin_d, "%Y%m%d")
    end = datetime.datetime.strptime(end_d, "%Y%m%d") # 범위 + 1
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


def get_sid():
    return {'속보': {'sid1': '001', 'sid2': {}},
            '정치': {'sid1': '100', 'sid2': {}},
            '경제': {'sid1': '101', 'sid2': {
                '금융': '259',
                '증권': '258',
                '재계': '261',
                '중소': '771',
                '부동산': '260',
                '글로벌': '262',
                '생활': '310',
                '일반': '263',
            }},
            '사회': {'sid1': '102', 'sid2': {}},
            '생활문화': {'sid1': '103', 'sid2': {}},
            '세계': {'sid1': '104', 'sid2': {}},
            'IT과학': {'sid1': '105', 'sid2': {}},
            '랭킹뉴스': {'sid1': '111', 'sid2': {}}}



def get_url_press(date_, oid):
    """
    base url:
    mode: LPOD=언론사뉴스 / LSD=분야별뉴스(전체) / LS2D=분야별뉴스(세부)
    mid: sec=페이지나눔 / shm= paper한정 전부다나옴 (잘 모르겠지만 listType=paper일경우 shm good)
    oid: 언론사 코드
    listType: paper=신문게재기사만 title=제목형 summary=요약형 photo=포토만
    """
    base_url = "https://news.naver.com/main/list.nhn"
    return "{base_url}?mode={mode}&mid={mid}&oid={oid}&listType={listType}&date={date_}".format(
        base_url=base_url, mode='LPOD', mid='shm', oid=oid, listType='paper', date_=date_)

def get_url_category(date_, sid1, sid2=None, page=1):
    """
    base url:
    mode: LPOD=언론사뉴스 / LSD=분야별뉴스(전체) / LS2D=분야별뉴스(세부)
    mid: sec=페이지나눔 / shm= paper한정 전부다나옴 (잘 모르겠지만 listType=paper일경우 shm good)
    oid: 언론사 코드
    listType: paper=신문게재기사만 title=제목형 summary=요약형 photo=포토만
    """
    base_url = "https://news.naver.com/main/list.nhn"
    if sid2 is None:
        mode = 'LSD'
    else:
        mode = 'LS2D'
    return "{base_url}?mode={mode}&sid2={sid2}&sid1={sid1}&mid={mid}&listType={listType}&date={date_}&page={page}".format(
        base_url=base_url, mode=mode, mid="sec", listType="title", date_=date_, sid1=sid1, sid2=sid2, page=page)


def get_articles_meta_press(cdriver, begin_d=None, end_d=None, metadir='./out/naver_news/meta', test=False):
    """
    base url:
    mode: LPOD=언론사뉴스 / LSD=분야별뉴스(전체) / LS2D=분야별뉴스(세부)
    mid: sec=페이지나눔 / shm= paper한정 전부다나옴 (잘 모르겠지만 listType=paper일경우 shm good)
    oid: 언론사 코드
    listType: paper=신문게재기사만 title=제목형 summary=요약형 photo=포토만
    """
    oid_dict = get_oid()
    date_list = get_date_list(begin_d, end_d)

    if not os.path.exists(metadir):
        os.makedirs(metadir)

    st_total = time.time()
    for date_ in date_list:
        s_t = time.time()
        time.sleep((0.2 + random.random()) * 3)

        metapath = os.path.join(metadir, 'meta-press_{}.json'.format(date_))
        if os.path.exists(metapath):
            with open(metapath, 'rb') as f:
                articles_meta = json.load(f)
            print("[already exist] date={} | total_file={}".format(date_, len(articles_meta)))
            continue
        else:
            articles_meta = dict()
            print("date={} begin".format(date_))

        for oid, press_name in oid_dict.items():
            # print("{}: {} start".format(date_, name))
            url = get_url_press(date_, oid)

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

                    articles_meta[id] = {'title': title,
                                        'url': url,
                                        'date': date_,
                                        'from': press_name}

                    # 작동 테스트
                    if test and len(articles_meta) >= 2:
                        with open(metapath, 'wb') as f:
                            s = json.dumps(articles_meta, indent=4, ensure_ascii=False).encode('utf-8')
                            f.write(s)
                        return articles_meta

            # print("{}: {} end".format(date_, name))

        with open(metapath, 'wb') as f:
            s = json.dumps(articles_meta, indent=4, ensure_ascii=False).encode('utf-8')
            f.write(s)

        print("date={} | total_file={} | time spent: {:.3f} sec".format(date_, len(articles_meta), time.time() - s_t))

    print('url scrapping done. {:.3f} sec'.format(time.time() - st_total))


def get_articles_meta_category(cdriver, begin_d=None, end_d=None, metadir='./out/naver_news/meta', test=False):
    """
    base url:
    mode: LPOD=언론사뉴스 / LSD=분야별뉴스(전체) / LS2D=분야별뉴스(세부)
    mid: sec=페이지나눔 / shm= paper한정 전부다나옴 (잘 모르겠지만 listType=paper일경우 shm good)
    oid: 언론사 코드
    listType: paper=신문게재기사만 title=제목형 summary=요약형 photo=포토만
    """
    sid_dict = get_sid()
    sid_type = {'sid1': '경제', 'sid2': ['금융', '증권', '글로벌']}
    date_list = get_date_list(begin_d, end_d)

    if not os.path.exists(metadir):
        os.makedirs(metadir)

    st_total = time.time()
    for date_ in date_list:
        s_t = time.time()
        time.sleep((0.2 + random.random()) * 3)

        metapath = os.path.join(metadir, 'meta-category_{}.json'.format(date_))
        if os.path.exists(metapath):
            with open(metapath, 'rb') as f:
                articles_meta = json.load(f)
            print("[already exist] date={} | total_file={}".format(date_, len(articles_meta)))
            continue
        else:
            articles_meta = dict()
            print("date={} begin".format(date_))

        sid1 = sid_dict[sid_type['sid1']]['sid1']
        sid2_list = [(sid2, category) for category, sid2 in sid_dict[sid_type['sid1']]['sid2'].items()
                     if category in sid_type['sid2']]

        for sid2, category in sid2_list:
            # print("{}: {} start".format(date_, name))
            pages_to_visit = deque(['1'])
            prev_page = None
            assert_visited_one = dict()
            while pages_to_visit:

                cur_page = pages_to_visit.popleft()
                if cur_page == '다음':
                    cur_page = str(int(prev_page) + 1)
                elif cur_page == '이전':
                    continue

                url = get_url_category(date_, sid1=sid1, sid2=sid2, page=cur_page)
                prev_page = cur_page

                cdriver.get(url)
                cdriver.implicitly_wait(10)

                if int(cur_page) % 10 == 1 and not assert_visited_one.get(cur_page, False):
                    paging = cdriver.find_element_by_class_name('paging')
                    add_pages = paging.text.split(' ')[1:]  # '이전' 제거
                    pages_to_visit.extend(add_pages)
                    assert_visited_one[cur_page] = True

                pages = cdriver.find_elements_by_class_name('type02')
                for page in pages:
                    li_list = page.find_elements_by_tag_name('li')
                    for li in li_list:
                        a = li.find_element_by_tag_name('a')
                        url = a.get_attribute('href')
                        id = url.split('aid=')[1]
                        title = a.text
                        from_ = li.find_element_by_class_name('writing').text
                        if id in articles_meta.keys():  # 중복뉴스 제거
                            continue

                        pattern = re.compile("[[].*[]]")
                        if len(pattern.findall(title)) >= 1:    # 인사|포토|속보|표 등 제거
                            continue

                        articles_meta[id] = {'title': title,
                                            'url': url,
                                            'date': date_,
                                            'from': from_,
                                            'class': category}

                        # 작동 테스트
                        if test and len(articles_meta) >= 2:
                            with open(metapath, 'wb') as f:
                                s = json.dumps(articles_meta, indent=4, ensure_ascii=False).encode('utf-8')
                                f.write(s)
                            return articles_meta

                # print("{}: {} end".format(date_, name))

        with open(metapath, 'wb') as f:
            s = json.dumps(articles_meta, indent=4, ensure_ascii=False).encode('utf-8')
            f.write(s)

        print("date={} | total_file={} | time spent: {:.3f} sec".format(date_, len(articles_meta), time.time() - s_t))

    print('url scrapping done. {:.3f} sec'.format(time.time() - st_total))


def scrap_news(cdriver, metadir='./out/naver_news/meta', filedir='./out/naver_news', test=False):

    if not os.path.exists(filedir):
        os.makedirs(filedir)

    meta_list = os.listdir(metadir)
    meta_list.sort()

    log = 'log.log'
    log_path = os.path.join(filedir, log)

    st_total = time.time()
    for meta_file in meta_list:
        st_meta = time.time()

        date_ = ''.join(re.findall('[0-9]', meta_file))

        filename = 'news_{}.json'.format(date_)
        backup = 'news_backup_{}.json'.format(date_)

        meta_path = os.path.join(metadir, meta_file)
        file_path = os.path.join(filedir, filename)
        backup_path = os.path.join(filedir, backup)

        with open(meta_path, 'rb') as f:
            articles_meta = json.load(f)

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
                if not article_meta.get('class', False):
                    article_meta['class'] = cdriver.find_element_by_class_name('guide_categorization_item').text

            except:
                with open(log_path, 'a') as f:
                    str_ = '[failed] date: {} id: {} {} {}\n'.format(date_, id, article_meta['title'], article_meta['url'])
                    f.write(str_)

                continue

            articles[id] = article_meta
            with open(file_path, 'wb') as f:
                s = json.dumps(articles, indent=4, ensure_ascii=False).encode('utf-8')
                f.write(s)

            copyfile(file_path, backup_path)
            time.sleep((0.2 + random.random()) * 5)
            elapsed_time = time.time() - st
            expected_total = elapsed_time * len(articles_meta) / (i+1)
            print("date:{} progress: {}/{} ({:.3f}%, expected {:.3f} | remaining {:.3f} sec)".format(date_, i+1, len(articles_meta), (i+1)/len(articles_meta) * 100, expected_total, expected_total-elapsed_time))

        print('date:{} done ({:.3f} sec)'.format(date_, time.time() - st_meta))
    print('done ({:.3f} sec)'.format(time.time() - st_total))


def main(args):
    # args = TestArgs()
    if platform.system().lower() == 'windows':
        path = args.chrome_driver_path
        
    elif platform.system().lower() == 'linux':
        from pyvirtualdisplay import Display
        display = Display(visible=0, size=(1024, 768))
        display.start()
        path = '/home/ubuntu/chromedriver'
    else:
        print("chrome driver not found (platform: {})".format(platform.system()))
        return 0

    cdriver = webdriver.Chrome(path)
    time.sleep(2)

    if not os.path.exists(args.filedir):
        os.makedirs(args.filedir)

    try:
        # dictionary: key=news_id | value=[title, link]
        print('meta start')
        if args.source == 'press':
            get_articles_meta_press(cdriver, begin_d=args.begin_d, end_d=args.end_d, metadir=args.metadir, test=args.test)

        elif args.source == 'category':
            get_articles_meta_category(cdriver, begin_d=args.begin_d, end_d=args.end_d, metadir=args.metadir, test=args.test)
        else:
            raise KeyError
        print('meta done')
        time.sleep(2)

        print('scrap start')
        scrap_news(cdriver, metadir=args.metadir, filedir=args.filedir, test=args.test)
        print('scrap done')
        cdriver.close()
    except:
        cdriver.close()


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)



    """
    l = os.listdir('./out/naver_news/category/meta')
    for n in l:
        a, b, c= re.split('[_.]', n)
        print(a, b, c)
        
    
    """