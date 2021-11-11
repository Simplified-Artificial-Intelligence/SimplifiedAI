from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
import pickle


# Save Model In artifacts
def save_model(model, path):
    pickle.dump(model, path)


# Clustering Class for custom training
class ClusteringModels:
    def __init__(self, X_train, X_test, path):
        self.X_train = X_train
        self.X_test = X_test
        self.path = path

    def kmeans_clustering(self, n_clusters=8, init='k-means++', n_init=10, max_iter=300, tol=0.0001, verbose=0,
                          random_state=None, copy_x=True, algorithm='auto'):
        model = KMeans(n_clusters=n_clusters, init=init, n_init=n_init, max_iter=max_iter, tol=tol,
                       verbose=verbose, random_state=random_state, copy_x=copy_x, algorithm=algorithm)

        model.fit(self.X_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def dbscan_clustering(self, eps=0.5, min_samples=5, metric='euclidean', metric_params=None,
                          algorithm='auto', leaf_size=30, p=None, n_jobs=None):
        model = DBSCAN(eps=eps, min_samples=min_samples, metric=metric, metric_params=metric_params,
                       algorithm=algorithm, leaf_size=leaf_size, p=p, n_jobs=n_jobs)
        model.fit(self.X_train)

        save_model(model, self.path)
        return model.predict(self.X_test)

    def agglomerative_clustering(self, n_clusters=2, affinity='euclidean', memory=None, connectivity=None,
                                 compute_full_tree='auto', linkage='ward', distance_threshold=None,
                                 compute_distances=False):
        model = AgglomerativeClustering(n_clusters=n_clusters, affinity=affinity, memory=memory,
                                        connectivity=connectivity,
                                        compute_full_tree=compute_full_tree, linkage=linkage,
                                        distance_threshold=distance_threshold, compute_distances=compute_distances)
        model.fit(self.X_train)

        save_model(model, self.path)
        return model.predict(self.X_test)
