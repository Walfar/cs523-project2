"""
Performance evaluation in term of communication and computation cost
"""

import time
from multiprocessing import Process, Queue
from tracemalloc import start
import numpy as np
import pytest
import random
import string

from expression import Scalar, Secret
from protocol import ProtocolSpec
from server import run

from smc_party import SMCParty

"""
n represents the number of measurements we make to calculate
the mean and the standard deviation for every performance
"""
n = 100 

samples_com = list()
samples_time = list()

def get_random_string(length):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    # return random string
    return result_str


def smc_client(client_id, prot, value_dict, queue_bytes,queue_time):
    cli = SMCParty(
        client_id,
        "localhost",
        5000,
        protocol_spec=prot,
        value_dict=value_dict
    )
    start = time.time()
    res = cli.run()
    end = time.time()
    queue_bytes.put(res)
    queue_time.put(end-start)
    print(f"{client_id} has finished!")


def smc_server(args):
    run("localhost", 5000, args)


def run_processes(server_args, *client_args):
    queue_bytes = Queue()
    queue_time = Queue()

    server = Process(target=smc_server, args=(server_args,))
    clients = [Process(target=smc_client, args=(*args, queue_bytes,queue_time)) for args in client_args]

    server.start()
    time.sleep(3)
    for client in clients:
        client.start()

    results_performance_time = list()
    results_performance_bytes = list()
    for client in clients:
        client.join()

    for client in clients:
        results_performance_bytes.append(queue_bytes.get())
        results_performance_time.append(queue_time.get())

    server.terminate()
    server.join()

    # To "ensure" the workers are dead.
    time.sleep(2)

    print("Server stopped.")

    return results_performance_bytes,results_performance_time


def suite(parties, expr):
    participants = list(parties.keys())

    prot = ProtocolSpec(expr=expr, participant_ids=participants)
    clients = [(name, prot, value_dict) for name, value_dict in parties.items()]

    results_performance_bytes,results_performance_time = run_processes(participants, *clients)
    
    total_time = 0
    total_bytes_length = 0
    for t in results_performance_time :
        total_time += t
    for l in total_bytes_length :
        total_bytes_length +=l
    return total_bytes_length,total_time

def perform_stat(parties,expr,num_participants) :
    global samples_com 
    global samples_time 
    global statistical_mean
    global statistical_std

    samples_com = list()
    samples_time = list()

    for i in range(n) :
      total_bytes_length,total_time = suite(parties, expr)
      mean_bytes = total_bytes_length/num_participants
      mean_time = total_time / num_participants
      samples_com.append(mean_bytes)
      samples_time.append(mean_time)
      
    statistical_mean = (np.mean(samples_com),np.mean(samples_time))
    statistical_std = (np.std(samples_com),np.std(samples_time))


def num_parties_performance():
    results = {}
    # test for 3 participants 
    num_participants = 3
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 66},
        "Bob": {bob_secret: 200},
        "Charlie": {charlie_secret: 30}
    }
    
    expr = (alice_secret + bob_secret + charlie_secret)
    
    perform_stat(parties,expr,num_participants)
    results['3 participants'] = (statistical_mean,statistical_std)

     # test for 10 participants 
    num_participants = 10
    ### we need to add 3 more random people 
    for i in range(7) :
        name = get_random_string(8)
        new_secret = Secret()
        parties[name] = {new_secret : 0}

    perform_stat(parties,expr,num_participants)

    results['10 participants'] = (statistical_mean,statistical_std)

    # test for 100 participants , the expr is the same
    num_participants = 100
    ### we need to add 90 more random people 
    for i in range(90) :
        name = get_random_string(8)
        new_secret = Secret()
        parties[name] = {new_secret : 0}

    perform_stat(parties,expr,num_participants)

    results['100 participants'] = (statistical_mean,statistical_std)

      # test for 500 participants ,expr is the same
    num_participants = 500
    ### we need to add 400 more random people 
    for i in range(400) :
        name = get_random_string(8)
        new_secret = Secret()
        parties[name] = {new_secret : 0}

    perform_stat(parties,expr,num_participants)

    results['500 participants'] = (statistical_mean,statistical_std)

def addition_performance():
    results = {}

    # test for 3 Addition 
    num_participants = 3
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 66},
        "Bob": {bob_secret: 200},
        "Charlie": {charlie_secret: 30}
    }
    
    expr = (alice_secret + bob_secret + charlie_secret)

    perform_stat(parties,expr,num_participants)
      
    results['3 additions'] = (statistical_mean,statistical_std)

     # test for 10 additions 
    ### we need to add 7 more additions to expr
    for i in range(7) :
        expr += alice_secret

    perform_stat(parties,expr,num_participants)

    results['10 additions'] = (statistical_mean,statistical_std)

    # test for 100 additions , we add 90 more additions

    ### we need to add 90 more additions with alice's secret
    for i in range(90) :
        expr += alice_secret

    perform_stat(parties,expr,num_participants)

    results['100 additions'] = (statistical_mean,statistical_std)

      # test for 500 participants ,expr is the same

    ### we need to add 400 more additions with alice's secret
    for i in range(400) :
        expr += alice_secret

    perform_stat(parties,expr,num_participants)

    results['500 additions'] = (statistical_mean,statistical_std)

     # test for 1000 additions ,expr is the same

    ### we need to add 500 more additions with alice's secret 
    for i in range(500) :
        expr += alice_secret

    perform_stat(parties,expr,num_participants)

    results['1000 additions'] = (statistical_mean,statistical_std)


def addition_scalar_performance():
    results = {}

    # test for 10 Addition 
    num_participants = 3
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    k = Scalar(10) 
    expr = Scalar(10)

    parties = {
        "Alice": {alice_secret: 66},
        "Bob": {bob_secret: 200},
        "Charlie": {charlie_secret: 30}
    }
   
    for i in range(9) :
        expr += k 

    perform_stat(parties,expr,num_participants)

    results['10 scalar additions'] = (statistical_mean,statistical_std)

     # test for 100 additions 
    
    for i in range(90) :
        expr += k

    perform_stat(parties,expr,num_participants)

    results['100 scalar additions'] = (statistical_mean,statistical_std)

    # test for 500 additions 

    for i in range(400) :
        expr += k

    perform_stat(parties,expr,num_participants)

    results['500 scalar additions'] = (statistical_mean,statistical_std)

      # test for 1000 additions 

    ### we need to add 400 more additions with alice's secret
    for i in range(500) :
        expr += k

    perform_stat(parties,expr,num_participants)

    results['1000 scalar additions'] = (statistical_mean,statistical_std)

     
def multiplication_performance():
    results = {}

    # test for 3 Multiplications 
    num_participants = 3
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    parties = {
        "Alice": {alice_secret: 15},
        "Bob": {bob_secret: 10},
        "Charlie": {charlie_secret: 4}
    }
    
    expr = (alice_secret * bob_secret * charlie_secret)

    perform_stat(parties,expr,num_participants)

    results['3 multiplications'] = (statistical_mean,statistical_std)

     # test for 3 Multiplications
    ### we need to add 7 more multiplications to expr
    for i in range(7) :
        expr *= alice_secret

    perform_stat(parties,expr,num_participants)

    results['10 multiplications'] = (statistical_mean,statistical_std)

    # test for 100 additions , we add 90 more additions

    ### we need to add 90 more additions with alice's secret
    for i in range(90) :
        expr *= alice_secret

    perform_stat(parties,expr,num_participants)

    results['100 multiplications'] = (statistical_mean,statistical_std)

      # test for 500 participants ,expr is the same

    ### we need to add 400 more additions with alice's secret
    for i in range(400) :
        expr *= alice_secret

    perform_stat(parties,expr,num_participants)

    results['500 multiplications'] = (statistical_mean,statistical_std)

     # test for 1000 additions ,expr is the same

    ### we need to add 500 more additions with alice's secret 
    for i in range(500) :
        expr *= alice_secret

    perform_stat(parties,expr,num_participants)

    results['1000 multiplications'] = (statistical_mean,statistical_std)

def multiplication_scalar_performance():
    results = {}

    # test for 10 Multiplication 
    num_participants = 3
    alice_secret = Secret()
    bob_secret = Secret()
    charlie_secret = Secret()

    k = Scalar(5) 
    expr = Scalar(5)

    parties = {
        "Alice": {alice_secret: 66},
        "Bob": {bob_secret: 200},
        "Charlie": {charlie_secret: 30}
    }
    
    for i in range(9) :
        expr *= k 

    perform_stat(parties,expr,num_participants)

    results['10 scalar multiplications'] = (statistical_mean,statistical_std)

     # test for 100 multiplications 
    
    for i in range(90) :
        expr *= k

    perform_stat(parties,expr,num_participants)

    results['100 scalar multiplications'] = (statistical_mean,statistical_std)

    # test for 500 multiplications 

    for i in range(400) :
        expr *= k

    perform_stat(parties,expr,num_participants)

    results['500 scalar multiplications'] = (statistical_mean,statistical_std)

      # test for 1000 additions 

    ### we need to add 400 more additions with alice's secret
    for i in range(500) :
        expr *= k

    perform_stat(parties,expr,num_participants)

    results['1000 scalar multiplications'] = (statistical_mean,statistical_std)