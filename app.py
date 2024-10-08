import streamlit as st
import yake
import nltk
from nltk.corpus import stopwords
import pandas as pd
import os
import textrazor
import requests

# Initialisation de Streamlit
st.set_page_config(page_title="Extraction de mots-clés avec YAKE et TextRazor", layout="wide")

# Vérifier si le répertoire de données NLTK existe
nltk_data_dir = os.path.join(os.path.expanduser('~'), 'nltk_data')
if not os.path.exists(nltk_data_dir):
    os.makedirs(nltk_data_dir)

# Télécharger les stopwords de nltk si nécessaire
nltk.data.path.append(nltk_data_dir)
try:
    nltk.download('stopwords', download_dir=nltk_data_dir)
except Exception as e:
    st.error(f"Erreur lors du téléchargement des stopwords : {e}")

# Lire les stopwords personnalisés à partir d'un fichier
def load_custom_stopwords(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        st.warning("Le fichier de stopwords personnalisé n'a pas été trouvé. Utilisation des stopwords par défaut.")
        return []

# Charger les stopwords personnalisés
custom_stopwords = load_custom_stopwords('custom_stopwords.txt')

# Fusionner les stopwords NLTK et les stopwords personnalisés
try:
    stopword_list = stopwords.words('french') + custom_stopwords
except LookupError:
    stopword_list = custom_stopwords
    st.warning("Impossible de charger les stopwords NLTK. Utilisation des stopwords personnalisés uniquement.")

# Fonction pour analyser une URL avec TextRazor
def analyze_url_with_textrazor(url, api_key):
    if not api_key:
        st.error("Clé API TextRazor manquante.")
        return None
    textrazor.api_key = api_key
    client = textrazor.TextRazor(extractors=["entities", "topics"])
    client.set_cleanup_mode("cleanHTML")
    client.set_cleanup_return_cleaned(True)
    try:
        response = client.analyze_url(url)
        if response.ok:
            return response.cleaned_text
        else:
            st.error(f"Erreur lors de l'analyse de l'URL avec TextRazor : {response.error}")
            return None
    except textrazor.TextRazorAnalysisException as e:
        st.error(f"Erreur lors de l'analyse de l'URL avec TextRazor : {e}")
        return None

# Fonction pour extraire les mots-clés avec YAKE
def extract_keywords_with_yake(text, stopword_list, max_ngram_size=3, deduplication_threshold=0.9, num_of_keywords=100):
    kw_extractor = yake.KeywordExtractor(
        lan="fr",
        n=max_ngram_size,
        dedupLim=deduplication_threshold,
        top=num_of_keywords,
        features=None,
        stopwords=stopword_list
    )
    return kw_extractor.extract_keywords(text)

# Navigation des pages
page = st.sidebar.radio("Navigation", ["Coller un texte", "Coller une URL", "Entrer un mot-clé"]) 

# Page : Coller un texte
if page == "Coller un texte":
    st.title("Extraction de mots-clés à partir d'un texte avec YAKE")
    
    # Champ de texte pour l'entrée utilisateur
    text_input = st.text_area("Entrez le texte ici :")

    # Bouton pour analyser le texte
    if st.button("Analyser le texte avec YAKE"):
        if text_input.strip():
            keywords = extract_keywords_with_yake(text_input, stopword_list)
            data = {
                "Mot Yake": [kw for kw, score in keywords],
                "Score": [score for kw, score in keywords],
                "Nombre d'occurrences": [text_input.lower().count(kw.lower()) for kw, score in keywords]
            }
            df = pd.DataFrame(data)
            st.subheader("Mots-clés extraits")
            st.dataframe(df)

# Page : Coller une URL
elif page == "Coller une URL":
    st.title("Analyse de contenu via URL avec TextRazor")
    
    # Champ de saisie pour l'URL
    url_input = st.text_input("Entrez l'URL ici :")
    textrazor_api_key = st.sidebar.text_input("Entrez votre clé API TextRazor", type="password")

    # Bouton pour analyser l'URL
    if st.button("Analyser l'URL"):
        if url_input.strip():
            analyzed_text = analyze_url_with_textrazor(url_input, textrazor_api_key)
            if analyzed_text:
                st.subheader("Texte analysé")
                st.write(analyzed_text)

# Page : Entrer un mot-clé
elif page == "Entrer un mot-clé":
    st.title("Recherche des SERP avec ValueSERP")
    
    # Champs dans la sidebar
    valueserp_api_key = st.sidebar.text_input("Entrez votre clé API ValueSERP", type="password")
    keyword_input = st.text_input("Entrez un mot-clé pour la recherche ValueSERP")
    location_query = st.text_input("Entrez une localisation pour les SERP")

    # Bouton pour rechercher les locations avec l'API ValueSERP
    if st.button("Rechercher les locations"):
        if not valueserp_api_key:
            st.error("Veuillez entrer votre clé API ValueSERP.")
        else:
            locations_url = f"https://api.valueserp.com/locations?api_key={valueserp_api_key}&q={location_query}"
            try:
                response = requests.get(locations_url)
                response.raise_for_status()
                locations = response.json().get("locations", [])
                if not locations:
                    st.warning("Aucune location trouvée.")
                else:
                    location_options = [loc['full_name'] for loc in locations]
                    selected_location = st.selectbox("Sélectionnez une location", location_options)
                    st.session_state['selected_location'] = selected_location
            except requests.RequestException as e:
                st.error(f"Erreur lors de la récupération des locations : {e}")

    # Afficher la location sélectionnée et lancer la recherche SERP
    if 'selected_location' in st.session_state:
        st.write(f"Location sélectionnée : {st.session_state['selected_location']}")
        if keyword_input and valueserp_api_key:
            search_url = f"https://api.valueserp.com/search?api_key={valueserp_api_key}&q={keyword_input}&location={st.session_state['selected_location']}&num=10"
            try:
                search_response = requests.get(search_url)
                search_response.raise_for_status()
                search_results = search_response.json().get("organic_results", [])
                if search_results:
                    st.subheader("Résultats de la recherche SERP")
                    for result in search_results:
                        st.write(f"- [{result['title']}]({result['link']})")
                else:
                    st.warning("Aucun résultat trouvé.")
            except requests.RequestException as e:
                st.error(f"Erreur lors de la recherche avec ValueSERP : {e}")
