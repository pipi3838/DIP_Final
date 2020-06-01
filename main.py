from PIL import Image
from palette import *
from util import *
import random
from test import *
from transfer import *

def main():
	img_name = 'lena.jpg'
	img = Image.open(img_name)
	print(img_name, img.format, img.size, img.mode)
	lab = rgb2lab(img)

	colors = lab.getcolors(img.width * img.height)
	bins = {}
	for count, pixel in colors:
		bins[pixel] = count
	bins = sample_bins(bins)
	means = k_means(bins,init_mean=True)

	color = random.sample(range(255),3)
	rbf_weights(color,means)
	print()
	calc_weights(color,means)
	# for m in means:
	# 	color = np.array(random.sample(range(255),3))
	# 	modified_palette = np.array(random.sample(range(255),3))
	# 	res = single_color_transfer(color, m, modified_palette)
	# 	my_res = single_palette_color_transfer(color, m, modified_palette)
	# 	print(res.data)
	# 	print(my_res)
	# for p,cnt in bins.items():
	# 	print('{}: {}'.format(p,cnt))

if __name__ == '__main__':
	main()
