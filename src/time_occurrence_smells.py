import matplotlib.pyplot as plt
import pandas as pd
import glob
import os


def plot_dominance_over_time(file_path, community_smells):
    """
    Analizza l'andamento temporale della dominanza basandosi sulle occorrenze
    dei community smell in ciascun periodo temporale definito dalla colonna `range.date`.

    :param file_path: Path del file CSV.
    :param community_smells: Lista dei community smell da analizzare.
    """
    # Leggi il file
    data = pd.read_csv(file_path)

    # Filtra i dati per i community smell specificati e la colonna `range.date`
    data_filtered = data[['range.date'] + community_smells].fillna(0)

    # Inizializza una lista per i risultati
    time_slots = data_filtered['range.date'].unique()

    # Crea il grafico
    plt.figure(figsize=(12, 6))

    # Colori per ogni smell (assumendo che ci siano al massimo 5 smells)
    colors = ['b', 'g', 'r', 'c', 'm']

    # Cicla attraverso ogni smell e tracciarlo separatamente
    for idx, smell in enumerate(community_smells):
        plt.plot(time_slots, data_filtered[smell], marker='o', linestyle='-', color=colors[idx], label=smell)

    # Aggiungi il nome dello smell dominante ai punti
    for idx, smell in enumerate(community_smells):
        for i, count in enumerate(data_filtered[smell]):
            plt.text(i, count, f'{count:.0f}', ha='center', fontsize=9, color=colors[idx])

    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Intervalli Temporali')
    plt.ylabel('Numero di Occorrenze')
    plt.title(
        f"Andamento dell'Occorrenza dei Community Smell nel Tempo - {os.path.basename(file_path).replace('_report.csv', '')}")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Community Smells', loc='upper left')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Cerca tutti i file _report.csv nella directory specificata
    file_list = glob.glob('../report/*_report.csv')  # Modifica il percorso se necessario

    # Definisci i community smells da analizzare
    community_smells = ['org.silo', 'prima.donnas', 'radio.silence', 'black.cloud', 'missing.links']

    # Processa ciascun file
    for file_path in file_list:
        project_name = os.path.basename(file_path).replace('_report.csv', '')
        print(f"\nProcessing {project_name}...")

        # Esegui l'analisi per ciascun file
        plot_dominance_over_time(file_path, community_smells)
