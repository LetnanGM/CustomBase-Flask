from bowlplate.kernel.foundation.manifest.plugins import Plugins


def test_plugin_loader():
    plugin = Plugins()
    plugin.load_all()

    assert True
