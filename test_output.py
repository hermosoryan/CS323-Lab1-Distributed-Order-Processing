from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    print(f"[Master] I am process {rank} out of {size}", flush=True)
    sys.stdout.flush()
else:
    print(f"[Worker {rank}] I am process {rank} out of {size}", flush=True)
    sys.stdout.flush()
