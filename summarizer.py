import os
import re
import numpy as np
import time
from selenium import webdriver

from gensim.summarization.summarizer import summarize
from gensim.summarization import keywords
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


def get_file_name(f_nm='news', suffix=''):
    outpath = 'out'
    out_dir = './{}/'.format(outpath)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    today_ = datetime.today().strftime('%Y%m%d')
    if suffix == '':
        file_nm = '{}_{}.txt'.format(f_nm, today_)
    else:
        file_nm = '{}_{}_{}.txt'.format(f_nm, today_, suffix)

    file_nm = os.path.join(out_dir, file_nm)

    return file_nm


def get_contents(cdriver, link):

    t_wait = np.random.randint(20, 30)
    pattern = '[A-Za-z0-9\.]+\.[A-Za-z]{2,4}'
    rex = re.compile(pattern)

    root_link = rex.search(link).group()

    if root_link == 'www.etftrends.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        result = cdriver.find_element_by_css_selector('div.alm-reveal')
        assert result.get_attribute('data-page') == '0'
        title = result.get_attribute('data-title')
        content = result.find_element_by_class_name('post-content').text

    elif root_link == 'www.etfstream.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        results = cdriver.find_element_by_tag_name('article')
        title = results.find_element_by_css_selector('h1.entry-title').text
        content = results.find_element_by_css_selector('div.entry-content').text

    elif root_link == 'www.nasdaq.com':
        title = None
        content = None
    elif root_link == 'seekingalpha.com':
        title = None
        content = None
    elif root_link == 'etfdailynews.com':
        title = None
        content = None
    elif root_link == 'www.zacks.com':
        title = None
        content = None
    # elif root_link == 'www.marketwatch.com':
    #     cdriver.get(link)
    #     cdriver.implicitly_wait(3)
    #     title = cdriver.find_element_by_id('article-headline').text
    #     content = cdriver.find_element_by_id('article-body').text
    elif root_link == 'www.etf.com':
        title = None
        content = None
    elif root_link == 'etfdb.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('h2.media-heading').text
        content = cdriver.find_element_by_css_selector('div.article__textile-block:not(.article__intro)').text
    elif root_link == 'finance.yahoo.com':
        title = None
        content = None
    elif root_link == 'www.investors.com':
        title = None
        content = None
    elif root_link == 'www.cnbc.com':
        title = None
        content = None

    # KOREAN NEWS
    elif root_link == 'www.ezyeconomy.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('div.article-head-title').text
        content = cdriver.find_element_by_id('article-view-content-div').text
    elif root_link == 'www.thebell.co.kr':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('p.tit').text
        content = cdriver.find_element_by_id('article-main').text
    elif root_link == 'www.mk.co.kr':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('h1.top_title').text
        content = cdriver.find_element_by_css_selector('div.art_txt').text
    elif root_link == 'biz.heraldcorp.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_tag_name('h1').text
        content = cdriver.find_element_by_id('articleText').text
    elif root_link == 'www.hankyung.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('h1.title').text
        content = cdriver.find_element_by_id('articletxt').text
    elif root_link == 'www.seoul.co.kr':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('h1.atit2').text
        content = cdriver.find_element_by_css_selector('div.v_article').text
    elif root_link == 'www.seoulfn.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('div.article-head-title').text
        content = cdriver.find_element_by_id('article-view-content-div').text
    # elif root_link == 'www.fntimes.com':
    #     cdriver.get(link)
    #     cdriver.implicitly_wait(3)
    #     title = cdriver.find_element_by_tag_name('h2').text
    #     content = cdriver.find_element_by_css_selector('div.vcon_con_intxt').text
    elif root_link == 'www.edaily.co.kr':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('div.news_titles>h2').text
        content = cdriver.find_element_by_css_selector('div.news_body').text
    elif root_link == 'www.asiae.co.kr':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('div.area_title>h3').text
        content = cdriver.find_element_by_id('txt_area').text
    # elif root_link == 'www.etoday.co.kr':
    #     time.sleep(t_wait)
    #     cdriver.get(link)
    #     cdriver.implicitly_wait(t_wait)
    #     title = cdriver.find_element_by_css_selector('h2.main_title').text
    #     content = cdriver.find_element_by_id('articleBody').text
    elif root_link == 'biz.chosun.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_id('news_title_text_id').text
        content = cdriver.find_element_by_css_selector('div.par').text
    elif root_link == 'www.fnnews.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('h1.mg').text
        content = cdriver.find_element_by_id('article_content').text
    elif root_link == 'www.econovill.com':
        title = None
        content = None
    elif root_link == 'www.sedaily.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_tag_name('h2').text
        content = cdriver.find_element_by_css_selector('div.view_con').text
    elif root_link == 'www.newspim.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('div.bodynews_title>h1').text
        content = cdriver.find_element_by_id('news_contents').text
    # elif root_link == 'news.mt.co.kr':
    #     cdriver.get(link)
    #     cdriver.implicitly_wait(t_wait)
    #     title = cdriver.find_element_by_css_selector('h1.subject').text
    #     content = cdriver.find_element_by_id('article-view-content-div').text
    elif root_link == 'www.datanet.co.kr':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('div.article-head-title').text
        content = cdriver.find_element_by_id('textBody').text
    elif root_link == 'news.joins.com':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_id('article_title').text
        content = cdriver.find_element_by_id('article_body').text
    elif root_link == 'www.it-b.co.kr':
        time.sleep(t_wait)
        cdriver.get(link)
        cdriver.implicitly_wait(t_wait)
        title = cdriver.find_element_by_css_selector('div.article-head-title').text
        content = cdriver.find_element_by_id('article-view-content-div').text
    else:
        title = None
        content = None

    return title, content


def google_news_list(cdriver, language='english', keyword='ETF', date='qdr:d'):

    if language == 'english':
        hl = 'en'
        lr = 'lang_en'
    elif language == 'korean':
        hl = 'kr'
        lr = 'lang_ko'
    # get google news titles and links
    url = "https://www.google.com/search?q={keyword}&num=100&start=0&hl={hl}&lr={lr}&tbs={date}&tbm=nws".format(
        keyword=keyword, hl=hl, lr=lr, date=date)

    cdriver.get(url)
    cdriver.implicitly_wait(3)

    results = cdriver.find_elements_by_css_selector('div.g')
    time.sleep(5)

    links = []
    titles = []
    for i in range(len(results)):
        content_div = results[i].find_element_by_css_selector('h3.r').find_element_by_tag_name('a')
        link = content_div.get_attribute('href')
        title = content_div.text

        links.append(link)
        titles.append(title)

    return titles, links


def write_file(news_list, file_nm):
    for i, news_summary in enumerate(news_list):
        if i == 0:
            write_mode = 'w'
        else:
            write_mode = 'a'
        with open(file_nm, write_mode, encoding='utf-8') as f:
            f.write(news_summary['title'])
            f.write('\n')
            f.write(news_summary['link'])
            f.write('\n')
            f.write(news_summary['summary'].replace('\n', ' '))
            f.write('\n\n')

    print('{} writed. [n_contents: {}]'.format(file_nm, len(news_list)))


def get_link_to_content(cdriver, titles_and_links, file_nm=None, word_count=200):
    if file_nm is not None:
        if not os.path.exists(file_nm):
            write_mode = 'w'
        else:
            write_mode = 'a'

        f = open(file_nm, write_mode, encoding='utf-8')

    titles, links = titles_and_links
    news_list = []
    j = 0
    for i in range(len(links)):
        if file_nm is not None:
            f.write("{}\n".format(i))
            f.write("{}\n".format(titles[i]))
            f.write("{}\n".format(links[i]))

        news_summary = dict()
        news_summary['i'] = i
        news_summary['link'] = links[i]
        news_summary['title'], news_summary['content'] = get_contents(cdriver, links[i])
        if news_summary['title'] is not None:
            print(j, i, titles[i], links[i])
            news_summary['summary'] = summarize(news_summary['content'], word_count=word_count)
            # news_summary['summary'] = summarize(news_summary['content'], ratio=0.05)
            news_list.append(news_summary)

            f.write("{}\n\n".format(news_summary['summary']))
            j += 1
        else:
            print(" " * len(str(j)), i, titles[i], links[i])

    if file_nm is not None:
        f.close()

    return news_list


def main():
    cdriver = webdriver.Chrome('d:/chromedriver_win32/chromedriver.exe')
    time.sleep(2)

    today_ = datetime.today().date()
    if today_.weekday() == 0:
        ref_date = today_ - timedelta(days=3)
        date_str = 'cdr%3A1%2Ccd_min%3A{}%2F{}%2F{}%2Ccd_max%3A{}%2F{}%2F{}'.format(ref_date.month, ref_date.day, ref_date.year, today_.month, today_.day, today_.year)
    else:
        date_str = 'qdr:d'


    # english
    keyword = 'etf'
    f_nm = 'news_{}'.format(keyword)
    file_nm = get_file_name(f_nm=f_nm, suffix='us')
    file_nm_tmp = get_file_name(f_nm=f_nm, suffix='us_tmp')
    en_titles_and_links = google_news_list(cdriver, language='english', keyword=keyword, date=date_str)
    en_news_list = get_link_to_content(cdriver, en_titles_and_links, file_nm=file_nm_tmp)
    write_file(en_news_list, file_nm)

    time.sleep(2)

    # korean
    keyword = 'etf'
    f_nm = 'news_{}'.format(keyword)
    file_nm = get_file_name(f_nm=f_nm, suffix='kr')
    file_nm_tmp = get_file_name(f_nm=f_nm, suffix='kr_tmp')
    kr_titles_and_links = google_news_list(cdriver, language='korean', keyword=keyword, date=date_str)
    kr_news_list = get_link_to_content(cdriver, kr_titles_and_links, file_nm=file_nm_tmp)
    write_file(kr_news_list, file_nm)

    cdriver.close()


if __name__ == '__main__':
    main()
