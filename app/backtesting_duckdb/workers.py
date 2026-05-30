# workers.py



import multiprocessing as mp
from multiprocessing import Process, Queue
import uuid
import threading
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import time
import pandas as pd

def cpu_intensive_work(id):
    temp = 0
    for i in range(0, 50_000):
        for j in range(0, 10_000):
            temp = i *1.2523
    print(f"temp {id}" ,temp)

# ── Worker Function (runs in separate process) ────────────────────────────────

# def worker(worker_id: int, job_queue: Queue, result_queue: Queue):
#     print(f"[Worker {worker_id}] Started | PID: {mp.current_process().pid}")
    
#     while True:
#         job = job_queue.get()
#         # cpu_intensive_work(worker_id)
#         print(f"job")
#         if job is None:  # shutdown signal
#             print(f"[Worker {worker_id}] Shutting down")
#             break

#         job_id    = job["job_id"]
#         stocks    = job["stocks"]
        
#         result_queue.put({
#             "job_id"    : job_id,
#             "worker_id" : worker_id,
#             "pid"       : mp.current_process().pid,
#             "stocks"    : stocks,
#             "df" : pd.DataFrame({"abc": [1,2,3,4,5,6]})
#         })

# ── Worker Pool ───────────────────────────────────────────────────────────────

class WorkerPool:
    def __init__(self, worker, num_workers: int):
        self.result_queue  = mp.Queue()
        self.job_queues    : dict[int, Queue]   = {}
        self.processes     : dict[int, Process] = {}
        self._pending      : dict[str, dict]    = {}  # job_id -> {event, result}
        self._pending_lock = threading.Lock()
        

        for wid in range(1, num_workers + 1):
            jq = mp.Queue()
            self.job_queues[wid] = jq
            p = Process(target=worker, args=(wid, jq, self.result_queue), daemon=True)
            p.start()
            self.processes[wid] = p

        self._start_result_listener()

    def _start_result_listener(self):
        def listen():
            while True:
                result = self.result_queue.get()
                job_id = result["job_id"]
                with self._pending_lock:
                    if job_id in self._pending:
                        self._pending[job_id]["result"] = result
                        self._pending[job_id]["event"].set()

        threading.Thread(target=listen, daemon=True).start()

    def submit(self, worker_id: int, data: dict) -> str:
        job_id = str(uuid.uuid4())
        event  = threading.Event()

        with self._pending_lock:
            self._pending[job_id] = {"event": event, "result": None}

        self.job_queues[worker_id].put({"job_id": job_id, "data": data})
        return job_id

    def get_result(self, job_id: str, timeout: float = 10.0) -> dict:
        # Grab the entry reference BEFORE waiting — don't pop yet
        with self._pending_lock:
            entry = self._pending.get(job_id)

        if entry is None:
            raise ValueError(f"Unknown job_id: {job_id}")

        # fired = entry["event"].wait(timeout=timeout)
        fired = entry["event"].wait()

        if not fired:
            raise TimeoutError(f"Job {job_id} timed out")

        # Clean up and return
        with self._pending_lock:
            self._pending.pop(job_id, None)

        return entry["result"]  # entry dict still exists in local scope

    async def submit_async(self, worker_id: int, data: dict) -> dict:
        loop   = asyncio.get_event_loop()
        job_id = self.submit(worker_id, data)
        result = await loop.run_in_executor(None, self.get_result, job_id , 10.0)
        return result

    def shutdown(self):
        for jq in self.job_queues.values():
            jq.put(None)
# ── FastAPI ───────────────────────────────────────────────────────────────────

# pool: WorkerPool = None

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     global pool
#     pool = WorkerPool(num_workers=4)
#     yield
#     pool.shutdown()

# app = FastAPI(lifespan=lifespan)


# @app.post("/query")
# async def query(request: list[dict]):
#     """
#     Request body:
#     {
#         "worker_id": 1,
#         "stocks": ["AAPL", "TSLA", "MSFT"]
#     }
#     """
#     # print(request)
#     for i in range(0, len(request)):
#         worker_id = request[i]["worker_id"]
#         stocks    = request[i]["stocks"]

#         result = await pool.submit_async(worker_id, stocks)
#     return result

# @app.post("/query")
# async def query(request: list[dict]):
#     init = time.perf_counter_ns()
#     tasks = [
#         pool.submit_async(item["worker_id"], item["stocks"])
#         for item in request
#     ]

#     results = await asyncio.gather(*tasks)
#     print(results)
#     print((time.perf_counter_ns() - init)/1000/1000)
#     # return results