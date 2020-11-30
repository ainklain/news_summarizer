import numpy as np
import torch
import transformers
from transformers import ElectraModel, ElectraTokenizer, ElectraForQuestionAnswering

from sklearn.feature_extraction.text import CountVectorizer

n_gram_range = (1, 1)
stop_words = "english"

doc = """
         Supervised learning is the machine learning task of 
         learning a function that maps an input to an output based 
         on example input-output pairs.[1] It infers a function 
         from labeled training data consisting of a set of 
         training examples.[2] In supervised learning, each 
         example is a pair consisting of an input object 
         (typically a vector) and a desired output value (also 
         called the supervisory signal). A supervised learning 
         algorithm analyzes the training data and produces an 
         inferred function, which can be used for mapping new 
         examples. An optimal scenario will allow for the algorithm 
         to correctly determine the class labels for unseen 
         instances. This requires the learning algorithm to  
         generalize from the training data to unseen situations 
         in a 'reasonable' way (see inductive bias).
      """

# Extract candidate words/phrases
count = CountVectorizer(ngram_range=n_gram_range, stop_words=stop_words).fit([doc])
candidates = count.get_feature_names()


from sentence_transformers import SentenceTransformer

# model = SentenceTransformer('distilbert-base-nli-mean-tokens')
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
doc_embedding = model.encode([doc])
candidate_embeddings = model.encode(candidates)

from sklearn.metrics.pairwise import cosine_similarity

top_n = 5
distances = cosine_similarity(doc_embedding, candidate_embeddings)
keywords = [candidates[index] for index in distances.argsort()[0][-top_n:]]


def soynlp_tokenizer(corpus):
    from soynlp.tokenizer import LTokenizer
    from soynlp.word import WordExtractor
    from soynlp.noun import LRNounExtractor_v2

    # word extractor
    word_extractor = WordExtractor(
        min_frequency=100,  # example
        min_cohesion_forward=0.05,
        min_right_branching_entropy=0.0
    )
    word_extractor.train(corpus)
    words = word_extractor.extract()

    cohesion_score = {word:score.cohesion_forward for word, score in words.items()}

    # noun extractor
    noun_extractor = LRNounExtractor_v2()
    nouns = noun_extractor.train_extract(corpus)  # list of str like

    noun_scores = {noun: score.score for noun, score in nouns.items()}
    combined_scores = {noun: score + cohesion_score.get(noun, 0)
                       for noun, score in noun_scores.items()}
    combined_scores.update(
        {subword: cohesion for subword, cohesion in cohesion_score.items()
         if not (subword in combined_scores)}
    )

    tokenizer = LTokenizer(scores=combined_scores)
    return tokenizer






# model = ElectraForQuestionAnswering.from_pretrained("monologg/koelectra-base-v3-discriminator")
model = ElectraModel.from_pretrained("monologg/koelectra-base-v3-discriminator")
tokenizer = ElectraTokenizer.from_pretrained("monologg/koelectra-base-v3-discriminator")

text = """윤석열 검찰총장이 차기 대권주자 선호도에서 1위를 차지했다는 소식에 관련주가 급등세다.
11일 오전 9시 8분 현재 덕성은 전 거래일 대비 810원(10.95%) 오른 8,210원에 거래되고 있다.
덕성은 이봉근 대표이사와 김원일 사외이사가 윤 총장과 서울대학교 법대 동문으로 알려져 `윤석열 관련주`로 분류돼 왔다.
같은 시각 진도(6.79%)와 서연(9.40%)도 비슷한 흐름이다.
진도는 안호봉 사외이사가 윤 총장의 사법연수원 동기란 사실로 관련주가 됐고 서연은 유재만 사외이사가 윤 총장과 서울대 법대 동문이란 이유로 관련주로 꼽혔다."""

token = tokenizer.encode(text)

base_input = tokenizer(text, return_tensors='pt')
# token = tokenizer.decode(base_input['input_ids'][0])
base_output = model(**base_input)[0]
vec1 = base_output.mean(dim=(0, 1))

key_output = dict()
for input_id, token_type_id, attn_mask in zip(base_input['input_ids'][0], base_input['token_type_ids'][0], base_input['attention_mask'][0]):
    name = tokenizer.decode(input_id)
    key_output[name] = model(input_ids=input_id.view(1, -1), token_type_ids=token_type_id.view(1, -1), attention_mask=attn_mask.view(1, -1))[0].squeeze()


def cos_similarity(vec1, vec2):
    vec1 = vec1.detach().cpu().numpy()
    vec2 = vec2.detach().cpu().numpy()

    return np.dot(vec1, vec2) / np.linalg.norm(vec1) / np.linalg.norm(vec2)

similar = []
for name, vec2 in key_output.items():
    val = cos_similarity(base_output, vec2)
    similar.append([-val, name])

import heapq
heapq.heapify(similar)










import urllib

from keybert import KeyBERT
text = """윤석열 검찰총장이 차기 대권주자 선호도에서 1위를 차지했다는 소식에 관련주가 급등세다.
11일 오전 9시 8분 현재 덕성은 전 거래일 대비 810원(10.95%) 오른 8,210원에 거래되고 있다.
덕성은 이봉근 대표이사와 김원일 사외이사가 윤 총장과 서울대학교 법대 동문으로 알려져 `윤석열 관련주`로 분류돼 왔다.
같은 시각 진도(6.79%)와 서연(9.40%)도 비슷한 흐름이다.
진도는 안호봉 사외이사가 윤 총장의 사법연수원 동기란 사실로 관련주가 됐고 서연은 유재만 사외이사가 윤 총장과 서울대 법대 동문이란 이유로 관련주로 꼽혔다."""


model = KeyBERT('distilbert-base-nli-mean-tokens')
keywords = model.extract_keywords(text)


