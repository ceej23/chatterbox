import logging
import time
from colorama import Fore, Style

def setup_logging():
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(__name__)

logger = setup_logging()

def check_run(client, thread_id, run_id):
    logger.info("Checking run status")
    while True:
        run = client.get_run_status(thread_id, run_id)
        if run.status == "completed":
            logger.info("Run is completed")
            break
        elif run.status == "expired":
            logger.warning("Run is expired")
            break
        else:
            logger.debug(f"Run status: {run.status}")
            time.sleep(1)
