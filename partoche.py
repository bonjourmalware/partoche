import argparse

from src.exc import MissingDependency
from src.runners.ElasticsearchRunner import ElasticsearchRunner
from src.runners.MelodyRunner import MelodyRunner

parser = argparse.ArgumentParser(description="Partoche pew pew map")
data_args = parser.add_mutually_exclusive_group(required=True)
data_args.add_argument(
    "-D",
    "--demo",
    action="store_true",
    help="Use the local demo dataset instead of querying Elasticsearch. Alias for '--data ./data/demo.ndjson'",
)
data_args.add_argument(
    "-d", "--data", help="Use local data instead of querying Elasticsearch"
)
parser.add_argument(
    "-k",
    "--kind",
    help="Data model to use",
    default="melody",
    choices=["melody", "elasticsearch"],
)

args = parser.parse_args()
if args.demo:
    args.data = "./data/demo.ndjson"

try:
    if args.kind == "melody":
        runner = MelodyRunner(local_data_path=args.data)
    elif args.kind == "elasticsearch":
        runner = ElasticsearchRunner(local_data_path=args.data)
except MissingDependency as e:
    print(f"Please make sure '{e}' is installed")
    exit(1)

try:
    runner.run()
except ConnectionRefusedError:
    print("Failed to connect to Elasticsearch")
except (KeyboardInterrupt, SystemExit):
    # Handle program interruption from user and exit()
    pass
finally:
    if args.data:
        if runner.local_data_file:
            runner.local_data_file.close()
