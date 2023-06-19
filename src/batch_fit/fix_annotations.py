from typing import List
from functools import partial
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.distance import pdist, squareform

import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KDTree
from sklearn.cluster import DBSCAN
from sklearn.neighbors import NearestNeighbors

from opencmiss.zinc.context import Context
from opencmiss.zinc.field import FieldGroup
from opencmiss.zinc.result import RESULT_OK
from opencmiss.zinc.field import Field


def load_exdata(file_name: str):
    context = Context('Single Data')
    region = context.getDefaultRegion()
    result = region.readFile(file_name)
    assert result == RESULT_OK, "Failed to load data file " + str(file_name)
    fieldmodule = region.getFieldmodule()
    coordinates = fieldmodule.findFieldByName('coordinates').castFiniteElement()
    components_count = coordinates.getNumberOfComponents()
    assert components_count in [1, 2, 3], 'extract_node_parameter. Invalid coordinates number of components'
    cache = fieldmodule.createFieldcache()

    return_values = list()
    nodes = fieldmodule.findNodesetByFieldDomainType(Field.DOMAIN_TYPE_DATAPOINTS)
    node_iter = nodes.createNodeiterator()
    node = node_iter.next()
    while node.isValid():
        cache.setNode(node)
        result, values = coordinates.getNodeParameters(cache, -1, 1, 1, components_count)
        return_values.append(values)
        node = node_iter.next()

    return np.asarray(return_values)


def generate_df(data: np.ndarray, label: str, label_ids: List):
    df = pd.DataFrame(data, columns=['x', 'y', 'z'])
    df['label'] = 'unlabeled'
    df.loc[label_ids, 'label'] = label

    return df


def downsample(data, factor=30):
    base_data = data[data['label'] == 'posterior edge of lower lobe of right lung']
    unlabeled_data = data[data['label'] == 'unlabeled']

    downsampled_unlabeled = unlabeled_data.iloc[::factor, :].copy()
    downsampled_data = pd.concat([base_data, downsampled_unlabeled], ignore_index=True)

    return downsampled_data


def check_distance(d, label):
    # Filter the ground-truth dataset to keep only the 'base' labeled points
    ground_truth_base = d[d['label'] == label]

    # Compute the pairwise distances between all 'base' labeled points
    # pairwise_distances = pdist(ground_truth_base[['x', 'y', 'z']].to_numpy())
    distance_matrix = squareform(pdist(ground_truth_base[['x', 'y', 'z']].to_numpy(), metric='euclidean'))
    # Calculate the mean and standard deviation of distances
    mean_distance = np.mean(distance_matrix)
    std_distance = np.std(distance_matrix)
    print(mean_distance)

    threshold = mean_distance * 0.30  # Set a threshold for ectopic labels
    # threshold_distance = np.percentile(pairwise_distances, 20)

    return threshold


def register(ground_truth_data, source_data):

    # incomplete

    scaler = StandardScaler()
    ground_truth_data[['x', 'y', 'z']] = scaler.fit_transform(ground_truth_data[['x', 'y', 'z']])
    source_data[['x', 'y', 'z']] = scaler.transform(source_data[['x', 'y', 'z']])

    # Run the CPD algorithm

    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # callback = partial(visualize, ax=ax)
    #
    # reg = DeformableRegistration(**{'X': ground_truth_data[['x', 'y', 'z']].values,
    #                                 'Y': source_data[['x', 'y', 'z']].values})
    # reg.register(callback)
    # plt.show()
    # reg = DeformableRegistration(**{'X': ground_truth_data[['x', 'y', 'z']].values,
    #                                 'Y': source_data[['x', 'y', 'z']].values})
    # reg.register(callback=visualize)
    # reg.register()
    # T = reg.R
    # t = reg.t

    # Apply the CPD transformation to the source dataset
    # transformed_source_data = np.dot(source_data[['x', 'y', 'z']].values, T) + t.T
    transformed_source_data = reg.transform_point_cloud(source_data[['x', 'y', 'z']].values)

    # Filter the ground-truth and source datasets to keep only the 'base' labeled points
    ground_truth_base = ground_truth_data[ground_truth_data['label'] == 'posterior edge of lower lobe of right lung']
    source_base = source_data[source_data['label'] == 'posterior edge of lower lobe of right lung']

    # Convert the filtered data to NumPy arrays
    ground_truth_base_points = ground_truth_base[['x', 'y', 'z']].to_numpy()
    source_base_points = source_base[['x', 'y', 'z']].to_numpy()

    # Choose the number of nearest neighbors (k)
    k = 5

    # Compute the average distances between each point and its k-nearest neighbors
    nearest_neighbors = NearestNeighbors(n_neighbors=k)
    nearest_neighbors.fit(transformed_source_data[source_base.index])
    distances, _ = nearest_neighbors.kneighbors(transformed_source_data[source_base.index])
    avg_distances = np.mean(distances, axis=1)
    # Plot the k-distance graph
    sorted_distances = np.sort(avg_distances)[::-1]
    plt.plot(sorted_distances)
    plt.xlabel("Points")
    plt.ylabel(f"Average distance to {k} nearest neighbors")
    plt.show()

    # Apply DBSCAN clustering on the transformed source points with the 'base' label
    dbscan = DBSCAN(eps=1, min_samples=2)
    clusters = dbscan.fit_predict(transformed_source_data[source_base.index])
    # Identify incorrect labels
    mismatches = clusters == -1

    # Build the KDTree using the filtered ground-truth points
    kd_tree = KDTree(ground_truth_base_points)

    # Find the nearest neighbors in the ground-truth dataset for each point in the transformed source dataset with the 'base' label
    # _, indices = kd_tree.query(transformed_source_data[source_base.index])

    # Find the nearest neighbors in the ground-truth dataset for each point in the transformed source dataset with the 'base' label
    distances, indices = kd_tree.query(transformed_source_data[source_base.index])

    # Set a threshold distance to consider a 'base' label as incorrect
    threshold_distance = check_distance(ground_truth_data, 'posterior edge of lower lobe of right lung')

    # Identify incorrect 'base' labels
    mismatches = distances > threshold_distance

    # Compare labels and identify incorrect labels only for the 'base' labeled points
    source_base_labels = source_base['label'].values
    ground_truth_base_labels = ground_truth_base['label'].values
    # mismatches = source_base_labels != ground_truth_base_labels[indices]


def visualize(iteration, error, X, Y, ax):
    plt.cla()
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], color='red', label='Target')
    ax.scatter(Y[:, 0], Y[:, 1], Y[:, 2], color='blue', label='Source')
    ax.text2D(0.87, 0.92, 'Iteration: {:d}'.format(
        iteration), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes,
              fontsize='x-large')
    ax.legend(loc='upper left', fontsize='x-large')
    plt.draw()
    plt.pause(0.001)


if __name__ == '__main__':
    # testing
    root = r'D:\12-labours\lung\merryn-data-fitting\new-annotations\high-rms'
    annotation = 'posterior edge of lower lobe of right lung'

    template_id = '18964E'
    target_id = '16565G'

    template_label_ids = [i for i in range(304, 360)]
    target_label_ids = [i for i in range(322, 397)]

    template = load_exdata(rf'{root}\{template_id}\{template_id}_combined_lung_data.ex')
    target = load_exdata(rf'{root}\{target_id}\{target_id}_combined_lung_data.ex')

    template_df = generate_df(template, annotation, template_label_ids)
    target_df = generate_df(target, annotation, target_label_ids)

    downsample_template = downsample(template_df)
    downsample_target = downsample(target_df)

    register(downsample_template, downsample_target)

    print()
