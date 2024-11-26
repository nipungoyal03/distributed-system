import numpy as np
from multiprocessing import Process
import grpc
from concurrent import futures
import knn_pb2
import knn_pb2_grpc
import numpy as np


class KNNServicer(knn_pb2_grpc.KNNServiceServicer):
    def __init__(self, dataset):
        self.dataset = dataset

    def FindKNearestNeighbors(self, request, context):
        query_point = np.array([coord for coord in request.query_point.coordinates])
        eu_distances = np.linalg.norm(self.dataset - query_point, axis=1)
        nearest_indices = np.argsort(eu_distances)[:request.k]
        partial_neigh = []
        for idx in nearest_indices:
            neighbor = knn_pb2.Neighbor(point=knn_pb2.Point(coordinates=self.dataset[idx].tolist()), distance=float(eu_distances[idx]))
            partial_neigh.append(neighbor)
        return knn_pb2.KNNResponse(neighbors=partial_neigh)

def serve(dataset, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    knn_pb2_grpc.add_KNNServiceServicer_to_server(KNNServicer(dataset), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Server started on port {port}")
    server.wait_for_termination()

if __name__ == '__main__':
    dataset = np.random.rand(10000, 2)  
    servers_available = [50060, 50061, 50062, 50063]
    datasets =np.array_split(dataset, len(servers_available))

    all_p = []
    for i in range(len(servers_available)):
        p = Process(target=serve, args=(datasets[i], servers_available[i]))
        p.start()
        all_p.append(p)
        print(f"Started server on port {servers_available[i]}")

    for p in all_p:
        p.join()