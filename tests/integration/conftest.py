import multiprocessing
import random
import time

import pytest
import uvicorn


def start_api(port: int) -> None:
    uvicorn.run(
        "tests.integration.test_app.budget.actors.api:app",
        reload=False,
        log_level="debug",
        port=port,
    )


@pytest.fixture(scope="session")
def port():
    return random.randint(8000, 9000)


@pytest.fixture(scope="session")
def fastapi_server(port):
    proc = multiprocessing.Process(target=start_api, args=(port,), daemon=True)
    proc.start()
    time.sleep(5)
    yield
    proc.kill()
