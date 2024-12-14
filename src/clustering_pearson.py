import os
import pandas as pd

# Percorso della cartella contenente i file
folder_path = '/Users/marco/PycharmProjects/Community_Smell_project/pearson-estimate'
pvalue_folder_path = '/Users/marco/PycharmProjects/Community_Smell_project/pearson_p-value'
output_folder = '/Users/marco/PycharmProjects/Community_Smell_project/data_dir_pearson'

# Community smells e metriche
data_pairs = {
    "Community Smell": ['prima.donnas', 'black.cloud', 'radio.silence', 'missing.links', 'org.silo'],
    "Metriche": ['global.turnover', 'code.turnover', 'core.global.turnover', 'core.mail.turnover', 'core.code.turnover', 'ratio.smelly.quitters']
}

# Soglia per p-value
pvalue_threshold = 0.05

# Assicura che la cartella di output esista
os.makedirs(output_folder, exist_ok=True)

# Ciclo per ogni combinazione di community smell e metrica
for smell in data_pairs["Community Smell"]:
    for metric in data_pairs["Metriche"]:
        # Inizializzazione del dizionario per i cluster
        clusters = {"Cluster positivo": [], "Cluster negativo": [], "Cluster neutro": []}

        # Ciclo per leggere i file nella cartella
        for file_name in os.listdir(folder_path):
            if file_name.endswith("pearson-estimate.csv"):
                file_path = os.path.join(folder_path, file_name)
                pvalue_file_path = os.path.join(pvalue_folder_path, file_name.replace("_pearson-estimate.csv", "_pearson-pvalue.csv"))

                # Carica il file CSV di correlazione e p-value
                data = pd.read_csv(file_path, index_col=0)
                pvalue_data = pd.read_csv(pvalue_file_path, index_col=0)

                # Estrai il valore della correlazione e del p-value
                try:
                    correlation_value = data.loc[smell, metric]
                    p_value = pvalue_data.loc[smell, metric]
                except KeyError:
                    print(f"Errore nel file {file_name}: '{smell}' o '{metric}' non trovati.")
                    continue

                # Applica la condizione del p-value
                if p_value > pvalue_threshold:
                    continue

                # Ignora i progetti con correlazione nulla
                if pd.isna(correlation_value):
                    continue

                # Determina il cluster
                if correlation_value >= 0.2:
                    cluster = "Cluster positivo"
                elif correlation_value <= -0.2:
                    cluster = "Cluster negativo"
                else:
                    cluster = "Cluster neutro"

                # Aggiungi il file al cluster corrispondente
                project_name = file_name.replace("pearson-estimate.csv", "").strip()
                clusters[cluster].append((project_name, correlation_value, p_value))

        # Trasforma i cluster in un DataFrame per salvare l'output
        output_data = []
        for cluster_name, project_list in clusters.items():
            for project, correlation_value, p_value in project_list:
                output_data.append({
                    "Project": project,
                    "Cluster": cluster_name,
                    "Correlation": correlation_value,
                    "P-Value": p_value
                })

        output_df = pd.DataFrame(output_data)

        # Salva il risultato solo se il DataFrame non è vuoto
        if not output_df.empty:
            output_file = os.path.join(output_folder, f'{smell}_{metric}_clusters.csv')
            output_df.to_csv(output_file, index=False)
            print(f"Risultato per {smell} e {metric} salvato in {output_file}")
        else:
            print(f"Nessun dato valido per {smell} e {metric}, file non salvato.")

