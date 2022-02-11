import pytest
from contextlib import redirect_stdout

def logger():
    with open("unitary_testing.out", "w") as file:
        with redirect_stdout(file):
            pytest.main(['--durations=0', '-v', '--color=yes'])    


if __name__ == '__main__':
    logger()
