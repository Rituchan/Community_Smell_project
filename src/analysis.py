import pandas as pd
import os
import glob
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# Directory contenente i file dei report
directory_path = 'C:/Universita/Magistrale/EQS/Community_Smell_project/report'

# Trova tutti i file CSV nella directory
file_paths = glob.glob(os.path.join(directory_path, "*.csv"))

# Lista per salvare i DataFrame
df_list = []

# Carica tutti i file CSV in DataFrame
for file_path in file_paths:
    project_name = os.path.basename(file_path).split('.')[0]  #basename restituisce il nome del file senza estensione
    project_name = project_name.replace("_report", "").strip()
    df_project = pd.read_csv(file_path)
    df_project['Project'] = project_name  # Aggiungi una colonna per il nome del progetto
    df_list.append(df_project)

# Unisci tutti i DataFrame in uno solo
df_all_projects = pd.concat(df_list, ignore_index=True)

# Aggiungi la colonna Cluster in base al progetto (se necessario)
# Esempio: mappa manualmente i progetti ai rispettivi cluster (positivo/negativo)
cluster_mapping = {
    'GitLab': 'Cluster positivo',
    'LLVM': 'Cluster positivo',
    'Salt': 'Cluster positivo',
    'U-boot': 'Cluster positivo',
    'Bitcoin': 'Cluster negativo',
    'Django': 'Cluster negativo',
    'Firefox': 'Cluster negativo',
    'QEMU': 'Cluster negativo',
}

df_all_projects['Cluster'] = df_all_projects['Project'].map(cluster_mapping) # Aggiungi la colonna Cluster

# Verifica la struttura del DataFrame unito
print(df_all_projects.head())

# 1. Correlazione delle metriche all'interno di ciascun cluster
# Separazione dei cluster
cluster_positivo = df_all_projects[df_all_projects['Cluster'] == 'Cluster positivo']
cluster_negativo = df_all_projects[df_all_projects['Cluster'] == 'Cluster negativo']

# Matrice di correlazione per il cluster positivo
corr_positivo = cluster_positivo.corr()

# Matrice di correlazione per il cluster negativo
corr_negativo = cluster_negativo.corr()

# Visualizzazione delle matrici di correlazione
plt.figure(figsize=(12, 6))
sns.heatmap(corr_positivo, annot=True, cmap='coolwarm', fmt='.2f', cbar=True)
plt.title('Correlazione tra metriche - Cluster Positivo')
plt.show()

plt.figure(figsize=(12, 6))
sns.heatmap(corr_negativo, annot=True, cmap='coolwarm', fmt='.2f', cbar=True)
plt.title('Correlazione tra metriche - Cluster Negativo')
plt.show()

# 2. Test statistici per differenze tra cluster
metrics = ['', 'ratio.smelly.quitters', 'altre_metriche']  # Sostituisci con le tue metriche reali

# Risultati dei test T
t_test_results = {}

for metric in metrics:
    # Estrazione delle metriche per ogni cluster
    data_pos = cluster_positivo[metric].dropna()
    data_neg = cluster_negativo[metric].dropna()

    # Esegui il T-test
    t_stat, p_value = ttest_ind(data_pos, data_neg)

    # Salva i risultati
    t_test_results[metric] = {'t_statistic': t_stat, 'p_value': p_value}

# Visualizza i risultati dei test T
for metric, results in t_test_results.items():
    print(f"Metrica: {metric}")
    print(f"T-statistic: {results['t_statistic']:.3f}, P-value: {results['p_value']:.3f}")
    print("Differenza significativa?" , "Sì" if results['p_value'] < 0.05 else "No")
    print("-" * 40)

# 3. Visualizzazione delle metriche tra i cluster per un confronto diretto
# Confronto per una metrica (esempio con 'missing.links')
sns.boxplot(x='Cluster', y='missing.links', data=df_all_projects)
plt.title('Confronto di Missing Links tra Cluster Positivi e Negativi')
plt.show()
