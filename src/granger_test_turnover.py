"""
Questo script carica i dati da file CSV contenenti informazioni su community smells, verifica la stazionarietà delle serie temporali,
differenziandole se necessario, e successivamente esegue il test di causalità di Granger per analizzare le relazioni di causa-effetto
tra diverse serie temporali. I risultati vengono salvati in un file di testo. Il processo è applicato a tutti i file nella directory
indicata.
"""

import os
import pandas as pd
from statsmodels.tsa.stattools import adfuller, grangercausalitytests

# Funzione per caricare e preprocessare i dati
def load_and_preprocess_data(filename):
    df = pd.read_csv(filename)
    return df

# Funzione per verificare la stazionarietà dei dati e differenziarli se necessario
def make_stationary(df, variables, output_file):
    with open(output_file, 'a') as f:
        for var in variables:
            # Verifica se la serie è costante (varianza = 0)
            if df[var].var() == 0:
                f.write(f"Serie costante per {var}. Test ADF non eseguito.\n")
                continue  # Salta il test di ADF per questa serie

            # Esegui il test ADF per verificare la stazionarietà
            result = adfuller(df[var])
            p_value = result[1]
            if p_value > 0.05:
                # Se p-value > 0.05, la serie non è stazionaria, quindi la differenziamo
                df[var] = df[var].diff().dropna()
                f.write(f"{var}: Serie non stazionaria, differenziata.\n")
            else:
                f.write(f"{var}: Serie stazionaria (p-value={p_value:.3f}).\n")
    return df

# Funzione per eseguire il test di Granger e salvare i risultati su un file
def granger_causality_test(df, smells, metrics, max_lag=1, output_file="../granger_results/granger_results_turnover.txt"):
    with open(output_file, 'a') as f:
        for smell in smells:
            for metric in metrics:
                data = df[[smell, metric]].dropna()
                if len(data) > max_lag:
                    try:
                        gc_test = grangercausalitytests(data, max_lag)
                        # Estrai solo i risultati rilevanti per l'interpretazione (p-value)
                        p_value = gc_test[max_lag][0]['ssr_chi2test'][1]
                        if p_value < 0.05:
                            f.write(f"\nTest di Granger: {metric} causa {smell}\n")
                            f.write(f"Significativo: {metric} causa {smell} (p-value={p_value:.3f})\n")
                        else:
                            print(f"Non significativo: {metric} non causa {smell} (p-value={p_value:.3f})\n")
                    except Exception as e:
                       print(f"Errore nel test di Granger tra {metric} e {smell}: {e}\n")
                else:
                    f.write(f"Dati insufficienti per il test di Granger tra {metric} e {smell}.\n")

# Funzione per processare tutti i file nella directory
def process_all_files_in_directory(directory_path, smells, metrics, output_file="../granger_results/ granger_results_turnover.txt"):
    with open(output_file, 'w') as f:
        f.write("=== Risultati Test di Granger ===\n")

    for filename in os.listdir(directory_path):
        if filename.endswith("_report.csv"):
            full_path = os.path.join(directory_path, filename)
            project_name = os.path.splitext(filename)[0]  # Nome del progetto (senza estensione)

            with open(output_file, 'a') as f:
                f.write(f"\n\n=== Risultati per il progetto: {project_name} ===\n")

            df = load_and_preprocess_data(full_path)

            # Rendi i dati stazionari
            df = make_stationary(df, smells + metrics, output_file)

            # Esegui il test di Granger
            granger_causality_test(df, smells, metrics, output_file=output_file)

# Imposta il percorso della cartella contenente i file CSV
directory_path = "../report"
community_smells = ['prima.donnas', 'black.cloud', 'radio.silence', 'missing.links', 'org.silo']
metrics = ['global.turnover', 'code.turnover', 'core.global.turnover', 'core.mail.turnover', 'core.code.turnover', 'ratio.smelly.quitters']

# Esegui il processo
process_all_files_in_directory(directory_path, community_smells, metrics)
