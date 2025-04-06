# Additional NLP imports

import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords


def clean_data(text):
    text = re.sub(r'\W', ' ', text.lower())
    tokenized_text = word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    lemmatized_text = [lemmatizer.lemmatize(
        word) for word in tokenized_text if word not in stop_words]
    return ' '.join(lemmatized_text)
