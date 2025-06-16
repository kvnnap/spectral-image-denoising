import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anvipy.anvil import Anvil
from anvipy.utils import *
from anvipy.system.system import load_systems

# Example usage
if __name__ == '__main__':
    # load configuration
    config = load('forge.json')

    anvil = Anvil.get_instance()
    load_systems(anvil, config["Systems"], 'forge')

    anvil.set_uri(config['WSUrl'])
    # entity = anvil.add_entity("MyEntity", {"key": "value"})
    anvil.start()

    # anvil = Anvil.get_instance()
    # anvil.set_uri("ws://10.60.10.68:8008")
    # anvil.add_system(MetricImageSystem())
    # anvil.start()