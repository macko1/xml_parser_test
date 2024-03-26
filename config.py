import logging
import os
import typing
from pathlib import Path

# init logger
log_file = 'debug.log'
if os.path.exists(log_file):
    os.remove(log_file)
logger = logging.getLogger('__name__')  # __main__
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[
                        logging.FileHandler('debug.log'),
                        logging.StreamHandler()]
                    )


SCRIPT_PARENT_FOLDER: Path = Path(__file__).resolve().parent
SPARE_PARTS_FEED_FOLDER: Path = Path(f"{SCRIPT_PARENT_FOLDER}/spare_parts_feed")
RELAXNG_SCHEMA_FILE: Path = Path(f"{SCRIPT_PARENT_FOLDER}/relaxng_schemas/products-complete-v10.rng")
OUTPUT_XML: Path = Path(f"{SCRIPT_PARENT_FOLDER}/output.xml")

XML_LIST: list = [xml_path for xml_path in SPARE_PARTS_FEED_FOLDER.rglob("*.xml")]
