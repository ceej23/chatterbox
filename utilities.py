import logging
import time
import requests
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

def download_file(url, local_filename):
    """
    Downloads a file from a given URL to a specified local file path.

    :param url: URL of the file to download.
    :param local_filename: Local path to save the downloaded file.
    :return: Path to the downloaded file.
    """
    logger.info(f"Downloading file: {url}")

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        raise


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
