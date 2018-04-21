import subprocess
from selenium import webdriver
import time
from selenium.webdriver.common.by import By
import dateutil.parser
import ast
import unicodedata
from selenium.webdriver.common.action_chains import ActionChains

ts = int(time.time())
print ts

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
# 	hrefs = x.split('href="')
# 	hrefs = [x.split('"')[0] for x in hrefs]
# 	hrefs = [x for x in hrefs if "/quote/" in x]
# 	for member in hrefs:
# 		member = member.split("quote/")[1].split("?")[0]
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

string='financial'
do(string, 975, string+'.txt')

# done: utilities, healthcare, services, basic_materials, conglomerates, industrial_goods, consumer_goods, technology

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


# getTotalCash('basic', 500, 'basicCash.txt')

def findGraph(company):
	driver = webdriver.Chrome("./chromedriver")
# 	driver.get("https://finance.yahoo.com/quote/"+company+"?p="+company)
	driver.get("https://finance.yahoo.com/chart/" + company + "#eyJpbnRlcnZhbCI6ImRheSIsInBlcmlvZGljaXR5IjoxLCJ0aW1lVW5pdCI6bnVsbCwiY2FuZGxlV2lkdGgiOjgsInZvbHVtZVVuZGVybGF5IjpmYWxzZSwiYWRqIjp0cnVlLCJjcm9zc2hhaXIiOnRydWUsImNoYXJ0VHlwZSI6ImxpbmUiLCJleHRlbmRlZCI6ZmFsc2UsIm1hcmtldFNlc3Npb25zIjp7fSwiYWdncmVnYXRpb25UeXBlIjoib2hsYyIsImNoYXJ0U2NhbGUiOiJsaW5lYXIiLCJwYW5lbHMiOnsiY2hhcnQiOnsicGVyY2VudCI6MSwiZGlzcGxheSI6IkdVVCIsImNoYXJ0TmFtZSI6ImNoYXJ0IiwidG9wIjowfX0sInNldFNwYW4iOnt9LCJsaW5lV2lkdGgiOjIsInN0cmlwZWRCYWNrZ3JvdWQiOnRydWUsImV2ZW50cyI6dHJ1ZSwiY29sb3IiOiIjMDA4MWYyIiwic3ltYm9scyI6W3sic3ltYm9sIjoiR1VUIiwic3ltYm9sT2JqZWN0Ijp7InN5bWJvbCI6IkdVVCJ9LCJwZXJpb2RpY2l0eSI6MSwiaW50ZXJ2YWwiOiJkYXkiLCJ0aW1lVW5pdCI6bnVsbCwic2V0U3BhbiI6e319XX0%3D")
	x = driver.page_source
# 	driver.findElements(By.xpath(
	print x
	elem = driver.find_element_by_id("fin-chartiq")
	print elem
	ac = ActionChains(driver)
	ac.move_to_element(elem).move_by_offset(5, 10).perform()
	time.sleep(10)
	
	driver.save_screenshot("1.png")
# 	ac.move_to_element(elem).move_by_offset(10, 10).perform()
# 	driver.save_screenshot("2.png")
# 	driver.close()
# findGraph("HSBC")



# def findHistoricalData(name, driver):
# 	x = returnPageSource(name, driver)
# 	x = unicodedata.normalize('NFKD', x).encode('ascii','ignore')
# 	x = x.split('<span data-reactid="')	
# 	x = [y.split('>')[1] for y in x]
# 	x = [y.split('<')[0] for y in x]
# 	x = x[x.index('Volume')+1:(x.index('*Close price adjusted for splits.'))]
# 	return x
# 
# months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


# def findAllOnPage(x, file, driver):
# 	hrefs = x.split('href="')
# 	hrefs = [x.split('"')[0] for x in hrefs]
# 	hrefs = [x for x in hrefs if "/quote/" in x]
# 	for member in hrefs:
# 		member = member.split("quote/")[1].split("?")[0]
# 		results = findHistoricalData(member,driver)
# 		file.write('\n'+member)
# 		for o in xrange(len(results)):
# 			member2 = results[o]
# 			member21 = ''
# 			try:
# 				member21=results[o+1]
# 			except:
# 				pass
# 			if not 'Dividend' in member2 and not 'Dividend' in member21:
# 				try:
# 					yourdate = dateutil.parser.parse(member2)
# 					if member2[0:3] in months:
# 						file.write('\n')	
# 				except:
# 					pass				
# 				file.write(member2+'\t')



# print x


# print hrefs
# findHistoricalData(sample, driver)

# driver.get("https://finance.yahoo.com/quote/V/history?p=V")


# sample="BLK"

# driver.find_element_by_link_text(sample).send_keys('\n')


# driver.get("http://www.facebook.com")
# time.sleep(5)
# subprocess.call("/Users/jeremycollins/test.command",shell=True)

# driver.get("https://finance.yahoo.com/quote/FB2A.DE/history?p=FB2A.DE")

# driver.find_element_by_link_text("Download Data").click()

# 	driver.find_element_by_link_text(name).send_keys('\n')
# 	print driver.page_source
# 	driver.find_element_by_link_text("Historical Data").click()
	

