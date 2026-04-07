# CS323 – First Laboratory: Distributed Order Processing

## Overview

A distributed order processing system using **MPI** (via `mpi4py`) for inter-process communication, **shared memory** (via `multiprocessing.Manager`), and **synchronization** (via `Lock`) to safely coordinate multiple concurrent worker processes.

---

## Project Structure

```
CS323-Lab1/
├── mpi_test.py          # Environment verification script
├── order_processing.py  # Main activity (MPI + shared memory + Lock)
└── README.md            # This file
```

---

## Environment Setup

### 1. Install MPI

**Windows (MS-MPI):**
- Download and install from: https://github.com/microsoft/Microsoft-MPI/releases
- Install both `msmpisetup.exe` and `msmpisdk.msi`

**Linux/Mac (OpenMPI):**
```bash
sudo apt install libopenmpi-dev   # Ubuntu/Debian
brew install open-mpi             # macOS
```

### 2. Install Python Dependencies

```bash
pip install mpi4py
```

### 3. Verify Installation

```bash
mpirun -np 4 python mpi_test.py
```

**Expected output:**
```
Process 0 out of 4
Process 1 out of 4
Process 2 out of 4
Process 3 out of 4
```

---

## Running the Main Program

```bash
mpirun -np 4 python order_processing.py
```

> `-np 4` launches 1 master + 3 workers. You can adjust the number.

---

## Reflection Questions

### 1. How did you distribute orders among worker processes?

The master process (rank 0) generated 5–8 orders and distributed them to worker processes using a **round-robin strategy**. Each order was assigned to a worker using `i % num_workers`, ensuring orders are spread as evenly as possible. The master then sent each worker's assigned orders using `comm.send()`, and workers received them via `comm.recv(source=0)`.

### 2. What happens if there are more orders than workers?

When there are more orders than workers, some workers receive more than one order. The round-robin distribution handles this naturally — for example, with 7 orders and 3 workers, Workers 1 and 2 get 2 orders each while Worker 3 gets 3 orders. Each worker processes its orders **sequentially** (one after another), so no order goes unprocessed.

### 3. How did processing delays affect the order completion?

Because each worker uses `time.sleep()` with a random delay between 0.5 and 2.0 seconds, orders do **not** complete in the order they were assigned. Workers finish at different times depending on their delay, so the output order is non-deterministic. This simulates real-world processing where tasks take varying amounts of time. The master waits for all workers to finish before collecting results.

### 4. How did you implement shared memory, and where was it initialized?

Shared memory was implemented using Python's `multiprocessing.Manager().list()`. The `Manager` was initialized in the `if __name__ == "__main__"` block, before branching into master or worker roles. The `shared_orders` list and `lock` were passed as arguments to both the master and worker functions so all processes share the same memory structure.

### 5. What issues occurred when multiple workers wrote to shared memory simultaneously?

Without synchronization, multiple workers writing to `shared_orders` at the same time can cause **race conditions** — two processes may attempt to append simultaneously, leading to corrupted data, missing entries, or inconsistent list states. This is especially visible when many workers finish at nearly the same time.

### 6. How did you ensure consistent results when using multiple processes?

A `Lock()` from `multiprocessing` was used to create a **critical section** around each write to `shared_orders`. The `with lock:` block ensures that only one worker can append to the shared list at a time, preventing race conditions. After all workers signal completion, the master reads the shared list and sorts it by order ID to display a clean, consistent final output.

---

## Commits

- `Initial setup and environment verification`
- `Task distribution implementation`
- `Shared memory integration`
- `Synchronization fixes`
