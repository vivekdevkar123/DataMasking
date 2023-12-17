import logging
import traceback
from logging.handlers import RotatingFileHandler
import re 

# configure logger
logger = logging.getLogger(__name__)


def configure_logger(
    logging,name="pivony-masking.log", level=logging.DEBUG
):
    """
    Configure logger

    params:
        - logging: logging module to be configured
        - name: local logfile name
        - level: logging level
    returns:
        - logger object
    """
    try:
        # configure root logging
        logging.basicConfig(
            handlers=[RotatingFileHandler(name, maxBytes=1000000, backupCount=2)],
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        # define logger object
        logger = logging.getLogger()
        return logger
    except Exception as e:
        logger.error("configuring error failed.")
        logger.error(str(e))
        logger.error(traceback.print_exc())
        # return failure
        return None

def ner_mask(text,ner):
  ner_doc = ner(text)
  to_mask = []
  for i in ner_doc:
    if i["entity"] in ["B-LOC","I-LOC","I-PER","B-PER"]:
      to_mask.append(i["word"])

  for i in to_mask:
    text = text.replace(i,"*****")
  return text


def mask_emails(text):
    match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    s = match
    if s and len(s)>0:
        for i in s:
            text = text.replace(i,"*****")
    return text

def mask_phone_numbers(text):
    """
        000-000-0000
        000 000 0000
        000.000.0000

        (000)000-0000
        (000)000 0000
        (000)000.0000
        (000) 000-0000
        (000) 000 0000
        (000) 000.0000

        000-0000
        000 0000
        000.0000
        0000000
        0000000000
        (000)0000000

        # Detect phone numbers with country code
        +00 000 000 0000
        +00.000.000.0000
        +00-000-000-0000
        +000000000000
        0000 0000000000
        0000-000-000-0000
        00000000000000
        +00 (000)000 0000
        0000 (000)000-0000
        0000(000)000-0000 
    """
    masked_phones = []
    match = re.findall(r'((?:\+\d{2}[-\.\s]??|\d{4}[-\.\s]??)?(?:\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}))', text)
    for i in match:
        masked_phones.append(i)
        text = text.replace(i,"*****")
    return text

def mask_private_info(text,ner):
    try:
        text = mask_emails(text)
        text = mask_phone_numbers(text)
        text = ner_mask(text,ner)
    except Exception as e:
        logger.warning("masking skipped")
    return text