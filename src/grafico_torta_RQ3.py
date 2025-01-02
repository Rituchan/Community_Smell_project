import os
import pandas as pd
import ast
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

def analyze_commit_categories(folder_path):
    """
    Analizza tutti i file CSV in una cartella che terminano con '_qualitative.csv',
    calcola la distribuzione delle categorie di commit e crea grafici a torta.

    Parameters:
        folder_path (str): Percorso della cartella contenente i file CSV.

    Returns:
        dict: Un dizionario con il nome del file e le distribuzioni delle categorie di commit.
    """
    results = {}

    # Itera su tutti i file nella cartella
    for file_name in os.listdir(folder_path):
        if file_name.endswith('_qualitative.csv'):
            file_path = os.path.join(folder_path, file_name)

            # Carica il file CSV
            try:
                data = pd.read_csv(file_path)
            except Exception as e:
                print(f"Errore nel caricamento del file {file_name}: {e}")
                continue

            # Verifica se la colonna commit_categories esiste
            if 'commit_categories' not in data.columns:
                print(f"Colonna 'commit_categories' mancante in {file_name}")
                continue

            # Calcola la distribuzione delle categorie di commit
            commit_counter = Counter()
            for categories in data['commit_categories'].dropna():
                parsed_categories = ast.literal_eval(categories.replace("Counter", ""))
                commit_counter.update(parsed_categories)

            # Salva i risultati
            results[file_name] = commit_counter

            # Calcola le percentuali
            total_commits = sum(commit_counter.values())
            category_percentages = {k: (v / total_commits) * 100 for k, v in commit_counter.items()}

            # Accorpa le categorie con percentuali inferiori al 3%
            aggregated_counter = Counter()
            for category, percentage in category_percentages.items():
                if percentage < 3:
                    aggregated_counter['Rimanenti<3%'] += commit_counter[category]
                else:
                    aggregated_counter[category] = commit_counter[category]

            # Ricalcola le percentuali con le categorie aggregate
            total_commits_aggregated = sum(aggregated_counter.values())
            category_percentages_aggregated = {k: (v / total_commits_aggregated) * 100 for k, v in aggregated_counter.items()}

            # Ordina le percentuali in modo discendente
            sorted_categories = dict(sorted(category_percentages_aggregated.items(), key=lambda item: item[1], reverse=True))

            # Crea il grafico a torta con colori unici
            unique_colors = sns.color_palette("flare", len(sorted_categories))
            plt.figure(figsize=(10, 8))
            plt.pie(sorted_categories.values(), labels=sorted_categories.keys(),
                    autopct='%1.1f%%', startangle=140, colors=unique_colors)
            plt.title(f"Distribuzione delle categorie di commit: {file_name}", y=1.05)
            plt.axis('equal')  # Assicura che il grafico sia un cerchio
            plt.show()

    return results


# Esempio di utilizzo
folder_path = "../output_qualitative_commit"  # Sostituisci con il percorso corretto
analyze_commit_categories(folder_path)
