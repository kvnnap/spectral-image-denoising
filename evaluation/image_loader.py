from utils.image import load_image, tone_map_aces

class ImageLoaderFactory:
    # Method returned expects (input, t, substitute)
    @staticmethod
    def create(il_name):
        name = il_name.strip().lower()
        if (name == "gray"): return lambda path: load_image(path, True, False)
        if (name == "gray_tm"): return lambda path: load_image(path, True, True)
        if (name == "gray_aces_tm"): return lambda path: load_image(path, True, True, tone_map_aces)
        if (name == "rgb"): return lambda path: load_image(path, False, False)
        if (name == "rgb_tm"): return lambda path: load_image(path, False, True)
        if (name == "rgb_aces_tm"): return lambda path: load_image(path, False, True, tone_map_aces)
        raise ValueError(f"Invalid image loader name {il_name}")
    