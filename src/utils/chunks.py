import json
from queue import Empty


class LinesChunk:
    def __init__(self, values):
        self.total = len(values)
        self.values = values


def check_chunk(
    signal_quit, pump_done, tasks, total_processed, task_id, iprep_db, queue
):
    results = []
    total_processed[task_id] = 0
    try:
        while True:
            try:
                loglines = queue.get(timeout=0.1)
            except Empty:
                if pump_done.is_set():
                    break
                elif not pump_done.is_set():
                    continue

            if signal_quit.is_set():
                break

            tasks[task_id] = {"progress": 0, "total": loglines.total}
            for idx, logline in enumerate(loglines.values):
                logline["ip_rep"] = ""

                if rep := iprep_db.get(logline["src_ip"]):
                    logline["ip_rep"] = rep

                # A new dict is required for the UI to be updated
                tasks[task_id] = {"progress": idx + 1, "total": loglines.total}
                total_processed[task_id] += 1

            results += loglines.values
    except KeyboardInterrupt:
        pass

    return results


def get_lines_chunk(size: int, source):
    lines = []
    idx = 0
    while line := source.readline():
        lines.append(json.loads(line.strip()))
        idx += 1
        if idx == size:
            break

    return LinesChunk(lines)


def chunk_lines(pump_done, queue, f, chunk_size):
    try:
        while (
            lines_chunk := get_lines_chunk(chunk_size, f)
        ) and lines_chunk.total > 0:
            queue.put(lines_chunk)
    except BrokenPipeError:
        pass
    finally:
        pump_done.set()
