from typing import List

from anvipy.system.system import System
from anvipy.entity import Entity
from anvipy.component import *
from anvipy.protocol_util import RemoveComponentTypes


from evaluation.image_loader import ImageLoaderFactory
from evaluation.thresholds import ThresholdFactory
from evaluation.denoiser_factory import DenoiserFactory
import feanor.anvil.protocol.Datum as Datum
from utils.image import *
from utils.serialisation import load_binary_file

class DPString:
    def __init__(self, imageLoader):
        self.imageLoader = imageLoader

# Example system that implements the System interface
# Entity name should be image name?
class SpectralDenoisingSystem(System):
    def execute(self, entities: List[Entity]):
        for entity in entities:
            for comp in entity.components:
                if comp.name != "Buffers":
                    continue

                coeff = next((c for c in entity.components if c.name == "CoefficientConfig"), None)
                if coeff is None:
                    continue
                
                
                # Load coeffs and everything
                dp = RemoveComponentTypes(coeff.datum['denoiserParams'])
                imageLoaderMethod = ImageLoaderFactory.create(dp['imageLoader'])
                thresholdMethod = ThresholdFactory.create(dp['thresholding'])
                denoiserMethod = DenoiserFactory.create({'name' : dp['denoiser']})

                x = RemoveComponentTypes(coeff.datum['denoiserResult'])['x']
                appliesTo = RemoveComponentTypes(coeff.datum['appliesTo'])

                buffs = RemoveComponentTypes(comp.datum['List'])

                den_buffs = []
                for buff in buffs:
                    if appliesTo and buff['Name'] not in appliesTo:
                        continue
                    path = f'sid-buff.{buff["Type"].lower()}'
                    with open(path, 'wb') as fp:
                        fp.write(buff['Data'])

                    image = imageLoaderMethod(path)
                    den_image = denoiserMethod.get_image(image, x, thresholdMethod)
                    save_image_as_exr(den_image, path)

                    den_buffs.append(
                        {
                            "Name": LeafDatum(Datum.Datum.StringDatum, f"{buff['Name']}-Denoised"),
                            "Data": LeafDatum(Datum.Datum.BinaryDatum, load_binary_file(path)),
                            "Type": LeafDatum(Datum.Datum.StringDatum, "EXR"), 
                            "BufferType": LeafDatum(Datum.Datum.StringDatum, buff['BufferType'])
                        }
                    )

                for d in den_buffs:
                    comp.datum['List'].append(d)
    
    def required_components(self) -> List[str]:
        return ["Buffers", "CoefficientConfig"]
