from collections import OrderedDict

incidents = {}

# ----------------------------------------------------
# ENTERPRISE SAFEGUARD: LRU Memory Cache for DataFrames
# ----------------------------------------------------
class LRUDataFrameCache:
    """
    Prevents Out-Of-Memory (OOM) crashes by strictly bounding 
    the number of lakh-row Pandas DataFrames held in RAM.
    """
    def __init__(self, capacity=2):
        self.cache = OrderedDict()
        self.capacity = capacity

    def __getitem__(self, key):
        # Move to end to show it was recently used
        val = self.cache.pop(key)
        self.cache[key] = val
        return val

    def __setitem__(self, key, value):
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.capacity:
            # Evict oldest DataFrame from RAM
            self.cache.popitem(last=False)
        self.cache[key] = value

    def __contains__(self, key):
        return key in self.cache
        
    def keys(self):
        return self.cache.keys()

batch_datasets = LRUDataFrameCache(capacity=2)