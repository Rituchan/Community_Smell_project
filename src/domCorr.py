import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Dati
data = pd.DataFrame({
    "org.silo": [293, 384, 359, 275, 441, 538, 217, 141, 121, 120, 114, 151],
    "radio.silence": [100, 96, 64, 59, 59, 61, 45, 24, 141, 17, 26, 27],
    "missing.links": [327, 395, 364, 275, 450, 539, 221, 142, 121, 120, 114, 151]
})

# Crea una matrice di dominanza
columns = data.columns
dominance_matrix = np.zeros((len(columns), len(columns)))
correlation_matrix = np.zeros((len(columns), len(columns)))

# Calcola il rapporto, la direzione di dominanza e la correlazione per tutte le coppie di variabili
for i in range(len(columns)):
    for j in range(len(columns)):
        if i != j:
            # Calcola il rapporto di dominanza (normalizzato)
            dominance_ratio = np.abs(data[columns[i]] - data[columns[j]]) / (data[columns[i]] + data[columns[j]] + 1e-9)

            # Calcola la direzione della dominanza (+1 se smell1 > smell2, -1 se smell2 > smell1)
            dominance_direction = np.sign(data[columns[i]] - data[columns[j]])

            # Combinare il rapporto e la direzione e calcolare la media
            dominance_matrix[i, j] = np.mean(dominance_ratio * dominance_direction)

            # Calcolare la correlazione tra le due variabili
            correlation_matrix[i, j] = np.corrcoef(data[columns[i]], data[columns[j]])[0, 1]

# Creare DataFrame dalla matrice di dominanza e correlazione
dominance_df = pd.DataFrame(dominance_matrix, columns=columns, index=columns)
correlation_df = pd.DataFrame(correlation_matrix, columns=columns, index=columns)

# Mostra le matrici
print("Matrice di Dominanza (Rapporto Normalizzato + Direzione):")
print(dominance_df)
print("\nMatrice di Correlazione:")
print(correlation_df)

# Visualizzare la matrice di dominanza come heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(dominance_df, annot=True, cmap="coolwarm", center=0, fmt=".2f",
            cbar_kws={'label': 'Dominance Ratio & Direction'})
plt.title('Matrice di Dominanza (Rapporto Normalizzato + Direzione)')
plt.show()

# Visualizzare la matrice di correlazione come heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_df, annot=True, cmap="coolwarm", center=0, fmt=".2f",
            cbar_kws={'label': 'Correlation Coefficient'})
plt.title('Matrice di Correlazione')
plt.show()

# Aggiungere grafico del cambiamento del rapporto di dominanza nel tempo per ogni coppia di colonne
plt.figure(figsize=(10, 6))

# Itera attraverso tutte le coppie di colonne
for i in range(len(columns)):
    for j in range(i + 1, len(columns)):  # Evita di ripetere la stessa coppia
        # Calcola il rapporto di dominanza per ogni riga del DataFrame
        dominance_ratio_series = np.abs(data[columns[i]] - data[columns[j]]) / (
                    data[columns[i]] + data[columns[j]] + 1e-9)

        # Traccia il grafico per il rapporto di dominanza
        plt.plot(dominance_ratio_series, label=f'{columns[i]} vs {columns[j]} (Rapporto)', linestyle='--')

# Aggiungere dettagli al grafico
plt.title('Evoluzione del Rapporto di Dominanza nel Tempo')
plt.xlabel('Tempo (Indici delle Righe)')
plt.ylabel('Rapporto di Dominanza')
plt.legend()
plt.grid(True)
plt.show()

# Aggiungere grafico della direzione della dominanza nel tempo per ogni coppia di colonne
plt.figure(figsize=(10, 6))

# Itera attraverso tutte le coppie di colonne
for i in range(len(columns)):
    for j in range(i + 1, len(columns)):  # Evita di ripetere la stessa coppia
        # Calcola la direzione della dominanza per ogni riga del DataFrame (+1 o -1)
        dominance_direction_series = np.sign(data[columns[i]] - data[columns[j]])

        # Traccia il grafico per la direzione di dominanza
        plt.plot(dominance_direction_series, label=f'{columns[i]} vs {columns[j]} (Direzione)', linestyle='-')

# Aggiungere dettagli al grafico
plt.title('Evoluzione della Direzione della Dominanza nel Tempo')
plt.xlabel('Tempo (Indici delle Righe)')
plt.ylabel('Direzione di Dominanza (+1 o -1)')
plt.legend()
plt.grid(True)
plt.show()

# Aggiungere grafico della correlazione nel tempo per ogni coppia di colonne
plt.figure(figsize=(10, 6))

# Itera attraverso tutte le coppie di colonne
for i in range(len(columns)):
    for j in range(i + 1, len(columns)):  # Evita di ripetere la stessa coppia
        # Calcola la correlazione per ogni riga del DataFrame
        correlation_series = np.corrcoef(data[columns[i]], data[columns[j]])[0, 1]

        # Traccia il grafico per la correlazione
        plt.plot([correlation_series] * len(data), label=f'{columns[i]} vs {columns[j]} (Correlazione)', linestyle='-.')

# Aggiungere dettagli al grafico
plt.title('Evoluzione della Correlazione nel Tempo')
plt.xlabel('Tempo (Indici delle Righe)')
plt.ylabel('Coefficiente di Correlazione')
plt.legend()
plt.grid(True)
plt.show()
