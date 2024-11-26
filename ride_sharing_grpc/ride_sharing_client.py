import grpc
import json
import ride_sharing_pb2_grpc as pb2_grpc
import ride_sharing_pb2 as pb2
import threading
import random
import time
import ssl
from grpc_interceptor import ClientCallDetails, ClientInterceptor
import logging
from datetime import datetime

# Set up logging
# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler("ride_sharing_simulation.log"),
        logging.StreamHandler()  # Also continue logging to console
    ]
)

# Configuration for load balancing
service_config = json.dumps({
    "loadBalancingConfig": [{"round_robin": {}}]
})

# Servers for rider and driver
rider_servers = ["localhost:50051", "localhost:50058", "localhost:50053"]
driver_servers = ["localhost:50054", "localhost:50055", "localhost:50056"]

class LoggingInterceptor(ClientInterceptor):
    def intercept(
        self,
        method,
        request_or_iterator,
        call_details: grpc.ClientCallDetails,
    ):
        start_time = time.time()
        method_name = call_details.method.split('/')[-1]
        client_type = 'rider' if 'rider' in call_details.metadata else 'driver'
        
        logging.info(f"gRPC call: {method_name} - Client: {client_type} - Start time: {datetime.now()}")
        
        try:
            response = method(request_or_iterator, call_details)
            return response
        finally:
            duration = time.time() - start_time
            logging.info(f"gRPC call: {method_name} - Client: {client_type} - Duration: {duration:.2f}s - End time: {datetime.now()}")

def create_secure_channel(server, client_type):
    # Load client credentials
    with open(f'{client_type}.key', 'rb') as f:
        private_key = f.read()
    with open(f'{client_type}.crt', 'rb') as f:
        certificate_chain = f.read()

    # Create SSL credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates=open('ca.crt', 'rb').read(),
        private_key=private_key,
        certificate_chain=certificate_chain
    )

    # Create channel with interceptor
    channel = grpc.secure_channel(server, credentials, options=[('grpc.service_config', service_config)])
    return grpc.intercept_channel(channel, LoggingInterceptor())

# Create channels and stubs for the rider and driver servers
rider_channels = [create_secure_channel(server, 'rider') for server in rider_servers]
driver_channels = [create_secure_channel(server, 'driver') for server in driver_servers]

rider_stubs = [pb2_grpc.RideSharingServiceStub(channel) for channel in rider_channels]
driver_stubs = [pb2_grpc.RideSharingServiceStub(channel) for channel in driver_channels]

# Round-robin indices
rider_index = 0
driver_index = 0

def get_next_rider_stub():
    global rider_index
    stub = rider_stubs[rider_index]
    rider_index = (rider_index + 1) % len(rider_stubs)
    return stub

def get_next_driver_stub():
    global driver_index
    stub = driver_stubs[driver_index]
    driver_index = (driver_index + 1) % len(driver_stubs)
    return stub

def simulate_ride_request(rider_id):
    rider_stub = get_next_rider_stub()
    driver_stub = get_next_driver_stub()

    try:
        # Request a ride
        ride_request = pb2.RideRequest(
            rider_id=rider_id,
            pickup_location=f"Location {random.choice('ABCDE')}",
            destination=f"Location {random.choice('VWXYZ')}"
        )
        metadata = [('client-type', 'rider')]
        ride_response = rider_stub.RequestRide(ride_request, metadata=metadata)
        logging.info(f"Rider {rider_id} - Ride assigned: {ride_response.ride_id}, Driver: {ride_response.driver_id}")

        if ride_response.status == "assigned":
            current_driver_id = ride_response.driver_id
            rejection_count = 0
            max_rejections = 3

            while rejection_count < max_rejections:
                # Simulate driver accepting or rejecting the ride
                if random.choice([True, False]):
                    accept_ride_request = pb2.AcceptRideRequest(
                        driver_id=current_driver_id,
                        ride_id=ride_response.ride_id
                    )
                    metadata = [('client-type', 'driver')]
                    accept_ride_response = driver_stub.AcceptRide(accept_ride_request, metadata=metadata)
                    logging.info(f"Rider {rider_id} - Ride acceptance status: {accept_ride_response.status}")

                    if accept_ride_response.status == "accepted":
                        # Complete the ride
                        complete_ride_request = pb2.RideCompletionRequest(
                            driver_id=current_driver_id,
                            ride_id=ride_response.ride_id
                        )
                        complete_ride_response = driver_stub.CompleteRide(complete_ride_request, metadata=metadata)
                        logging.info(f"Rider {rider_id} - Ride completion status: {complete_ride_response.status}")
                        break
                else:
                    reject_ride_request = pb2.RejectRideRequest(
                        driver_id=current_driver_id,
                        ride_id=ride_response.ride_id
                    )
                    metadata = [('client-type', 'driver')]
                    reject_ride_response = driver_stub.RejectRide(reject_ride_request, metadata=metadata)
                    logging.info(f"Rider {rider_id} - Ride rejection status: {reject_ride_response.status}")
                    
                    if reject_ride_response.status == "reassigned":
                        rejection_count += 1
                        current_driver_id = reject_ride_response.new_driver_id
                        logging.info(f"Rider {rider_id} - Ride reassigned to driver: {current_driver_id}. Attempt {rejection_count}/{max_rejections}")
                    elif reject_ride_response.status == "no driver available":
                        logging.info(f"Rider {rider_id} - No driver available after {rejection_count + 1} attempts")
                        break
            else:
                logging.info(f"Rider {rider_id} - No driver accepted the ride after {max_rejections} attempts")
        else:
            logging.info(f"Rider {rider_id} - No driver available initially")

    except grpc.RpcError as e:
        logging.error(f"Rider {rider_id} - RPC failed with status code {e.code()}: {e.details()}")

def run_simulation(num_requests):
    threads = []
    for i in range(num_requests):
        rider_id = f"rider{i+1}"
        thread = threading.Thread(target=simulate_ride_request, args=(rider_id,))
        threads.append(thread)
        thread.start()
        time.sleep(0.1)  # Small delay between requests to simulate real-world scenario

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    num_requests = 20  # Simulate 20 simultaneous ride requests
    run_simulation(num_requests)

    # Close all channels
    for channel in rider_channels + driver_channels:
        channel.close()