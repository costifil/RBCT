'''
producer_text module
produce random text and push it into a queue
'''
from threading import Thread, Event
import time
import logging
import random
import string

class ProducerText(Thread):
    '''
    Producer class: read from breezetranslate web page and add to the queue
    '''

    def __init__(self, write_queue, **kwargs):
        super().__init__(name="Text_Thrd")

        self.write_q = write_queue

        self.max_lines = int(kwargs.get("BreezeTranslate", {}).get("max_subtitle_lines", 2))

        self.stop_process = Event()

    def stop(self):
        '''stop the thread'''
        self.stop_process.set()
        time.sleep(0.2)
        logging.info("%s stopped!", self.name)

    def run(self):
        logging.info("ProducerText started ...")

        used_text: list[str] = []
        count = 1
        while not self.stop_process.is_set():
            used_text = used_text[-20:]

            gen_text = ''
            if count % 5:
                words = random.randint(3, 15)
            else:
                count = 0
                words = 30
            count += 1
            for _ in range(words):
                value = random.randint(1, 7)
                gen_text += ''.join(random.choice(string.ascii_letters) for _ in range(value)) + ' '

            if gen_text in used_text:
                logging.debug("Text already in the used list: %s", gen_text)
                continue

            gen_text = gen_text.lower()
            self.write_q.add(gen_text)
            used_text.append(gen_text)
            logging.debug("Text added to the queue: %s", gen_text)
            print(f"- {len(gen_text):>3} - {gen_text}")
            #print("-", len(gen_text), "-", gen_text)

            if self.stop_process.is_set():
                break

            delay = random.uniform(2.0, 4.0)
            time.sleep(delay)
