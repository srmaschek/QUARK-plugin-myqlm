from quark.plugin_manager import factory

from quark_plugin_myqlm.devices import MyQLMDigitalQPU
from quark_plugin_myqlm.mappings import GHZtoQaptivaCircuit

def register() -> None:
    """
    Register all modules exposed to quark by this plugin.
    For each module, add a line of the form:
        factory.register("module_name", Module)

    The "module_name" will later be used to refer to the module in the configuration file.
    """

    # devices
    factory.register("MyQLMDigitalQPU", MyQLMDigitalQPU)

    # mappings
    factory.register("GHZtoQaptivaCircuit", GHZtoQaptivaCircuit)
