import urllib2
import mechanize
from bs4 import BeautifulSoup
import cookielib
import time
import re
import requests
from requests import Request, Session
from tqdm import tqdm
from threading import Thread
import Queue
import argparse

def run(enter_url,enter_filename,enter_pw):
    print 'Welcome to firedrop file getter'
    print '--------------------------------'
    scrape_pages(enter_url,enter_filename,enter_pw)

def scrape_pages(enter_url,enter_filename,enter_pw):
    #setup our instance variables.
    cj = cookielib.CookieJar()
    br = mechanize.Browser()
    br.set_cookiejar(cj)
    #browser methods (we get input from user input)
    #note br.form is coupled to firedrop.com
    br.open(enter_url)
    br.select_form(nr=0)
    br.form['folderPassword'] = enter_pw
    br.submit()
    #read the inital 'link page' and copy the response (this is the page with all the download links).
    first_resp = br.response().read()
    soup = BeautifulSoup(first_resp, 'html.parser')
    #a quick little password check that checks the response page for the given filename text
    if enter_filename not in soup.text:
        print '---Sorry, Incorrect Password. Quiting...'
        raise SystemExit
    else:
        print '---Password Successful!' 
    mainpage_links = []
    mainpage_links_name = []
    for link in soup.find_all('a',href=True):
        if enter_filename in link.text:
            print 'Copying mainpage link...',link
            mainpage_links.append(link['href'])
            mainpage_links_name.append(link.text)
    print 'Copying mainpage links complete!'
    #then we open an individual link (which takes us to the download page of that file).
    #note: this is done once. Basically first we parse the main page for links, 
    #then we open every mainlink to get the actual file link, but we don't download yet.
    download_urls = []
    print 'Opening mainpage links and finding file download URLs...'
    for page in mainpage_links:
	    #here we need to parse the final dl page for the actual file url.
	    download_page = urllib2.urlopen(page)
	    new_soup = BeautifulSoup(download_page.read(), 'html.parser')
	    script = new_soup.find_all('script')
	    script_bit = ''
	    for item in script:
		    if 'Download File' in item.text:
			    script_bit = item.text
	    pattern = re.compile("(\w+)='(.*?)'")
	    fields = dict(re.findall(pattern, script_bit))
	    print 'Copying file download URL...',fields['href']
	    #append the actual download file url to a list.
	    download_urls.append(fields['href'])
    thread_queue(download_urls, mainpage_links_name)

def download(i,q,counter, file):
    while True:
        print '%s: Looking at next URL...' % i
        url = q.get()
        print '%s: Downloading:' % i, url
        #download
        file_name = file[counter]
        counter += 1
        #first HTTP request.
        res = requests.get(url,stream=False)
        #get header/cookie info.
        #decouple this later.
        pattern = re.compile("(\w+)")
        fields = re.findall(pattern, url)
        short_url = 'https://firedrop.com/' + fields[3]
        cookie = res.headers['Set-Cookie']
        #post second HTTP request with cookie stuff.
        #this is a custom request so that firedrop will serve the file.
        s = Session()
        req = Request('POST',url)
        prepped = s.prepare_request(req)
        prepped.headers['Host'] = 'firedrop.com'
        prepped.headers['Connection'] = 'Keep-Alive'
        prepped.headers['Accept-Encoding'] = 'gzip, deflate, sdch'
        prepped.headers['Accept'] = '*/*'
        prepped.headers['Upgrade-Insecure-Requests'] = '1'
        prepped.headers['DNT'] = '1'
        prepped.headers['Referer'] = short_url
        prepped.headers['Cookie'] = cookie + ';, jstree_open=%23-1;, jstree_load=;, jstree_select=%233530'
        #note this timer is vital (response.js will not serve file without the delay)
        print 'Preparing file download... (Takes 10sec)'
        time.sleep(10)
        #download - GET second HTTP response.
        file_resp = s.send(prepped, stream=True)
        #write file.
        #problem here for large files, this needs to be iter_content or else it won't DL.
        print '---Downloading file: ', file_name
        with open(file_name,'wb') as code:
            for data in tqdm(file_resp.iter_content(512)):
                code.write(data)
        q.task_done()

def thread_queue(download_urls, mainpage_links_name):
    #setup our queue.
    #multithread option.
    num_threads = 1
    enclosed_q = Queue.Queue()
    counter = 0

    for i in range(num_threads):
        dae = Thread(target=download, args=(i, enclosed_q, counter, mainpage_links_name))
        dae.setDaemon(True)
        dae.start()

    for url in download_urls:
        enclosed_q.put(url)

    enclosed_q.join()
    print '\n---------- DONE ----------'

if __name__ == "__main__":
    # Setup args.
    parser = argparse.ArgumentParser()
    parser.add_argument('url',help='The main firedrop folder URL')
    parser.add_argument('filename',help='Part of the actual filename(s) of files you want to download')
    parser.add_argument('password',help='The folder password')
    args = parser.parse_args()
    run(args.url,args.filename,args.password)
