import streamlit as st
import requests
import json

# Initialisation de Streamlit
st.set_page_config(page_title="Top 20 Google Search", layout="wide")

# Fonction pour obtenir les locations disponibles via l'API ValueSERP
def get_location(location_query, api_key):
    if not api_key:
        st.error("Clé API ValueSERP manquante.")
        return None
    locations_url = f"https://api.valueserp.com/locations"
    params = {
        'api_key': api_key,
        'q': location_query
    }
    try:
        response = requests.get(locations_url, params=params)
        response.raise_for_status()
        locations = response.json().get('locations', [])
        if not locations:
            st.warning("Aucune localisation trouvée.")
            return None
        return locations
    except requests.RequestException as e:
        st.error(f"Erreur lors de la recherche de la localisation avec ValueSERP : {e}")
        return None

# Fonction pour effectuer une recherche Google avec l'API ValueSERP
def get_google_top_20(keyword, location, api_key):
    if not api_key:
        st.error("Clé API ValueSERP manquante.")
        return None
    search_url = f"https://api.valueserp.com/search?api_key={api_key}&q={keyword}&location={location}&num=30"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        return response.json().get('organic_results', [])
    except requests.RequestException as e:
        st.error(f"Erreur lors de la recherche avec ValueSERP : {e}")
        return None

# Interface utilisateur
st.title("Recherche des Top 20 de Google par Localisation")

valueserp_api_key = st.sidebar.text_input("Entrez votre clé API ValueSERP", type="password")
keyword_input = st.text_input("Entrez un mot-clé pour la recherche Google")
location_query = st.text_input("Entrez une localisation (par exemple, 'Paris')")
user_url = st.text_input("Votre URL")

# Bouton pour rechercher la localisation
search_location = st.button("Rechercher la localisation")

selected_location = None
if search_location and location_query:
    locations = get_location(location_query, valueserp_api_key)
    if locations:
        location_options = [loc['full_name'] for loc in locations]
        selected_location = st.selectbox("Sélectionnez une localisation", location_options)

# Bouton pour lancer la recherche
display_results = st.button("Rechercher")

if display_results and keyword_input and selected_location:
    results = get_google_top_20(keyword_input, selected_location, valueserp_api_key)
    if results:
        st.subheader("Top 20 des résultats Google")
        for i, result in enumerate(results[:20], start=1):
            st.write(f"{i}. [{result['title']}]({result['link']})")

        # Vérifier si l'URL de l'utilisateur est dans le top 30
        if user_url:
            urls = [result['link'] for result in results]
            if user_url in urls:
                rank = urls.index(user_url) + 1
                st.write(f"Votre URL est classée #{rank} dans les résultats de Google.")
            else:
                st.write("Votre URL n'est pas dans le top 30 des résultats de Google.")
