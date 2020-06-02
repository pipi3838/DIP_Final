from PIL import Image
from palette import *
from util import *
import random
from transfer import *
import time
def main():
	# load image
	img_name = 'lena.png'
	img = Image.open(img_name)
	print(img_name, img.format, img.size, img.mode)
	
	t1 = time.time()
	# transfer to lab
	lab = rgb2lab(img)

	# get palettes from kmeans ( means = palettes)
	colors = lab.getcolors(img.width * img.height)
	bins = {}
	for count, pixel in colors:
		bins[pixel] = count
	bins = sample_bins(bins)

	k_palettes = 5
	means = k_means(bins, k=k_palettes, init_mean=True)

	# sample grid from RGB colors and the get rbf weights
	sample_level = 16
	sample_colors = sample_RGB_color(sample_level)
	# used only when new image is loaded
	sample_weight_map = rbf_weights(means, sample_colors) 

	# img color transfer given any modified_p 
	modified_p = [random.sample(range(255),3) for _ in range(k_palettes)] 
	result = img_color_transfer(lab, means, means, sample_weight_map, sample_colors, sample_level)
	result.save('result.jpg')
	t2 = time.time()

	print('First Total time: {}'.format(str(t2 - t1)))

if __name__ == '__main__':
	main()
