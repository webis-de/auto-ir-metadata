#!/usr/bin/env python3
from pathlib import Path

import click
import pandas as pd
import pyterrier as pt

from autometadata import persist_ir_metadata


@click.command()
@click.argument("output-directory", type=Path)
def main(output_directory):
    run = pd.DataFrame(
        [
            {"qid": "q-1", "docno": "doc-01", "rank": 1, "score": 10},
            {"qid": "q-1", "docno": "doc-02", "rank": 2, "score": 9},
            {"qid": "q-1", "docno": "doc-03", "rank": 3, "score": 8},
        ]
    )
    output_directory.mkdir(exist_ok=True, parents=True)
    pt.io.write_results(run, output_directory / "run.txt", format="trec")
    persist_ir_metadata(output_directory)


if __name__ == "__main__":
    main()
