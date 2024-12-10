import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import networkx as nx

# Dati di esempio per gli odori di comunità
data = pd.DataFrame({
    "org.silo": [293, 384, 359, 275, 441, 538, 217, 141, 121, 120, 114, 151],
    "radio.silence": [100, 96, 64, 59, 59, 61, 45, 24, 141, 17, 26, 27],
    "missing.links": [327, 395, 364, 275, 450, 539, 221, 142, 121, 120, 114, 151]
})

# Inizializza le matrici di dominanza e co-occorrenza
columns = data.columns
dominance_matrix = np.zeros((len(columns), len(columns)))
co_occurrence_matrix = np.zeros((len(columns), len(columns)))

# Calcola il rapporto di dominanza e la direzione della dominanza per tutte le coppie di variabili
for i in range(len(columns)):
    for j in range(len(columns)):
        if i != j:
            # Calcola il rapporto di dominanza (normalizzato)
            dominance_ratio = np.abs(data[columns[i]] - data[columns[j]]) / (data[columns[i]] + data[columns[j]] + 1e-9)

            # Calcola la direzione della dominanza (+1 se smell1 > smell2, -1 se smell2 > smell1)
            dominance_direction = np.sign(data[columns[i]] - data[columns[j]])

            # Combinare il rapporto e la direzione
            dominance_matrix[i, j] = np.mean(dominance_ratio * dominance_direction)

            # Calcola la co-occorrenza (quanto spesso gli odori appaiono insieme)
            co_occurrence_matrix[i, j] = np.sum((data[columns[i]] > 0) & (data[columns[j]] > 0))

# Crea i DataFrame per visualizzare le matrici
dominance_df = pd.DataFrame(dominance_matrix, columns=columns, index=columns)
co_occurrence_df = pd.DataFrame(co_occurrence_matrix, columns=columns, index=columns)

# Mostra le matrici
print("Matrice di Dominanza (Rapporto Normalizzato + Direzione):")
print(dominance_df)
print("\nMatrice di Co-occorrenza:")
print(co_occurrence_df)

# Visualizza la matrice di dominanza come heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(dominance_df, annot=True, cmap="coolwarm", center=0, fmt=".2f", cbar_kws={'label': 'Dominance Ratio & Direction'})
plt.title('Matrice di Dominanza (Rapporto Normalizzato + Direzione)')
plt.show()

# Visualizza la matrice di co-occorrenza come heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(co_occurrence_df, annot=True, cmap="Blues", fmt=".2f", cbar_kws={'label': 'Co-occurrence Count'})
plt.title('Matrice di Co-occorrenza')
plt.show()

# Creazione del grafo di dominanza
G_dominance = nx.DiGraph()

# Aggiungi nodi per ciascun community smell
for column in columns:
    G_dominance.add_node(column)

# Aggiungi archi per ogni coppia di odori, con pesi basati sulla dominanza
for i in range(len(columns)):
    for j in range(i + 1, len(columns)):  # Evita di ripetere la stessa coppia
        dominance_weight = dominance_matrix[i, j]
        if dominance_weight != 0:  # Aggiungi l'arco solo se la dominanza non è zero
            G_dominance.add_edge(columns[i], columns[j], weight=dominance_weight)

# Visualizza il grafo della dominanza
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G_dominance)
nx.draw(G_dominance, pos, with_labels=True, node_color="skyblue", node_size=3000, edge_color="gray", font_size=12)
labels = nx.get_edge_attributes(G_dominance, 'weight')
formatted_labels = {k: f'{v:.2f}' for k, v in labels.items()}  # Formatta i pesi con due decimali
nx.draw_networkx_edge_labels(G_dominance, pos, edge_labels=formatted_labels)
plt.title('Grafo di Dominanza tra Odori di Comunità')
plt.show()

# Creazione del grafo di co-occorrenza
G_co_occurrence = nx.Graph()

# Aggiungi nodi per ciascun community smell
for column in columns:
    G_co_occurrence.add_node(column)

# Aggiungi archi per ogni coppia di odori, con pesi basati sulla co-occorrenza
for i in range(len(columns)):
    for j in range(i + 1, len(columns)):  # Evita di ripetere la stessa coppia
        co_occurrence_weight = co_occurrence_matrix[i, j]
        if co_occurrence_weight > 0:  # Aggiungi l'arco solo se la co-occorrenza è maggiore di zero
            G_co_occurrence.add_edge(columns[i], columns[j], weight=co_occurrence_weight)

# Visualizza il grafo della co-occorrenza
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G_co_occurrence)
nx.draw(G_co_occurrence, pos, with_labels=True, node_color="lightgreen", node_size=3000, edge_color="gray", font_size=12)
labels = nx.get_edge_attributes(G_co_occurrence, 'weight')
formatted_labels = {k: f'{v:.2f}' for k, v in labels.items()}  # Formatta i pesi con due decimali
nx.draw_networkx_edge_labels(G_co_occurrence, pos, edge_labels=formatted_labels)
plt.title('Grafo di Co-occorrenza tra Odori di Comunità')
plt.show()