

MODEL_NUMBER = 1

if __name__ == "__main__":
	from environment import Environment, load_simple_bot, simple_bot_logic
	from qlearning3 import DQNAgent, state_size, action_size
	import time
	env = Environment(True)
	features = env.reset()
	load_simple_bot(DQNAgent(state_size, action_size)._build_model(), "chosen_one-{}.h5".format(MODEL_NUMBER))
	it = 0
	while True:
		#l_t = time.clock()
		features = env.step2(simple_bot_logic(features))[0]
		if it > 10000:
			env.render()
		else:
			print(it)
		it += 1
		#print(time.clock() - l_t)