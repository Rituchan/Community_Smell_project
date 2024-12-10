import pandas as pd
import numpy as np
import glob
import os
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx

# Imposta pandas per mostrare tutte le righe e colonne
pd.set_option('display.max_rows', None)  # Mostra tutte le righe
pd.set_option('display.max_columns', None)  # Mostra tutte le colonne
pd.set_option('display.width', 1000)  # Imposta una larghezza massima per evitare troncamenti


# Definisci i community smells da analizzare
#community_smells = ['org.silo', 'prima.donnas', 'radio.silence', 'black.cloud', 'missing.links']
community_smells = ['org.silo', 'radio.silence', 'missing.links']

def process_smells(file_path, community_smells):
    """
    Processa un file CSV per calcolare le matrici di dominanza e co-occorrenza
    per i community smell specificati.
    """
    # Leggi il file
    data = pd.read_csv(file_path)

    # Filtra i dati per i community smell specificati
    data_filtered = data[community_smells].fillna(0)

    # Inizializza le matrici
    columns = data_filtered.columns
    dominance_matrix = np.zeros((len(columns), len(columns)))
    co_occurrence_matrix = np.zeros((len(columns), len(columns)))

    # Calcola le matrici
    for i in range(len(columns)):
        for j in range(len(columns)):
            if i != j:
                dominance_ratio = np.abs(data_filtered[columns[i]] - data_filtered[columns[j]]) / \
                                  (data_filtered[columns[i]] + data_filtered[columns[j]] + 1e-9)
                dominance_direction = np.sign(data_filtered[columns[i]] - data_filtered[columns[j]])
                dominance_matrix[i, j] = np.mean(dominance_ratio * dominance_direction)
                co_occurrence_matrix[i, j] = np.sum((data_filtered[columns[i]] > 0) & (data_filtered[columns[j]] > 0))

    # Crea DataFrame per le matrici
    dominance_df = pd.DataFrame(dominance_matrix, columns=columns, index=columns)
    co_occurrence_df = pd.DataFrame(co_occurrence_matrix, columns=columns, index=columns)

    # Ordina le righe e colonne in modo che siano coerenti
    dominance_df = dominance_df.sort_index(axis=0).sort_index(axis=1)
    co_occurrence_df = co_occurrence_df.sort_index(axis=0).sort_index(axis=1)

    # Imposta la diagonale principale a 0
    np.fill_diagonal(dominance_matrix, 0)
    np.fill_diagonal(co_occurrence_matrix, 0)

    return dominance_df, co_occurrence_df



def aggregate_results(all_dominance_dfs, all_co_occurrence_dfs, project_names):
    """
    Aggrega i risultati tra i progetti per identificare trend generali.
    """
    # Media delle matrici di dominanza
    avg_dominance_df = pd.concat(all_dominance_dfs).groupby(level=0).mean()

    # Media delle matrici di co-occorrenza
    avg_co_occurrence_df = pd.concat(all_co_occurrence_dfs).groupby(level=0).mean()

    # Mostra le matrici aggregate
    print("\nMatrice di Dominanza Media:")
    print(avg_dominance_df)
    print("\nMatrice di Co-occorrenza Media:")
    print(avg_co_occurrence_df)

    # Visualizza le heatmap delle medie
    plt.figure(figsize=(8, 6))
    sns.heatmap(avg_dominance_df, annot=True, cmap="coolwarm", center=0, fmt=".2f",
                cbar_kws={'label': 'Dominance Ratio & Direction'})
    plt.title('Matrice di Dominanza Media (Trend Generali)')
    plt.show()

    plt.figure(figsize=(8, 6))
    sns.heatmap(avg_co_occurrence_df, annot=True, cmap="Blues", fmt=".2f",
                cbar_kws={'label': 'Co-occurrence Count'})
    plt.title('Matrice di Co-occorrenza Media (Trend Generali)')
    plt.show()

    # Identifica i community smells più dominanti e più co-occorrenti
    most_dominant = avg_dominance_df.mean(axis=1).idxmax()
    most_co_occurrent = avg_co_occurrence_df.mean(axis=1).idxmax()

    print(f"Community smell più dominante in media: {most_dominant}")
    print(f"Community smell più co-occorente in media: {most_co_occurrent}")


# Cerca tutti i file _report.csv nella directory corrente
file_list = glob.glob('./*_report.csv')  # Modifica il percorso se necessario

# Liste per salvare i risultati
all_dominance_dfs = []
all_co_occurrence_dfs = []
project_names = []

# Processa ciascun file e salva i risultati
for file in file_list:
    project_name = os.path.basename(file).replace('_report.csv', '')
    project_names.append(project_name)
    print(f"\nProcessing {project_name}...")

    dominance_df, co_occurrence_df = process_smells(file, community_smells)
    all_dominance_dfs.append(dominance_df)
    all_co_occurrence_dfs.append(co_occurrence_df)

# Aggrega e analizza i trend generali
aggregate_results(all_dominance_dfs, all_co_occurrence_dfs, project_names)
