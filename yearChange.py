from functions import *

if __name__ == "__main__":
	time = 1041415948
	results = []
	while time < 1524219587:
		results.append(experiment2(time))
		time = time + secondsInAYear
	print results