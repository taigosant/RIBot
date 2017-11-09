# coding: utf-8



import json
import numpy
import nltk

# from pprint import pprint


# In[3]:


with open('data/salao/04.json', 'r') as f:
    data = json.load(f)



corpusCategory = {}
for item in data['loja']['categorias']:
    # print item['nome']
    corpusCategory[item['id']] = item['nome']    
for item in data['servicos']:    
    corpusCategory[item['categoria']] += " \n " +item['nome']
# #     print item['nome']




stopwords = nltk.corpus.stopwords.words('portuguese')



from nltk.stem import RSLPStemmer
# nltk.download()
stemmer = RSLPStemmer()


# In[9]:

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems




from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(analyzer='word', tokenizer=tokenize, stop_words= stopwords)



tfidf_vectorizer.fit(corpusCategory.values())





# print "Stop Words :5", tfidf_vectorizer.stop_words[:5]
# print "Vocabulary [size]:", len(tfidf_vectorizer.vocabulary_)
# print "Vocabulary:", tfidf_vectorizer.vocabulary_


# ### Calculando o TF/IDF com TfidfTransformer

# In[14]:


tfidf_matrix = tfidf_vectorizer.transform(corpusCategory.values())
# # print corpusCategory.values()
# print tfidf_matrix.shape




from sklearn.metrics.pairwise import cosine_similarity




def rankingInput(model, matrix, sentence):
    response = model.transform(sentence)
    cosine_similarities  = cosine_similarity(response, matrix).flatten()
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1]]
    return [(index, cosine_similarities[index]) for index in related_docs_indices][0:10]



services = data['loja']['categorias']


corpusItemsService = [0] * len(data['servicos'])
# # print data['servicos']
for index, item in enumerate(data['servicos']):
    corpusItemsService[index] = item['nome']

precos = {}
for item in data['servicos']:
    precos[item['nome']] = item['preco']

# print(precos)



tfidf_items = TfidfVectorizer(analyzer='word', tokenizer=tokenize, stop_words= stopwords)
tfidf_items.fit(corpusItemsService)


# # print "Stop Words :5", tfidf_items.stop_words[:5]
# # print "Vocabulary [size]:", len(tfidf_items.vocabulary_)
# # print "Vocabulary:", tfidf_items.vocabulary_


tfidf_items_matrix = tfidf_items.transform(corpusItemsService)
# print tfidf_items_matrix.shape



# # print raking
items_service = data['servicos']


def searchCategory(sentence):
    ranking1 = rankingInput(model=tfidf_vectorizer, matrix=tfidf_matrix, sentence=[sentence])
    # print ranking1
    candidates = [x for x, y in ranking1 if y > 0]
    candidatesName = [item['nome'] for item in services if item['id'] in candidates]
    # print candidatesName
    connectlist = [index for index, item in enumerate(data['servicos']) if item['categoria'] in candidates]
    prodFilter = tfidf_items_matrix.todense()[[connectlist]]
    ranking2 = rankingInput(model=tfidf_items, matrix=prodFilter, sentence=[sentence])
    prods = []
    # return "Acho que voce esta procurando por este servico: " + items_service[connectlist[raking2[0][0]]]['nome'] + ', custando R$: ' + items_service[connectlist[raking2[0][0]]]['preco']
    for index, score in ranking2:
        if score != 0:
            nome = str(items_service[connectlist[index]]['nome'])
            preco = str(items_service[connectlist[index]]['preco'])
            prods.append((nome, preco))
    if prods:
        return prods
    else:
        return candidatesName


print(services)
# print(data['servicos'])
# # print searchCategory('quero cortar o cabelo')