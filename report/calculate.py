import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt
import networkx as nx

# Definisci i community smells da analizzare
community_smells = ['org.silo', 'prima.donnas', 'radio.silence', 'black.cloud', 'missing.links']
#community_smells = ['org.silo', 'radio.silence', 'missing.links']

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
    co_occurrence_matrix = np.zeros((len(columns), len(columns))) #zeros crea una matrice di zeri

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

    return dominance_df, co_occurrence_df


def visualize_graphs(dominance_df, co_occurrence_df, project_name):
    """
    Crea e visualizza grafi basati sulle matrici di dominanza e co-occorrenza.
    """
    # Creazione del grafo di dominanza
    G_dominance = nx.DiGraph()
    columns = dominance_df.columns

    for column in columns:
        G_dominance.add_node(column)

    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            dominance_weight = dominance_df.iloc[i, j]
            if dominance_weight != 0:
                G_dominance.add_edge(columns[i], columns[j], weight=dominance_weight)

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G_dominance)
    nx.draw(G_dominance, pos, with_labels=True, node_color="skyblue", node_size=3000, edge_color="gray", font_size=12)
    labels = nx.get_edge_attributes(G_dominance, 'weight')
    formatted_labels = {k: f'{v:.2f}' for k, v in labels.items()}
    nx.draw_networkx_edge_labels(G_dominance, pos, edge_labels=formatted_labels)
    plt.title(f'Grafo di Dominanza - {project_name}')
    plt.show()

    # Creazione del grafo di co-occorrenza
    G_co_occurrence = nx.Graph()

    for column in columns:
        G_co_occurrence.add_node(column)

    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            co_occurrence_weight = co_occurrence_df.iloc[i, j]
            if co_occurrence_weight > 0:
                G_co_occurrence.add_edge(columns[i], columns[j], weight=co_occurrence_weight)

    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G_co_occurrence)
    nx.draw(G_co_occurrence, pos, with_labels=True, node_color="lightgreen", node_size=3000, edge_color="gray",
            font_size=12)
    labels = nx.get_edge_attributes(G_co_occurrence, 'weight')
    formatted_labels = {k: f'{v:.2f}' for k, v in labels.items()}
    nx.draw_networkx_edge_labels(G_co_occurrence, pos, edge_labels=formatted_labels)
    plt.title(f'Grafo di Co-occorrenza - {project_name}')
    plt.show()


# Cerca tutti i file _report.csv nella directory corrente
file_list = glob.glob('./*_report.csv')  # Modifica il percorso se necessario

# Processa ciascun file e salva i risultati
for file in file_list:
    project_name = os.path.basename(file).replace('_report.csv', '')
    print(f"\nProcessing {project_name}...")

    dominance_df, co_occurrence_df = process_smells(file, community_smells)

    # Visualizza le matrici
    print(f"\nProgetto: {project_name}")
    print("Matrice di Dominanza:")
    print(dominance_df)
    print("\nMatrice di Co-occorrenza:")
    print(co_occurrence_df)

    '''
    # Visualizza come heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(dominance_df, annot=True, cmap="coolwarm", center=0, fmt=".2f",
                cbar_kws={'label': 'Dominance Ratio & Direction'})
    plt.title(f'Matrice di Dominanza - {project_name}')
    plt.show()

    plt.figure(figsize=(8, 6))
    sns.heatmap(co_occurrence_df, annot=True, cmap="Blues", fmt=".2f",
                cbar_kws={'label': 'Co-occurrence Count'})
    plt.title(f'Matrice di Co-occorrenza - {project_name}')
    plt.show()
    '''
    # Visualizza i grafi
    visualize_graphs(dominance_df, co_occurrence_df, project_name)
