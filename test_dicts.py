from mpi4py import MPI
import random
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

print(f"Process {rank} started", flush=True)

def worker_process(rank):
    """Worker receives orders, processes them, and stores results."""
    assigned = comm.recv(source=0, tag=rank)
    print(f"Worker {rank} received: {assigned}", flush=True)
    results = []

    for order in assigned:
        delay = random.uniform(0.1, 0.3)
        time.sleep(delay)
        result = {"order_id": order["order_id"], "processed": True}
        results.append(result)

    comm.send(results, dest=0, tag=0)
    print(f"Worker {rank} done", flush=True)

def master_process():
    """Master generates and distributes orders."""
    print("Master started", flush=True)
    
    orders = [{"order_id": 1, "item": "A"}, {"order_id": 2, "item": "B"}]
    num_workers = size - 1
    worker_orders = [orders[i::num_workers] for i in range(num_workers)]

    for w in range(1, size):
        print(f"Master sending to worker {w}", flush=True)
        comm.send(worker_orders[w - 1], dest=w, tag=w)

    completed = []
    for _ in range(1, size):
        worker_results = comm.recv(source=MPI.ANY_SOURCE, tag=0)
        print(f"Master received: {worker_results}", flush=True)
        completed.extend(worker_results)

    print(f"Master done with {len(completed)} results", flush=True)


if rank == 0:
    master_process()
else:
    worker_process(rank)

print(f"Process {rank} exiting", flush=True)
