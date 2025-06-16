from typing import List, TypeVar

from anvipy.system.system import System
from anvipy.entity import Entity
from anvipy.component import *
from anvipy.protocol_util import RemoveComponentTypes


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
        for entity in entities:
            for comp in entity.components:
                if comp.name != "Buffers":
                    continue

                buffs = RemoveComponentTypes(comp.datum['List'])

                if len(buffs) < 2:
                    continue

                metrics = next((c for c in entity.components if c.name == "Metrics"), None)

                # If we don't have a Metrics component, create one and add it to the entity
                if metrics is None:
                    metrics = Component()
                    metrics.name = "Metrics"
                    entity.components.append(metrics)

                # Is there a basic config?
                if not metrics.datum or 'List' not in metrics.datum:
                    metrics.datum = {"List": [
                        {
                            'Input': self.create_string(buffs[0]['Name']),
                            'Reference': self.create_string(buffs[1]['Name'])
                        }
                    ]}

                # create buffs map
                buffs_map = {b['Name']: b for b in buffs}

                for meta in metrics.datum["List"]:
                    meta_nc = RemoveComponentTypes(meta)
                    inName = meta_nc['Input']
                    refName = meta_nc['Reference']
                    imageLoaderObj = meta_nc['ImageLoader'] if 'ImageLoader' in meta_nc else 'rgb_aces_tm_nogamma'
                    if isinstance(imageLoaderObj, str):
                        imageLoaderObj = {
                            'Input': imageLoaderObj,
                            'Reference': imageLoaderObj
                        }
                    

                    if inName not in buffs_map or refName not in buffs_map:
                        continue

                    images = []

                    buffs_loaders = zip([buffs_map[inName], buffs_map[refName]], [imageLoaderObj['Input'], imageLoaderObj['Reference']])

                    for buff, imageLoaderStr in buffs_loaders:
                        path = f'buff.{buff["Type"].lower()}'
                        with open(path, 'wb') as fp:
                            fp.write(buff['Data'])
                        if imageLoaderStr == 'raw':
                            imageLoaderStr = 'rgb' # Loads without postproc or grayscale conversion
                        imageLoader = ImageLoaderFactory.create(imageLoaderStr)
                        images.append(imageLoader(path))

                    metNames = meta_nc['Metrics'] if 'Metrics' in meta_nc else ['mse', 'ssim', 'psnr', 'hdrvdp3', 'flip']
                    meta['Result'] = {x : LeafDatum(Datum.Datum.FloatDatum, MetricFactory.create(x)(images[0], images[1], DPString(imageLoaderStr))) for x in metNames}
                    meta['Computed'] = LeafDatum(Datum.Datum.BoolDatum, True)

    def required_components(self) -> List[str]:
        return ["Buffers", "Metrics"]
