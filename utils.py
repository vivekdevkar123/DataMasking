import logging
import traceback
from logging.handlers import RotatingFileHandler
import re
import spacy

logger = logging.getLogger(__name__)

def configure_logger(logging, name="pivony-masking.log", level=logging.DEBUG):
    try:
        logging.basicConfig(
            handlers=[RotatingFileHandler(name, maxBytes=1000000, backupCount=2)],
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S",
        )
        global logger
        logger = logging.getLogger()
        return logger
    except Exception as e:
        logger.error("Configuring error failed.")
        logger.error(str(e))
        logger.error(traceback.print_exc())
        return None

def load_ner_model():
    # Load spaCy NER model (you can replace 'en_core_web_sm' with a model that supports your language)
    return spacy.load('en_core_web_sm')

def mask_emails(text):
    match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
    s = match
    if s and len(s) > 0:
        for i in s:
            text = text.replace(i, "*****")
    return text

def mask_phone_numbers(text):
    phone_number_pattern = re.compile(r'\b\d{10}\b')

    def mask(match):
        return "*****"

    return phone_number_pattern.sub(mask, text)

def ner_mask_entities(text, ner):
    doc = ner(text)
    to_mask = []
    for ent in doc.ents:
        to_mask.append(ent.text)

    for entity in to_mask:
        text = text.replace(entity, "*****")
    return text

def mask_private_info(text, ner):
    try:
        text = mask_emails(text)
        text = mask_phone_numbers(text)
        text = ner_mask_entities(text, ner)
    except Exception as e:
        logger.warning("Masking skipped")
    return text
