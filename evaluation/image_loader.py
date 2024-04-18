from utils.image import load_image, tone_map, tone_map_aces

class ImageLoaderDescriptor:
    def __init__(self):
        self.gray = True
        self.toneMapped = True
        self.toneMapper = 'reinhard'
        self.gammaCorrected = True

    def isToneMapped(self):
        return self.toneMapped
    
    def setToneMapped(self, val):
        self.toneMapped = True if val else False

    def toString(self):
        out = ''
        out += 'gray' if self.gray else 'rgb'
        if self.toneMapped:
            out += '_'
            if self.toneMapper != 'reinhard':
                out += f'{self.toneMapper.strip().lower()}_'
            out += 'tm'
            if not self.gammaCorrected:
                out += '_nogamma'
        return out
    
    def fromString(self, label):
        s = label.strip().lower().split('_')

        # Extra checks
        if s[0] not in ['gray', 'rgb']:
            raise ValueError(f'Invalid label: {label} - Color format invalid')
        
        gray = s[0] == 'gray'
        toneMapped = len(s) > 1
        if toneMapped:
            i = 1
            if s[i] == 'tm':
                toneMapper = 'reinhard'
            else:
                toneMapper = s[i]
                i += 1
                if i >= len(s) or s[i] != 'tm':
                    raise ValueError(f'Invalid label: {label}')
            i += 1
            gammaCorrected = not (i < len(s) and s[i] == 'nogamma')

            # Extra checks
            if toneMapper not in ['reinhard', 'aces'] or (i < len(s) and s[i] != 'nogamma'):
                raise ValueError(f'Invalid label: {label} - Tone Mapper not found or only nogamma is expected')
        else: # Use defaults instead of stored ones?
            n = ImageLoaderDescriptor()
            toneMapper = n.toneMapper
            gammaCorrected = n.gammaCorrected

        self.gray = gray
        self.toneMapped = toneMapped
        self.toneMapper = toneMapper
        self.gammaCorrected = gammaCorrected
        return self


class ImageLoaderFactory:
    # Method returned expects (input, t, substitute)
    @staticmethod
    def create(il_name):
        imgLoaderDesc = ImageLoaderDescriptor().fromString(il_name)
        tmSel = {
            'reinhard': tone_map,
            'aces': tone_map_aces
        }
        if imgLoaderDesc.toneMapper not in tmSel.keys():
            raise ValueError(f"Invalid image loader name {il_name}. ToneMapper not found")
        return lambda path: load_image(path, imgLoaderDesc.gray, imgLoaderDesc.toneMapped, imgLoaderDesc.gammaCorrected, tmSel[imgLoaderDesc.toneMapper])
