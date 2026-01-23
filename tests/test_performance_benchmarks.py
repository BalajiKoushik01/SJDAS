"""
Performance Benchmark Suite for SJ-DAS
Measures and tracks performance metrics
"""
from sj_das.utils.image_cache import get_cache
from sj_das.core.quantizer import ColorQuantizerEngine
from sj_das.core.loom_engine import LoomEngine
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))


class PerformanceBenchmark:
    """Performance benchmarking suite."""

    def __init__(self):
        self.results = {}

    def benchmark(self, name, func, iterations=3):
        """Run benchmark."""
        times = []

        for i in range(iterations):
            start = time.time()
            result = func()
            elapsed = time.time() - start
            times.append(elapsed)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        self.results[name] = {
            'avg': avg_time,
            'min': min_time,
            'max': max_time,
            'iterations': iterations
        }

        print(
            f"  {name}: {avg_time:.3f}s avg (min: {min_time:.3f}s, max: {max_time:.3f}s)")

        return result

    def save_results(self, filename='benchmark_results.json'):
        """Save results to file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📊 Results saved to {filename}")


def benchmark_quantization_sizes():
    """Benchmark quantization at different sizes."""
    bench = PerformanceBenchmark()
    quantizer = ColorQuantizerEngine()

    sizes = [(100, 100), (500, 500), (1000, 1000), (2000, 2000)]

    print("\n📏 Quantization Performance by Size:")
    for size in sizes:
        img = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)

        def quantize():
            return quantizer.quantize(img, k=8)

        result = bench.benchmark(
            f"Quantize {size[0]}x{size[1]}",
            quantize,
            iterations=3)

        # Calculate pixels/sec
        pixels = size[0] * size[1]
        avg_time = bench.results[f"Quantize {size[0]}x{size[1]}"]['avg']
        pixels_per_sec = pixels / avg_time
        print(f"    → {pixels_per_sec/1000:.0f}K pixels/sec")

    return bench


def benchmark_cache_performance():
    """Benchmark cache hit vs miss performance."""
    bench = PerformanceBenchmark()
    quantizer = ColorQuantizerEngine()
    cache = get_cache()
    cache.clear()

    img = np.random.randint(0, 255, (500, 500, 3), dtype=np.uint8)

    print("\n💾 Cache Performance:")

    # Cache miss
    def first_call():
        return quantizer.quantize(img, k=8)

    bench.benchmark("Cache MISS (first call)", first_call, iterations=1)

    # Cache hit
    def second_call():
        return quantizer.quantize(img, k=8)

    bench.benchmark("Cache HIT (cached)", second_call, iterations=5)

    # Calculate speedup
    miss_time = bench.results["Cache MISS (first call)"]['avg']
    hit_time = bench.results["Cache HIT (cached)"]['avg']
    speedup = miss_time / hit_time
    print(f"    → Speedup: {speedup:.0f}x faster with cache")

    return bench


def benchmark_weave_generation():
    """Benchmark weave generation."""
    bench = PerformanceBenchmark()
    loom = LoomEngine()

    sizes = [100, 500, 1000, 2000]

    print("\n🧵 Weave Generation Performance:")
    for size in sizes:
        design = np.random.randint(0, 8, (size, size), dtype=np.uint8)

        def generate():
            return loom.design_to_weave(design, hooks=size)

        bench.benchmark(f"Weave {size}x{size}", generate, iterations=3)

    return bench


def benchmark_memory_usage():
    """Benchmark memory usage."""
    from sj_das.utils.memory_manager import get_memory_manager

    mm = get_memory_manager()

    print("\n💾 Memory Usage:")

    initial = mm.get_usage_mb()
    print(f"  Initial: {initial:.1f}MB")

    # Create large arrays
    arrays = []
    for i in range(10):
        arrays.append(
            np.random.randint(
                0, 255, (1000, 1000, 3), dtype=np.uint8))

    peak = mm.get_usage_mb()
    print(f"  Peak: {peak:.1f}MB")
    print(f"  Increase: {peak - initial:.1f}MB")

    # Cleanup
    arrays.clear()
    import gc
    gc.collect()

    final = mm.get_usage_mb()
    print(f"  After cleanup: {final:.1f}MB")


if __name__ == "__main__":
    print("=" * 60)
    print("SJ-DAS Performance Benchmark Suite")
    print("=" * 60)

    # Run benchmarks
    bench1 = benchmark_quantization_sizes()
    bench2 = benchmark_cache_performance()
    bench3 = benchmark_weave_generation()
    benchmark_memory_usage()

    # Combine results
    all_results = {**bench1.results, **bench2.results, **bench3.results}

    # Save
    with open('benchmark_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "=" * 60)
    print("✅ Benchmarks complete!")
    print("=" * 60)
