'''  
Copyright (c) 2017 Intel Corporation.
Licensed under the MIT license. See LICENSE file in the project root for full license information.
'''

import numpy as np
import cv2
import copy
import argparse
import pickle
import os
import boto3

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--days", type=int, default=1, help="days in past")
ap.add_argument("-b", "--buffer", type=int, default=1, help="buffer from today")
# ap.add_argument("-a", "--min-area", type=int, default=250, help="minimum area size")
args = vars(ap.parse_args())


def get_data(tstamp_l, tstamp_h, src=0):

    data = []
    if src == 0:

        filelist = os.listdir("output")
        out = [files for files in filelist if ( float(files[:-4]) > tstamp_l and float(files[:-4]) < tstamp_h )]

        for files in out:
            file_name = "output" + "/" + files
            with open(file_name, "rb") as f:              
                data.extend([pickle.load(f)])
    else:
        tl = str(int(tstamp_l) - 1)
        th = str(int(tstamp_h) + 1)
        prefix = "hm_"
        for i in range(len(tl)):
            if tl[i] == th[i]:
                prefix = prefix + tl[i]
            else:
                break

        print(prefix)
        s3 = boto3.client('s3')
        aws_s3 = boto3.resource('s3')   
        obj_list = s3.list_objects(Bucket="axelta-production",EncodingType="url",Prefix=prefix)

        for obj in obj_list["Contents"]:
            ts = float(obj["Key"][3:-4])
            if ts > tstamp_l and ts < tstamp_h:     
                try:
                    aws_s3.Bucket("axelta-production").download_file(obj["Key"], "temp.pkl")
                except botocore.exceptions.ClientError as e:
                    if e.response['Error']['Code'] == "404":
                        print("The object does not exist.")
                    else:
                        raise

                with open("temp.pkl", "rb") as f:
                    data.extend([pickle.load(f)])

    print(len(data))                
    return(data)



def image_gen(motiondata=None):

    if motiondata == None or len(motiondata) < 1:
        exit()
    
    first_iter = 1

    for data in motiondata:
        if first_iter == 1:
            accum_image = data[1]
            first_iter = 0
        else:
            accum_image = np.add(accum_image, data[1])
   
    
    first_frame = motiondata[0][0]

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

    b = 1551467731
    a = 1551267473	 
    motiondata = get_data(a,b,1)

    image_gen(motiondata)



     # with open(args["input"], "rb") as f:
     #        images = pickle.load(f)



        # aws_s3 = boto3.resource('s3')
        # s3 = boto3.client('s3')
        # s3.upload_file(file_path,"axelta-production",file_name)
        # object_acl = aws_s3.ObjectAcl("axelta-production",file_name)
        # response = object_acl.put(ACL='public-read')
        # try:
        #     aws_s3.Bucket("axelta-production").download_file(file_name, "test.pkl")
        # except botocore.exceptions.ClientError as e:
        #     if e.response['Error']['Code'] == "404":
        #         print("The object does not exist.")
        #     else:
        #         raise

        # with open("test.pkl", "rb") as f:
        #     print(pickle.load(f))
