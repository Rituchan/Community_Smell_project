import os
import pandas as pd

# Percorso della cartella contenente i file
folder_path = 'C:/Universita/Magistrale/EQS/Community_Smell_project/spearman-estimate'  # Sostituisci con il percorso corretto

# Inizializzazione del dizionario per i cluster
clusters = {"Cluster positivo": [], "Cluster negativo": [], "Cluster neutro": []}

# Ciclo per leggere i file nella cartella
for file_name in os.listdir(folder_path):
    if file_name.endswith("spearman-estimate.csv"):
        file_path = os.path.join(folder_path, file_name)

        # Carica il file CSV
        data = pd.read_csv(file_path, index_col=0)

        # Estrai il valore della correlazione
        try:
            correlation_value = data.loc['black.cloud', 'core.mail.turnover']
        except KeyError:
            print(f"Errore nel file {file_name}: 'community smell' o 'metrica' non trovati.")
            continue
        # Determina il cluster
        if correlation_value >= 0.4:
            cluster = "Cluster positivo"
        elif correlation_value <= -0.4:
            cluster = "Cluster negativo"
        else:
            cluster = "Cluster neutro"

        # Aggiungi il file al cluster corrispondente
        project_name = file_name.replace("spearman-estimate.csv", "").strip()
        clusters[cluster].append(project_name)

# Trasforma i cluster in un DataFrame per salvare l'output
output_data = []
for cluster_name, project_list in clusters.items():
    for project in project_list:
        output_data.append({"Project": project, "Cluster": cluster_name})

output_df = pd.DataFrame(output_data)

# Salva il risultato in un file CSV
output_file = 'C:/Universita/Magistrale/EQS/Community_Smell_project/data_dir_spearman/black_cloud-core_mail_turnover.csv'
output_df.to_csv(output_file, index=False)

print(f"Risultato salvato in {output_file}")

