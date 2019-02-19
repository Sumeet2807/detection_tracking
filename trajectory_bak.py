import numpy as np
import pickle
import argparse
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d



ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", required=True, help="path to the video file")
ap.add_argument("-t", "--thresh", default=10, help="path to the video file")
args = vars(ap.parse_args())

file_name = args["video"] + ".pyd"


with open(file_name, "rb") as f:
	frame_centroids = pickle.load(f)
	

#trajectory manipulate
tracks = []

for cntrs in frame_centroids:
	if len(tracks) == 0:
		for val in cntrs[1]:
			tracks.append([val])

	else:
		
		for val in cntrs[1]:
			d = []
			j = 0
			#print(len(tracks))
			for track in tracks:
				j += 1 
				#print(j)
				i = len(track)
				ed = (np.sqrt(np.square(val[0] - track[i-1][0]) + np.square(val[1] - track[i-1][1])))
				#print(ed)
				if len(d) == 0:
					d.append(j-1)
					d.append(ed)
				else:
					if ed < d[1]:

						#print(d[0],j-1)
						d[0] = (j-1)
						d[1] = ed
			#print(d[1], d[0])
			if d[1] < int(args["thresh"]):
				tracks[d[0]].append(val)
			else:
				tracks.append([val])
				

colors = cm.rainbow(np.linspace(0, 1, len(tracks)))


z_plt = []
for track ,c in zip(tracks, colors):
	x_plt = []
	y_plt = []
	for cntrs in track:		
	
		x_plt.append(cntrs[0])
		y_plt.append(cntrs[1])

	plt.scatter(x_plt, y_plt, s=2,  color=c)


# fig = plt.figure()
# ax = fig.add_subplot(111, projection = "3d") 	
# ax.scatter(x_plt, z_plt, y_plt,)
#ax.axis([0,W,0,600,H,0])
#plt.scatter(x_plt, y_plt, s=1)
plt.axis([0,500,300,0])
plt.show()




