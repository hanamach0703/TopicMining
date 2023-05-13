import pandas as pd
import re
import string
# from custom_stemmer import CustomStemmer
import swifter
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import csv
import nltk
from nltk.tokenize import word_tokenize 
from nltk.probability import FreqDist
from nltk.corpus import stopwords
import os
import glob

# ----- Case Folding -----
def change_lower_case(text):
  return text.lower()

def remove_news_special(text):
  # remove tab, new line, and back slice
  text = text.replace('\\t'," ").replace('\\n'," ").replace('\\u'," ").replace('\\'," ")
  # remove non ASCII (emoticon, kanji, .etc)
  text = text.encode('ascii', 'replace').decode('ascii')
  # remove mention, link, hashtag
  text = ' '.join(re.sub("([@#][A-Za-z0-9]+)|(\w+:\/\/\S+)"," ", text).split())
  # remove incomplete url
  return text.replace("http://", " ").replace("https://", " ")

#remove number
def remove_number(text):
  return re.sub(r'[-+]?[0-9]+', '', text)

#remove punctuation
def remove_punctuation(text):
  return text.translate(str.maketrans("", "", string.punctuation))

#remove whitespace leading & trailing
def remove_whitespace_LT(text):
  return text.strip()

#remove multiple whitespace into single whitespace
def remove_whitespace_multiple(text):
  return re.sub('\s+',' ',text)

#remove single char
def remove_single_char(text):
  return re.sub(r"\b[a-zA-Z]\b", "", text)

# #NLTK word rokenize 
# def word_tokenize_wrapper(text):
#     return word_tokenize(text)

# #NLTK calc frequency distribution
# def freqDist_wrapper(text):
#     return FreqDist(text)

 # ----- Stopwords Removal ----- 
def stopwords_removal(text):
  list_stopwords = stopwords.words('indonesian')
  list_stopwords.extend(["detik", "detikjatim", "detikjateng", "detikjabar", "detiksulsel", "detiksumbar", "detikbali", "detikpapua", "detiksulteng", "detikmaluku", "detjatim", "detikcom", "allahumma", "aamiin", "allah", "bismillah", "20detik", "gambasvideo", "video", "selengkapnya"])
  list_stopwords.extend(["yang","yg", "dg", "rt", "dgn", "ny", "d", 'klo', 
                       'kalo', 'amp', 'biar', 'bikin', 'bilang', 
                       'gak', 'ga', 'krn', 'nya', 'nih', 'sih', 
                       'si', 'tau', 'tdk', 'tuh', 'utk', 'ya', 
                       'jd', 'jgn', 'sdh', 'aja', 'n', 't', 
                       'nyg', 'hehe', 'pen', 'u', 'nan', 'loh', 'rt',
                       '&amp', 'yah', 'dkk', 
                       'senin', 'selasa', 'rabu', 'kamis', 'jumat', 'sabtu', 'minggu',
                       'januari', 'februari', 'maret', 'april', 'mei', 'juni', 'juli', 'agustus', 'september', 'oktober', 'november', 'desember'])
  list_stopwords = set(list_stopwords)

  text = ' '.join(word for word in text.split() if word not in list_stopwords)
  return text

# # ----- Stemming ----- 
def stemming_word(text):
  factory = StemmerFactory()
  stemmer = factory.create_stemmer()
  text = stemmer.stem(text)
  print(text)
  return text
   

if __name__ == "__main__":
  # nltk.download_shell()
  nltk.download('stopwords')
  # ----- Merge Data -----
  #list all csv files only
  csv_files = glob.glob('*.{}'.format('csv'))
  news_data = pd.DataFrame()
  #append all files together
  for file in csv_files:
    df_temp = pd.read_csv(file)
    news_data = news_data._append(df_temp, ignore_index=True)
#   news_data = pd.read_csv("scrapped_news.csv", encoding = "ISO-8859-1")
  # print(news_data['description'].isnull())
  # print(news_data['description'].isnull())
  # ----- Delete Duplicate Data ----- 
  news_data.drop_duplicates(subset=None, keep="first", inplace=True)
  news_data['description'] = news_data['description'].apply(change_lower_case)
  news_data['description'] = news_data['description'].apply(remove_news_special)
  news_data['description'] = news_data['description'].apply(remove_number)
  news_data['description'] = news_data['description'].apply(remove_punctuation)
  news_data['description'] = news_data['description'].apply(remove_whitespace_LT)
  news_data['description'] = news_data['description'].apply(remove_whitespace_multiple)
  news_data['description'] = news_data['description'].apply(remove_single_char)
#   news_data['description_tokens'] = news_data['description'].apply(word_tokenize_wrapper)
#   news_data['description_tokens_fdist'] = news_data['description_tokens'].apply(freqDist_wrapper)
#   news_data['description_tokens_wsw'] = news_data['description_tokens'].apply(freqDist_wrapper)
  news_data['description_clean_stop'] = news_data['description'].apply(stopwords_removal)
  news_data['description_clean_stem'] = news_data['description_clean_stop'].apply(stemming_word)

#  stemmer = CustomStemmer(news_data['description_tokens_wsw'])
#   news#  _data['description_tokens_stemmed'] = news_data['description_tokens_wsw'].swifter.apply(stemmer.get_stemmed_term)
  # We will skip normalization word 
  
  news_stop = news_data['description_clean_stop']
  news_stem = news_data['description_clean_stem']

#   news_data.to_csv('text_preprocessing.csv')
  news_stop.to_csv('text_preprocessing_stop.csv')
  news_stem.to_csv('text_preprocessing_stem.csv')

  csv_file = input('Enter the name of your input file: ')
  txt_file = input('Enter the name of your output file: ')
  with open(txt_file, "w") as my_output_file:
    with open(csv_file, "r") as my_input_file:
        [ my_output_file.write(" ".join(row)+'\n') for row in csv.reader(my_input_file)]
    my_output_file.close()

  csv_file = input('Enter the name of your input file: ')
  txt_file = input('Enter the name of your output file: ')
  with open(txt_file, "w") as my_output_file:
    with open(csv_file, "r") as my_input_file:
        [ my_output_file.write(" ".join(row)+'\n') for row in csv.reader(my_input_file)]
    my_output_file.close()