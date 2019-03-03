'''  
Copyright (c) 2017 Intel Corporation.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
'''

import numpy as np
import cv2
import copy
import argparse
import pickle

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="input file")
# ap.add_argument("-a", "--min-area", type=int, default=250, help="minimum area size")
args = vars(ap.parse_args())

def main():
    with open(args["input"], "rb") as f:
            images = pickle.load(f)

    accum_image = images[1]
    first_frame = images[0]

    max_pixel = np.max(accum_image)
    accum_image = accum_image * (255/max_pixel)    
    accum_image = accum_image.astype(dtype=np.uint8)
    # apply a color map
    # COLORMAP_PINK also works well, COLORMAP_BONE is acceptable if the background is dark
    color_image = im_color = cv2.applyColorMap(accum_image, cv2.COLORMAP_JET)
    # for testing purposes, show the colorMap image
    # cv2.imwrite('diff-color.jpg', color_image)

    # overlay the color mapped image to the first frame
    result_overlay = cv2.addWeighted(first_frame, 0.7, color_image, 0.7, 0)

    # save the final overlay image
    cv2.imwrite('diff-overlay.jpg', result_overlay)

    # cleanup
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()