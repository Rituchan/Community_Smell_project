import os
import pandas as pd
from itertools import product


# Percorso della cartella contenente i file
folder_path = '/Users/marco/PycharmProjects/Community_Smell_project/pearson-estimate'
output_dir = '/Users/marco/PycharmProjects/Community_Smell_project/data_dir_pearson'
os.makedirs(output_dir, exist_ok=True)

# Array per le combinazioni
community_smells = ['org.silo', 'prima.donnas', 'radio.silence', 'black.cloud', 'missing.links']
metrics = [
    'global.turnover', 'code.turnover', 'core.global.turnover', 'core.mail.turnover',
    'core.code.turnover', 'ratio.smelly.quitters'
]

# Inizializzazione del dizionario per i cluster
for smell, metric in product(community_smells, metrics):
    clusters = {"Cluster positivo": [], "Cluster negativo": [], "Cluster neutro": []}

    # Ciclo per leggere i file nella cartella
    for file_name in os.listdir(folder_path):
        if file_name.endswith("pearson-estimate.csv"):
            file_path = os.path.join(folder_path, file_name)

            # Carica il file CSV
            data = pd.read_csv(file_path, index_col=0)

            # Estrai il valore della correlazione
            try:
                correlation_value = data.loc[smell, metric]
            except KeyError:
                print(f"Errore nel file {file_name}: '{smell}' o '{metric}' non trovati.")
                continue

            # Determina il cluster
            if correlation_value >= 0.3:
                cluster = "Cluster positivo"
            elif correlation_value <= -0.3:
                cluster = "Cluster negativo"
            else:
                cluster = "Cluster neutro"

            # Aggiungi il file al cluster corrispondente
            project_name = file_name.replace("pearson-estimate.csv", "").strip()
            clusters[cluster].append((project_name, correlation_value))

    # Trasforma i cluster in un DataFrame per salvare l'output
    output_data = []
    for cluster_name, project_list in clusters.items():
        for project, correlation in project_list:
            output_data.append({"Project": project, "Cluster": cluster_name, "Correlation Value": correlation})

    output_df = pd.DataFrame(output_data)

    # Salva il risultato in un file CSV
    output_file = os.path.join(output_dir, f"{smell.replace('.', '_')}-{metric.replace('.', '_')}.csv")
    output_df.to_csv(output_file, index=False)

    print(f"Risultato salvato in {output_file}")
