from typing import List, TypeVar

from anvipy.system.system import System
from anvipy.entity import Entity
from anvipy.component import *

from evaluation.metric import *
from evaluation.image_loader import *
import feanor.anvil.protocol.Datum as Datum
from utils.image import *

class DPString:
    def __init__(self, imageLoader):
        self.imageLoader = imageLoader

# Example system that implements the System interface
# Entity name should be image name?
class MetricImageSystem(System):
    def execute(self, entities: List[Entity]):
        imageLoaderStr = 'rgb_aces_tm_nogamma'
        imageLoader = ImageLoaderFactory.create(imageLoaderStr)
        metNames = ['mse', 'ssim', 'psnr', 'hdrvdp3', 'flip']

        for entity in entities:
            for comp in entity.components:
                if comp.name != "Buffers":
                    continue

                metrics = next((c for c in entity.components if c.name == "Metrics"), None)

                # If we don't have a Metrics component, create one and add it to the entity
                if metrics is None:
                    metrics = Component()
                    metrics.name = "Metrics"
                    entity.components.append(metrics)

                buffs = comp.datum['List']

                images = []
                for buffI in buffs:
                    buff = buffI['Radiance']
                    path = f'buff.{str(buff["Type"]).lower()}'
                    with open(path, 'wb') as fp:
                        fp.write(buff['Data'].datum)
                    images.append(imageLoader(path))

                metrics.datum = {x : LeafDatum(Datum.Datum.FloatDatum, MetricFactory.create(x)(images[0], images[1], DPString(imageLoaderStr))) for x in metNames}
                
                # print(f"Pos: {comp.datum['Position']}")
                # print(f"Dir: {comp.datum['Direction']}")
                # print(f"tHit: {comp.datum['tHit']}")
    
    def required_components(self) -> List[str]:
        return ["Buffers", "Metrics"]
