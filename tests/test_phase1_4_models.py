"""
Test Suite for AI Model Lazy Loading
Tests Phase 1.4 model management
"""
from sj_das.utils.model_manager import ModelManager, get_model_manager
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_model_registration():
    """Test model loader registration."""
    manager = ModelManager(timeout=60)

    # Register a dummy loader
    def load_dummy():
        return {"model": "dummy"}

    manager.register_loader('dummy', load_dummy)

    stats = manager.get_stats()
    assert stats['registered_loaders'] == 1

    print("✅ Model registration works")


def test_lazy_loading():
    """Test lazy loading of models."""
    manager = ModelManager(timeout=60)

    # Register loader
    load_count = [0]

    def load_test():
        load_count[0] += 1
        return {"model": "test", "loaded_at": time.time()}

    manager.register_loader('test', load_test)

    # First call should load
    model1 = manager.get_model('test')
    assert load_count[0] == 1

    # Second call should use cache
    model2 = manager.get_model('test')
    assert load_count[0] == 1  # Still 1, not reloaded
    assert model1 is model2

    print("✅ Lazy loading works (model loaded once, cached)")


def test_model_unloading():
    """Test automatic model unloading."""
    manager = ModelManager(timeout=1, max_models=2)  # 1 second timeout

    # Register loaders
    manager.register_loader('model1', lambda: {"name": "model1"})
    manager.register_loader('model2', lambda: {"name": "model2"})

    # Load models
    m1 = manager.get_model('model1')
    time.sleep(0.5)
    m2 = manager.get_model('model2')

    assert len(manager.loaded_models) == 2

    # Wait for timeout
    time.sleep(1.5)
    manager.cleanup_unused()

    # model1 should be unloaded (older)
    assert len(manager.loaded_models) < 2

    print(
        f"✅ Auto-unloading works ({len(manager.loaded_models)} models remaining)")


def test_max_models_limit():
    """Test maximum models limit."""
    manager = ModelManager(timeout=60, max_models=2)

    # Register 3 loaders
    for i in range(3):
        manager.register_loader(f'model{i}', lambda i=i: {"id": i})

    # Load 3 models (should only keep 2)
    for i in range(3):
        manager.get_model(f'model{i}')
        time.sleep(0.1)  # Ensure different timestamps

    assert len(manager.loaded_models) <= 2

    print(f"✅ Max models limit works ({len(manager.loaded_models)}/2 loaded)")


def test_model_manager_stats():
    """Test model manager statistics."""
    manager = get_model_manager()

    stats = manager.get_stats()

    assert 'loaded_models' in stats
    assert 'registered_loaders' in stats
    assert 'max_models' in stats

    print(f"✅ Stats work: {stats}")


if __name__ == "__main__":
    print("=" * 60)
    print("Phase 1.4 AI Model Lazy Loading Tests")
    print("=" * 60)

    print("\n📦 Testing Model Registration...")
    test_model_registration()

    print("\n⚡ Testing Lazy Loading...")
    test_lazy_loading()

    print("\n🗑️ Testing Auto-Unloading...")
    test_model_unloading()

    print("\n📊 Testing Max Models Limit...")
    test_max_models_limit()

    print("\n📈 Testing Stats...")
    test_model_manager_stats()

    print("\n" + "=" * 60)
    print("✅ All Phase 1.4 tests passed!")
    print("=" * 60)
