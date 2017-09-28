from environment import Environment
import numpy as np
import matplotlib.pyplot as plt

env = Environment(True)
features = env.reset()
it = 0
data = []
rews = []

for i in range(10000):
	actions = []
	for i in features:
		interval = i[5]
		#actions.append(0)
		if abs(interval) < 50 and not i[16] < 2:
			actions.append(1)
		else:
			if interval > 0 or i[16] < 2:
				actions.append(0)
			else:
				actions.append(2)

	#env.render()
	features, rew, _, _ = env.step(actions)
	rews.append(rew)
	it += 1
	print(it, rew)

env.render()

print(env.reward_history)
print(np.ma.average(env.reward_history))
x = np.arange(len(rews))
plt.plot(x, rews)
plt.show()

