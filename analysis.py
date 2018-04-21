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
# 	return scipy.special.binom(N,x)*(prob**x)*((1-prob)**(N-x))
# def binomialCoefficient)

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
# 			print counter
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
	# 						x = min(x, 0.09)
						results.append(x)
						
# 						print company
# 						print original
# 						print next
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
# 1514798050
def experiment2(timestamp):
	iresults=[]
	for i in range(1,2):
		a=1
		delay=0
		s=260
# 		x = simulation4(filename='financialAndTechnology.txt', lower=0, upper=0.9,fromTime=1483244024, toTime=1514798050, previousOffset=1, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=1, nextNextColumn=1, sample=True, sampleNumber=s, showGraph=False)		
		x = simulation4(filename='financial2.txt', lower=0, upper=0.9,fromTime=timestamp, toTime=None, previousOffset=1, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=1, nextNextColumn=1, sample=False, sampleNumber=s, showGraph=False)		

		length=s
		y = x**length
		print 'y'
		print y
		iresults.append(y)
	print iresults
	return x
time = 1041415948
results = []
while time < 1524219587:
	results.append(experiment2(time))
	time = time + secondsInAYear
print results
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
# 		x = simulation4(filename='financialAndTechnology.txt', lower=0, upper=0.9,fromTime=1483244024, toTime=1514798050, previousOffset=1, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=1, nextNextColumn=1, sample=True, sampleNumber=s, showGraph=False)		
# 		x = simulation4(filename='financialAndTechnology.txt', lower=0, upper=0.9,fromTime=1514798050, toTime=None, previousOffset=1, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=1, nextNextColumn=1, sample=True, sampleNumber=s, showGraph=False)		
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
# 		x = simulation4(filename='financialAndTechnology.txt', lower=0, upper=0.9,fromTime=1483244024, toTime=1514798050, previousOffset=1, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=1, nextNextColumn=1, sample=True, sampleNumber=s, showGraph=False)		
# 		x = simulation4(filename='financialAndTechnology.txt', lower=0, upper=0.9,fromTime=1514798050, toTime=None, previousOffset=1, previousTime=None,nextOffset=delay, nextTime=None, nextNextOffset=delay+a, previousColumn=1, currentColumn=1, nextColumn=1, nextNextColumn=1, sample=True, sampleNumber=s, showGraph=False)		
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
def combineFiles(filenames):	
	result = ''
	for filename in filenames:
		result = result + open(filename,'r').read()
	return result.replace('START\n','')

def generateTableWithCompanyNames(filename):
	file = open(filename, 'r').readlines()
	table=[]
	company=''
	for n in xrange(len(file)):
		line=file[n]
		print n
		if 'COMPANY:' in line:
			company = line.replace('COMPANY:','').replace('\n','')
		else:
			if not 'START' in line and not line=='\n':
				line = line.replace('\n','') + company +'\n'
				print line
				table.append(line)
	table.sort(key = lambda x:int(x.split('\t')[0]))
	return table

def writeTableWithCompanyNames(filename1, filename2):
	file = open(filename2, 'w')
	table = generateTableWithCompanyNames(filename1)
	for m in table:
		file.write(m)

def generateTableWithCompanyNamesVersion2(file):
	file=file.split('\n')
	table=[]
	company=''
	for n in xrange(len(file)):
# 		print n
		if 'COMPANY:' in file[n]:
			company = file[n].replace('COMPANY:','').replace('\n','')
		else:
			if not 'START' in file[n]:
				line = file[n].replace('\n','') + company +'\n'
				if len(line.split('\t')) < 2:
					print 'moose'
					print n
				table.append(line)
# 	print table
	table.sort(key = lambda x:int(x.split('\t')[0]))
	return table
		
def writeTableWithCompanyNamesVersion2(filenames, filename2):
	file = open(filename2, 'w')
	text = combineFiles(filenames)
	table = generateTableWithCompanyNamesVersion2(text)
	for m in table:
		print m
		file.write(m)

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

# a = combineFiles(['financial.txt','technology.txt'])
# b = open('tex.txt','w')
# b.write(a)
# results=[]
# for i in xrange(10):
# 	results.append(experiment4())
# print results

# def biggestReturns(filename):
# 	for com


# writeTableWithCompanyNamesVersion2(['financial.txt','technology.txt','industrial_goods.txt','services.txt','utilities.txt','basic_materials.txt','consumer_goods.txt','conglomerates.txt'],'combined.txt')
# writeTableWithCompanyNamesVersion2(['financial.txt','technology.txt'],'financialAndTechnology.txt')

# filename = 'financialCash.txt'
# file=open(filename,'r').readlines()
# medianCash = str(returnMedianCash(file))
# percentileCash = str(returnPercentileCash(file, 90))

# strings=['services','industrial_goods','services','utilities','basic_materials','consumer_goods','conglomerates']
# string='services'
# for string in strings:
# 	writeTableWithCompanyNames(string+'.txt',string+'2.txt')
# writeTableWithCompanyNames('technology.txt','technology2.txt')
# writeTableWithCompanyNames('financial.txt','financial2.txt')



# print medianCash	
# print percentileCash
# writeTableWithCompanyNames('industrial_goods.txt','industrial_goods2.txt')	
# simulation2('financial2.txt', 'random', filterFunction = 'hasMoreCashThan'+percentileCash, cashFilename = 'financialCash.txt')
# simulation2('financial2.txt', 'random')

# parameters;
# filename
# fromTime
# toTime
# previousOffset
# previousTime
# nextOffset
# nextTime
# previousColumn
# currentColumn
# nextColumn





# print binomial(5,10)	
# print findMeanAndConfidenceInterval(5,10)
# 	counter=0
# 	
# 	while counter < len(file):
# 		currentTime = int(file[0].split('\t')[0])
# 	for m in xrange(len(file)):
# 		line = file[m].split('\t')
# 		timestamp = int(line[0])
# 		
# 		if not timestamp == currentTime:
# 			prices = [
		
		

	
# def simulation1():
# 	results=[]
# 	times=[]
# 	for n in xrange(len(companies)):
# 		x= readCompany(firstReadFunction, companies[n],0.05,3,3, thirdAnalysisFunction)[0]
# # 		print x
# 		timeresult=x[1]
# 		profit=x[0]
# 		results.append(profit)
# 		times.append(timeresult)
# 	print results
# 	print np.mean(results)
# # 	print times
# # 	print max(times)
# # 	print results[times.index(max(times))]
# # 	print companies[times.index(max(times))]
		
# simulation1()		
		
# bigtotal=0
# N=0
# 
# results = []
# # 	print total
# print bigtotal/N
# print results



# def simulation2(filename, method = 'random', year = 'all', function = np.average, filterFunction = None, cashFilename = None):
# 	
# 	def filter(file, filterFunction, number = None):
# 		result = []
# 		for n in xrange(len(file)):
# 			line = file[n]
# 			if filterFunction(line.split('\t')[7].replace('\n',''), number) == True:
# 				result.append(line)
# 		return result
# 	
# 	def hasMoreCashThan(company, number):
# # 		print number
# 		cashFile = open(cashFilename,'r').readlines()
# 		for m in xrange(len(cashFile)):
# 			line = cashFile[m]
# 			if company in line:
# 				amount = int(float(line.split('\t')[1].replace('\n','')))
# # 				print company
# # 				print amount
# 				if amount > number:
# 
# # 					print 'True'
# 					return True
# 				else:
# # 					print 'False'
# 					return False
# 		return None
# 				
# 	def hasLessCashThan(company, number):
# 		cashFile = open(cashFilename,'r').readlines()
# 		for m in xrange(len(cashFile)):
# 			line = cashFile[m]
# 			if company in line:
# 				
# 				amount = int(float(line.split('\t')[1].replace('\n','')))
# # 				print company
# # 				print amount
# 				if amount < number:
# 
# # 					print 'True'
# 					return True
# 				else:
# # 					print 'False'
# 					return False
# 		return None	
# 	if isinstance(filename, basestring):
# 		file = open(filename, 'r').readlines()
# 	else:
# 		file = filename
# 	if not filterFunction == None:
# 		if 'hasMoreCashThan' in filterFunction:
# 			number = float(filterFunction.replace('hasMoreCashThan',''))
# 			file = filter(file, hasMoreCashThan, number)
# 		if 'hasLessCashThan' in filterFunction:
# 			number = float(filterFunction.replace('hasLessCashThan',''))
# 			file = filter(file, hasLessCashThan, number)
# 		
# 	def findPriceForDayOffset(company, lineNumber, offset, forwards = True):
# 		counter = lineNumber
# 		offsetCounter = 0
# 		while counter > 0:
# 			if forwards:
# 				counter = counter + 1
# 			if not forwards:
# 				counter = counter - 1
# 			try:
# 				line = file[counter].split('\t')
# 			except:
# 				return None
# 			if company + '\n' in line:				
# 				if offsetCounter == offset:
# 					try:
# 						return float(line[1])
# 					except:
# 						print line
# 				else:
# 					offsetCounter = offsetCounter + 1
# 		return None
# 								
# 	def findPreviousPrice(company, lineNumber, timestamp):
# 		counter = lineNumber
# 		while counter > 0 and counter < len(file):
# 			counter = counter - 1
# 			line = file[counter].split('\t')
# 			if company + '\n' in line:
# 				if line[0] > timestamp - (secondsInADay * 7):
# 					return float(line[1])
# 				else:
# 					return None
# 		return None
# 	def findNextPrice(company, lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		while counter < len(file) - 1:
# 			counter = counter + 1
# 			line = file[counter].split('\t')
# 			if company + '\n' in line and int(line[0]) > timestamp:
# 				if not line[1] == 'None':
# 					return float(line[1])
# 				else:
# 					return None
# 		return None
# 	def findWorstNextPrice(company, lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		while counter < len(file) - 1:
# 			counter = counter + 1
# 			line = file[counter].split('\t')
# 			if company + '\n' in line and int(line[0]) > timestamp:
# 				if not line[1] == 'None':
# 					return float(line[3])
# 				else:
# 					return None
# 		return None
# 	def findAverageNextPrice(company, lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		while counter < len(file) - 1:
# 			counter = counter + 1
# 			line = file[counter].split('\t')
# 			if company + '\n' in line and int(line[0]) > timestamp:
# 				if not line[1] == 'None':
# 					return (float(line[3]) + float(line[2]))/2
# 				else:
# 					return None
# 		return None
# 	def findNextPriceEnd(company, lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		while counter < len(file) - 1:
# 			counter = counter + 1
# 			line = file[counter].split('\t')
# 			if company + '\n' in line and int(line[0]) > timestamp:
# 				if not line[1] == 'None':
# 					return float(line[4])
# 				else:
# 					return None
# 		return None
# 	def findPriceForEndOfDay(company, lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		while counter < len(file) - 1:
# 			
# 			line = file[counter].split('\t')
# 			if company + '\n' in line and int(line[0]) == timestamp:
# 				if not line[1] == 'None':
# 					return float(line[4])
# 				else:
# 					return None
# 			counter = counter + 1
# 		return None
# 	def findPricesForThatDay(lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			counter = counter - 1
# 			lineTimestamp = int(file[counter].split('\t')[0])
# 		counter = counter + 1
# 		prices = {}
# 		lineTimestamp = int(file[counter].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			line = file[counter].split('\t')
# 			company = line[7].replace('\n','')
# 			try:
# 				price = float(line[1])
# 				prices[company] = price
# 			except:
# 				pass			
# 			counter = counter + 1
# # 			print counter
# 			if not counter == len(file)-1:
# 				lineTimestamp = int(file[counter].split('\t')[0])
# 			else:
# 				return prices
# 		return prices
# 	def findPricesForBeginningOfDay(lineNumber):
# 		return findPricesForThatDay(lineNumber)
# 	def findPricesForEndOfDay(lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			counter = counter - 1
# 			lineTimestamp = int(file[counter].split('\t')[0])
# 		counter = counter + 1
# 		prices = {}
# 		lineTimestamp = int(file[counter].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			line = file[counter].split('\t')
# 			company = line[7].replace('\n','')
# 			try:
# 				price = float(line[4])
# 				prices[company] = price
# 			except:
# 				pass			
# 			counter = counter + 1
# # 			print counter
# 			if not counter == len(file)-1:
# 				lineTimestamp = int(file[counter].split('\t')[0])
# 			else:
# 				return prices
# 		return prices
# 	def findPricesForPreviousDay(lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			counter = counter - 1
# 			lineTimestamp = int(file[counter].split('\t')[0])
# 		return findPricesForThatDay(counter)
# 	def findPricesForPreviousDayNonWeekend(lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			counter = counter - 1
# 			lineTimestamp = int(file[counter].split('\t')[0])
# 			if lineTimestamp == timestamp - secondsInADay:
# 				
# 				return findPricesForThatDay(counter)
# 			else:
# 				return {}
# 	def findPricesForPreviousDayWeekend(lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			counter = counter - 1
# 			lineTimestamp = int(file[counter].split('\t')[0])
# 			if lineTimestamp == timestamp - secondsInADay*3:
# 				
# 				return findPricesForThatDay(counter)
# 			else:
# 				return {}
# 	def findPricesForPreviousDayEnd(lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			counter = counter - 1
# 			lineTimestamp = int(file[counter].split('\t')[0])
# 		return findPricesForEndOfDay(counter)		
# 	def findPriceThatHasFallen(lineNumber, lower, upper):
# 		results={}
# 		prices = findPricesForThatDay(lineNumber)
# 		previousPrices = findPricesForPreviousDay(lineNumber)
# # 		print prices
# # 		print previousPrices
# 		companies = list(set(prices.keys()).intersection(previousPrices.keys()))
# 		for member in companies:
# 			if prices[member] < previousPrices[member]*upper and prices[member] > previousPrices[member]*lower:
# # 				print prices[member]
# # 				print previousPrices[member]
# 				results[member] = prices[member]
# # 				print member
# # 				print previousPrices[member]
# # 				print prices[member]				
# # 				print findNextPrice(member, lineNumber)
# # 				timestamp =  int(file[lineNumber].split('\t')[0])
# # 				print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
# 		return results
# 	def findPriceThatHasFallenNonWeekend(lineNumber, lower, upper):
# 		results={}
# 		prices = findPricesForThatDay(lineNumber)
# 		previousPrices = findPricesForPreviousDayNonWeekend(lineNumber)
# # 		print prices
# # 		print previousPrices
# 		companies = list(set(prices.keys()).intersection(previousPrices.keys()))
# 		for member in companies:
# 			if prices[member] < previousPrices[member]*upper and prices[member] > previousPrices[member]*lower:
# # 				print prices[member]
# # 				print previousPrices[member]
# 				results[member] = prices[member]
# # 				print member
# # 				print previousPrices[member]
# # 				print prices[member]				
# # 				print findNextPrice(member, lineNumber)
# # 				timestamp =  int(file[lineNumber].split('\t')[0])
# # 				print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
# 		return results
# 	def findPriceThatHasFallenWeekend(lineNumber, lower, upper):
# 		results={}
# 		prices = findPricesForThatDay(lineNumber)
# 		previousPrices = findPricesForPreviousDayWeekend(lineNumber)
# # 		print prices
# # 		print previousPrices
# 		companies = list(set(prices.keys()).intersection(previousPrices.keys()))
# 		for member in companies:
# 			if prices[member] < previousPrices[member]*upper and prices[member] > previousPrices[member]*lower:
# # 				print prices[member]
# # 				print previousPrices[member]
# 				results[member] = prices[member]
# # 				print member
# # 				print previousPrices[member]
# # 				print prices[member]				
# # 				print findNextPrice(member, lineNumber)
# # 				timestamp =  int(file[lineNumber].split('\t')[0])
# # 				print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
# 		return results
# 
# 	def findPriceThatHasFallenEnd(lineNumber, lower, upper):
# 		results={}
# 		prices = findPricesForEndOfDay(lineNumber)
# 		previousPrices = findPricesForPreviousDayEnd(lineNumber)
# # 		print prices
# # 		print previousPrices
# 		companies = list(set(prices.keys()).intersection(previousPrices.keys()))
# 		for member in companies:
# 			if prices[member] < previousPrices[member]*upper and prices[member] > previousPrices[member]*lower:
# # 				print prices[member]
# # 				print previousPrices[member]
# 				results[member] = prices[member]
# # 				print member
# # 				print previousPrices[member]
# # 				print prices[member]
# # 				print findNextPrice(member, lineNumber)
# 		return results
# 	def findPriceThatHasFallenEnd3(lineNumber, lower, upper):
# 		results={}
# 		prices = findPricesForBeginningOfDay(lineNumber)
# 		previousPrices = findPricesForPreviousDayEnd(lineNumber)
# # 		print prices
# # 		print previousPrices
# 		companies = list(set(prices.keys()).intersection(previousPrices.keys()))
# 		for member in companies:
# 			if prices[member] < previousPrices[member]*upper and prices[member] > previousPrices[member]*lower:
# # 				print prices[member]
# # 				print previousPrices[member]
# 				results[member] = prices[member]
# # 				print member
# # 				print previousPrices[member]
# # 				print prices[member]
# # 				print findNextPrice(member, lineNumber)
# 		return results
# 	def findPriceThatHasFallenTwice(lineNumber, lower, upper, lower2, upper2):
# 		results={}
# 		prices = findPricesForThatDay(lineNumber)
# 		previousPrices = findPricesForPreviousDay(lineNumber)
# # 		print prices
# # 		print previousPrices
# 		companies = list(set(prices.keys()).intersection(previousPrices.keys()))
# 		for member in companies:
# 			try:
# 				if prices[member] < previousPrices[member]*upper and prices[member] > previousPrices[member]*lower:
# 					previousPreviousPrice = findPriceForDayOffset(member, lineNumber, 2, False)
# 					if previousPrices[member] < previousPreviousPrice * upper2 and previousPrices[member] > previousPreviousPrice * lower2:
# 	# 				print prices[member]
# 	# 				print previousPrices[member]
# 						results[member] = prices[member]
# 			except:
# 				pass
# 		return results
# 		
# 	def findPriceThatHasFallenVersion2(lineNumber, lower, upper):
# 		results={}
# 		prices = findPricesForEndOfDay(lineNumber)
# 		previousPrices = findPricesForBeginningOfDay(lineNumber)
# # 		print prices
# # 		print previousPrices
# 		companies = list(set(prices.keys()).intersection(previousPrices.keys()))
# 		for member in companies:
# 			if prices[member] < previousPrices[member]*upper and prices[member] > previousPrices[member]*lower:
# # 				print prices[member]
# # 				print previousPrices[member]
# 				results[member] = prices[member]
# # 				print member
# # 				print previousPrices[member]
# # 				print prices[member]
# # 				print findNextPrice(member, lineNumber)
# 		return results		
# 		
# 		
# 	def goToNextRow(lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			counter = counter + 1
# 			lineTimestamp = int(file[counter].split('\t')[0])
# 			if counter == len(file) - 1:
# 				return None
# 		return counter						
# 	def findProfitFromPriceThatHasFallen(lineNumber, lower, upper, method = 'random'):
# # 		print lineNumber
# 		companies = findPriceThatHasFallen(lineNumber, lower, upper)
# # 		print companies
# 		if len(companies) == 0:
# 			return 1
# 		if method == 'random':
# 			company = random.sample(companies.keys(),1)[0]
# 		if method == 'lowest':
# 			company = min(companies, key = companies.get)
# 		if method == 'highest':
# 			company = max(companies, key = companies.get)
# 			
# 		price = companies[company]
# 		nextPrice = findNextPrice(company,lineNumber)
# 		if nextPrice == None:
# 			return 1
# 		percentRise = 1 + ((nextPrice - price)/price)
# # 		print company
# # 		print price
# # 		print nextPrice
# 		return percentRise
# 		
# 	def isWithinYear(counter, year):
# 		if year =='all':
# 			return True
# 		else:
# 			timestamp =  yearToTimestamp(year)
# 			time = int(file[counter].split('\t')[0])
# 			if time >= timestamp and time < timestamp + secondsInAYear:	
# 				return True
# 			else:
# 				return False
# 		
# 	def simulate(lower, upper, method, year):
# 		
# 		counter = 0
# 		total = 1
# 		while not goToNextRow(counter) == None:
# 			
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# # 				print counter
# 	# 			assuming you trade once every three days
# 				coinToss = random.sample(xrange(1),1)[0]
# 				if coinToss == 0:
# 	# 				normal calculation of ROI:
# 					total = total * findProfitFromPriceThatHasFallen(counter, lower, upper, method)
# 	# 				if you can only trade the original investment:
# # 					total = total + findProfitFromPriceThatHasFallen(counter, lower, upper) - 1
# 		return total
# 		
# 	def collectAverageMovements(lower, upper, year):
# 		counter = 0
# 		results=[]
# 		
# 		while not goToNextRow(counter) == None:
# 			
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallen(counter, lower, upper)
# 				for company in companies:
# 					next = findNextPrice(company, counter)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						x = (next - original)/original
# # 						x = min(x, 0.09)
# 						results.append(x)
# 						
# 						print company
# 						print original
# 						print next
# 						time = int(file[counter].split('\t')[0])
# 						print datetime.datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S')
# 		return results
# 	def collectAverageMovementsWeekend(lower, upper, year):
# 		counter = 0
# 		results=[]
# 		
# 		while not goToNextRow(counter) == None:
# 			
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallenWeekend(counter, lower, upper)
# 				for company in companies:
# 					next = findNextPrice(company, counter)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						x = (next - original)/original
# # 						x = min(x, 0.09)
# 						results.append(x)
# 						
# # 						print company
# # 						print original
# # 						print next
# 		return results
# 	def collectAverageMovementsNonWeekend(lower, upper, year):
# 		counter = 0
# 		results=[]
# 		
# 		while not goToNextRow(counter) == None:
# 			
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallenNonWeekend(counter, lower, upper)
# 				for company in companies:
# 					next = findNextPrice(company, counter)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						x = (next - original)/original
# # 						x = min(x, 0.09)
# 						results.append(x)
# 						
# # 						print company
# # 						print original
# # 						print next
# 		return results
# 	def collectAverageMovementsForFallenTwice(lower, upper, lower2, upper2, year):
# 		counter = 0
# 		results=[]
# 		counter = goToNextRow(counter)
# 		while not goToNextRow(counter) == None:
# 			
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallenTwice(counter, lower, upper, lower2, upper2)
# 				for company in companies:
# 					next = findNextPrice(company, counter)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						results.append((next - original)/original)			
# 		return results
# 
# 	def collectAverageMovementsVersion2(lower, upper, year):
# 		counter = 0
# 		results=[]	
# 		while not goToNextRow(counter) == None:
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallenVersion2(counter, lower, upper)
# 				for company in companies:
# # 					next = findNextPrice(company, counter)
# 					next = findPriceForDayOffset(company, counter, 1, forwards = True)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						results.append((next - original)/original)
# # 						print company
# # 						print original
# # 						print next
# 		return results
# 
# 	def collectAverageMovementsEnd(lower, upper, year):
# 		counter = 0
# 		results=[]	
# 		while not goToNextRow(counter) == None:
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallenEnd(counter, lower, upper)
# 				for company in companies:
# # 					next = findNextPrice(company, counter)
# 					next = findNextPriceEnd(company, counter)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						results.append((next - original)/original)
# # 						print company
# # 						print original
# # 						print next
# 		return results
# 		
# 	def collectAverageMovementsEnd2(lower, upper, year):
# 		counter = 0
# 		results=[]	
# 		while not goToNextRow(counter) == None:
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallenEnd(counter, lower, upper)
# 				for company in companies:
# # 					next = findNextPrice(company, counter)
# 					next = findNextPrice(company, counter)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						results.append((next - original)/original)
# # 						print company
# # 						print original
# # 						print next
# 		return results
# 	def collectAverageMovementsEnd3(lower, upper, year):
# 		counter = 0
# 		results=[]	
# 		while not goToNextRow(counter) == None:
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallenEnd3(counter, lower, upper)
# 				for company in companies:
# # 					next = findNextPrice(company, counter)
# 					next = findNextPrice(company, counter)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						results.append((next - original)/original)
# # 						print company
# # 						print original
# # 						print next
# 		return results
# 	def collectAverageMovementsEnd4(lower, upper, year):
# 		counter = 0
# 		results=[]	
# 		while not goToNextRow(counter) == None:
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallenEnd3(counter, lower, upper)
# 				for company in companies:
# # 					next = findNextPrice(company, counter)
# 					next = findPriceForEndOfDay(company, counter)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						results.append((next - original)/original)
# # 						print company
# # 						print original
# # 						print next
# 		return results	
# 	def collectAverageMovements10(lower, upper, year):
# 		counter = 0
# 		results=[]
# 		
# 		while not goToNextRow(counter) == None:
# 			
# 			counter = goToNextRow(counter)
# 			if isWithinYear(counter, year):
# 				companies = findPriceThatHasFallen(counter, lower, upper)
# 				for company in companies:
# 					next = findNextPriceEnd(company, counter)
# # 					next = findPriceForDayOffset(company, counter, 3, forwards = True)
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						results.append((next - original)/original)
# # 						print company
# # 						print original
# # 						print next
# 		return results	
# 	def experiment1():
# 		toTry = [0.7, 0.8, 0.9, 0.95, 1, 1.05, 1.1, 1.15]
# 		mainResults = []
# 		for m in toTry:
# 			x = m
# 			for n in [z for z in toTry if z>m]:
# 				y = n 
# 				results = []
# 				for i in xrange(10):
# 					results.append(simulate(x, y, method, year))
# 				mainResults.append([x, y, function(results)])
# 				mainResults.sort(key = lambda x : x[2], reverse = True)
# 				print mainResults
# 	def experiment2():
# 		results = collectAverageMovements(0.7, 0.9, year)
# # 		print results
# 		median = np.median(results)
# 		threshold = 0
# 		
# 		a =  len([x for x in results if x > threshold ])
# 		b  = len(results)
# 		try:
# 			result = findMeanAndConfidenceInterval(a,b)
# 			print result
# 		except:
# 			print a/b, 0.01
# 			print 'sample size too large'
# 		print year	
# 		print 'median'
# 		print median
# 		returns = [1+x for x in results]
# 		roi = np.product(returns)
# 		print 'roi'
# 		print roi
# 		geometricMean = roi ** (1 / len(returns))
# 		print geometricMean
# 		print geometricMean**156
# 		print len(returns)
# # 		print min(returns)
# 		plt.hist(returns, bins='auto')
# # 		plt.show()
# 		print mean_confidence_interval(returns)
# 		
# 	def experiment3():
# 		results = collectAverageMovementsForFallenTwice(1, 3,0.7,0.95, year)
# # 		print results
# 		median = np.median(results)
# 		threshold = 0
# 		
# 		a =  len([x for x in results if x > threshold ])
# 		b  = len(results)
# 		try:
# 			result = findMeanAndConfidenceInterval(a,b)
# 			print result
# 		except:
# 			print a/b, 0.01
# 			print 'sample size too large'
# 		print 'median'
# 		print median	
# 	print len(file)
# 	
# 	def experiment4():
# 		results = collectAverageMovementsVersion2(0.7,0.95,year)
# # 		print results
# 		median = np.median(results)
# 		threshold = 0
# 		
# 		a =  len([x for x in results if x > threshold ])
# 		b  = len(results)
# 		try:
# 			result = findMeanAndConfidenceInterval(a,b)
# 			print result
# 		except:
# 			print a/b, 0.01
# 			print 'sample size too large'
# 		print 'median'
# 		print median
# 
# 	def experiment5():
# 		results = collectAverageMovementsEnd(0.7,0.95,year)
# # 		print results
# 		median = np.median(results)
# 		threshold = 0
# 		
# 		a =  len([x for x in results if x > threshold ])
# 		b  = len(results)
# 		try:
# 			result = findMeanAndConfidenceInterval(a,b)
# 			print result
# 		except:
# 			print a/b, 0.01
# 			print 'sample size too large'
# 		print 'median'
# 		print median
# 	def experiment6():
# 		results = collectAverageMovementsEnd2(0.7,0.95,year)
# # 		print results
# 		median = np.median(results)
# 		threshold = 0
# 		
# 		a =  len([x for x in results if x > threshold ])
# 		b  = len(results)
# 		try:
# 			result = findMeanAndConfidenceInterval(a,b)
# 			print result
# 		except:
# 			print a/b, 0.01
# 			print 'sample size too large'
# 		print 'median'
# 		print median
# 	def experiment7():
# 		results = collectAverageMovementsEnd3(0.7,0.98,year)
# # 		print results
# 		median = np.median(results)
# 		threshold = 0
# 		
# 		a =  len([x for x in results if x > threshold ])
# 		b  = len(results)
# 		try:
# 			result = findMeanAndConfidenceInterval(a,b)
# 			print result
# 		except:
# 			print a/b, 0.01
# 			print 'sample size too large'
# 		print 'median'
# 		print median	
# 	def experiment8():
# 		results = collectAverageMovementsEnd4(0.7,0.98,year)
# # 		print results
# 		median = np.median(results)
# 		threshold = 0
# 		
# 		a =  len([x for x in results if x > threshold ])
# 		b  = len(results)
# 		try:
# 			result = findMeanAndConfidenceInterval(a,b)
# 			print result
# 		except:
# 			print a/b, 0.01
# 			print 'sample size too large'
# 		print 'median'
# 		print median
# 	def experiment9():
# 		results = collectAverageMovementsVersion2(0.7,0.95,year)
# # 		print results
# 		median = np.median(results)
# 		threshold = 0
# 		
# 		a =  len([x for x in results if x > threshold ])
# 		b  = len(results)
# 		try:
# 			result = findMeanAndConfidenceInterval(a,b)
# 			print result
# 		except:
# 			print a/b, 0.01
# 			print 'sample size too large'
# 		print 'median'
# 		print median
# 	def experiment10():
# 		results = collectAverageMovements10(0.7,0.95,year)
# # 		print results
# 		median = np.median(results)
# 		threshold = 0
# 		
# 		a =  len([x for x in results if x > threshold ])
# 		b  = len(results)
# 		try:
# 			result = findMeanAndConfidenceInterval(a,b)
# 			print result
# 		except:
# 			print a/b, 0.01
# 			print 'sample size too large'
# 		print 'median'
# 		print median
# 
# 	experiment2()
# # def combine(first, second, *therest):
# # 	return first + second + therest
# 
# 
# def simulation3(filename, lower, upper,fromTime=None, toTime=None, previousOffset=1, previousTime=None, nextOffset=1, nextTime=None, previousColumn=1, currentColumn=1, nextColumn=1):
# 	if isinstance(filename, basestring):
# 		file = open(filename, 'r').readlines()
# 	else:
# 		file = filename
# 		
# 	def goToNextRow(lineNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			counter = counter + 1
# 			lineTimestamp = int(file[counter].split('\t')[0])
# 			if counter == len(file) - 1:
# 				return None
# 		return counter			
# 	def isWithinTimeInterval(counter):
# 		time = int(file[counter].split('\t')[0])
# 		if not fromTime == None:
# 			if time < fromTime:
# 				return False
# 		if not toTime == None:
# 			if time > toTime:
# 				return False
# 		return True
# 
# 	def findPricesForThatDay(lineNumber, columnNumber):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			counter = counter - 1
# 			lineTimestamp = int(file[counter].split('\t')[0])
# 		counter = counter + 1
# 		prices = {}
# 		lineTimestamp = int(file[counter].split('\t')[0])
# 		while lineTimestamp == timestamp:
# 			line = file[counter].split('\t')			
# 			company = line[7].replace('\n','')
# 			try:
# 				price = float(line[columnNumber])
# 				prices[company] = price
# 			except:
# 				pass			
# 			counter = counter + 1
# # 			print counter
# 			if not counter == len(file)-1:
# 				lineTimestamp = int(file[counter].split('\t')[0])
# 			else:
# 				return prices
# 		return prices
# 		
# 	def findPricesForDayOffset(lineNumber, numberOfDays, columnNumber, timeFilter = None, direction = 'forwards'):
# 		counter = lineNumber
# 		timestamp = int(file[lineNumber].split('\t')[0])
# 		lineTimestamp = int(file[lineNumber].split('\t')[0])
# 		if direction == 'backwards':
# 			while lineTimestamp > timestamp - secondsInADay*numberOfDays and counter>0:
# 				counter = counter - 1
# 				lineTimestamp = int(file[counter].split('\t')[0])
# 			if timeFilter == None or lineTimestamp == timestamp - secondsInADay*timeFilter:				
# 				return findPricesForThatDay(counter, columnNumber)
# 			else:
# 				return {}
# 		if direction == 'forwards':	
# 			while lineTimestamp < timestamp + secondsInADay*numberOfDays and counter<len(file)-2:
# 				counter = counter + 1
# 				lineTimestamp = int(file[counter].split('\t')[0])
# 			if timeFilter == None or lineTimestamp == timestamp + secondsInADay*timeFilter:
# 				return findPricesForThatDay(counter, columnNumber)
# 			else:
# 				return {}
# 						
# 	def generalFindPriceThatHasFallen(lineNumber):
# 		results={}
# 		prices = findPricesForDayOffset(lineNumber, 0, currentColumn, timeFilter = None, direction = 'backwards')
# 		previousPrices = findPricesForDayOffset(lineNumber, previousOffset, previousColumn, timeFilter = previousTime, direction = 'backwards')		
# 		companies = list(set(prices.keys()).intersection(previousPrices.keys()))
# 		for member in companies:
# 			if prices[member] < previousPrices[member]*upper and prices[member] > previousPrices[member]*lower:
# 				results[member] = prices[member]
# 		return results
# 			
# 	def generalCollectAverageMovements():
# 		counter = 0
# 		results=[]		
# 		while not goToNextRow(counter) == None:			
# 			counter = goToNextRow(counter)
# 			if isWithinTimeInterval(counter):
# 				companies = generalFindPriceThatHasFallen(counter)		
# 				nextPrices = findPricesForDayOffset(counter, nextOffset, nextColumn, timeFilter = nextTime, direction = 'forwards')
# 				for company in companies:
# 					try:
# 						next = nextPrices[company]
# 					except:
# 						continue
# 					if not companies[company] == None and not next == None:
# 						original = companies[company]
# 						x = (next - original)/original
# 	# 						x = min(x, 0.09)
# 						results.append(x)
# 						
# # 						print company
# # 						print original
# # 						print next
# 		return results	
# 		
# 	results = generalCollectAverageMovements()
# 	median = np.median(results)
# 	threshold = 0
# 	
# 	a =  len([x for x in results if x > threshold ])
# 	b  = len(results)
# 	try:
# 		result = findMeanAndConfidenceInterval(a,b)
# 		print result
# 	except:
# 		print a/b, 0.01
# 		print 'sample size too large'
# 	print 'median'
# 	print median
# 	returns = [1+x for x in results]
# 	roi = np.product(returns)
# 	print 'roi'
# 	print roi
# 	geometricMean = roi ** (1 / len(returns))
# 	print geometricMean
# 	print geometricMean**156
# 	print len(returns)
# # 		print min(returns)
# 	plt.hist(returns, bins='auto')
# # 		plt.show()
# 	print mean_confidence_interval(returns)

# def firstAnalysisFunction(prices, threshold, timescale1, timescale2):	
# 	n=len(prices)-1
# 	profits = []
# 	numberOfTransactions=0
# 	total=0
# 	if timescale2==None:
# 		timescale2 = timescale1
# 	while n>0:
# 		try:
# 			a=prices[n]
# 			b=prices[n+timescale1]
# 			c=prices[n-timescale2]
# 			if a>(b+threshold*b):
# 				profit = (c-a)/a
# 				total = total+ profit
# 				print 'moose'
# 				print c,a,b
# 				print profit
# 				profits.append(profit)
# 				n=n-timescale2
# 				print 'john'
# 				print total
# 			else:
# 				n=n-1
# 		except:
# 			n=n-1
# 	print profits 
# 	print 'mateys'
# 	return total
# 
# def secondAnalysisFunction(prices, threshold, timescale1, timescale2):	
# 	n=len(prices)-1
# 	profits = []
# 	numberOfTransactions=0
# 	total=1
# 	if timescale2==None:
# 		timescale2 = timescale1
# 	if timescale2=='entire':
# 		timescale2 = len(prices)-2
# 	while n>0:
# 		try:
# 			a=prices[n]
# 			b=prices[n+timescale1]
# 			if not n<timescale2:	
# 				c=prices[n-timescale2]
# 			else:	
# 				c = prices[0]
# 			if a>(b+threshold*b):
# 				profit = (c-a)/a
# 				total = total * (1+profit)
# 				print 'moose'
# 				print c,a,b
# 				print profit
# 				profits.append(profit)
# 				n=n-timescale2
# 				print 'john'
# 				print total
# 			else:
# 				n=n-1
# 		except:
# 			n=n-1
# 	print profits 
# 	print 'mateys'
# 	return total
# 
# 
# def thirdAnalysisFunction(prices, threshold, timescale1, timescale2):	
# 	timeresult='unassigned'
# 	n=len(prices)-1
# 	profits = []
# 	numberOfTransactions=0
# 	total=1
# 	if timescale2==None:
# 		timescale2 = timescale1
# 	if timescale2=='entire':
# 		timescale2 = len(prices)-2		
# 	while n>0:
# 		a=prices[n]
# 		if not n+timescale1 > len(prices)-1:
# 			b=prices[n+timescale1]
# 		else:
# 			n=n-1
# 			continue
# 		if not n<timescale2:	
# 			c=prices[n-timescale2]
# 		else:	
# 			c = prices[0]
# 		if a>(b+threshold*b):
# 			if timeresult=='unassigned':
# 				timeresult=n
# 			profit = (c-a)/a
# 			total = total * (1+profit)
# 			profits.append(profit)
# 			n=n-timescale2
# 		else:
# 			n=n-1
# 			
# 	if timeresult=='unassigned':
# 		timeresult=0
# 	return total, timeresult

# file=open('results.txt','r').readlines()
# dictionary = {}
# for n in xrange(len(file)):
# 	if 'COMPANY:' in file[n]:
# 		dictionary[file[n].replace('COMPANY:','').replace('\n','')] = n
# companies = dictionary.keys()