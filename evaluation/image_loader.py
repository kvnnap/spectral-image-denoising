from utils.image import load_image

class ImageLoaderFactory:
    # Method returned expects (input, t, substitute)
    @staticmethod
    def create(il_name):
        name = il_name.strip().lower()
        if (name == "gray"): return lambda path: load_image(path, True, False)
        if (name == "gray_tm"): return lambda path: load_image(path, True, True)
        if (name == "rgb"): return lambda path: load_image(path, False, False)
        if (name == "rgb_tm"): return lambda path: load_image(path, False, True)
        raise ValueError(f"Invalid image loader name {il_name}")
    