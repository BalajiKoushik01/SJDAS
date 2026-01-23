
import os
import unittest
from unittest.mock import MagicMock

from sj_das.core.feature_flags import FeatureFlagManager
from sj_das.core.ioc_container import ServiceContainer


class TestInterface:
    pass


class TestImplementation(TestInterface):
    pass


class TestArchitecture(unittest.TestCase):

    def setUp(self):
        # Reset container
        ServiceContainer.instance().reset()

    def test_ioc_singleton(self):
        """Verify IoC Container handles singletons correctly."""
        container = ServiceContainer.instance()
        instance = TestImplementation()

        container.register_singleton(TestInterface, instance)
        resolved = container.resolve(TestInterface)

        self.assertEqual(instance, resolved)

    def test_ioc_factory(self):
        """Verify IoC Container handles factories correctly."""
        container = ServiceContainer.instance()
        container.register_factory(TestInterface, lambda: TestImplementation())

        obj1 = container.resolve(TestInterface)
        obj2 = container.resolve(TestInterface)

        self.assertIsInstance(obj1, TestImplementation)
        self.assertNotEqual(obj1, obj2)  # Should be different instances

    def test_ioc_missing(self):
        """Verify IoC throws error for missing dependency."""
        container = ServiceContainer.instance()
        with self.assertRaises(ValueError):
            container.resolve(TestInterface)

    def test_feature_flags(self):
        """Verify Feature Flag Manager toggles."""
        fm = FeatureFlagManager.instance()

        # Test Default
        self.assertFalse(fm.is_enabled("NON_EXISTENT"))

        # Test Toggle
        fm.enable("TEST_FEATURE")
        self.assertTrue(fm.is_enabled("TEST_FEATURE"))

        fm.disable("TEST_FEATURE")
        self.assertFalse(fm.is_enabled("TEST_FEATURE"))


if __name__ == '__main__':
    unittest.main()
