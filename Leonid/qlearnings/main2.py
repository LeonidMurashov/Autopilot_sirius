from environment import Environment
import random
import pickle
import threading

def generate_data(thread):
	
	env = Environment(False)
	print('lol')
	features = env.reset()
	it = 1
	rew = 0
	data = []
	while it < 1000000:
		actions = []

		for k in features:
			interval = k[5]
			if abs(interval) < 50 and not k[16] < 2:
				actions.append(1)
			else:
				if interval > 0 or k[16] < 2:
					actions.append(0)
				else:
					actions.append(2)
		if it % 10:
			for b in range(len(features)):
				data.append([features[b], actions[b], rew])

		features, rew, _, _2 = env.step(actions)
		if it % 10000 == 0:
			features = env.reset()
		if it % 10000 == 0:
		        print('wait...')
		        with open("thread-{}/data-{}.pkl".format(thread, it//10000), 'wb') as f:
		            print("thread-{}/data-{}.pkl".format(thread, it//10000))
		            pickle.dump(data, f)
		        data.clear()
		        print('cool!')
		if it % 1000 == 0:
			print(it)

		it += 1
generate_data(10)



