import logging
import time
from colorama import Fore, Style

def setup_logging(level=logging.INFO):
    """
    Sets up logging with a specified level.

    :param level: Logging level (e.g., logging.INFO, logging.DEBUG)
    """
    logging.basicConfig(level=level, 
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    return logging.getLogger(__name__)

logger = setup_logging()

def check_run(client, thread_id, run_id):
    """
    Continuously checks the status of a run and logs the status.

    :param client: The AssistantClient instance.
    :param thread_id: The thread ID of the run.
    :param run_id: The run ID to be checked.
    """
    logger.info("Checking run status")
    while True:
        run = client.get_run_status(thread_id, run_id)
        if run.status == "completed":
            logger.info("Run is completed")
            return "completed"
            break
        if run.status == "requires_action":
            logger.info("Run requires action")
            return "requires_action"
            break
        elif run.status == "expired":
            logger.warning("Run is expired")
            return "expired"
            break
        else:
            logger.debug(f"Run status: {run.status}")
            time.sleep(1)
