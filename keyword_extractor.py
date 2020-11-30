import json
import os
import numpy as np
import re
import string
import heapq
from collections import defaultdict
from soynlp.noun import LRNounExtractor
from soykeyword.proportion import CorpusbasedKeywordExtractor
from wordcloud import WordCloud


def cleansing_text(content):
    # "[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]" # 한글
    pattern1 = re.compile("[^\s]*[\s]?[(기자)]*[\s]+[a-zA-Z0-9]+[\._]?[a-zA-Z0-9]+[@]\w+[.]\w{2,3}") # 기자 및 이메일 주소
    pattern2 = re.compile("[[].*[(신문)|(기자)].*[]]")  # [**기자] [**신문]
    pattern3 = re.compile(string.whitespace[1:])  # 공백뺀 나머지 (\t\n\r\x0b\x0c)
    pattern4 = re.compile("[一-龥]")  # 한자
    pattern5 = re.compile("[\s]{2,}")  # 공백 여러개 => 공백 하나로
    # pattern5 = re.compile("[^a-zA-Z0-9가-힣\s.,!?-]") # 특수문자

    content = pattern1.split(content)[:-1]  # 이메일 주소 이후 정보 제거

    if len(content) > 1:  # 이메일주소 두개 이상
        content = [token for token in content if len(token) > 20]  # 정상문장 이하 토큰 제거

    content = "".join(content)
    content = re.sub(pattern2, '', content)  # [**기자] [**신문] 제거
    content = re.sub(pattern3, '', content)  # 탭 제거
    content = re.sub(pattern4, '', content)  # 한자 제거
    content = re.sub(pattern5, ' ', content)  # 공백여러개 -> 공백한개
    # content = re.sub(pattern5, '', content)  # 특수문자 제거
    content = "".join([token for token in content.split('\n') if len(token) > 20])  # 정상 이하 문장 제거

    # sp = re.findall(pattern5, content)
    # if len(sp) > 0:
    #     print(set(sp))

    return content


def make_corpus(begin_d=None, end_d=None, sections: list = None):
    data_path = './data/naver_news/'
    if begin_d is None:
        begin_d = '19000101'
    if end_d is None:
        end_d = '99991231'
    if sections is None:
        sections = []

    section_list = ['IT', '경제', '사회', '생활', '세계', '오피니언', '정치']
    if len(sections) >= 1:
        for section in sections:
            if section not in section_list:
                print("section {} not in {}".format(section, section_list))
                raise AssertionError

    news_list = []
    for news_file in os.listdir(data_path):
        splitted = re.split('[._]', news_file)
        if splitted[-1] != 'json':
            continue

        _, date_, ext = splitted
        if date_ >= begin_d and date_ <= end_d:
            news_list.append(news_file)

    corpus_raw = dict()
    for news_file in news_list:
        with open(os.path.join(data_path, news_file), 'rb') as f:
            corpus_raw.update(json.load(f))

    corpus_txt = []
    for id, info in corpus_raw.items():
        # content = re.sub(pattern, '', info['content'])

        if len(sections) >= 1 and info['class'] not in sections:
            continue

        content = info['content']
        if len(content) < 300:  # photo news
            continue

        content = cleansing_text(content)
        corpus_txt.append(content)
    corpus_txt = corpus_txt
    return corpus_raw, corpus_txt


def make_word_cloud(word_freq):
    default_font_path = 'C://Windows//Fonts//'
    fonts = {
        '휴먼편지체': 'HMFMPYUN.TTF',
        'HY견명조': 'H2MJRE.TTF',}
    wc = WordCloud(font_path=os.path.join(default_font_path, fonts['HY견명조']),
                   background_color='white',
                   max_words=100,
                   width=500,
                   height=500,
                   max_font_size=200
                   )

    wc.generate_from_frequencies(word_freq)
    wc.to_file('./wc.jpg')

def get_noun_words(begin_d=None, end_d=None):
    _, sentences = make_corpus(begin_d=begin_d, end_d=end_d)

    noun_extractor = LRNounExtractor()
    nouns = noun_extractor.train_extract(sentences)  # list of str like

    # noun_words = [(-stat.score, word, stat.frequency) for word, stat in nouns.items()]
    return nouns


def train_extractor(begin_d=None, end_d=None, sections: list = None):
    _, sentences = make_corpus(begin_d=begin_d, end_d=end_d, sections=sections)
    # nouns = get_noun_words(begin_d='20201101', end_d='20201130')

    noun_extractor = LRNounExtractor()
    nouns = noun_extractor.train_extract(sentences)  # list of str like

    if sections is not None and len(sections) >= 1:
        min_tf = 10
        min_df = 2
    else:
        min_tf = 20
        min_df = 2
    corpusbased_extractor = CorpusbasedKeywordExtractor(
        min_tf=min_tf,
        min_df=min_df,
        tokenize=lambda x:x.strip().split(),
        verbose=True
    )
    # docs: list of str like
    corpusbased_extractor.train(sentences)
    return corpusbased_extractor, nouns


def extract_keywords(keyword, keyword_extractor, nouns, min_score=0.8, min_frequency=50):

    keywords_candidates = keyword_extractor.extract_from_word(
        keyword,
        min_score=min_score,
        min_frequency=min_frequency
    )

    is_noun_keywords = []
    for candidate in keywords_candidates:
        is_noun = nouns.get(candidate.word, None)
        if is_noun is None or is_noun.score < 0.6:
            continue

        word = candidate.word
        frequency = nouns[word].frequency   # noun freq
        score = candidate.score             # keyword score
        is_noun_keywords.append([-score, word, frequency, is_noun.score])

    heapq.heapify(is_noun_keywords)
    sorted_keywords = []
    keywords_str = []
    for _ in range(len(is_noun_keywords)):
        val, word, frequency, noun_score = heapq.heappop(is_noun_keywords)
        sorted_keywords.append((-val, word, frequency, noun_score))
        keywords_str.append("{}\t\t(score: {:.3f} freq: {} noun_score: {:.3f})".format(word, -val, frequency, noun_score))

    return sorted_keywords, keywords_str


def test():
    # begin_d = '20200701'
    begin_d = '20201101'
    end_d = None
    sections = ['IT', '경제']    # ['IT', '경제', '사회', '생활', '세계', '오피니언', '정치']
    keyword_extractor, nouns = train_extractor(begin_d=begin_d, end_d=end_d, sections=sections)

    keyword_dict = defaultdict(list)
    keyword_list = ['미국']
    for keyword in keyword_list:
        keyword_tuples, keywords_str = extract_keywords(keyword=keyword, keyword_extractor=keyword_extractor, nouns=nouns,
                                    min_frequency=5, min_score=0.7)

        for keyword_tuple in keyword_tuples:
            score_, name_, freq_, noun_score_ = keyword_tuple
            keyword_dict[name_].append(keyword_tuple)

    new_scores = []
    for key, val_list in keyword_dict.items():
        n_match = len(val_list)
        new_score = n_match + np.mean([val[0] * 3 + np.log(max(val[2], 20)) + val[3] for val in val_list])
        new_scores.append([-new_score, n_match, key])

    heapq.heapify(new_scores)

    for i in range(len(new_scores)):
        if i < 0:
            heapq.heappop(new_scores)
            continue
        else:
            print(heapq.heappop(new_scores))

        if i == 50:
            break
