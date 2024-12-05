import os
import pandas as pd

# Percorso della cartella contenente i file CSV
folder_path = 'C:/Universita/Magistrale/EQS/Community_Smell_project/spearman-pvalue'  # Sostituisci con il percorso della tua cartella

# Specifica le colonne da controllare
columns_to_check = ['code.turnover', 'core.code.turnover', 'core.global.turnover', 'global.turnover', 'ratio.smelly.turnover', 'core.mail.turnover']  # Modifica con i nomi delle colonne

# Lista per salvare tutti i risultati
all_results = []

# Analizza ogni file nella cartella
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):  # Considera solo i file CSV
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path)

        # Controlla ogni colonna specificata
        for col in columns_to_check:
            if col in df.columns:  # Verifica che la colonna esista
                for idx, value in df[col].items():
                    if value <= 0.05:

                        all_results.append({
                            'File': filename,
                            'Colonna': col,
                            'Indice Riga': idx,
                            'Valore': value
                        })

# Crea un DataFrame dai risultati
results_df = pd.DataFrame(all_results)

# Salva i risultati in un file CSV
output_file = 'risultati_analisi_spearman-pvalue.csv'
results_df.to_csv(output_file, index=False)

print(f"Analisi completata. Risultati salvati in '{output_file}'.")
