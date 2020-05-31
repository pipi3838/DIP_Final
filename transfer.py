import math
import itertools
import numpy as np
from util import *

def monotonic_luminance_transfer(ori_palette, index, new_l):
	"""
	Args:
		ori_palette: k color palette
		index: index of the changed color palette
		new_l: new set luminance

	Return: 
		modified_palette
	"""
	modified_palette = ori_palette
	modified_palette[index] = (new_l, *modified_palette[index][-2:])
	for i in range(index+1, len(original_p)):
		modified_palette[i] = (min(modified_palette[i][0], modified_palette[i-1][0]), *modified_palette[i][-2:])
	for i in range(index-1, -1, -1):
		modified_palette[i] = (max(modified_palette[i][0], modified_palette[i+1][0]), *modified_palette[i][-2:])

	return modified_palette

def luminance_transfer(pixel_color, ori_palette, modified_palette):
	"""
	Args:
		pixel_color: pixel to be transfered by modified palette
		ori_palette: original palette
		modified_palette: modified palette
	Return: 
		modified luminance
	"""
	l = pixel_color[0]
	if l <= 0: return 0
	if l > 100: return 100
	ori_l = [100] + [*ori_palette[:,0]] + [0]
	modified_l = [100] + [*modified_palette[:,0]] + [0]

	# find the nearest two palette by luminance
	for i in range(len(ori_l)):
		if ori_l[i] == l: return modified_l[i]
		if ori_l[i] < l < ori_l[i+1]:
			return (modified_l[i+1] * (l - ori_l[i]) + modified_l[i] * (ori_l[i+1] - l)) / (ori_l[i+1] - ori_l[i])

def single_palette_color_transfer(pixel_color, ori_color, modified_color):

	def get_boundary(ori, direct, k_min, k_max, max_iter=20):
		start = ori + k_min * direct
		end = ori + k_max * direct
		for _ in range(max_iter):
			mid = (start + end) / 2
			if ValidLAB(mid) and ValidRGB(LABtoRGB(mid)): start = mid
			else: end = mid

		return (start + end) / 2

	pixel_color = np.array(RegularLAB(pixel_color))
	ori_color = np.array(RegularLAB(ori_color))
	modified_color = np.array(RegularLAB(modified_color))

	offset = modified_color - ori_color

	c_boundary = get_boundary(ori_color, offset, 1,255)
	lab = pixel_color + offset
	if ValidLAB(lab) and ValidRGB(LABtoRGB(lab)):
		x_boundary = get_boundary(pixel_color, offset, 1, 255)
	else:
		x_boundary = get_boundary(modified_color,pixel_color - ori_color,0,1)

	ratio = min(1, (distance(x_boundary,pixel_color) / distance(c_boundary, ori_color)))
	res = pixel_color + (x_boundary - pixel_color) / distance(x_boundary, pixel_color) * distance(modified_color,ori_color) * ratio
	return res

def rbf_weights(pixel_color, ori_palette):

	dist = []
	for p1, p2 in itertools.combinations(ori_palette, 2):
		dist.append(distance(p1,p2))
	mean_dist = sum(dist) / len(dist)

	def gaussian(a,b):
		r = distance(a,b)
		return math.exp(-(r**2) / (2 * (mean_dist**2)))

	palette_cnt = len(ori_palette)

	p_matrix = np.zeros((palette_cnt,palette_cnt))
	for i in range(palette_cnt):
		for j in range(palette_cnt):
			p_matrix[i,j] = gaussian(ori_palette[j], ori_palette[i])

	p_matrix = np.linalg.inv(p_matrix)
	lamda = []
	for i in range(palette_cnt):
		ans = np.zeros(palette_cnt)
		ans[i] = 1
		lamda.append(np.dot(ans,p_matrix))

	weights = np.zeros(palette_cnt)
	for i in range(palette_cnt):
		for j in range(palette_cnt):
			weights[i] += lamda[i][j] * gaussian(pixel_color, ori_palette[j])
	weights = [w if w > 0 else 0 for w in weights]
	weights /= np.sum(weights)

	return weights











