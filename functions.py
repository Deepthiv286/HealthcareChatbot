import operator
from collections import Counter
import pandas as pd
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
from statistics import mean


lemmatizer = WordNetLemmatizer()
splitter = RegexpTokenizer(r'\w+')

model = pickle.load(open(c.MODEL_PATH, 'rb'))
model_symptoms = pickle.load(open(c.SYMPTOMS_PATH, 'rb'))
model_scores = pickle.load(open(c.MODEL_SCORES_PATH, 'rb'))

df_norm = pd.read_csv(c.PATH_TO_DATASET2)
Y = df_norm.iloc[:, 0:1]

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
    pickle.dump(found_symptoms, open(c.MATCHING_SYMPTOMS_PATH, 'wb'))
    # Print all found symptoms
    bot_response = "Top matching symptoms from your search!"
    for idx, symp in enumerate(found_symptoms):
        bot_response = bot_response+'\n'+str(idx) + " : " + symp

    # Show the related symptoms found in the dataset and ask user to select among them
    bot_response = bot_response + \
        "\n\nPlease select the relevant symptoms. Enter indices (space-separated):"

    return bot_response


def get_cooccurring_symptoms(symptoms):
    select_list = symptoms.split()
    dataset_symptoms = model_symptoms
    found_symptoms = pickle.load(open(c.MATCHING_SYMPTOMS_PATH, 'rb'))
    df_norm = pd.read_csv(c.PATH_TO_DATASET2)

    dis_list = set()
    final_symp = []
    counter_list = []

    for idx in select_list:
        symp = found_symptoms[int(idx)]
        final_symp.append(symp)
        dis_list.update(set(df_norm[df_norm[symp] == 1]['label_dis']))

    for dis in dis_list:
        row = df_norm.loc[df_norm['label_dis'] == dis].values.tolist()
        row[0].pop(0)
        for idx, val in enumerate(row[0]):
            if val != 0 and dataset_symptoms[idx] not in final_symp:
                counter_list.append(dataset_symptoms[idx])

    # Symptoms that co-occur with the ones selected by user
    dict_symp = dict(Counter(counter_list))
    dict_symp_tup = sorted(
        dict_symp.items(), key=operator.itemgetter(1), reverse=True)
    pickle.dump(dict_symp_tup, open(c.COOCCURRING_SYMPTOMS_PATH, 'wb'))
    pickle.dump(final_symp, open(c.FINAL_SYMPTOMS_PATH, 'wb'))

    cooccurring_symptoms = get_next_cooccurring_symptoms(select_list, 0)

    return cooccurring_symptoms


def get_next_cooccurring_symptoms(symptoms, count):
    print(symptoms)
    select_list = symptoms
    dict_symp_tup = pickle.load(open(c.COOCCURRING_SYMPTOMS_PATH, 'rb'))
    # Iteratively, suggest top co-occuring symptoms to the user and ask to select the ones applicable
    found_symptoms = []
    text=''
    final_symp = pickle.load(open(c.FINAL_SYMPTOMS_PATH, 'rb'))

    del dict_symp_tup[:5*count]
    tup = dict_symp_tup[slice(0, 5)]

    for ele in tup:
        found_symptoms.append(ele[0])

    if select_list[0] == 'no':
        text = get_predicted_diseases()
    elif select_list[0] == '-1':
        found_symptoms = []
        get_next_cooccurring_symptoms([''], count+1)
    else:
        text = "Common co-occuring symptoms:"
        for idx, ele in enumerate(found_symptoms):
            text = text+'\n'+str(idx)+" : "+ele
        
        text = text + "\n\nDo you have have of these symptoms? If Yes, enter the indices (space-separated), 'no' to stop, '-1' to skip:"
        
    for idx in select_list:
        final_symp.append(found_symptoms[int(idx)])

    pickle.dump(final_symp, open(c.FINAL_SYMPTOMS_PATH, 'wb'))
    found_symptoms = []

    return text


def get_predicted_diseases():
    final_symp = pickle.load(open(c.FINAL_SYMPTOMS_PATH, 'rb'))
    dataset_symptoms = model_symptoms
    # Create query vector based on symptoms selected by the user
    text="Final list of Symptoms that will be used for prediction:"
    sample_x = [0 for x in range(0,len(dataset_symptoms))]
    for val in final_symp:
        text=text+'\n'+val
        sample_x[dataset_symptoms.index(val)]=1

    prediction = model.predict_proba([sample_x])
    k = 10
    diseases = list(set(Y['label_dis']))
    diseases.sort()
    topk = prediction[0].argsort()[-k:][::-1]

    text=text+"\n\nTop 10 diseases predicted based on symptoms"
    topk_dict = {}
    # Show top 10 highly probable disease to the user.
    for idx,t in  enumerate(topk):
        match_sym=set()
        row = df_norm.loc[df_norm['label_dis'] == diseases[t]].values.tolist()
        row[0].pop(0)

        for idx,val in enumerate(row[0]):
            if val!=0:
                match_sym.add(dataset_symptoms[idx])
        prob = (len(match_sym.intersection(set(final_symp)))+1)/(len(set(final_symp))+1)
        prob *= mean(model_scores)
        topk_dict[t] = prob
    j = 0
    topk_index_mapping = {}
    topk_sorted = dict(sorted(topk_dict.items(), key=lambda kv: kv[1], reverse=True))
    for key in topk_sorted:
        prob = topk_sorted[key]*100
        text=text+'\n'+str(j) + " Disease name:"+diseases[key]+ "\tProbability:"+str(round(prob, 2))+"%"
        topk_index_mapping[j] = key
        j += 1

    return text