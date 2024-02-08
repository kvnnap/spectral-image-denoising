from utils.image import *
from evaluation.metric import *
from skimage.metrics import peak_signal_noise_ratio
import cv2

ref_image = load_image('images/exp_1/povray_reflect_caustics_8.exr', False, False)
noisy_image = load_image('images/exp_1/povray_reflect_caustics_2.exr', False, False)
score = local_ssim(ref_image, noisy_image)

print(f'rgb score: {score}')

gref_image = convert_to_grayscale(ref_image)
gnoisy_image = convert_to_grayscale(noisy_image)
gray_score = local_ssim(gref_image, gnoisy_image)
print(f'gray score: {gray_score}')

tm_ref_image = tone_map(ref_image)
tm_noisy_image = tone_map(noisy_image)
tm_score = local_ssim(tm_ref_image, tm_noisy_image)

print(f'tm score: {tm_score}')


# ref_image = gref_image
# noisy_image = gnoisy_image

result = cv2.PSNR(ref_image, noisy_image, noisy_image.max() - noisy_image.min())
result2 = local_psnr_old(ref_image, noisy_image)

result3 = peak_signal_noise_ratio(ref_image, noisy_image, data_range=noisy_image.max() - noisy_image.min())

#ss_result = cv2.compareSSIM(ref_image, noisy_image, full=True)

print((result, result2, result3))

#"args": ["--result", "results/paper_exp_1_gmsessim-result.json", "--image-base", "images/exp_1"],
#"args": ["--result", "results/result_ssim_psnr_temp.json", "--image-base", "images/exp_1"],
#"args": ["--result", "results/paper_exp_1_gray-result.json", "--result", "results/paper_exp_1_gmsessim-result.json", "--image-base", "images/exp_1"],

# "args": [
#                 "--result", "results/paper_exp_1-result.json", 
#                 "--result", "results/paper_exp_1_gmsessim-result.json", 
#                 "--result", "results/paper_exp_1_gray-result.json",  
#                 "--image-base", "images/exp_1"
#             ]