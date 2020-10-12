import os
import gzip

def load_mock_data(filename):
    """Load a gzip test data file."""
    cur_fp = os.path.realpath(__file__)
    cur_dir = os.path.dirname(cur_fp)
    fp = os.path.join(cur_dir, "mocks", filename)
    with gzip.open(fp, "rb") as fh:
        content = fh.read().decode("utf-8")
        return content