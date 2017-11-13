# coding: utf-8



import json
import numpy
import nltk
from nltk.stem import RSLPStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class Search(object):
    def __init__(self, loja):
        if loja == 'Bemol':
            loja = 'data/eletro/bemol.json'
        elif loja == 'Casas Bahia':
            loja = 'data/eletro/casasbahia.json'
        elif loja == 'Walmart':
            loja = 'data/eletro/Walmart.json'
        elif loja == 'Salao Sempre Bela':
            loja = 'data/salao/02.json'
        elif loja == 'Salao Top':
            loja = 'data/salao/03.json'
        elif loja == 'Salao Rainha':
            loja = 'data/salao/03.json'

        with open(loja, 'r') as f:
            self.data = json.load(f)
        self.corpusCategory = {}
        for item in self.data['loja']['categorias']:
            self.corpusCategory[item['id']] = item['nome']
        for item in self.data['servicos']:
            self.corpusCategory[item['categoria']] += " \n " +item['nome']

        self.stemmer = RSLPStemmer()
        self.stopwords = nltk.corpus.stopwords.words('portuguese')
        self.tfidf_vectorizer = TfidfVectorizer(analyzer='word', tokenizer=self.tokenize, stop_words=self.stopwords)
        self.tfidf_vectorizer.fit(self.corpusCategory.values())
        self.tfidf_matrix = self.tfidf_vectorizer.transform(self.corpusCategory.values())

        self.services = self.data['loja']['categorias']

        self.corpusItemsService = [0] * len(self.data['servicos'])
        # # print self.data['servicos']
        for index, item in enumerate(self.data['servicos']):
            self.corpusItemsService[index] = item['nome']

        self.precos = {}
        for item in self.data['servicos']:
            self.precos[item['nome']] = item['preco']

        self.tfidf_items = TfidfVectorizer(analyzer='word', tokenizer=self.tokenize, stop_words=self.stopwords)
        self.tfidf_items.fit(self.corpusItemsService)

        self.tfidf_items_matrix = self.tfidf_items.transform(self.corpusItemsService)

        self.items_service = self.data['servicos']


    def stem_tokens(self, tokens, stemmer):
        stemmed = []
        for item in tokens:
            stemmed.append(stemmer.stem(item))
        return stemmed

    def tokenize(self, text):
        tokens = nltk.word_tokenize(text)
        stems = self.stem_tokens(tokens, self.stemmer)
        return stems


    def rankingInput(self, model, matrix, sentence):
        response = model.transform(sentence)
        cosine_similarities  = cosine_similarity(response, matrix).flatten()
        related_docs_indices = [i for i in cosine_similarities.argsort()[::-1]]
        return [(index, cosine_similarities[index]) for index in related_docs_indices][0:10]


    def searchCategory(self, sentence):
        ranking1 = self.rankingInput(model=self.tfidf_vectorizer, matrix=self.tfidf_matrix, sentence=[sentence])
        print(ranking1)
        candidates = [x for x, y in ranking1 if y > 0]
        # print(candidates)
        candidatesName = [item['nome'] for item in self.services if int(item['id']) in candidates]
        # print(self.services)
        # print(candidatesName)
        connectlist = [index for index, item in enumerate(self.data['servicos']) if int(item['categoria']) in candidates]
        prodFilter = self.tfidf_items_matrix.todense()[[connectlist]]
        ranking2 = self.rankingInput(model=self.tfidf_items, matrix=self.tfidf_items_matrix, sentence=[sentence])
        print(ranking2)
        prods = []
        for index, score in ranking2:
            if score != 0.0:
                nome = str(self.items_service[index]['nome'])
                preco = str(self.items_service[index]['preco'])
                prods.append((nome, preco))
        if prods:
            return prods
        else:
            return candidatesName


if __name__== '__main__':
    se = Search('Bemol')
    print(se.searchCategory('quero um notebook'))