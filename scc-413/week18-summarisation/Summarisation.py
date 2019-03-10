import bs4 as bs  
import urllib.request  
import re
import nltk

query = 'Language'
print(urllib.parse.quote(query))
scraped_data = urllib.request.urlopen('https://en.wikipedia.org/wiki/'+urllib.parse.quote(query))
article = scraped_data.read()

print(article, file=open("rawArticle.txt", "a", encoding="utf8"))

parsed_article = bs.BeautifulSoup(article,'lxml')

paragraphs = parsed_article.find_all('p')

article_text = ""

for p in paragraphs:  
    article_text += p.text

# Removing special characters and digits
formatted_article_text = re.sub('[!@#$%^&*]g', ' ', article_text )  
formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)

print(formatted_article_text, file=open("cleanArticle.txt", "a", encoding="utf8"))


#detect language (optional)
from langdetect import detect
lang = detect(formatted_article_text)

if lang == 'ar':
    lang = 'arabic'
if lang == 'en':
    lang = 'english'
if lang == 'es':
    lang = 'spanish';
print(lang)
print("=======================")

#split text into sentences
nltk.download('punkt')
# from nltk.tokenize import sent_tokenize
sentence_list = nltk.sent_tokenize(article_text)

#Get relevent stop words list.
nltk.download('stopwords')
stopwords = nltk.corpus.stopwords.words(lang)

#Find Weighted Frequency of Occurrence
word_frequencies = {}  
for word in nltk.word_tokenize(formatted_article_text):  
    if word not in stopwords:
        if word not in word_frequencies.keys():
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1
            
maximum_frequncy = max(word_frequencies.values())

for word in word_frequencies.keys():  
    word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

#Calculating Sentence Scores
sentence_scores = {}  
for sent in sentence_list:  
    for word in nltk.word_tokenize(sent.lower()):
        if word in word_frequencies.keys():
            if len(sent.split(' ')) < 30:
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word]
                else:
                    sentence_scores[sent] += word_frequencies[word]

#Create summary, threshold defines number of top sentences with highest weight to include
import heapq
threshold = 3
summary_sentences = heapq.nlargest(threshold, sentence_scores, key=sentence_scores.get)

#Merge sentences into one summary
summary = ' '.join(summary_sentences)  
print(summary)
print("=====================================================")
