import time
from multiprocessing import Process, Queue
from tokenize import Double
from numpy import char

import pytest

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

from smc_party import SMCParty



def smc_client(client_id, prot, value_dict, queue):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    res = cli.run()
    queue.put(res)
    print(f"{client_id} has finished!")  


def smc_server(args):
    run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue)) for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results = list()
    for client in clients:
        client.join()

    for client in clients:
        results.append(queue.get())

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results

def runApplication(parties):

    participants = list(parties.keys())
    
    student1_secret = list(parties[participants[0]].keys())[0]
    student2_secret = list(parties[participants[1]].keys())[0]
    student3_secret = list(parties[participants[2]].keys())[0]

    # First, we want to calculate the mean
    sum = (((student1_secret + Scalar(0.5))
        +(student2_secret + Scalar(0.5)))
        +(student3_secret+ Scalar(0.5)))

    prot_mean = ProtocolSpec(expr=sum, participant_ids=participants)
    clients = [(name, prot_mean, value_dict) for name, value_dict in parties.items()]

    results = run_processes(participants, *clients)
    # Make sure that all clients got the same result 
    for result in results:
        assert result == results[0]  

    mean = results[0]/3

    # Now, we calculate the variance
    variance = ((
        (Scalar(mean) - (student1_secret + Scalar(0.5))) * (Scalar(mean) - (student1_secret + Scalar(0.5)))
        + ((student2_secret + Scalar(0.5)) - Scalar(mean)) * ((student2_secret + Scalar(0.5)) - Scalar(mean))
        )
        + (Scalar(mean) - (student3_secret + Scalar(0.5))) * (Scalar(mean) - (student3_secret + Scalar(0.5)))
    )

    prot_variance = ProtocolSpec(expr=variance, participant_ids=participants)
    new_clients = [(name, prot_variance, value_dict) for name, value_dict in parties.items()]

    results = run_processes(participants, *new_clients)
    # Make sure that all clients got the same result 
    for result in results:
        assert result == results[0]    
    variance = results[0]/3    
    return mean, variance  



