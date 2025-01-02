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
def make_stationary(df, smells, output_file):
    with open(output_file, 'a') as f:
        for smell in smells:
            # Verifica se la serie è costante (varianza = 0)
            if df[smell].var() == 0:
                f.write(f"Serie costante per {smell}. Test ADF non eseguito.\n")
                continue  # Salta il test di ADF per questa serie

            # Esegui il test ADF per verificare la stazionarietà
            result = adfuller(df[smell])
            p_value = result[1]
            if p_value > 0.05:
                # Se p-value > 0.05, la serie non è stazionaria, quindi la differenziamo
                df[smell] = df[smell].diff().dropna()
                f.write(f"{smell}: Serie non stazionaria, differenziata.\n")
            else:
                f.write(f"{smell}: Serie stazionaria (p-value={p_value:.3f}).\n")
    return df


# Funzione per eseguire il test di Granger e salvare i risultati su un file
def granger_causality_test(df, smells, max_lag=1, output_file="../granger_results/granger_results.txt"):
    with open(output_file, 'a') as f:
        for smell1 in smells:
            for smell2 in smells:
                if smell1 != smell2:
                   # f.write(f"\nTest di Granger: {smell1} causa {smell2}\n")
                    data = df[[smell1, smell2]].dropna()

                    if len(data) > max_lag:
                        try:
                            gc_test = grangercausalitytests(data, max_lag)
                            # Estrai solo i risultati rilevanti per l'interpretazione (p-value)
                            p_value = gc_test[max_lag][0]['ssr_chi2test'][1]
                            if p_value < 0.05:
                                f.write(f"\nTest di Granger: {smell1} causa {smell2}\n")
                                f.write(f"Significativo: {smell1} causa {smell2} (p-value={p_value:.3f})\n")
                            else:
                                print(f"Non significativo: {smell1} non causa {smell2} (p-value={p_value:.3f})\n")
                        except Exception as e:
                            print(f"Errore nel test di Granger tra {smell1} e {smell2}: {e}\n")
                    else:
                        print(f"Dati insufficienti per il test di Granger tra {smell1} e {smell2}.\n")


# Funzione per processare tutti i file nella directory
def process_all_files_in_directory(directory_path, smells, output_file="../granger_results/granger_results.txt"):
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
            df = make_stationary(df, smells, output_file)

            # Esegui il test di Granger
            granger_causality_test(df, smells, output_file=output_file)


# Imposta il percorso della cartella contenente i file CSV
directory_path = "../report"
community_smells = ['prima.donnas', 'black.cloud', 'radio.silence', 'missing.links', 'org.silo']

# Esegui il processo
process_all_files_in_directory(directory_path, community_smells)
