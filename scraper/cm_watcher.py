import urllib,urllib2,re,time,datetime,MySQLdb
import smtplib
from email.mime.text import MIMEText
from array import *
def main():
	debug=0
	#open DB
	db = open_db_mysql()
	#Load the 'all auctions' page
	print 'Getting url..'
	req = urllib2.Request('http://www.cigarmonster.com/')
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	print 'compiling url...'
	link = link.replace('\r\n','').replace("'","").replace('(','').replace(')','')
	print link
	if (link.find('monsteritemdes') > 0):
		#match=re.compile('checkItem(.+?);(.+?)<h2 class="monsteritemdes">(.+?)</h2>(.+?)<span class="monsteritemprs size2a">(.+?)</span>').findall(link)
		match=re.compile('checkItem(.+?);(.+?)<h2 class="monsteritemdes">(.+?)</h2>(.+?)<div class="detail-r">(.+?)</div>').findall(link)
	else:
		match=re.compile('<a class="mashupItem" name="(.+?)"(.+?)<div class="mashupitemdes">(.+?)</div>(.+?)<span class="mashupitemprice">(.+?)<').findall(link)
	
	# This is where I should be reading the DB. It should loop and call sendemail with recipent and auctions id'ed. 
	# Table should have one entry per address, with a comma delimited field of strings to search for
	curList = db.cursor()
	#curInsert = db.cursor()
	curList.execute("Select * from watcher_list where watcher_verified='1' and watcher_cm='1'")
	rowsList = curList.fetchall()
	curList.execute("Select * from watcher_reported")
	rowsRep = curList.fetchall()
	allRep = ''
	for rowRep in rowsRep:
		allRep = allRep + ',' + rowRep[2]
	for rowList in rowsList:
		recipient = rowList[1]
		tmpSearch = rowList[2]
		tmpUser = rowList[3]
		if tmpSearch:
			searchstring = tmpSearch.split(',')
		else:
			tmpSearch = ''
			searchstring = tmpSearch.split(',')
		
		lotCount = 0
		print 'Looping results...(' + recipient + ')'
		results = []
		for aulotid,fill0,auitem,fill1,auprice in match:
		# search the title only, nothing fancy.
			#auitem = auitem.strip()
			for x in searchstring:
				if (x.lower().strip(' ') in auitem.lower()) and (len(x)>0):
					print 'auitem=' + auitem.strip()
					if aulotid not in allRep:
						# found string, add to results
						results.append([auitem,auprice])
						# add to db
						#print 'recipient: ' + recipient
						#print 'aulotid: ' + aulotid
						if (debug==0):
							InsertResult = curList.execute("INSERT INTO watcher_reported(reported_recipient,reported_lotid) values('" + recipient + "','" + aulotid + "')")
						else:
							print "Debug: Didnt add item:" + aulotid
							InsertResult=2
						lotCount = lotCount + 1
						if InsertResult == 1:
							db.commit()
						else:
							print 'error adding item: ' + aulotid 
			
		# Add the search string and URL to the message text
		msgtxt = """\
		<html>
		<body>
		CigarMonster results for user: """
		msgtxt = msgtxt + tmpUser
		msgtxt = msgtxt + """\
		<table width="100%" align="left" border=1>
		<tr align=left><th>Item</th><th>Price</th></tr>
		"""
		for x in results:
			msgtxt = msgtxt + "<tr align=left><td>" + x[0] + "</td><td>" + x[1] + "</td></tr>"
			print 'results=' + x[0]
		msgtxt = msgtxt + """\
		</table>
		<br><br>
		"""
		msgtxt = msgtxt + "<a href=http://sloppymcnubble.com/cbid/cbid_watcher.php>Adjust Your Watches</a>"
		msgtxt = msgtxt + """\
		</body>
		</html>
		"""
		if lotCount>0:
			sendemail(recipient,msgtxt)
	f = open('c:\users\matt\documents\cbid\cbid_watcher_log.txt','a')
	f.write(str(datetime.datetime.now()) + ' : Run complete\n')
	f.close()
	if ((debug == 1)):
		sendemail('matt.**domain**@gmail.com','watcher run complete')

def sendemail(to,text):
	debug = 0
	if ((debug == 0) or (to == 'sloppy@sloppymcnubble.com')):
		print 'Sending email to: ' + to
		content = text
		me = 'cbid_watcher@sloppymcnubble.com'
		you = to
		subject = 'CM Watcher Results'
		
		msg = MIMEText(content,'html')
		msg['Subject'] = subject
		msg['From'] = me
		msg['To'] = you
		s = smtplib.SMTP('mail.sloppymcnubble.com')
		s.login('cbid_watcher+sloppymcnubble.com','******')
		print msg.as_string()
		s.sendmail(me, you, msg.as_string())
		s.quit()
	else:
		print 'Debug: Bypassed email: ' + to

def open_db_mysql():
    print 'Opening DB connection...'
    db = MySQLdb.connect(host="**domain**.org", user="**domain**org_cb", passwd="*******",db="**domain**org_cb")
    return db

if __name__ == '__main__':
    main()
