import grpc
from concurrent import futures
import time
import ride_sharing_pb2_grpc as pb2_grpc
import ride_sharing_pb2 as pb2
import threading
import random
import redis
import json
import ssl

class RideSharingService(pb2_grpc.RideSharingServiceServicer):
    def __init__(self, redis_client):
        self.redis = redis_client
        self.lock = threading.Lock()

        # Initialize data in Redis if not already present
        if not self.redis.exists("available_drivers"):
            self.redis.lpush("available_drivers", *["driver1", "driver2", "driver3", "driver4", "driver5", "driver6"])
        if not self.redis.exists("rides"):
            self.redis.set("rides", 0)

    def assign_driver(self, ride_id):
        assigned_driver = self.redis.rpop("available_drivers")
        if not assigned_driver:
            return None
        
        assigned_driver = assigned_driver.decode('utf-8')
        self.redis.hset(f"ride:{ride_id}", "driver", assigned_driver)
        self.redis.hset(f"ride:{ride_id}", "status", "assigned")
        print(f"Assigned ride {ride_id} to driver {assigned_driver}")
        return assigned_driver

    def RequestRide(self, request, context):
        ride_id = self.redis.incr("rides")
        print(f"Server received: Rider {request.rider_id} requested a ride {ride_id} from {request.pickup_location} to {request.destination}")

        ride_info = {
            "rider": request.rider_id,
            "pickup": request.pickup_location,
            "destination": request.destination,
            "attempts": "0"
        }
        self.redis.hmset(f"ride:{ride_id}", ride_info)

        assigned_driver = self.assign_driver(ride_id)
        if not assigned_driver:
            self.redis.hset(f"ride:{ride_id}", "status", "no driver available")
            return pb2.RideResponse(ride_id=ride_id, status="no driver available", driver_id="none")

        return pb2.RideResponse(ride_id=ride_id, status="assigned", driver_id=assigned_driver)

    def GetRideStatus(self, request, context):
        ride_info = self.redis.hgetall(f"ride:{request.ride_id}")
        if not ride_info:
            return pb2.RideStatusResponse(ride_id=request.ride_id, status="unknown", driver_id="none")

        return pb2.RideStatusResponse(
            ride_id=request.ride_id,
            status=ride_info[b"status"].decode('utf-8'),
            driver_id=ride_info[b"driver"].decode('utf-8') if b"driver" in ride_info else "none"
        )

    def AcceptRide(self, request, context):
        ride_key = f"ride:{request.ride_id}"
        ride_info = self.redis.hgetall(ride_key)

        if not ride_info or ride_info[b"status"] != b"assigned" or ride_info[b"driver"] != request.driver_id.encode('utf-8'):
            return pb2.AcceptRideResponse(status="Invalid request")

        self.redis.hset(ride_key, "status", "accepted")
        print(f"Driver {request.driver_id} accepted ride {request.ride_id}")
        return pb2.AcceptRideResponse(status="accepted")

    def RejectRide(self, request, context):
        ride_key = f"ride:{request.ride_id}"
        ride_info = self.redis.hgetall(ride_key)

        if not ride_info or ride_info[b"status"] != b"assigned" or ride_info[b"driver"] != request.driver_id.encode('utf-8'):
            return pb2.RejectRideResponse(status="Invalid request")

        self.redis.lpush("available_drivers", request.driver_id)
        
        attempts = int(ride_info[b"attempts"].decode('utf-8'))
        attempts += 1
        self.redis.hset(ride_key, "attempts", str(attempts))

        if attempts >= 3:
            self.redis.hset(ride_key, "status", "no driver available")
            print(f"Ride {request.ride_id} rejected 3 times. No driver available.")
            return pb2.RejectRideResponse(status="no driver available")

        new_driver = self.assign_driver(request.ride_id)
        if not new_driver:
            self.redis.hset(ride_key, "status", "no driver available")
            print(f"No more drivers available for ride {request.ride_id}")
            return pb2.RejectRideResponse(status="no driver available")

        print(f"Driver {request.driver_id} rejected ride {request.ride_id}. Reassigned to {new_driver}")
        return pb2.RejectRideResponse(status="reassigned", new_driver_id=new_driver)

    def CompleteRide(self, request, context):
        ride_key = f"ride:{request.ride_id}"
        ride_info = self.redis.hgetall(ride_key)

        if not ride_info or ride_info[b"status"] != b"accepted" or ride_info[b"driver"] != request.driver_id.encode('utf-8'):
            return pb2.RideCompletionResponse(status="Invalid request")

        self.redis.hset(ride_key, "status", "completed")
        self.redis.lpush("available_drivers", request.driver_id)
        print(f"Driver {request.driver_id} completed ride {request.ride_id}")
        return pb2.RideCompletionResponse(status="completed")

def serve(port, redis_client):
    class LoggingInterceptor(grpc.ServerInterceptor):
        def intercept_service(self, continuation, handler_call_details):
            print(f"Server on port {port} received a call to {handler_call_details.method}")
            return continuation(handler_call_details)

    # Load server credentials
    server_credentials = grpc.ssl_server_credentials(
        [(open('server.key', 'rb').read(), open('server.crt', 'rb').read())],
        root_certificates=open('ca.crt', 'rb').read(),
        require_client_auth=True
    )

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(LoggingInterceptor(),)
    )
    pb2_grpc.add_RideSharingServiceServicer_to_server(RideSharingService(redis_client), server)
    server.add_secure_port(f"[::]:{port}", server_credentials)
    server.start()
    print(f"Secure server started on port {port}")
    return server

def start_servers():
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    ports = [50051, 50058, 50053, 50054, 50055, 50056]
    servers = [serve(port, redis_client) for port in ports]

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        for server in servers:
            server.stop(0)

if __name__ == "__main__":
    start_servers()