import numpy as np
import pickle
import os
import argparse
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d



ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input", required=True, help="path to the pyd files")
ap.add_argument("-t", "--thresh", default=10, help="min distance between centroids")
ap.add_argument("-f", "--frames", default=10, help="min time difference between centroids to be considered single path")
ap.add_argument("-l", "--length", default=1, help="minimum path lengths to be output")
args = vars(ap.parse_args())


files = os.listdir(args["input"])
files.sort()

frame_centroids = []
print("loading files...")
for file in files:
	if file.endswith(".pyd"):		

		file_name = args["input"] + "/" + file
		with open(file_name, "rb") as f:
			centroids = pickle.load(f)

		frame_centroids.extend(centroids)	

#trajectory manipulate

print(len(frame_centroids))
tracks = []
print("generating tracks...")
index = 0
for cntrs in frame_centroids:
	index += 1
	print(index)
	if len(tracks) == 0:		
		tracks.append([cntrs])

	else:		
		#for val in cntrs[1]:
		d = []
		j = 0
			#print(len(tracks))
		for track in tracks:
			j += 1 
			#print(j)
			i = len(track)
			ed = (np.sqrt(np.square(cntrs[1] - track[i-1][1]) + np.square(cntrs[2] - track[i-1][2])))
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
		i = len(tracks[d[0]])
		if d[1] < int(args["thresh"]) and (cntrs[0]-tracks[d[0]][i-1][0]) < int(args["frames"]):
			tracks[d[0]].append(cntrs)
		else:
			tracks.append([cntrs])
			
print(len(tracks))

print("plotting graphs...")
colors = cm.rainbow(np.linspace(0, 3, len(tracks)))



z_plt = []
total = 0
for track ,c in zip(tracks, colors):
	if len(track) < int(args["length"]):
		continue
	total += 1	
	x_plt = []
	y_plt = []
	for cntrs in track:		
	
		x_plt.append(cntrs[1])
		y_plt.append(cntrs[2])

	plt.scatter(x_plt, y_plt, s=4,  color=c)
print(total)

# fig = plt.figure()
# ax = fig.add_subplot(111, projection = "3d") 	
# ax.scatter(x_plt, z_plt, y_plt,)
#ax.axis([0,W,0,600,H,0])
#plt.scatter(x_plt, y_plt, s=1)
plt.axis([0,500,300,0])
plt.savefig("graph.png")




