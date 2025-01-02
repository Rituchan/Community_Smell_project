"""
Questo script analizza un file CSV contenente intervalli di commit da un repository GitHub, categorizza i commit
in base ai loro messaggi utilizzando parole chiave definite in un file di configurazione JSON, e salva i risultati
in un file CSV. Inoltre, i messaggi che non appartengono a nessuna categoria vengono salvati separatamente in un
file di testo. Utilizza il multithreading per velocizzare l'analisi degli intervalli di commit.
"""
import json
import os
import requests
import time
import pandas as pd
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import re  # Importa il modulo delle espressioni regolari

# Configurazione
GITHUB_TOKEN = ""   # Sostituisci con il tuo token
REPO_OWNER = "hashicorp"  # Proprietario del repository
REPO_NAME = "vagrant"  # Nome del repository
CSV_FILE = "../report/Vagrant_report.csv"  # Percorso file CSV input
OUTPUT_FILE = f"../output_qualitative_commit/{REPO_NAME}_qualitative.csv"

# Lista per memorizzare i messaggi "Other"
other_messages = []

# Funzione per caricare la configurazione delle categorie da un file JSON
def load_category_config(config_path):
    with open(config_path, "r") as file:
        return json.load(file)

# Funzione per categorizzare i commit con punteggi
def categorize_commit_with_scores(message, category_config):
    message = message.lower()
    category_scores = {category: 0 for category in category_config}

    # Usare set per evitare ricerche multiple inutili
    message_set = set(message.split())

    for category, keywords in category_config.items():
        for keyword in keywords:
            # Usa una regex per cercare la parola chiave in qualsiasi forma, come prefisso o parte di una parola
            if re.search(r'\b' + re.escape(keyword) + r'\w*\b', message):  # Aggiungi la regex
                category_scores[category] += 1

    if all(score == 0 for score in category_scores.values()):
        # Salva il messaggio che va in "Other"
        other_messages.append(message)
        return "Other"

    # Seleziona la categoria con il punteggio più alto
    return max(category_scores, key=category_scores.get)

# Funzione per recuperare i commit tra due commit specifici con gestione paginazione
def fetch_commits_between(start_commit, end_commit):
    commits = []
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits"
    params = {"sha": end_commit, "per_page": 100}
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    while url:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            for commit in data:
                commits.append(commit)
                if commit['sha'] == start_commit:
                    return commits  # Se raggiungiamo il commit di partenza, ritorniamo i commit
            url = _get_next_page_url(response)  # Gestione paginazione
        elif response.status_code == 403:
            wait_time = _handle_rate_limit(response)
            print(f"Limite di richieste raggiunto. Attendere {wait_time} secondi.")
            time.sleep(wait_time)  # Attendere fino a reset del limite
        else:
            print(f"Errore nella richiesta API: {response.status_code}")
            break

    return commits

def _get_next_page_url(response):
    """Estrai l'URL della pagina successiva per la paginazione"""
    if 'Link' in response.headers and 'rel="next"' in response.headers['Link']:
        return response.headers['Link'].split(';')[0][1:-1]
    return None

def _handle_rate_limit(response):
    """Gestisce il limite di richieste API"""
    reset_time = int(response.headers.get('X-RateLimit-Reset'))
    return reset_time - int(time.time())

def analyze_commit_ranges(file_path, category_config):
    if not os.path.exists(file_path):
        print(f"Errore: il file {file_path} non esiste.")
        return

    df = pd.read_csv(file_path)

    if 'range' not in df.columns:
        print("Errore: la colonna 'range' non esiste nel file CSV.")
        return

    commit_categories = [None] * len(df)  # Per mantenere lo stesso ordine
    commit_counts = [None] * len(df)

    # Usare ThreadPoolExecutor per analizzare gli intervalli in parallelo
    with ThreadPoolExecutor() as executor:
        futures = []
        for index, row in df.iterrows():
            commit_range = row['range']
            print(f"Analizzando intervallo: {commit_range}")
            futures.append(executor.submit(process_commit_range, commit_range, category_config, index, commit_categories, commit_counts))

        # Attendere la fine di tutte le operazioni in parallelo
        for future in futures:
            future.result()

    # Aggiungi i risultati nel DataFrame
    df['commit_range'] = df['range']
    df['commit_count'] = commit_counts
    df['commit_categories'] = commit_categories

    # Calcolare il totale dei commit
    total_commits = df['commit_count'].sum()  # Somma dei valori nella colonna 'commit_count'

    # Aggiungi una riga per il totale dei commit
    columns = df.columns.tolist()
    totals_row = ["Totale", "", total_commits, {}] + [None] * (len(columns) - 4)
    df.loc[len(df.index)] = totals_row

    # Salva i risultati
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Analisi completata. File aggiornato salvato in: {OUTPUT_FILE}")

    # Salva i messaggi "Other" in un file separato
    with open("other_messages.txt", "w", encoding="utf-8") as f:
        for message in other_messages:
            f.write(message + "\n")
    print(f"Messaggi classificati come 'Other' salvati in: other_messages.txt")

def process_commit_range(commit_range, category_config, index, commit_categories, commit_counts):
    """Processa ciascun intervallo in parallelo mantenendo l'ordine"""
    try:
        if '-' not in commit_range:
            print(f"Intervallo malformato: {commit_range}")
            return

        start_commit, end_commit = commit_range.split('-')
        start_commit, end_commit = start_commit.strip(), end_commit.strip()

        # Recupero dei commit per l'intervallo
        commits = fetch_commits_between(start_commit, end_commit)

        # Categorizzazione dei commit usando la funzione con punteggi
        categories = [categorize_commit_with_scores(commit['commit']['message'], category_config) for commit in commits]
        category_counts = Counter(categories)

        # Conteggio dei commit in questo intervallo
        commit_categories[index] = category_counts
        count = len(commits)
        commit_counts[index] = count
        print(f"Intervallo {commit_range}: {count} commit")

    except Exception as e:
        print(f"Errore per l'intervallo {commit_range}: {e}")
        commit_categories[index] = {}
        commit_counts[index] = 0

# Percorso del file di configurazione delle categorie
category_config_path = "./config_categories.json"
category_config = load_category_config(category_config_path)

# Esecuzione
analyze_commit_ranges(CSV_FILE, category_config)
