METRICS = ['flip', 'hdrvdp3', 'mse', 'psnr', 'ssim']
NAMEMAP = {
    'caustic_glass': 'cup',
    'povray_cup': 'cups',
    'povray_dice': 'dice',
    'povray_reflect': 'reflect',
    'povray_test': 'outer',
    'torus': 'torus',
    'veach_bidir': 'egg',
    'water_caustic': 'water',
}
CONV = {
    'flip':     lambda x: f'{ x:.2e}',
    'hdrvdp3':  lambda x: f'{-x:.2f}',
    'mse':      lambda x: f'{ x:.2e}',
    'psnr':     lambda x: f'{-x:.2f}',
    'ssim':     lambda x: f'{-x:.2f}',
}