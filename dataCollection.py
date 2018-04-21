import subprocess
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import dateutil.parser
import ast
import unicodedata
from selenium.webdriver.common.action_chains import ActionChains

def returnPageSource(name, driver=webdriver.Chrome("./chromedriver"), timeLimit=5):
	for i in range(0,timeLimit) :
		try:
			driver.get("https://finance.yahoo.com/quote/"+name+"/history?period1="+str(932054400)+"&period2="+str(ts)+"&interval=1d&filter=history&frequency=1d")
			break
		except:
			print('Waiting')
			time.sleep(1)
			if i==timeLimit-1:
				print("History unavailable")
	return driver.page_source
				
def findHistoricalData(name, driver = webdriver.Chrome("./chromedriver")):
	x = returnPageSource(name, driver)
	x = unicodedata.normalize('NFKD', x).encode('ascii','ignore')
	try:
		x = x.split('"HistoricalPriceStore":{"prices":[')[1]
	except:
		print 'Unavailable'
	y = x.split(']')[0]
	y = '[' + y + ']'
	y = ast.literal_eval(y)
	return y

columns=["date","open","high","low","close","volume","adjclose"]

def listCompanies(x, driver):
	results = []
	hrefs = x.split('href="')
	hrefs = [x.split('"')[0] for x in hrefs]
	hrefs = [x for x in hrefs if "/quote/" in x]
	for member in hrefs:
		member = member.split("quote/")[1].split("?")[0]
		results.append(member)
	return results

def findAllOnPage(x, file, driver):
	hrefs = listCompanies(x, driver)
	for member in hrefs:
		if not '^' in member and not '=' in member:
			try:
				print member
				results = findHistoricalData(member,driver)
				file.write('\nCOMPANY:'+member)
				for o in xrange(len(results)):
					file.write('\n')
					member2 = results[o]
					for col in columns:
						file.write(str(member2.get(col))+'\t')
				print 'success'
			except:
				pass
						
def do(sector, limit, filename):
	file=open(filename,'w')
	file.write('START')
	driver = webdriver.Chrome("./chromedriver")
	driver.get("https://finance.yahoo.com/sector/" +sector)
	x = driver.page_source
	findAllOnPage(x, file, driver)
	n=25	
	while n<=limit:	
		try:			
			driver.get("https://finance.yahoo.com/screener/predefined/"+sector+"?offset="+str(n)+"&count=25")
			x = driver.page_source
			findAllOnPage(x, file, driver)
			n=n+25
		except:
			break

def getCash(company, driver):	
	driver.get("https://finance.yahoo.com/quote/" + company + "/key-statistics?p=" + company)
	x = driver.page_source
	x = x.split('"totalCash":')[1]
	x = x.split("}")[0]
	x = x + "}"
	print x
	y = ast.literal_eval(x)
	print y
	return y["raw"]

def getTotalCash(sector, limit, filename):
	driver = webdriver.Chrome("./chromedriver")
	driver.get("https://finance.yahoo.com/sector/" +sector)
	x = driver.page_source
	file=open(filename,'w')
	file.write('START')
	companies = listCompanies(x, driver)
	print companies
	n=25	
	while n<=limit:	
		try:			
			driver.get("https://finance.yahoo.com/screener/predefined/"+sector+"?offset="+str(n)+"&count=25")
			x = driver.page_source
			companies = companies + listCompanies(x, driver)
			n=n+25
		except:
			pass

	companiesCash = {}
	for member in companies:
		try:
			companiesCash[member] = getCash(member, driver)
		except:
			print 'Failed at ' + member

	for member in companiesCash:
		file.write('\n' + member + '\t' + str(companiesCash[member]))

def findGraph(company):
	driver = webdriver.Chrome("./chromedriver")
	driver.get("https://finance.yahoo.com/chart/" + company + "#eyJpbnRlcnZhbCI6ImRheSIsInBlcmlvZGljaXR5IjoxLCJ0aW1lVW5pdCI6bnVsbCwiY2FuZGxlV2lkdGgiOjgsInZvbHVtZVVuZGVybGF5IjpmYWxzZSwiYWRqIjp0cnVlLCJjcm9zc2hhaXIiOnRydWUsImNoYXJ0VHlwZSI6ImxpbmUiLCJleHRlbmRlZCI6ZmFsc2UsIm1hcmtldFNlc3Npb25zIjp7fSwiYWdncmVnYXRpb25UeXBlIjoib2hsYyIsImNoYXJ0U2NhbGUiOiJsaW5lYXIiLCJwYW5lbHMiOnsiY2hhcnQiOnsicGVyY2VudCI6MSwiZGlzcGxheSI6IkdVVCIsImNoYXJ0TmFtZSI6ImNoYXJ0IiwidG9wIjowfX0sInNldFNwYW4iOnt9LCJsaW5lV2lkdGgiOjIsInN0cmlwZWRCYWNrZ3JvdWQiOnRydWUsImV2ZW50cyI6dHJ1ZSwiY29sb3IiOiIjMDA4MWYyIiwic3ltYm9scyI6W3sic3ltYm9sIjoiR1VUIiwic3ltYm9sT2JqZWN0Ijp7InN5bWJvbCI6IkdVVCJ9LCJwZXJpb2RpY2l0eSI6MSwiaW50ZXJ2YWwiOiJkYXkiLCJ0aW1lVW5pdCI6bnVsbCwic2V0U3BhbiI6e319XX0%3D")
	x = driver.page_source
	print x
	elem = driver.find_element_by_id("fin-chartiq")
	print elem
	ac = ActionChains(driver)
	ac.move_to_element(elem).move_by_offset(5, 10).perform()
	time.sleep(10)	
	driver.save_screenshot("1.png")
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
	table.sort(key = lambda x:int(x.split('\t')[0]))
	return table
		
def writeTableWithCompanyNamesVersion2(filenames, filename2):
	file = open(filename2, 'w')
	text = combineFiles(filenames)
	table = generateTableWithCompanyNamesVersion2(text)
	for m in table:
		print m
		file.write(m)

if __name__ == "__main__":
	sectors = ["utilities", "healthcare", "services", "basic_materials", "conglomerates", "industrial_goods", "consumer_goods", "technology"]
	for sector in sectors:
		do(sector, 975, sector+'.txt')
	writeTableWithCompanyNamesVersion2(['financial.txt','technology.txt','industrial_goods.txt','services.txt','utilities.txt','basic_materials.txt','consumer_goods.txt','conglomerates.txt'],'combined.txt')


	

