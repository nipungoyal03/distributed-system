import grpc
import knn_pb2
import knn_pb2_grpc
import numpy as np
import heapq

def find_k_nearest_neighbors(servers, query_point, k):
    heap = []
    for server_address in servers:
        with grpc.insecure_channel(server_address) as channel:
            stub = knn_pb2_grpc.KNNServiceStub(channel)
            request = knn_pb2.KNNRequest(
                query_point=knn_pb2.Point(coordinates=query_point),
                k=k
            )
            response = stub.FindKNearestNeighbors(request)
            # print(response.neighbors)
            
            for n in response.neighbors:
                if len(heap) < k:
                    heapq.heappush(heap, (-n.distance, n))
                else:
                    if -heap[0][0] > n.distance:
                        heapq.heappushpop(heap, (-n.distance, n))

    return [n for dist, n in heap]


if __name__ == '__main__':
    servers = ['localhost:50060', 'localhost:50061', 'localhost:50062', 'localhost:50063']
    query_point = [0.5, 0.5]  
    k = 2
    global_neigh = find_k_nearest_neighbors(servers, query_point, k)
    print(f"given data_point = {query_point}")
    print(f"given k = {k}")
    print(f"Neighbours:")
    for n in global_neigh:
        print(f"coordinates: {n.point.coordinates}, dist: {n.distance}")