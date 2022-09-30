# import requests
# from click.testing import CliRunner
# from g4.app import g4
# import pytest
# from multiprocessing import Process


# def run_server():
#     runner = CliRunner()
#     runner.invoke(g4, ["run"])


# def run_server_fixture():
#     proc = Process(target=run_server, args=(), daemon=True)
#     proc.start()
#     yield
#     proc.kill()  # Cleanup after test


# def test_run_server():
#     try:
#         from pytest_cov.embed import cleanup_on_sigterm
#     except ImportError:
#         pass
#     else:
#         cleanup_on_sigterm()

#     p = Process(target=run_server_fixture, args=(), daemon=True)
#     try:
#         p.start()
#     finally:
#         p.join()  # necessary so that the Process exists before the test suite exits (thus coverage is collected)
