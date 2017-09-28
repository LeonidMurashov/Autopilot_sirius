from environment import Environment
import random
import pickle
env = Environment(False)
print(1)
features = env.reset()
it = 1
rew = 0
data = []
for i in range(10000000000):
	actions = []
	print(it)
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
            random.shuffle(data)
            with open("data/data-{}.pkl".format(it//10000), 'wb') as f:
                pickle.dump(data, f)
            data.clear()

	if it % 10000 == 0:
		print(it)

	it += 1
