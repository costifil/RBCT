'''
string_queue module
queue that accepts strings and is used by both
    - producer
    - consumer
'''
from collections import deque
from typing import Deque, Set

class StringQueue:
    '''StringQueue class'''

    def __init__(self):
        self._queue: Deque[str] = deque()
        self._set: Set[str] = set()

    def add(self, item: str) -> bool:
        '''
        Add a string if it does not already exist

        Args:
            item (str): string to be added to the queue

        Returns:
            True if added and False otherwise
        '''
        if item in self._set:
            return False

        self._queue.append(item)
        self._set.add(item)

        return True

    def exists(self, item: str) -> bool:
        '''
        Check if a string already exists in the queue

        Args:
            item (str): string to be check if exists in queue

        Returns:
            True if exists and False otherwise
        '''
        return item in self._set

    def pop(self):
        '''
        Remove and return the next string from the queue

        Returns:
            item (str) if the queue is not empty
            None if the queue is empty
        '''
        if not self._queue:
            return None

        item = self._queue.popleft()
        self._set.remove(item)
        return item

    def __len__(self):
        return len(self._queue)

    def __repr__(self):
        return f"StringQueue({list(self._queue)})"
