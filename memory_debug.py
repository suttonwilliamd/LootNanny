import gc
import psutil
import os
import tracemalloc
from typing import Dict, Any
import threading

class MemoryProfiler:
    """Memory profiling utility for debugging memory leaks"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.initial_memory = self.get_memory_usage()
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage in MB"""
        memory_info = self.process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
            'percent': self.process.memory_percent()
        }
    
    def log_memory_usage(self, label: str = "") -> None:
        """Log current memory usage"""
        memory = self.get_memory_usage()
        print(f"[MEMORY] {label}: RSS={memory['rss']:.2f}MB, VMS={memory['vms']:.2f}MB, {memory['percent']:.2f}%")
    
    def start_tracing(self):
        """Start memory allocation tracing"""
        tracemalloc.start()
    
    def get_top_allocators(self, limit: int = 10) -> list:
        """Get top memory allocators"""
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        return top_stats[:limit]
    
    def force_garbage_collection(self):
        """Force garbage collection"""
        collected = gc.collect()
        print(f"[GC] Collected {collected} objects")
        return collected

# Global memory profiler instance
memory_profiler = MemoryProfiler()