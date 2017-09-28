import numpy as np
import matplotlib.pyplot as plt



arr = np.float32(np.load("buses_data.npy"))
arr = np.concatenate(arr)

print(arr)

for i in range(len(arr)):
	arr[i][2] = arr[i][2]%(3600*24)/3600
	if arr[i][1] == 0:
		arr[i][0] = 0
		continue
	if (arr[i][0] - arr[i][1])/0.27 > 50:
		pass#print(arr[i])
	arr[i][0] = (arr[i][0] - arr[i][1])/0.27
	#print(arr[i][0], arr[i][1])
	#print(arr[i][1])

plt.scatter(arr[::10,2], arr[::10,0])
plt.show()


arr = np.load("stops_data.npy")
arr = np.float32(np.concatenate(arr))
np.random.shuffle(arr)
print(arr)

for i in range(len(arr)):
	arr[i][1] = arr[i][1]%(3600*24)/3600
	arr[i][0] /= 60
	#print(arr[i])
	#print(arr[i])
	#print(arr[i][1])

print(len(arr[::10,1]))
plt.scatter(arr[::10,1], arr[::10,0])
plt.show()

'''with open("stops.csv", "w") as file:
	file.write("wait_time;TIME\n")
	for i in arr:
		file.write("{};{}\n".format(i[0],i[1]))'''