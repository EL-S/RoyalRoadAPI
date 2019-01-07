from bs4 import BeautifulSoup #for processing html for info
from tornado import ioloop, httpclient #for asynchronous ioloops for downloading chapters
from datetime import datetime #for timestamping epubs
import re #for regex operations to clean up information
import os #to delete and create and modify files and folders
import uuid #to give each epub a unique identifier
from shutil import rmtree #to create archives and delete files
import zipfile #to create archives
import base64 #to encode and decode base64 data (like images)

i = 0 #to track the ioloop
chapters_downloaded = []
chapters_html = {} #the dictionary containing all the downloaded chapter ids with their respective html
fiction_html = "" #the html of the entire fiction in one variable
directory = "Error/" #to have a fallback directory in case of errors
epub_index_start = 1 #to ensure the epub index starts at 1
file_name_chapter_range = "" #to have a default empty chapter range expression

def get_fiction(fiction_id,directory="Fictions/",start_chapter="first",end_chapter="last"): #download a fiction by id or search
    global epub_index_start,file_name_chapter_range,final_location,plural #access global variables
    try:
        int(fiction_id) #check for fiction id
    except:
        search_term = fiction_id #not an id so declare a search term
        fiction_id = search_fiction(search_term) #perform a search and return the most likely fiction id
    if fiction_id:
        fiction_object = get_fiction_object(fiction_id) #collect a fiction object (fiction page)
        get_fiction_info(fiction_object) #collect info from the fiction object
        start_chapter,end_chapter,epub_index_start = get_chapter_range(start_chapter,end_chapter) #clarify and validate the chapter range
        chapter_links_approved = chapter_links[start_chapter:end_chapter] #remove excess chapters outside the range from the queue
        if chapter_links_approved != []: #if any chapter links remain
            downloading_chapter_amount = len(chapter_links_approved) #count them
            chapter_amount = len(chapter_links) #count how many there would have been in total
            start_chapter,end_chapter,epub_index_start,chapter_amount,downloading_chapter_amount,file_name_chapter_range,plural = chapter_range_string_expressions(start_chapter,end_chapter,epub_index_start,chapter_amount,downloading_chapter_amount) #generate a string that represents the chapter range specified
            if file_name_chapter_range != "": #if the string is not empty
                downloading_chapter_str = "chapter"+plural+file_name_chapter_range+", "+str(downloading_chapter_amount)+"/"+str(chapter_amount) #add it to the downloading str
            else:
                downloading_chapter_str = "chapter"+plural+" "+"1-" + str(chapter_amount)+", "+str(downloading_chapter_amount)+"/"+str(chapter_amount) #if it's empty, specify that you are downloading everything
            print("Downloading ({}".format(downloading_chapter_str) + ") ID {}: ".format(fiction_id) + title + " - " + author + file_name_chapter_range + ".epub") #print downloading alert to the console
            get_chapters(chapter_links_approved,directory) #perform download of chapters in the range
            return final_location #return the final location it was saved at
        else: #there are no chapters left to download
            if chapter_links == []: #there was none to begin with
                print("Fiction {} contains no chapters.".format(fiction_id)) #alert the user that the fiction has no chapters
            else: #there was some to begin with
                print("Fiction {} contains no chapters in the given range".format(fiction_id),str(epub_index_start)+"-"+str(end_chapter)+".") #alert the user that the fiction has no chapters in that range
    else:
        print("'{}' does not exist.".format(search_term))
def get_fictions(fiction_id_start=1,fiction_id_end=None,directory="Fictions/"): #downloads multiple fictions, defaulting to download all
    try: #confirm the range is valid
        if fiction_id_end == None:
            fiction_id_end = find_latest_fiction_id() #returns the most recent fictions id to download all fictions
        fiction_id_start = int(fiction_id_start) #to confirm int validity
        fiction_id_end = int(fiction_id_end) #to confirm int validity
        total = (fiction_id_end-fiction_id_start)+1 #the amount of fictions to download
        if (fiction_id_end < fiction_id_start): #you can't download backwards
            raise Exception('Invalid Range.') #raise a custom error about an invalid range
        else:
            print("Invalid Range.") #the range given is out of order (backwards) or invalid(mistyped)
    except:
        print("Please use valid numbers!") #the numbers are actually letters, words, symboles or floats, etc.
    else:
        for i in range(fiction_id_start,fiction_id_end+1): #begin downloading queue
            try: #attempt download
                get_fiction(i,directory) #download fiction
                print("Progress:",str(round((((i-(fiction_id_start))+1)/total)*100,2))+"%") #print progress
                print("Remaining:",str((total-1)-(i-(fiction_id_start)))) #print remaining
            except: #the download failed for some reason, often it doesn't exist
                print("Fiction {} Not Available.".format(i)) #the fiction download failed
                print("Progress:",str(round((((i-(fiction_id_start))+1)/total)*100,2))+"%") #print progress
                print("Remaining:",str((total-1)-(i-(fiction_id_start)))) #print remaining
    finally:
        print("Program Complete.") #the multidownload has failed or completed

def find_latest_fiction_id(): #find the latest fictiond id
    url = "https://www.royalroad.com/fictions/new-releases" #specify a url
    soup = request_soup(url) #request the soup
    latest_fiction_id = int(soup.find("a",attrs={"class":"font-red-sunglo bold"}).get("href").split("/")[2]) #search the html for the latest fiction id
    return latest_fiction_id #return the latest fiction id

def get_chapter_range(start_chapter,end_chapter):
    try:
        end_chapter = int(end_chapter) #ensure it is an int
        if end_chapter < 1: #if less than 1
            end_chapter = 1 #equate to 1
    except:
        end_chapter = chapter_amount #if not an int, end range is up to the last chapter
    try:
        start_chapter = int(start_chapter) #ensure it is an int
        if start_chapter > 0: #if greater than 0
            epub_index_start = start_chapter #declare the index start num as the start_chapter
            start_chapter -= 1 #minus one from the start_chapter as arrays start at 0
        else:
            raise Exception('Negative Number.') #raise a custom error about a negative number
    except:
        start_chapter,epub_index_start = 0,1 #declare as default values if an error occurs
    return start_chapter,end_chapter,epub_index_start #return values to continue download

def chapter_range_string_expressions(start_chapter,end_chapter,epub_index_start,chapter_amount,downloading_chapter_amount):
    if downloading_chapter_amount > 1: #more than one, make prints pretty by recognising plurals
        plural = "s" #add an s to the end
    else: #it's only one 
        plural = "" #so no s is needed
    if end_chapter > chapter_amount: #make sure the chapter range is not too large
        end_chapter = chapter_amount #set to max
    if start_chapter > chapter_amount: #make sure the chapter range is not too large
        start_chapter = chapter_amount #set to max
    if downloading_chapter_amount != chapter_amount: #if the amount isn't the entire fiction
        if downloading_chapter_amount != 1: #if the chapter range is more than one
            file_name_chapter_range = " "+str(epub_index_start)+"-"+str(end_chapter) #name the file with the range
        else: #if the chapter range is only 1
            file_name_chapter_range = " "+str(epub_index_start) #name the file with the chapter
    else:
        file_name_chapter_range = "" #name the fiction normally without a range
    return start_chapter,end_chapter,epub_index_start,chapter_amount,downloading_chapter_amount,file_name_chapter_range,plural #return values to continue download

def search_fiction(search_term): #search royalroad for a fiction using a given string
    search_term = search_term.replace(" ","+") #replace spaces with plus signs
    url = "https://www.royalroad.com/fictions/search?name="+str(search_term) #construct the url
    print(url) #print the search url for debug or console purposes
    soup = request_soup(url) #request the soup
    try:
        fiction_id = soup.find("div", attrs={"class":"col-sm-8 col-xs-10 search-content"}).find("input").get("id").split("-")[1] #attempt to gather the first fiction id
    except: #there was no fiction id or the html is incorrect
        return None #return none
    return fiction_id #return the fiction id

def get_fiction_location(fiction_id,directory="Fictions/",start_chapter="first",end_chapter="last"): #without downloading the fiction, determine where it would be stored exactly
    try:
        int(fiction_id) #check if fiction_id is a fiction id
    except: #it isn't
        search_term = fiction_id #declare search_term
        fiction_id = search_fiction(search_term) #perform a search and return the most likely fiction_id
    fiction_object = get_fiction_object(fiction_id) #collect the fiction page html
    get_fiction_info(fiction_object) #collect the data from the fiction page and store it in global variables
    start_chapter,end_chapter,epub_index_start = get_chapter_range(start_chapter,end_chapter) #validate and return a chapter range
    chapter_links_approved = chapter_links[start_chapter:end_chapter] #trim off excess chapters outside the range from the queue
    downloading_chapter_amount = len(chapter_links_approved) #get the amount of chapters being downloaded
    chapter_amount = len(chapter_links) #get the total amount of chapters
    if chapter_links_approved != []: #if there are chapters queued
        start_chapter,end_chapter,epub_index_start,chapter_amount,downloading_chapter_amount,file_name_chapter_range,plural = chapter_range_string_expressions(start_chapter,end_chapter,epub_index_start,chapter_amount,downloading_chapter_amount) #update all the values
    else:
        file_name_chapter_range = "" #set the variable as empty
    try:
        final_location = determine_file_location(title,directory,author,file_name_chapter_range) #finally collate all the information into a final location
    except:
        final_location = None #it failed so equate to none
    return final_location #return the final location

def determine_file_location(title,directory,author,file_name_chapter_range):
    title = re.sub(r'[\\/*?:"<>|]',"",re.sub(r'[<>]',"",title)).strip() #prevent breaking the xhtml because of html characters
    try:
        if author[-1] == "?": #if the questionmark is the last character
            author = author.replace("?","qstnmrk") #prevent an empty name when the ? are removed if they are the last character
    except:
        author = "Unknown" #the name is probably empty
    author = re.sub(r'[\\/*?:"<>|]',"",author).strip() #remove invalid characters
    try:
        if author[-1] == ".": #if the period is the last character
            author = author.replace(".","dot").strip() #replace all periods if they are the last character to prevent extension issues
    except:
        author = "Unknown" #the name is probably empty
    final_location = directory + title + " - " + author + file_name_chapter_range + ".epub" #collact all previous information
    return final_location #return the final location

def get_fiction_object(fiction_id):
    global url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount
    url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount = [None for i in range(10)] #reset all the global variables
    url = "https://www.royalroad.com/fiction/"+str(fiction_id) #construct the url
    soup = request_soup(url) #request the soup
    check_active = check_active_fiction(soup,fiction_id) #check if the fiction is not removed
    if check_active: #if it is active
        return soup #return the info
    else:
        return None #else don't return info

def request_soup(url):
    try:
        http_client = httpclient.HTTPClient() #initialise the url request
        html = http_client.fetch(url).body.decode('utf-8') #decode the html response
        soup = BeautifulSoup(html, "lxml") #parse the html
        return soup #return the soup object
    except httpclient.HTTPError as e: #if the http request fails
        if e.code != 404: #and it is a 404
            request_soup(url) #retry

def get_fiction_info(fiction_obj): #get fiction info and return and set global variables
    global url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount #access global variables
    if fiction_obj: #if the fiction_obj is not empty
        fiction_id = get_fiction_id(fiction_obj) #get the fiction id
        url = "https://www.royalroad.com/fiction/"+str(fiction_id) #get the url
        title = get_fiction_title(fiction_obj) #get the title
        cover_image = get_fiction_cover_image(fiction_obj) #get the cover_image address
        author = get_fiction_author(fiction_obj) #get the author
        description = get_fiction_description(fiction_obj) #get the description
        genres = get_fiction_genres(fiction_obj) #get the genres
        ratings = get_fiction_rating(fiction_obj) #get the ratings
        stats = get_fiction_statistics(fiction_obj) #get the stats
        chapter_links = get_chapter_links(fiction_obj) #get the chapter_links
        chapter_amount = len(chapter_links) #get the chapter amount
        return url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount #return all the info

def get_fiction_id(soup): #get the fiction
    fiction_id = soup.find("input", attrs={"name":"id"}).get("value") #collect the fiction id
    return fiction_id #return the fiction id

def check_active_fiction(soup,fiction_id): #get the fiction status
    not_active = soup.find('div', attrs={'class': 'number font-red-sunglo'}) #if the fiction is not active it returns a value
    if not not_active: #the fiction is active
        return True #return active
    print("No Fiction with ID "+str(fiction_id)) #alert the console with the fiction id

def get_fiction_title(soup): #get the title of the fiction
    title = soup.find('h1', attrs={'property': 'name'}).text.strip() #collect title and strip whitespace
    return title #return title

def get_fiction_cover_image(soup): #get the cover image source
    cover_image = soup.find('img', attrs={'property': 'image'}).get('src') #get the source
    if cover_image.lower() == "/content/images/rr-placeholder.jpg" or cover_image == "undefined": #if the source refers to the default internal source or if the source is a string containing undefined
        cover_image = "http://www.royalroadl.com/Content/Images/rr-placeholder.jpg" #convert it to an external source
    return cover_image #return the image source

def get_fiction_author(soup): #get the author
    author = soup.find('span', attrs={'property': 'name'}).text.strip() #collect and strip the author name
    if author == "": #if the author is empty
        author = "NONE" #change their name to none
    return author #return author

def get_fiction_description(soup): #get the description
    description = soup.find('div', attrs={'property': 'description'}).text.strip() #collect the description and strip whitespace
    if description == "": #if the description is empty
        description = "No Description" #change description to a message stating there is no description
    return description #return the description

def get_fiction_genres(soup): #get fiction genres
    genres = [] #declare the genres variable
    genre_tags_part1 = soup.findAll('span', attrs={'class': 'label label-default label-sm bg-blue-hoki'}) #get the main genre tags
    genre_tags_part2 = soup.findAll('span', attrs={'property': 'genre'}) #get the secondary genre tags
    for tag in genre_tags_part1: #for genre in main genres
        genres.append(tag.text.strip()) #collect the genre
    for tag in genre_tags_part2: #for genre in secondary genres
        genres.append(tag.text.strip()) #collect the genre
    return genres #return the genres

def get_fiction_rating(soup): #get the fiction ratings
    overall_rating = soup.find('meta', attrs={'property': 'ratingValue'}).get("content") #get overall rating
    best_rating = soup.find('meta', attrs={'property': 'bestRating'}).get("content") #get best rating
    rating_count = soup.find('meta', attrs={'property': 'ratingCount'}).get("content") #get rating count
    style_rating = soup.find('span', attrs={'data-original-title': 'Style Score'}).get("data-content") #get style rating
    story_rating = soup.find('span', attrs={'data-original-title': 'Story Score'}).get("data-content") #get story rating
    character_rating = soup.find('span', attrs={'data-original-title': 'Character Score'}).get("data-content") #get character rating
    grammar_rating = soup.find('span', attrs={'data-original-title': 'Grammar Score'}).get("data-content") #get grammar rating
    rating = [overall_rating,best_rating,rating_count,style_rating,story_rating,character_rating,grammar_rating] #collate all the ratings
    return rating #return ratings

def get_fiction_statistics(soup): #get fiction statistics
    stats = [stat.text.strip() for stat in soup.findAll('li', attrs={'class': 'bold uppercase font-red-sunglo'})][:6] #collate stats like total_views,average_views,followers,favorites,rating_amount,pages
    return stats #return stats

def get_chapter_links(soup): #get chapter links
    chapter_links = [tag.get("data-url") for tag in soup.findAll('tr', attrs={'style': 'cursor: pointer'})] #collect the url tags and then add the url to the chapter_links list
    return chapter_links #return the chapter links

def get_chapter_amount(soup): #get chapter amount
    chapter_amount = len(get_chapter_links(soup)) #get chapter links and then find the len of the list
    return chapter_amount #return chapter amount

def get_chapters(chapter_links,directory_loc="Fictions/"): #create a loop object with the chapter links, then download them and finally save them to the hdd
    global chapters_downloaded,chapters_html,fiction_html,directory,http_client #get global variables
    globals()['directory'] = directory_loc #Sets the global variable directory to the variable directory_loc, might not be necessary now
    chapters_downloaded = [] #reset the downloaded chapters
    chapters_html = {} #reset the chapter list and html
    fiction_html = "" #reset the fiction html
    http_client = httpclient.AsyncHTTPClient(force_instance=True,defaults=dict(user_agent="Mozilla/5.0"),max_clients=20) #initiate the async http loop
    for chapter_id in chapter_links: #for each chapter in chapter links
        global i #access the global variable i
        i += 1 #add one to it
        url = "https://www.royalroad.com/"+str(chapter_id) #construct the url
        http_client.fetch(url.strip(),handle_chapter_response, method='GET',connect_timeout=10000,request_timeout=10000) #add the url to the event loop
    if chapter_links != []: #if there are links in the loop
        ioloop.IOLoop.instance().start() #start the download
        save_to_hdd(fiction_html,chapters_html,chapters_downloaded,directory) #when the download is finished, save the files

def get_chapter_content(html): #get the chapter html from the chapter page
    soup = BeautifulSoup(html, "lxml") #create a soup object
    chapter_title = soup.find('h1', attrs={'style': 'margin-top: 10px','class': 'font-white'}).text.strip() #extract the chapter title and strip it
    content_html = str(soup.find('div', attrs={'class': 'chapter-inner chapter-content'})) #extract the chapter html and convert it to a str to prevent type errors
    return content_html,chapter_title #return the chapter html and chapter title


def save_to_hdd(fiction_html,chapters_html,chapters_downloaded,directory="Fictions/"): #convert the chapter html and fiction info to an epub and save it locally
    global url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount,epub_index_start,file_name_chapter_range,plural #access global variable info
    time = datetime.now().strftime("%Y-%m-%d %H:%M") #create a timestamp for the epub info
    genre_html = "" #declare genre_html
    for genre in genres: #for each genre
        if genre_html == "": #check if the string is empty
            genre_html += genre #if so, add the genre to it
        else: #if not empty
            genre_html += " | " + genre #add a fancy separator and the genre to the end
    if file_name_chapter_range != "": #if the chapter range is not default
        chapter_range_html = "<p><h2>Chapter" + plural + " " + file_name_chapter_range + "</h2></p>" #specify the chapters contained in the epub
    else: #else
        chapter_range_html = "<p><h2>Chapter" + plural + " " + "1-" + str(chapter_amount) + "</h2></p>" #add it to the start of the epub info
    stats_html = "</p><p><b>Total Views:</b> " + stats[0] + "<b> | Average Views:</b> " + stats[1] + "<b> | Followers:</b> " + stats[2] + "<b> | Favorites:</b> " + stats[3] + "<b> | Pages:</b> " + stats[5] #format the stats into html
    statistics = "<b>Chapters:</b> " + str(chapter_amount) + "<b> | Overall Score:</b> " + ratings[0] + "<b> | Best Score:</b> " + ratings[1] + "<b> | Ratings:</b> " + ratings[2] + "</p><p><b>Style Score:</b> " + ratings[3] + "<b> | Story Score:</b> " + ratings[4] + "<b> | Character Score:</b> " + ratings[5] + "<b> | Grammar Score:</b> " + ratings[6] + stats_html + "</p>" #format for info into html
    data = "<center><img src='../cover.jpg'></img><p><b><h1> \"<a href='" + url + "'>" + str(title) + "</a>\" by \"" + str(author) + "\"</h1></b></p>" + chapter_range_html + "<p><b>" + genre_html + "</b></p><p>" + statistics + "<p><h2>Last updated: " + time + "</h2></p></center><p><h3>Description:</h3> " + str(description) + "</p>"#add the last few pieces of info to the html
    title_clean = re.sub(r'[\\/*?:"<>|]',"",title) #clean the title for windows and other systems
    try:
        if author[-1] == "?": #check for a question mark as the last character
            author = author.replace("?","qstnmrk") #if so, replace it with 'qstnmrk' to prevent empty author names
    except:
        author = "Unknown" #the name is likely empty and is replaced with 'Unknown'
    author_clean = re.sub(r'[\\/*?:"<>|]',"",author) #clean the author
    try:
        if author_clean[-1] == ".": #check the clean author for a dot
            author_clean = author_clean.replace(".","dot") #if so, replace it as it might cause extension problems, or windows might remove it because of having 2 or more periods in a row
    except:
        author_clean = "Unknown" #the author_clean is likely empty so replace it with 'Unknown'
    print("Saving EPUB: " + directory + title_clean + " - " + author_clean + file_name_chapter_range + ".epub") #output the final location to the console
    name = title_clean + " - " + author_clean + file_name_chapter_range #create the name variable using the clean title and author with the chapter range
    folder_name = name + "/" #create the folder name variable
    os.makedirs(directory+folder_name+"OEBPS/", exist_ok=True) #make the OEBPS folder for where the epub archive with the chapter html will be located before deletion
    os.makedirs(directory+folder_name+"META-INF/", exist_ok=True) #make the META-INF folder for where the epub archive meta-inf will be located before deletion
    os.makedirs(directory+folder_name+"OEBPS/style/", exist_ok=True) #make the style folder for where the epub css tables will come from for the formatting before deletion of their root folder, could combine with first os.makedir
##    file_name = name + ".html" #create the file name for the html file
##    full_path = directory + folder_name + file_name #create the full path for the html file
##    with open(full_path, "w", encoding="utf-8") as file_webnovel: #create the html file
##        file_webnovel.write(data) #write the fiction data to it
##    print("Saved:",full_path) #output the save location to the console
    uuid_str = str(uuid.uuid4()) #create the uuid for the epub
    
    with open(directory + folder_name + "toc.ncx", "w", encoding="utf-8") as file_toc: #create and write to the table of contents for the epub with the uuid and title
        file_toc.write("""<?xml version='1.0' encoding='UTF-8'?>
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
    <meta name="dtb:uid" content=\"""" + uuid_str + """\"/>
    <meta name="dtb:generator" content="DumbEpub"/>
    <meta name="dtb:depth" content="2"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>"""+str(title_clean)+"""</text>
  </docTitle>
  <navMap>""")

    with open(directory + folder_name + "OEBPS/style/style.css", "w", encoding="utf-8") as file_css: #write the css code for the tables found on royalroad
        file_css.write(""".chapter-content table,.forum .post-content table {
background:#004b7a;
width:90%;
border:none;
box-shadow:1px 1px 1px rgba(0,0,0,.75);
border-collapse:separate;
border-spacing:2px;
margin:10px auto;
}

.chapter-content table td,.forum .post-content table td {
color:#ccc;
border:1px solid hsla(0,0%,100%,.25)!important;
background:rgba(0,0,0,.1);
margin:3px;
padding:5px;
}""")
    
    with open(directory + folder_name + "META-INF/container.xml", "w", encoding="utf-8") as file_container: #create and write to the file container for the epub with info about the content.opf
        file_container.write("""<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
	<rootfiles>
		<rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
	</rootfiles>
</container>""")
        
    with open(directory + folder_name + "content.opf", "w", encoding="utf-8") as file_content: #create and write to the content file for the epub with info about the uuid, author and title
        file_content.write("""<?xml version='1.0' encoding='UTF-8'?>
<opf:package version="2.0" unique-identifier="BookId" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <opf:metadata>
    <dc:identifier id="BookId" opf:scheme="UUID">""" + uuid_str + """</dc:identifier>
    <dc:title>""" + title_clean + """</dc:title>
    <dc:creator opf:role="aut">""" + author_clean + """</dc:creator>
    <dc:language>en</dc:language>
    <dc:language>eng</dc:language>
    <opf:meta name="generator" content="DumbEpub"/>
    <opf:meta name="cover" content="cover"/>
  </opf:metadata>
  <opf:manifest>
    <opf:item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    <opf:item id="cover" href="cover.jpg" media-type="image/jpeg"/>
    <opf:item id="css-style" href="OEBPS/style/style.css" media-type="text/css"/>
    <opf:item id="cover-page" href="titlepage.xhtml" media-type="application/xhtml+xml"/>
    <opf:item id="prov_idx_1" href="OEBPS/info.xhtml" media-type="application/xhtml+xml"/>""")
        
    for i in range(epub_index_start,epub_index_start+len(chapters_downloaded)): #for each chapter number
        with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content: #append a line container the link to the file internally and its index num
            file_content.write("""
    <opf:item id="prov_idx_""" + str(i+1) + """\" href="OEBPS/chapter_""" + str(i) + """.xhtml" media-type="application/xhtml+xml"/>""")
            
    with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content: #append the end tags to the content file
        file_content.write("""
  </opf:manifest>
  <opf:spine toc="ncx">""")
    
    with open(directory + folder_name + "toc.ncx", "a", encoding="utf-8") as file_toc: #append the info page to the table of contents
            file_toc.write("""
    <navPoint class="chapter" id="navPoint-""" + str(0) + """\" playOrder=\"""" + str(1) + """\">
      <navLabel>
        <text>Information</text>
      </navLabel>
      <content src="OEBPS/info.xhtml"/>
    </navPoint>""")
            
    full_path = directory + folder_name + "OEBPS/info.xhtml" #declare the full path to the info page html
    
    with open(full_path, "w", encoding="utf-8") as file_info: #write to the info page xhtml file with all the info data html
        file_info.write("""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
				<head>
					<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
					<title>Information</title>
				</head>
				<body>
					"""+data+"""</body>
			</html>""")
        
    with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content: #append the itemref opening tag to the content file
        file_content.write("""
    <opf:itemref idref="prov_idx_1\"/>""")
        
    chp = epub_index_start - 1 #declare the starting chapter number
    for chp_id in chapters_downloaded: #for each chapter id that was downloaded
        chp += 1 #add one to the chp number
        chapter_title = "Chapter " + str(chp) + ": " + chapters_html[chp_id][1] #and use it to name the chapter title with the original chapter title
        chapter_html = "<?xml version='1.0' encoding='utf-8'?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n\t\t\t\t<head>\n\t\t\t\t\t<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/>\n\t\t\t\t\t<title>Chapter " + str(chp) + ": " + chapters_html[chp_id][1] + "</title>\n\t\t\t\t\t<link href=\"style/style.css\" rel=\"stylesheet\" type=\"text/css\"/>\n\t\t\t\t</head>\n\t\t\t\t<body>\n\t\t\t\t\t<h1>Chapter " + str(chp) + ": " + chapters_html[chp_id][1] + "</h1>\n\t\t\t\t\t" + chapters_html[chp_id][0] + "\n\t\t\t\t</body>\n\t\t\t</html>" #create the internal epub chapter html
        chapter_file_name = "chapter_"+str(chp)+".xhtml" #name the chapter file appropriately
        full_path = directory + folder_name + "OEBPS/" + chapter_file_name #declare the full path
        
        with open(full_path, "w", encoding="utf-8") as file_chapter: #create and open the chapter xhtml and write the the html to it
            file_chapter.write(chapter_html.replace("&","&#38;"))
            
        with open(directory + folder_name + "toc.ncx", "a", encoding="utf-8") as file_toc: #append the chapter reference to the table of content, while cleaning up the title
            file_toc.write("""
    <navPoint class="chapter" id="navPoint-""" + str(chp) + """\" playOrder=\"""" + str(chp+1) + """\">
      <navLabel>
        <text>""" + chapter_title.replace("&","&#38;") + """</text>
      </navLabel>
      <content src="OEBPS/chapter_""" + str(chp) + """.xhtml"/>
    </navPoint>""")
            
        with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content: #append the internal chapter reference to the content.opf file
            file_content.write("""
    <opf:itemref idref="prov_idx_""" + str(chp+1) + """\"/>""")
            
    with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content: #append the cover titlepage to the content.opf file
            file_content.write("""
  </opf:spine>
  <opf:guide>
    <opf:reference href="titlepage.xhtml" title="Cover" type="cover"/>
  </opf:guide>
</opf:package>""")
            
    with open(directory + folder_name + "toc.ncx", "a", encoding="utf-8") as file_toc: #append the closing tags to the table of contents file
        file_toc.write("""
  </navMap>
</ncx>""")
    with open(directory + folder_name + "titlepage.xhtml", "w", encoding="utf-8") as titlepage: #create and open the title page and write the cover image internal address to it, for pretty display in epub reading software
        titlepage.write("""<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
        <meta name="calibre:cover" content="true" />
        <title>Cover</title>
        <style type="text/css" title="override_css">
            @page {padding: 0pt; margin:0pt}
            body { text-align: center; padding:0pt; margin: 0pt; }
        </style>
    </head>
    <body>
        <div>
            <svg version="1.1" xmlns="http://www.w3.org/2000/svg"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                width="100%" height="100%" viewBox="0 0 600 800"
                preserveAspectRatio="none">
                <image width="600" height="800" xlink:href="cover.jpg"/>
            </svg>
        </div>
    </body>
</html>""")
    obtain_and_save_image(directory,folder_name,cover_image) #either decode the base64 image or download the image from the external image address and save it
    output_location = directory #declare the output location
    folder_location = directory + folder_name #declare the folder location
    compress_and_convert_to_epub(directory,folder_location,output_location) #compress and covert the epub from the local archive that was created and then remove the archive and folder

def obtain_and_save_image(directory,folder_name,cover_image): #decode the base64 image or download the image and then save it
    if (cover_image.split(",")[0] != "data:image/jpeg;base64") and (cover_image.split(",")[0] != "data:image/gif;base64") and (cover_image.split(",")[0] != "data:image/png;base64"): #if the image is not base64 encoded
        image_data = download_image_data(cover_image) #download the image
        if image_data == None: #if the image is empty
            image_data = download_image_data("http://www.royalroadl.com/Content/Images/rr-placeholder.jpg") #download the default image instead
    else: #else decode the image if it is base64 encoded
        try:
            image_data = base64.b64decode(image_data) #decode the image
        except:
            image_data = download_image_data("http://www.royalroadl.com/Content/Images/rr-placeholder.jpg") #download the default image if the decode fails
    try:
        with open(directory + folder_name + "cover.jpg", "wb") as cover_image_file: #write the image data to the local location in bytes
            cover_image_file.write(image_data)
    except:
        image_data = download_image_data("http://www.royalroadl.com/Content/Images/rr-placeholder.jpg") #download the default image if the decode fails
        with open(directory + folder_name + "cover.jpg", "wb") as cover_image_file: #write the image data to the local location in bytes
            cover_image_file.write(image_data)
            
def download_image_data(cover_image): #download the image data
    try:
        http_client_image = httpclient.HTTPClient() #initiate the http request
        image_data = http_client_image.fetch(cover_image).body #collect the body from the response
        return image_data #return the image data
    except httpclient.HTTPError: #if a http error occurs
        try:
            if e.code != 404: #and it's not a 404, retry the download
                download_image_data(cover_image)
        except:
            download_image_data("http://www.royalroadl.com/Content/Images/rr-placeholder.jpg") #else download the default image

def compress_and_convert_to_epub(directory,folder_location,output_location): #compress and convert the file to epub
    global final_location #access global variables
    new_zip_name = folder_location.split("/")[-2] #create a zip name based on the current folder name
    output_location = directory+new_zip_name #declare the output location of the archive function
    zip_file_epub = zipfile.ZipFile(output_location+".zip", "w") #create a zipfile
    zip_file_epub.writestr("mimetype", "application/epub+zip") #write a mimetype file as the FIRST FILE in the zip, this is critical to the function of an epub as it is the only method of identifying it (must be the first file)
    addFolderToZip(zip_file_epub, folder_location) #add the prepared epub contents to the zip file
    zip_file_epub.close() #close the zipfile
    remove_dir(folder_location) #delete the directory used to make the zipfile
    try: #to prevent file exists error, fails if file is open
        os.remove(output_location+".epub") #remove any epubs that already exist with the name of the current epub
    except:
        pass
    try:
        os.rename(output_location+".zip",output_location+".epub") #rename the epub zip to be an epub file
    except Exception as e: #the rename failed (the last step)
        print(output_location,"Error",e) #the file likely already exists and as such the old one must be manually remove and then the zip file needs to be renamed manually
    final_location = output_location+".epub" #declare the final location of the epub file
    print("Saved EPUB:",final_location) #print the saved location of the epub to the console

def remove_dir(folder_location): #remove a dir
    try:
        rmtree(folder_location) #remove all nested directories
    except:
        os.listdir(folder_location) #if that fails list the directory, maybe useless?
        remove_dir(folder_location) #remove the directory

def addFolderToZip(zip_file_epub, folder_location): #add a folder recursively to a zip file
    for file in os.listdir(folder_location): #for each file in a directory
        full_path = os.path.join(folder_location, file) #construct the full path to the file
        if os.path.isfile(full_path): #if the path is correct
            zip_file_epub.write(str(full_path), str("/".join(full_path.split("/")[2:])), zipfile.ZIP_DEFLATED) #add the file to the zip
        elif os.path.isdir(full_path): #if the path is actually a folder
            addFolderToZip(zip_file_epub, full_path) #add that folder to the zip too

def handle_chapter_response(response): #asynchronously handle the chapter responses
    global i,chapters_downloaded,chapters_html,fiction_html,directory,http_client #access global variables
    if response.code == 599: #if the request failed
        print(response.effective_url,"error") #print an error to the console
        http_client.fetch(response.effective_url.strip(), handle_chapter_response, method='GET',connect_timeout=10,request_timeout=10) #add the failed url to the loop and give it a 10 second timeout
    else:
        html = response.body.decode('utf-8') #decode the response html
        url = response.effective_url #clarify the url of the response
        if "Could not find host | www.royalroad.com | Cloudflare".lower() in html.lower(): #if the page is incorrect and actually a cloudflare auto flag
            print("Cloudflare Problem! Retrying") #alert the console that cloudflare is interfering
            http_client.fetch(response.effective_url.strip(), handle_chapter_response, method='GET',connect_timeout=10,request_timeout=10) #retry the chapter request with a 10 second timeout
        else: #if the page is not cloudflare
            try:
                chapter_id = int(url.split("/")[-2]) #get the chapter id from the url
            except:
                chapter_id = int(url.split("?")[0].split("/")[-1]) #the chapter id is presented weirdly occasionally and as such this is the other method to get the chapter id from the url
            chapters_downloaded.append(chapter_id) #append the chapter id to the chapters_downloaded list
            html = get_chapter_content(html) #get the html content of the chapter from the page
            chapters_html[chapter_id] = html #set the chapter id value in the chapters_html dictionary to the chapter html
            i -= 1 #subtract 1 from the remaining chapter links
            if i == 0: #if all the chapters are downloaded for the fiction
                chapters_downloaded.sort(key=int) #sort the chapter ids so the fiction is in chronological order (very important)
                chp = 0 #declare chp as 0
                for chp_id in chapters_downloaded: #for each chp id downloaded
                    chp += 1 #add one to chp count
                    fiction_html = fiction_html + "<center><h1 style='margin-top: 10px' class='font-white'>(" + str(chp) + ") " + chapters_html[chp_id][1] + "</center></h1>" + chapters_html[chp_id][0] #and append the entire chapter html to the rest of the story
                ioloop.IOLoop.instance().stop() #stop the ioloop and then progress to the save_to_hdd function
