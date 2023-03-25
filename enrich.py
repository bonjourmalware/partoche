import argparse
import concurrent
import json
import logging
import multiprocessing
import os
import signal
import threading
import timeit

import math
from concurrent.futures import ProcessPoolExecutor

import mmap
import yaml
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, MofNCompleteColumn, TimeElapsedColumn
from yaml import CBaseLoader

from src.utils.chunks import check_chunk, chunk_lines

parser = argparse.ArgumentParser(description="Partoche enrichment tool for Melody logs")
parser.add_argument("-d", "--data", required=True, help="Log file to enrich")
parser.add_argument(
    "-r",
    "--iprep-db",
    default="data/listbot/live/iprep.yaml",
    help="YAML file containing the IP-to-reputation mapping. See 'data/listbot' to generate it",
)
parser.add_argument(
    "-a",
    "--geoip-ASN-db",
    default="data/GeoLite2-ASN.mmdb",
    help="Path to the Maxmind ASN DB file",
)
parser.add_argument(
    "-c",
    "--geoip-city-db",
    default="data/GeoLite2-City.mmdb",
    help="Path to the Maxmind city DB file",
)
parser.add_argument(
    "-s", "--chunk-size", help="Log lines per worker", type=int, default=500000
)
parser.add_argument(
    "-i",
    "--in-place",
    action="store_true",
    help="Update the source file directly instead of making a copy",
)
parser.add_argument("-o", "--out", default="parsed.ndjson", help="Output filepath")
parser.add_argument(
    "-w",
    "--max-workers",
    help="Max workers quantity. Note that the number will be adjusted depending on the chunks size. Default: number of CPU cores as reported by the OS (minus one that's reserved for the chunking subprocess process)",
    type=int,
    default=os.cpu_count(),
)

args = parser.parse_args()

results = []
chunks_count = 0
total_checked = 0

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

log = logging.getLogger("rich")

data_fp = open(args.data, "r+")
mapped_data_fp = mmap.mmap(data_fp.fileno(), 0)
total_lines = sum(1 for _ in iter(mapped_data_fp.readline, b""))

with Progress(
    SpinnerColumn(),
    *Progress.get_default_columns(),
    MofNCompleteColumn(),
    TimeElapsedColumn(),
) as progress:
    with ProcessPoolExecutor(max_workers=args.max_workers) as pool:
        with multiprocessing.Manager() as manager:
            loading_iprep_task = progress.add_task(f"[cyan]Loading IP reputation file ({args.iprep_db})...", total=None)
            with open(args.iprep_db) as f:
                iprep_db = yaml.load(f, Loader=CBaseLoader)

            progress.remove_task(loading_iprep_task)

            parsing_task = progress.add_task(f"[cyan]Parsing log data...", total=total_lines)

            shared_iprep_db = manager.dict()
            shared_iprep_db.update(iprep_db)

            jobs = []
            batch_results = []
            tasks = manager.dict()
            queue = manager.Queue()
            pump_done = manager.Event()
            signal_quit = manager.Event()
            total_processed = manager.dict()

            threading.Thread(target=chunk_lines, args=(pump_done, queue, data_fp, args.chunk_size)).start()

            if (max_workers := math.ceil(total_lines / args.chunk_size)) < args.max_workers:
                progress.log(f"Adjusted number of workers from {args.max_workers} to {max_workers}")
                args.max_workers = max_workers

            for i in range(args.max_workers):
                task_id = progress.add_task(f"[magenta] * Worker {i + 1}", total=None)
                jobs.append(
                    pool.submit(
                        check_chunk,
                        signal_quit,
                        pump_done,
                        tasks,
                        total_processed,
                        task_id,
                        shared_iprep_db,
                        queue,
                    )
                )

            def signal_handler(sig, frame):
                try:
                    signal_quit.set()
                except EOFError:
                    pass

                progress.log("[yellow]Exiting...")
                pool.shutdown()
                concurrent.futures.wait(jobs, timeout=5)
                exit()

            signal.signal(signal.SIGINT, signal_handler)

            start = timeit.default_timer()
            while (finished := sum([job.done() for job in jobs])) < len(jobs):
                end = timeit.default_timer()
                if end - start >= 0.2:
                    for task_id, task_state in tasks.items():
                        task_progress = task_state["progress"]
                        task_total = task_state["total"]
                        progress.update(task_id, completed=task_progress, total=task_total)
                    progress.update(parsing_task, completed=sum(total_processed.values()))
                    start = timeit.default_timer()

            progress.log("Parsing complete")
            progress.log("Fetching results...")
            progress.refresh()

            for job in jobs:
                batch_results.append(job.result())

            for res in batch_results:
                if res:
                    results += res

    outfile = args.out if not args.in_place else args.data
    with open(outfile, "w") as f:
        f.write("\n".join(json.dumps(line) for line in results))

    progress.log(f"[green]Results written to {outfile}")
