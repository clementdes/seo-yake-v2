import streamlit as st
import yake
import nltk
from nltk.corpus import stopwords
import pandas as pd
import os
import textrazor
import requests

# Initialisation de Streamlit avec plusieurs pages
st.set_page_config(page_title="SEO Entity Finder", layout="wide")

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

# Navigation des pages de l'application
pages = ["Introduction", "Analyse à partir d'un texte", "Analyse à partir d'une URL", "Analyse à partir des SERPs", "Paramètres"]
page = st.sidebar.selectbox("Navigation", pages)

if page == "Introduction":
    # Page d'introduction
    st.title("SEO Entity Finder")
    st.write("Find Entities in a text, from a URL or directly from SERPs")
    st.write("""
    Choisissez une option :
    - **À partir d'un texte** : Analyser les entités dans un texte donné.
    - **À partir d'une URL** : Analyser les entités présentes sur une page web.
    - **À partir des SERPs Google** : Rechercher des entités à partir des résultats de recherche Google.
    """)

elif page == "Analyse à partir d'un texte":
    # Page pour analyser à partir d'un texte
    st.title("Analyse de texte avec YAKE")
    text_input = st.text_area("Entrez le texte ici :")

    if st.button("Analyser le texte avec YAKE"):
        if text_input.strip():
            keywords = yake.KeywordExtractor(
                lan="fr",
                n=3,
                dedupLim=0.9,
                top=20,
                features=None,
                stopwords=stopword_list
            ).extract_keywords(text_input)

            data = {
                "Mot Yake": [kw for kw, score in keywords],
                "Score": [score for kw, score in keywords],
                "Nombre d'occurrences": [text_input.lower().count(kw.lower()) for kw, score in keywords]
            }
            df = pd.DataFrame(data)
            st.subheader("Mots-clés extraits")
            st.dataframe(df)
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="Télécharger le tableau en CSV",
                data=csv,
                file_name="mots_cles_yake.csv",
                mime='text/csv',
            )
        else:
            st.warning("Veuillez entrer un texte pour procéder à l'analyse.")

elif page == "Analyse à partir d'une URL":
    # Page pour analyser à partir d'une URL
    st.title("Analyse d'une URL avec TextRazor")
    url_input = st.text_input("Entrez l'URL ici :")
    textrazor_api_key = st.sidebar.text_input("Entrez votre clé API TextRazor", type="password")

    if st.button("Analyser l'URL"):
        if not textrazor_api_key:
            st.error("Clé API TextRazor manquante.")
        elif not url_input.strip():
            st.warning("Veuillez entrer une URL pour procéder à l'analyse.")
        else:
            textrazor.api_key = textrazor_api_key
            client = textrazor.TextRazor(extractors=["entities", "topics"])
            client.set_cleanup_mode("cleanHTML")
            client.set_cleanup_return_cleaned(True)
            try:
                response = client.analyze_url(url_input)
                if response.ok:
                    st.write(response.cleaned_text)
                else:
                    st.error(f"Erreur lors de l'analyse de l'URL avec TextRazor : {response.error}")
            except textrazor.TextRazorAnalysisException as e:
                st.error(f"Erreur lors de l'analyse de l'URL avec TextRazor : {e}")

elif page == "Analyse à partir des SERPs":
    # Page pour analyser à partir des SERPs
    st.title("Analyse des SERPs Google")
    valueserp_api_key = st.sidebar.text_input("Entrez votre clé API ValueSERP", type="password")
    keyword_input = st.text_input("Entrez un mot-clé pour la recherche ValueSERP")
    location_query = st.text_input("Entrez une localisation pour les SERP")
    user_url = st.text_input("Votre URL")

    if st.button("Rechercher les SERPs et analyser"):
        if not valueserp_api_key:
            st.error("Clé API ValueSERP manquante.")
        elif not keyword_input.strip():
            st.warning("Veuillez entrer un mot-clé pour procéder à l'analyse.")
        else:
            search_url = f"https://api.valueserp.com/search?api_key={valueserp_api_key}&q={keyword_input}&location={location_query}&num=30"
            try:
                search_response = requests.get(search_url)
                search_response.raise_for_status()
                search_results = search_response.json()

                organic_results = search_results.get('organic_results', [])
                urls = [result['link'] for result in organic_results]
                st.subheader("URLs des résultats organiques")
                st.write(urls[:30])

                if user_url in urls[:30]:
                    rank = urls.index(user_url) + 1
                    st.write(f"Votre URL est classée #{rank} dans les résultats de Google.")
            except requests.RequestException as e:
                st.error(f"Erreur lors de la recherche avec ValueSERP : {e}")

elif page == "Paramètres":
    # Page des paramètres
    st.title("Paramètres")
    st.write("Ici, vous pouvez entrer vos clés API pour utiliser l'application.")
    textrazor_api_key = st.text_input("Clé API TextRazor", type="password")
    valueserp_api_key = st.text_input("Clé API ValueSERP", type="password")
    if st.button("Enregistrer les clés API"):
        st.session_state['textrazor_api_key'] = textrazor_api_key
        st.session_state['valueserp_api_key'] = valueserp_api_key
        st.success("Clés API enregistrées avec succès.")
