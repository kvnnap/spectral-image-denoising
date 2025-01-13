import os,sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from anvipy.anvil import Anvil

from forge.metric_image_system import MetricImageSystem

# Example usage
if __name__ == '__main__':
    anvil = Anvil.get_instance()
    anvil.set_uri("ws://10.60.10.68:8008")
    anvil.add_system(MetricImageSystem())
    anvil.start()
    pass