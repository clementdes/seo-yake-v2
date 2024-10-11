# README - Extraction de Mots-Clés avec YAKE et TextRazor

## Description

Cette application Streamlit permet d'extraire des mots-clés à partir de textes, d'URL ou de résultats de recherche SERP en utilisant les outils suivants :

- **YAKE** : Extraction de mots-clés basée sur la fréquence et d'autres critères.
- **TextRazor** : Analyse de contenu à partir d'une URL, y compris l'extraction d'entités et de sujets.
- **ValueSERP** : Recherche des résultats Google SERP pour un mot-clé donné et extraction des URLs pour analyse.

L'application est divisée en trois sections :
1. **Coller un texte** : Extraction de mots-clés à partir d'un texte fourni.
2. **Coller une URL** : Analyse de contenu d'une URL via TextRazor et extraction de mots-clés.
3. **Entrer un mot-clé** : Recherche des résultats Google SERP et analyse des URLs avec TextRazor et YAKE.

Pour l'essayer en ligne : (https://seo-yake-v2.streamlit.app/)[https://seo-yake-v2.streamlit.app/]

## Installation

### Prérequis
1. Python 3.x
2. Les bibliothèques suivantes doivent être installées :
   - `streamlit`
   - `yake`
   - `nltk`
   - `textrazor`
   - `requests`
   - `pandas`

### Installation des dépendances
Clonez ce dépôt et installez les dépendances via `pip` :

```bash
git clone https://github.com/votreutilisateur/votre-repo.git
cd votre-repo
pip install -r requirements.txt
```

### Configuration NLTK
Assurez-vous que les stopwords NLTK sont téléchargés. L'application gère automatiquement ce téléchargement. Vous pouvez aussi ajouter vos propres stopwords personnalisés dans un fichier `custom_stopwords.txt`.

## Clés API

Certaines fonctionnalités nécessitent des clés API :

- **TextRazor** : Pour analyser le contenu d'une URL.
- **ValueSERP** : Pour effectuer des recherches SERP.

Renseignez vos clés API dans les champs dédiés de l'interface Streamlit.

## Utilisation

Pour lancer l'application, exécutez la commande suivante dans le répertoire du projet :

```bash
streamlit run app.py
```

### Options disponibles

1. **Extraction de texte** : Collez un texte et obtenez les mots-clés extraits par YAKE.
2. **Analyse d'URL** : Entrez une URL pour obtenir les mots-clés à partir du contenu de la page analysée par TextRazor.
3. **Recherche SERP** : Entrez un mot-clé et une localisation pour obtenir les résultats SERP, puis analysez les mots-clés des 10 premières URL.

## Fonctionnalités

- **Téléchargement CSV** : Les résultats des mots-clés extraits peuvent être téléchargés au format CSV.
- **Personnalisation des stopwords** : Ajoutez vos propres stopwords dans `custom_stopwords.txt`.
- **Suivi de positionnement** : L'application vous permet de suivre le classement de votre URL dans les résultats Google.

## Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à soumettre des pull requests pour ajouter des fonctionnalités ou corriger des bugs.

## Licence

Ce projet est sous licence MIT.
