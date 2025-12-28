'''
translate module
'''
import time
from ch_logger.logger_config import setup_logger    # pylint: disable=import-error
from translate_app.producer import Producer         # pylint: disable=import-error
from translate_app.consumer import Consumer         # pylint: disable=import-error
from translate_app.string_queue import StringQueue  # pylint: disable=import-error
from ch_utils import ch_utils as util               # pylint: disable=import-error

def main():
    '''main function'''
    setup_logger() # logging initialized ONCE

    strque = StringQueue()

    data = util.get_config_info()
    for item in data:
        if item.get("application") == "translate_subtitle_OBS":
            data = item
            break

    producer = Producer(strque, **data)
    consumer = Consumer(strque, **data)
    producer.start()
    consumer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        producer.stop()
        consumer.stop()
        time.sleep(1)

        producer.join()
        consumer.join()

    #logging.info("Done!")

if __name__ == "__main__":
    main()
