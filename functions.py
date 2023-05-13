from nltk.corpus import wordnet
import configuration as c
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from itertools import combinations
from bs4 import BeautifulSoup
from tensorflow.keras.models import load_model
import requests
import pickle
import nltk
nltk.download('wordnet')


lemmatizer = WordNetLemmatizer()
splitter = RegexpTokenizer(r'\w+')

model = pickle.load(open(c.MODEL_PATH, 'rb'))
model_symptoms = pickle.load(open(c.SYMPTOMS_PATH, 'rb'))
model_scores = pickle.load(open(c.MODEL_SCORES_PATH, 'rb'))

# returns the list of synonyms of the input word from thesaurus.com (https://www.thesaurus.com/) and wordnet (https://www.nltk.org/howto/wordnet.html)


def get_synonyms(term):
    synonyms = []
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(term))
    soup = BeautifulSoup(response.content,  "html.parser")
    try:
        container = soup.find('section', {'class': 'MainContentContainer'})
        row = container.find(
            'div', {'class': 'css-191l5o0-ClassicContentCard'})
        row = row.find_all('li')
        for x in row:
            synonyms.append(x.get_text())
    except:
        None
    for syn in wordnet.synsets(term):
        synonyms += syn.lemma_names()
    return set(synonyms)


def split_symptoms(symptoms):
    user_symptoms = symptoms.lower().split(',')
    # Preprocessing the input symptoms
    processed_user_symptoms = []
    for sym in user_symptoms:
        sym = sym.strip()
        sym = sym.replace('-', ' ')
        sym = sym.replace("'", '')
        sym = ' '.join([lemmatizer.lemmatize(word)
                       for word in splitter.tokenize(sym)])
        processed_user_symptoms.append(sym)

    return processed_user_symptoms


def generate_synonyms(symptoms):
    # Taking each user symptom and finding all its synonyms and appending it to the pre-processed symptom string
    processed_user_symptoms = split_symptoms(symptoms)
    user_symptoms = []
    for user_sym in processed_user_symptoms:
        user_sym = user_sym.split()
        str_sym = set()
        for comb in range(1, len(user_sym)+1):
            for subset in combinations(user_sym, comb):
                subset = ' '.join(subset)
                subset = get_synonyms(subset)
                str_sym.update(subset)
        str_sym.add(' '.join(user_sym))
        user_symptoms.append(' '.join(str_sym).replace('_', ' '))
    # query expansion performed by joining synonyms found for each symptoms initially entered

    return user_symptoms


def find_matching_symptoms(symptoms):
    # Loop over all the symptoms in dataset and check its similarity score to the synonym string of the user-input
    # symptoms. If similarity>0.5, add the symptom to the final list
    dataset_symptoms = model_symptoms
    user_symptoms = generate_synonyms(symptoms)
    found_symptoms = set()
    for idx, data_sym in enumerate(dataset_symptoms):
        data_sym_split = data_sym.split()
        for user_sym in user_symptoms:
            count = 0
            for symp in data_sym_split:
                if symp in user_sym.split():
                    count += 1
            if count/len(data_sym_split) > 0.5:
                found_symptoms.add(data_sym)
    found_symptoms = list(found_symptoms)

    return found_symptoms


def get_matching_symptoms(symptoms):
    found_symptoms = find_matching_symptoms(symptoms)
    # Print all found symptoms
    bot_response = "Top matching symptoms from your search!"
    for idx, symp in enumerate(found_symptoms):
        bot_response = bot_response+'\n'+str(idx) + " : " + symp

    # Show the related symptoms found in the dataset and ask user to select among them
    bot_response = bot_response + \
        "\n\nPlease select the relevant symptoms. Enter indices (separated-space):"

    return bot_response
