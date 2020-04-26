import re

from ixmp.testing import get_cell_output, run_notebook


# The TypeError message differs:
# - Python 3.6: "must be str, not float"
# - Python 3.7: "can only concatenate str (not "float") to str"
EXPECTED = re.compile(r"""computing 'test' using:

\(<function fail at \w+>,\)

Use Reporter.describe\(...\) to trace the computation.

Computation traceback:
  File "<ipython-input-\d*-\w+>", line 4, in fail
    'x' \+ 3.4  # Raises TypeError
TypeError: .*str.*float.*
""")


def test_computationerror_ipython(test_data_path, tmp_path, tmp_env):
    fname = test_data_path / 'reporting-exceptions.ipynb'
    nb, _ = run_notebook(fname, tmp_path, tmp_env, allow_errors=True)

    observed = get_cell_output(nb, 0, kind='evalue')
    assert EXPECTED.match(observed), observed
