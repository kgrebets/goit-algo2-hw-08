import random
from typing import Dict
import time
from collections import deque

class SlidingWindowRateLimiter:
   
    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        
        # key - user_id, value - deque з часовими мітками повідомлень
        self.user_messages: Dict[str, deque] = {} 

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        if user_id not in self.user_messages:
            self.user_messages[user_id] = deque()

        window = self.user_messages[user_id]

        # Видаляємо старі записи з початку черги
        while len(window) > 0:
            oldest_timestamp = window[0]
            time_diff = current_time - oldest_timestamp

            if time_diff > self.window_size:
                window.popleft()  
            else:
                break  

    def can_send_message(self, user_id: str) -> bool:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        messages_count_per_window = len(self.user_messages[user_id])
        return messages_count_per_window < self.max_requests

    def record_message(self, user_id: str) -> bool:
        if self.can_send_message(user_id):
            self.user_messages[user_id].append(time.time())
            return True
        return False
       
    def time_until_next_allowed(self, user_id: str) -> float:
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        window = self.user_messages.get(user_id, deque())
        messages_count_per_window =  len(window)

        if messages_count_per_window < self.max_requests:
            return 0
        else:
           oldest_timestamp = window[0]
           time_passed = current_time - oldest_timestamp
           remaining = self.window_size - time_passed
           return max(0, remaining)

# Демонстрація роботи
def test_rate_limiter():
    # Створюємо rate limiter: вікно 10 секунд, 1 повідомлення
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    # Симулюємо потік повідомлень від користувачів (послідовні ID від 1 до 20)
    print("\n=== Симуляція потоку повідомлень ===")
    for message_id in range(1, 11):
        # Симулюємо різних користувачів (ID від 1 до 5)
        user_id = message_id % 5 + 1

        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")

        # Невелика затримка між повідомленнями для реалістичності
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

    # Чекаємо, поки вікно очиститься
    print("\nОчікуємо 4 секунди...")
    time.sleep(4)

    print("\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))
        print(f"Повідомлення {message_id:2d} | Користувач {user_id} | "
              f"{'✓' if result else f'× (очікування {wait_time:.1f}с)'}")
        # Випадкова затримка від 0.1 до 1 секунди
        time.sleep(random.uniform(0.1, 1.0))

if __name__ == "__main__":
    test_rate_limiter()
