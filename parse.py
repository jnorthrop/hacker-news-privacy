import urllib2
import json
import re

url ='http://api.ihackernews.com/ask/'
next = ''
post_count = 0
post_ids = []
urls = []

# Loop until we have 100 posts or at the end of the available posts to search
while post_count < 100:
	try: 
		response = urllib2.urlopen(url + next)
	
		content = response.read()
		data = json.loads(content)
		next = data['nextId']
		if not next:
			break;
		
		print "NEXT: " + next
		
		for x in data:
			if x=='items':
				for items in data[x]:
					if re.match('Show HN', items['title']):
						post_ids.append(items['id'])
						++post_count
						print "ITEM: " + str(items['id'])
				
	except urllib2.HTTPError, e:
		print e.code
	
print "FOUND " + len(post_ids) + " posts"
print "... now grabbing posts"

# Now look through the posts and pull the URL from the post
url ='http://api.ihackernews.com/post/'

# from http://daringfireball.net/2010/07/improved_regex_for_matching_urls
URL_IN_TEXT = re.compile(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))')

def retreive_url(post_ids):
	print "ID: " + post_ids[0]
	try: 
		response = urllib2.urlopen(url + post_ids[0])
	
		content = response.read()
		data = json.loads(content)
		post_ids.pop(0)
		post_text = data['text']
		urls = URL_IN_TEXT.findall(post_text)
		print "TEXT: " + post_text
		for url_found in urls:
			print "URL: " + url_found[0]
			urls.append(url_found[0])
				
	except urllib2.HTTPError, e:
		print e.code 
		
	return post_ids	

# run recursively to retry posts not returned due to API error
while len(post_ids) > 0:
	post_ids = retreive_url(post_ids)
		
# Finally get the URL and check if it has "privacy" on the page
f = open('results.csv', 'w')

print "SEARCHING " + len(urls) + " URLS"

for url in urls:
	try: 
		response = urllib2.urlopen(url)
		content = response.read()
		if re.search("privacy", content):
			print "FOUND: " + url
			f.write("'found', '" + url + "'\n")
		else:
			print "NOT FOUND: " + url
			f.write("'not found', '" + url + "'\n")
				
	except urllib2.HTTPError, e:
		print e.code 
	
f.close()