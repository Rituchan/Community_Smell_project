import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.metrics import silhouette_score
import matplotlib.pyplot as plt

# Funzione per caricare e combinare i dataset
def load_data(directory):
    all_data = []
    for file in os.listdir(directory):
        if file.endswith('_report.csv'):
            file_path = os.path.join(directory, file)
            data = pd.read_csv(file_path)
            all_data.append(data)
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

# Funzione per eseguire il clustering
def clustering_analysis(data):
    # Preprocessing
    features = ['org.silo', 'prima.donnas', 'radio.silence', 'black.cloud', 'missing.links']
    X = data[features].fillna(0)  # Sostituisci i valori mancanti con 0
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K-Means Clustering
    print("Eseguendo K-Means...")
    inertia = []
    silhouette_scores = []
    for k in range(2, 11):
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(X_scaled)
        inertia.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, labels))

    # Elbow Method
    plt.figure(figsize=(10, 5))
    plt.plot(range(2, 11), inertia, marker='o')
    plt.title("Elbow Method")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Inertia")
    plt.show()

    # Silhouette Scores
    plt.figure(figsize=(10, 5))
    plt.plot(range(2, 11), silhouette_scores, marker='o')
    plt.title("Silhouette Scores")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Silhouette Score")
    plt.show()

    optimal_k = silhouette_scores.index(max(silhouette_scores)) + 2
    print(f"Numero ottimale di cluster secondo il Silhouette Score: {optimal_k}")

    kmeans = KMeans(n_clusters=optimal_k, random_state=42)
    kmeans_labels = kmeans.fit_predict(X_scaled)

    # DBSCAN
    print("Eseguendo DBSCAN...")
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    dbscan_labels = dbscan.fit_predict(X_scaled)

    # Agglomerative Clustering
    print("Eseguendo Agglomerative Clustering...")
    agglomerative = AgglomerativeClustering(n_clusters=optimal_k)
    agglomerative_labels = agglomerative.fit_predict(X_scaled)

    # Risultati
    data['KMeans_Cluster'] = kmeans_labels
    data['DBSCAN_Cluster'] = dbscan_labels
    data['Agglomerative_Cluster'] = agglomerative_labels

    return data

# Funzione principale
def main():
    directory = "/Users/marco/PycharmProjects/Community_Smell_project/report"  # Sostituisci con il percorso della directory
    data = load_data(directory)
    print("Dataset combinato:")
    print(data.head())

    clustered_data = clustering_analysis(data)
    print("Dati con clustering:")
    print(clustered_data.head())

    # Salva i risultati
    clustered_data.to_csv("clustered_results.csv", index=False)
    print("Risultati salvati in clustered_results.csv")

if __name__ == "__main__":
    main()
