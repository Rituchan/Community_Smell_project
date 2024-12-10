import pandas as pd
import os
import glob
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# Directory contenente i file dei report
directory_path = 'C:/Universita/Magistrale/EQS/Community_Smell_project/analysys_data'

# Trova tutti i file CSV nella directory
file_paths = glob.glob(os.path.join(directory_path, "*.csv"))

# Lista per salvare i DataFrame
df_list = []

# Carica tutti i file CSV in DataFrame
for file_path in file_paths:
    project_name = os.path.basename(file_path).split('.')[0]  # Nome progetto dal nome del file
    project_name = project_name.replace("_report", "").strip()
    df_project = pd.read_csv(file_path)
    df_project['Project'] = project_name  # Aggiungi una colonna per il nome del progetto
    df_list.append(df_project)

# Unisci tutti i DataFrame in uno solo
df_all_projects = pd.concat(df_list, ignore_index=True)

# Aggiungi la colonna Cluster in base al progetto (esempio di mappatura manuale)
cluster_mapping = {
    'Django' : 'Cluster negativo',
    'Firefox' : 'Cluster negativo',
    'GitLab' : 'Cluster negativo',
    'Gstreamer' : 'Cluster negativo',
    'iPython' : 'Cluster negativo',
    'Mesa' : 'Cluster negativo',
    'Nodejs' : 'Cluster negativo',
    'Python' : 'Cluster negativo',
    'Rails' : 'Cluster negativo',
    'Salt' : 'Cluster negativo',
}
df_all_projects['Cluster'] = df_all_projects['Project'].map(cluster_mapping)



def calculate_correlation_per_project(df_cluster, metric, cluster_name, output_directory):
    # Crea la directory di output se non esiste
    os.makedirs(output_directory, exist_ok=True)

    # Ottieni l'elenco dei progetti unici nel cluster
    unique_projects = df_cluster['Project'].unique()

    for project in unique_projects:
        # Filtra i dati per il progetto specifico
        df_project = df_cluster[df_cluster['Project'] == project]

        # Filtra solo le colonne numeriche
        df_project_numeric = df_project.select_dtypes(include=['float64', 'int64'])

        # Rimuovi colonne con varianza nulla e valori NaN
        df_project_numeric = df_project_numeric.loc[:, df_project_numeric.var() > 0].dropna(axis=1, how='all')

        if metric in df_project_numeric.columns:
            # Calcola la correlazione della metrica con le altre colonne
            correlation_with_metric = df_project_numeric.corrwith(df_project_numeric[metric])

            # Salva i risultati in un CSV
            output_file = os.path.join(output_directory, f"{project}_{metric}_correlations.csv")
            correlation_with_metric.to_csv(output_file, header=['Correlation'], index_label='Metric')
            print(f"File salvato: {output_file}")

            # Visualizza la correlazione
            print(f"\nCorrelazione con '{metric}' per il progetto '{project}' nel {cluster_name}:")
            print(correlation_with_metric)

            # Visualizzazione grafica
            correlation_with_metric.drop(metric, errors='ignore').sort_values().plot(kind='barh', figsize=(10, 6),
                                                                                     color='skyblue')
            plt.title(f"Correlazione di '{metric}' con altre metriche - Progetto '{project}' ({cluster_name})")
            plt.xlabel("Correlazione")
            plt.ylabel("Metriche")
            plt.show()
        else:
            print(f"La metrica '{metric}' non è presente nei dati del progetto '{project}' ({cluster_name}).")

output_directory = 'C:/Universita/Magistrale/EQS/Community_Smell_project/correlation_'  # Sostituisci con il percorso desiderato
# Cluster positivi (es. NodeJs)
cluster_positivo = df_all_projects[df_all_projects['Cluster'] == 'Cluster positivo']

# Cluster negativi (es. Firefox, Vagrant)
cluster_negativo = df_all_projects[df_all_projects['Cluster'] == 'Cluster negativo']

# Metrica di interesse
metric = 'mail.mod'

# Calcola e salva la correlazione per ogni progetto nel Cluster Positivo
print("\n--- Correlazioni nel Cluster Positivo ---")
calculate_correlation_per_project(cluster_positivo, metric, "Cluster Positivo", output_directory)

# Calcola e salva la correlazione per ogni progetto nel Cluster Negativo
print("\n--- Correlazioni nel Cluster Negativo ---")
calculate_correlation_per_project(cluster_negativo, metric, "Cluster Negativo", output_directory)



'''
# 2. Test statistici per differenze tra cluster
metrics = ['core.mail.turnover', 'missing.links']  # Sostituisci con le tue metriche reali

# Risultati dei test T
t_test_results = {}

for metric in metrics:
    if metric in cluster_positivo.columns and metric in cluster_negativo.columns:
        # Estrai le metriche per ogni cluster, gestendo i valori mancanti
        data_pos = cluster_positivo[metric].dropna()
        data_neg = cluster_negativo[metric].dropna()

        # Esegui il T-test
        t_stat, p_value = ttest_ind(data_pos, data_neg)

        # Salva i risultati
        t_test_results[metric] = {'t_statistic': t_stat, 'p_value': p_value}
    else:
        print(f"Attenzione: La metrica '{metric}' non è presente in uno dei cluster.")

# Visualizza i risultati dei test T
for metric, results in t_test_results.items():
    print(f"Metrica: {metric}")
    print(f"T-statistic: {results['t_statistic']:.3f}, P-value: {results['p_value']:.3f}")
    print("Differenza significativa?", "Sì" if results['p_value'] < 0.05 else "No")
    print("-" * 40)

# 3. Visualizzazione delle metriche tra i cluster per un confronto diretto
# Confronto per una metrica (esempio con 'missing.links')
if 'missing.links' in df_all_projects.columns:
    sns.boxplot(x='Cluster', y='missing.links', data=df_all_projects.dropna(subset=['missing.links']))
    plt.title('Confronto di Missing Links tra Cluster Positivi e Negativi')
    plt.show()
else:
    print("La metrica 'missing.links' non è presente nei dati.")
'''