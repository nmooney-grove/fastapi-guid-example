import os

def pytest_generate_tests(metafunc):
    os.environ['TESTING'] = "True"
