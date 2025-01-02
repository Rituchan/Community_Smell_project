"""
Questo script analizza i commit qualitativi in base a categorie e community smells nel tempo. Per ogni file CSV contenente i dati
dei commit, il codice esegue le seguenti operazioni:

1. Gestisce i valori nulli sostituendoli con un Counter vuoto.
2. Organizza i dati in un DataFrame per rappresentare la distribuzione temporale delle categorie e dei community smells.
3. Filtra le categorie e i community smells selezionati.
4. Crea un grafico a linee combinato che mostra l'evoluzione nel tempo delle categorie e degli smells, utilizzando linee continue per le categorie e linee tratteggiate per gli smells.
5. Salva e mostra il grafico con etichette appropriate e una legenda.

L'obiettivo principale è visualizzare l'andamento delle categorie di commit e dei community smells nel tempo per ogni progetto.
"""


import os
import pandas as pd
import ast
from collections import Counter
import matplotlib.pyplot as plt

# Liste di categorie da visualizzare
selected_categories = ['Bug Fix', 'Merge/Conflict Resolution', 'Feature Addition', 'Dependencies']
selected_smells = ['missing.links', 'org.silo']

# Percorso della directory
dir_path = '../output_qualitative_commit/'  # Percorso della cartella dei file

# Itera sui file nella directory
for file_name in os.listdir(dir_path):
    if file_name.endswith('salt_qualitative.csv'):
        file_path = os.path.join(dir_path, file_name)  # Usa os.path.join per costruire correttamente il percorso

        # Carica i dati dal file CSV
        data = pd.read_csv(file_path)

        # Gestione dei valori nulli: sostituisci con un Counter vuoto
        data['parsed_categories'] = data['commit_categories'].apply(
            lambda x: Counter(ast.literal_eval(x.replace("Counter", ""))) if pd.notna(x) else Counter()
        )

        # Organizza i dati in un DataFrame per la distribuzione temporale
        time_distribution = pd.DataFrame(data['parsed_categories'].tolist(), index=data['range.date']).fillna(0)

        # Escludi l'ultima riga
        time_distribution = time_distribution.iloc[:-1]
        time_distribution.index = time_distribution.index.astype(str)

        # Filtra solo le categorie selezionate
        filtered_distribution = time_distribution[selected_categories].fillna(0)

        # Filtra i community smells
        smell_distribution = data[selected_smells].iloc[:-1].fillna(0)

        # Crea un grafico a linee combinato per le categorie e i community smells
        plt.figure(figsize=(14, 8))

        # Aggiungi le categorie al grafico
        for category in selected_categories:
            if category in filtered_distribution.columns:
                plt.plot(filtered_distribution.index, filtered_distribution[category], label=f"Categoria: {category}")

        # Aggiungi i community smells al grafico
        for smell in selected_smells:
            if smell in smell_distribution.columns:
                plt.plot(smell_distribution.index, smell_distribution[smell], label=f"Smell: {smell}", linestyle='--')

        # Aggiungi etichette, titolo e legenda
        nome_progetto = file_name.split('_qualitative')[0]
        plt.title(f'Distribuzione delle categorie e dei community smells nel tempo per il progetto: {nome_progetto}',
                  fontsize=16)
        plt.xlabel('Intervalli temporali', fontsize=14)
        plt.ylabel('Valore', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.legend(title='Categorie e Smells', fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Mostra il grafico
        plt.show()