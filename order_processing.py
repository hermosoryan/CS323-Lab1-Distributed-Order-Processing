"""
Distributed Order Processing System
CS323 - First Laboratory Activity

Uses:
- mpi4py  : for distributing orders across processes
- Manager : for shared memory (shared_orders list)
- Lock    : for synchronization when writing to shared memory
"""

from mpi4py import MPI
import time
import random

# ─────────────────────────────────────────────
# MPI Setup
# ─────────────────────────────────────────────
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

def generate_orders():
    """Master generates 5-8 orders."""
    items = ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard",
             "Mouse", "Headset", "Webcam", "Charger", "Speaker"]
    num_orders = random.randint(5, 8)
    orders = [{"order_id": i + 1, "item": items[i % len(items)]}
              for i in range(num_orders)]
    return orders

def distribute_orders(orders, num_workers):
    """Distribute orders evenly among workers (round-robin)."""
    worker_orders = [[] for _ in range(num_workers)]
    for i, order in enumerate(orders):
        worker_orders[i % num_workers].append(order)
    return worker_orders

def worker_process(rank):
    """Worker receives orders, processes them, and stores results."""
    assigned = comm.recv(source=0, tag=rank)
    results = []

    for order in assigned:
        # Simulate processing delay
        delay = random.uniform(0.5, 2.0)
        time.sleep(delay)

        result = {
            "order_id": order["order_id"],
            "item": order["item"],
            "processed_by": rank,
            "delay": round(delay, 2)
        }

        print(f"  [Worker {rank}] DONE - Processed Order #{order['order_id']} "
              f"({order['item']}) in {delay:.2f}s", flush=True)
        
        results.append(result)

    # Send results back to master
    comm.send(results, dest=0, tag=0)

def master_process(orders=None):
    """Master generates and distributes orders, then collects results."""
    print("\n" + "="*55, flush=True)
    print("   DISTRIBUTED ORDER PROCESSING SYSTEM", flush=True)
    print("="*55, flush=True)

    # ── Step 1: Generate orders
    if orders is None:
        orders = generate_orders()
    print(f"\n[Master] Generated {len(orders)} orders:", flush=True)
    for o in orders:
        print(f"         Order #{o['order_id']} - {o['item']}", flush=True)

    # ── Step 2: Distribute to workers 
    num_workers = size - 1
    worker_orders = distribute_orders(orders, num_workers)

    print(f"\n[Master] Distributing to {num_workers} worker(s)...\n", flush=True)
    for w in range(1, size):
        comm.send(worker_orders[w - 1], dest=w, tag=w)
        print(f"  -> Sent {len(worker_orders[w-1])} order(s) to Worker {w}", flush=True)

    # ── Step 3: Wait for all workers to finish 
    print("\n[Master] Waiting for workers to finish processing...\n", flush=True)
    
    completed = []
    for _ in range(1, size):
        worker_results = comm.recv(source=MPI.ANY_SOURCE, tag=0)
        completed.extend(worker_results)
        print(f"  [Master] Received {len(worker_results)} result(s)", flush=True)

    # ── Step 4: Collect and print final results 
    print("\n" + "="*55, flush=True)
    print("   FINAL COMPLETED ORDERS", flush=True)
    print("="*55, flush=True)

    completed.sort(key=lambda x: x["order_id"])

    for result in completed:
        print(f"  Order #{result['order_id']:>2} | {result['item']:<12} | "
              f"Worker {result['processed_by']} | {result['delay']}s", flush=True)

    print(f"\n[Master] Total orders completed: {len(completed)}/{len(orders)}", flush=True)
    print("="*55 + "\n", flush=True)

# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if rank == 0:
    master_process()
else:
    worker_process(rank)

comm.Barrier()  # Synchronization barrier

