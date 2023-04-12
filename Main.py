import nltk
import random
import spacy
from verbecc import Conjugator
import os

def load_dict(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return [tuple(line.strip().split("\t")) for line in lines]

dictionary = load_dict("lefff-3.4.mlex.txt")

cg = Conjugator(lang='fr')

# Charger le modèle en français
nlp = spacy.load('fr_core_news_sm')

# Charger le texte des Misérables
with open(f'LesMiserables1.txt', 'r') as f:
    corpus = f.read()


with open("tags.txt", "r", encoding="utf-8") as f:
    tags = f.read().splitlines()
doc = [tuple(tag.split("\t")) for tag in tags if len(tag.split("\t")) == 2]

# Prétraitement : enlever les caractères indésirables, les espaces et les mots vides
corpus = corpus.split()
corpus = [word.lower() for word in corpus if word.isalpha()]
stopwords = set(nltk.corpus.stopwords.words('french'))
corpus = [word for word in corpus if word not in stopwords and word not in ["tout"]]

# Définir les tags de parties de discours pour les phrases SV
subject_tags = ['DET']
noun_tags = ['NOUN']
verb_tags = ['VERB', 'AUX']
adjective_tags = ['ADJ']
connector_tags = ['CCONJ']
end_tags = ['PUNCT']


# Calculer les fréquences des différents mots dans le corpus
freq_dist = nltk.FreqDist(corpus)
total_words = len(corpus)

# Fonction pour générer des phrases SV aléatoires
def generate_sentence(level=0):
    subject = ["",""]
    noun = ["",""]
    for k in range(2):
        # Choisir un sujet au hasard, en fonction de leur fréquence dans le corpus
        genre = ""
        while genre not in ["ms", "fs", "mp", "fp"]:
            subject[k] = random.choice([token[0] for token in doc if token[1] in subject_tags])
            for line in dictionary:
                if line[0]==subject[k] and line[1] == "det":
                    genre = line[-1]
                    break
            
        # Choisir un nom au hasard, en fonction de leur fréquence dans le corpus
        genre_noun = ""
        while genre_noun != genre:
            noun[k] = random.choices([token[0] for token in doc if token[1] in noun_tags],
                                    weights=[freq_dist[token[0]] / total_words for token in doc if token[1] in noun_tags])[0]
            for line in dictionary:
                if line[0]==noun[k] and line[2] == noun[k]:
                    genre_noun = line[-1]
                    break
        if noun[k].startswith(("a", "e", "i", "o", "u", "y", "h")) and subject[k] in ["le", "la"]:
            subject[k] = "L'" if k == 0 and level == 0 else "l'"     
        
        if k == 0:
            genre_adj = ""
            while genre_adj != genre:
                # Choisir un adjectif au hasard, en fonction de leur fréquence dans le corpus
                adj = random.choices([token[0] for token in doc if token[1] in adjective_tags],
                                    weights=[freq_dist[token[0]] / total_words for token in doc if token[1] in adjective_tags])[0]
                for line in dictionary:
                    if line[0]==adj and line[2] == adj:
                        genre_adj = line[-1]
                        break
    if level == 0:
        subject[0] = subject[0].capitalize()
    
    # Choisir un verbe au hasard, en fonction de leur fréquence dans le corpus
    verb = random.choices([token[0] for token in doc if token[1] in verb_tags],
                          weights=[freq_dist[token[0]]**(1/2) / total_words for token in doc if token[1] in verb_tags])[0]
    try:
        if genre == "ms" or genre == "fs":
            conjugation = cg.conjugate(verb)
            conj = conjugation['moods']['indicatif']['présent'][2]
            verb = conj.split(' ')[-1]
        elif genre == "mp" or genre == "fp":
            conjugation = cg.conjugate(verb)
            conj = conjugation['moods']['indicatif']['présent'][5]
            verb = conj.split(' ')[-1]
    except:
        pass
    
    # Choisir une fin de phrase au hasard, en fonction de leur fréquence dans le corpus
    end = random.choice([".", ","])
    if level == 1:
        end = "."
    elif end == ",":
        # Choisir un connecteur au hasard, en fonction de leur fréquence dans le corpus
        connector = random.choices([token[0] for token in doc if token[1] in connector_tags and token[0] not in ["être"]],
                                   weights=[freq_dist[token[0]] / total_words for token in doc if token[1] in connector_tags and token[0] not in ["être"]])[0]
        end = end + " " + connector + " " + generate_sentence(1)
    
    # Retourner la phrase générée
    return f"{subject[0]} {noun[0]} {adj} {verb} {subject[1]} {noun[1]}{end}"




# Générer 10 phrases aléatoires dans le style de Victor Hugo
for i in range(10):
    print("Sentence #", i+1, ":")
    print(generate_sentence())