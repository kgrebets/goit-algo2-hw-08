import random
import time


def make_queries(n, q, hot_pool=30, p_hot=0.95, p_update=0.03):
    hot = [(random.randint(0, n//2), random.randint(n//2, n-1))
           for _ in range(hot_pool)]
    queries = []
    for _ in range(q):
        if random.random() < p_update:        # ~3% запитів — Update
            idx = random.randint(0, n-1)
            val = random.randint(1, 100)
            queries.append(("Update", idx, val))
        else:                                 # ~97% — Range
            if random.random() < p_hot:       # 95% — «гарячі» діапазони
                left, right = random.choice(hot)
            else:                             # 5% — випадкові діапазони
                left = random.randint(0, n-1)
                right = random.randint(left, n-1)
            queries.append(("Range", left, right))
    return queries



#LRU cache
class Node:
    def __init__(self, key, value):
        self.data = (key, value)
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def push(self, key, value):
        new_node = Node(key, value)
        new_node.next = self.head
        if self.head:
            self.head.prev = new_node
        else:
            self.tail = new_node
        self.head = new_node
        return new_node

    def remove(self, node):
        if node.prev:
            node.prev.next = node.next
        else:
            self.head = node.next
        if node.next:
            node.next.prev = node.prev
        else:
            self.tail = node.prev
        node.prev = None
        node.next = None

    def move_to_front(self, node):
        if node is None or node == self.head:
            return
        self.remove(node)
        node.next = self.head
        if self.head:
            self.head.prev = node
        else:
            self.tail = node
        self.head = node

    def remove_last(self):
        if self.tail:
            last = self.tail
            self.remove(last)
            return last
        return None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}
        self.list = DoublyLinkedList()

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self.list.move_to_front(node)
            return node.data[1]
        return -1

    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.data = (key, value)
            self.list.move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                last = self.list.remove_last()
                if last:
                    del self.cache[last.data[0]]
            new_node = self.list.push(key, value)
            self.cache[key] = new_node

    def delete(self, key):
        node = self.cache.pop(key, None)
        if node:
            self.list.remove(node)

    def clear(self):
        self.cache.clear()
        self.list.head = None
        self.list.tail = None

    def keys(self):
        return list(self.cache.keys())


def range_sum_no_cache(array, left, right):
    return sum(array[left:right + 1])

def update_no_cache(array, index, value):
    array[index] = value



CACHE = LRUCache(capacity=1000)

def range_sum_with_cache(array, left, right):
    key = (left, right)
    cached = CACHE.get(key)
    if cached != -1:
        return cached
    total = range_sum_no_cache(array, left, right)
    CACHE.put(key, total)
    return total

def update_with_cache(array, index, value):
    update_no_cache(array, index, value)
    
    # інвалідація ключів кешу
    for (L, R) in CACHE.keys():
        if L <= index <= R:
            CACHE.delete((L, R))


# допоміжні ранери для замірів
def run_no_cache(arr, queries):
    for op, a, b in queries:
        if op == "Range":
            range_sum_no_cache(arr, a, b)
        else:  
            update_no_cache(arr, a, b)

def run_with_cache(arr, queries):
    CACHE.clear()
    for op, a, b in queries:
        if op == "Range":
            range_sum_with_cache(arr, a, b)
        else:
            update_with_cache(arr, a, b)


if __name__ == "__main__":
    n = 100_000   # розмір масиву
    q = 50_000    # кількість запитів
    base_array = [random.randint(1, 100) for _ in range(n)]
    arr1 = base_array.copy()
    arr2 = base_array.copy()

    queries = make_queries(n, q)

    # замір без кешу
    t0 = time.perf_counter()
    run_no_cache(arr1, queries)
    t1 = time.perf_counter()
    no_cache_time = t1 - t0

    # замір з кешем
    t2 = time.perf_counter()
    run_with_cache(arr2, queries)
    t3 = time.perf_counter()
    with_cache_time = t3 - t2

    # вивід результатів
    speedup = (no_cache_time / with_cache_time) if with_cache_time > 0 else float('inf')
    print(f"Без кешу :  {no_cache_time:6.2f} c")
    print(f"LRU-кеш  :  {with_cache_time:6.2f} c  (прискорення ×{speedup:0.1f})")
