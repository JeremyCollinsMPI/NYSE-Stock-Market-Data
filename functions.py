from __future__ import division
import time
import datetime
import numpy as np
import random
import math
import scipy.special
import matplotlib.pyplot as plt
import scipy
import scipy.stats

infinity = 10**20
secondsInAYear=60*60*24*365
secondsInADay = 60*60*24

def mean_confidence_interval(data, confidence=0.95):
   a = 1.0*np.array(data)
   n = len(a)
   m, se = np.mean(a), scipy.stats.sem(a)
   h = se * scipy.stats.t._ppf((1+confidence)/2., n-1)
   return m, m-h, m+h

def factorial(x):
	return math.factorial(x)

def yearToTimestamp(year):
	return int(time.mktime(datetime.datetime.strptime("01/01/"+str(year), "%d/%m/%Y").timetuple()))

def firstReadFunction(company, year):
	n = dictionary[company]
	if year == 'all':
		timestampLowerLimit = 0
		timestampUpperLimit = infinity
	else:
		timestampLowerLimit = yearToTimestamp(year)
		timestampUpperLimit = yearToTimestamp(int(year)+1)
	prices=[]
	m=n+1
	if not m>=len(file)-1:
		while not 'COMPANY:' in file[m] and not m==len(file)-1:
			try:
				line=file[m].split('\t')
				time=int(line[0])
				if time>timestampLowerLimit and time<timestampUpperLimit:
					prices.append(float(line[1]))
			except:
				pass
			m=m+1		
	return prices

def returnTimePeriod(n):
	m=n+1
	time1=int(file[m].split('\t')[0])
	time2=time1
	if not m>=len(file):
		while not 'COMPANY:' in file[m] and not m==len(file)-1:
			m=m+1	
			if 'COMPANY:' in file[m]:
				time2=int(file[m-1].split('\t')[0])
	return (time1-time2)/secondsInAYear

def binomial(x, N, prob=0.5):
	return (factorial(N)/(factorial(x)*factorial(N-x)))*(prob**x)*((1-prob)**(N-x))

def findMeanAndConfidenceInterval(x, N):
	def normalise(list):
		new = []
		total = sum(list)
		return [x/total for x in list]
	results = []
	for i in xrange(100):
		j = i/100
		results.append(binomial(x, N, j))
	results = normalise(results)
	interval = 0
	prob=0
	while prob <0.9:
		interval = interval + 1
		maximum = max(results)
		maxIndex = results.index(maximum)
		a = max(0,maxIndex-interval)
		b = min(len(results)-1, maxIndex+interval)
		prob = sum(results[a:b])
	return maxIndex/100, interval/100
	
def readCompany(readFunction, company, threshold, timescale1, timescale2=None, analysisFunction=None, year = 'all'):
	if timescale2==None:
		timescale2 = timescale1
	start = dictionary[company]
	prices = readFunction(company, year)
	if not analysisFunction == None:
		return analysisFunction(prices, threshold, timescale1, timescale2), returnTimePeriod(start)

def collectAllTimestamps():
	timestamps=[]
	for n in xrange(len(file)):
		if not 'COMPANY:' in file[n]:
			timestamps.append(int(file[n].split('\t')[0]))
	return sorted(unique(timestamps))
	
def simulation4(filename, lower, upper,fromTime=None, toTime=None, previousOffset=1, previousTime=None, nextOffset=1, nextTime=None, nextNextOffset=None, nextNextTime=None, nextNextColumn=1, previousColumn=1, currentColumn=1, nextColumn=1, sample=False, sampleNumber=150, showGraph=False):
	if isinstance(filename, basestring):
		file = open(filename, 'r').readlines()
	else:
		file = filename
		
	def goToNextRow(lineNumber):
		counter = lineNumber
		timestamp = int(file[lineNumber].split('\t')[0])
		lineTimestamp = int(file[lineNumber].split('\t')[0])
		while lineTimestamp == timestamp:
			counter = counter + 1
			lineTimestamp = int(file[counter].split('\t')[0])
			if counter == len(file) - 1:
				return None
		return counter			
	def isWithinTimeInterval(counter):
		time = int(file[counter].split('\t')[0])
		if not fromTime == None:
			if time < fromTime:
				return False
		if not toTime == None:
			if time > toTime:
				return False
		return True

	def findPricesForThatDay(lineNumber, columnNumber):
		counter = lineNumber
		timestamp = int(file[lineNumber].split('\t')[0])
		lineTimestamp = int(file[lineNumber].split('\t')[0])
		while lineTimestamp == timestamp:
			counter = counter - 1
			lineTimestamp = int(file[counter].split('\t')[0])
		counter = counter + 1
		prices = {}
		lineTimestamp = int(file[counter].split('\t')[0])
		while lineTimestamp == timestamp:
			line = file[counter].split('\t')	
			
			try:
				company = line[7].replace('\n','')
				price = float(line[columnNumber])
				prices[company] = price
			except:
				pass			
			counter = counter + 1
			if not counter == len(file)-1:
				lineTimestamp = int(file[counter].split('\t')[0])
			else:
				return prices
		return prices
		
	def findPricesForDayOffset(lineNumber, numberOfDays, columnNumber, timeFilter = None, direction = 'forwards'):
		counter = lineNumber
		timestamp = int(file[lineNumber].split('\t')[0])
		lineTimestamp = int(file[lineNumber].split('\t')[0])
		if direction == 'backwards':
			while lineTimestamp > timestamp - secondsInADay*numberOfDays and counter>0:
				counter = counter - 1
				lineTimestamp = int(file[counter].split('\t')[0])
			if timeFilter == None or lineTimestamp == timestamp - secondsInADay*timeFilter:				
				return findPricesForThatDay(counter, columnNumber)
			else:
				return {}
		if direction == 'forwards':	
			while lineTimestamp < timestamp + secondsInADay*numberOfDays and counter<len(file)-2:
				counter = counter + 1
				lineTimestamp = int(file[counter].split('\t')[0])
			if timeFilter == None or lineTimestamp == timestamp + secondsInADay*timeFilter:
				return findPricesForThatDay(counter, columnNumber)
			else:
				return {}
						
	def generalFindPriceThatHasFallen(lineNumber):
		results={}
		prices = findPricesForDayOffset(lineNumber, 0, currentColumn, timeFilter = None, direction = 'backwards')
		previousPrices = findPricesForDayOffset(lineNumber, previousOffset, previousColumn, timeFilter = previousTime, direction = 'backwards')		
		companies = list(set(prices.keys()).intersection(previousPrices.keys()))
		for member in companies:
			if prices[member] < previousPrices[member]*upper and prices[member] > previousPrices[member]*lower:
				results[member] = prices[member]
		return results
			
	def generalCollectAverageMovements():
		counter = 0
		results=[]		
		while not goToNextRow(counter) == None:			
			counter = goToNextRow(counter)
			if isWithinTimeInterval(counter):
				companies = generalFindPriceThatHasFallen(counter)		
				nextPrices = findPricesForDayOffset(counter, nextOffset, nextColumn, timeFilter = nextTime, direction = 'forwards')
				for company in companies:
					try:
						next = nextPrices[company]
					except:
						continue
					if not companies[company] == None and not next == None:
						original = companies[company]
						x = (next - original)/original
						results.append(x)
		return results	
	def generalCollectAverageMovements2():
		counter = 0
		results=[]		
		while not goToNextRow(counter) == None:			
			counter = goToNextRow(counter)
			if isWithinTimeInterval(counter):
				companies = generalFindPriceThatHasFallen(counter)		
				nextPrices = findPricesForDayOffset(counter, nextOffset, nextColumn, timeFilter = nextTime, direction = 'forwards')
				nextNextPrices = findPricesForDayOffset(counter, nextNextOffset, nextNextColumn, timeFilter = nextNextTime, direction = 'forwards')
				for company in companies:
					try:
						next = nextPrices[company]
					except:
						continue
					try:
						nextNext = nextNextPrices[company]
					except:
						continue	
					if not companies[company] == None and not next == None and not nextNext == None:
						original = companies[company]
						x = (nextNext - next)/next
						results.append(x)
		return results			
	results = generalCollectAverageMovements2()
	median = np.median(results)
	threshold = 0	
	a =  len([x for x in results if x > threshold ])
	b  = len(results)
	try:
		result = findMeanAndConfidenceInterval(a,b)
		print result
	except:
		print a/b, 0.01
		print 'sample size too large'
	print 'median'
	print median
	print 'mean'
	print np.mean(results)
	returns = [1+x for x in results]
	if sample:
		try:
			returns = random.sample(returns,sampleNumber)	
		except:
			pass
	roi = np.product(returns)
	print 'roi'
	print roi
	geometricMean = roi ** (1 / len(returns))
	print geometricMean
	print len(returns)
	plt.hist(returns, bins='auto')
	if showGraph:
		plt.show()
	print mean_confidence_interval(returns)
	return geometricMean


def experiment1():
	iresults=[]
	for i in range(1,2):
		a=1
		delay=1
		s=30
		x = simulation4(filename='financial2.txt', lower=0.92, upper=0.94,fromTime=None, toTime=None, previousOffset=1, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=4, currentColumn=1, nextColumn=4, nextNextColumn=1, sample=True, sampleNumber=s, showGraph=False)		
		length=260/(max(1,a))
		y = x**s
		print 'y'
		print y
		iresults.append(y)
	print iresults

def experiment2(timestamp):
	iresults=[]
	for i in range(1,2):
		a=1
		delay=0
		s=260
		x = simulation4(filename='financial2.txt', lower=0, upper=0.9,fromTime=timestamp, toTime=None, previousOffset=1, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=1, nextNextColumn=1, sample=False, sampleNumber=s, showGraph=False)		

		length=s
		y = x**length
		print 'y'
		print y
		iresults.append(y)
	print iresults
	return x

def experiment3():
	iresults=[]
	for i in range(1,2):
		a=30
		delay=60
		x = simulation4(filename='healthcare2.txt', lower=0, upper=10,fromTime=1397279218, toTime=None, previousOffset=30, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=1, nextNextColumn=1, sample=False, sampleNumber=260, showGraph=False)		
		length=260/(max(1,a))
		y = x**length
		print 'y'
		print y
		iresults.append(y)
	print iresults

def experiment4():
	iresults=[]
	for i in range(1,2):
		timescale = 6
		a=timescale
		delay=0
		s=30
		x = simulation4(filename='financial2.txt', lower=0, upper=0.85,fromTime=1483244024, toTime=None, previousOffset=timescale, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=4, nextNextColumn=1, sample=True, sampleNumber=s, showGraph=False)		
		length=s
		y = x**length
		print 'y'
		print y
		iresults.append(y)
	print iresults
	return y

def experiment5():
	iresults=[]
	for i in range(1,2):
		a=1
		delay=0
		s=30
		x = simulation4(filename='financial2.txt', lower=0, upper=0.85,fromTime=1483244024, toTime=None, previousOffset=timescale, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=4, nextNextColumn=1, sample=True, sampleNumber=s, showGraph=False)		
		length=s
		y = x**length
		print 'y'
		print y
		iresults.append(y)
	print iresults
	return y

def experiment6():
	iresults=[]
	for i in range(1,2):
		a=1
		delay=1
		s=260
		x = simulation4(filename='financial2.txt', lower=0, upper=0.9,fromTime=None, toTime=None, previousOffset=1, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=4, currentColumn=1, nextColumn=4, nextNextColumn=1, sample=True, sampleNumber=s, showGraph=False)		
		length=260/(max(1,a))
		y = x**s
		print 'y'
		print y
		iresults.append(y)
	print iresults

def returnMedianCash(file):	
	x = []
	for m in range(1,len(file)):
		try:
			x.append(float(file[m].split('\t')[1]))
		except:
			pass
	return np.median(x)

def returnPercentileCash(file, percentile):	
	x = []
	for m in range(1,len(file)):
		try:
			x.append(float(file[m].split('\t')[1]))
		except:
			pass
	return np.percentile(x, percentile)

