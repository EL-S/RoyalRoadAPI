from bs4 import BeautifulSoup
from tornado import ioloop, httpclient
from datetime import datetime
import re
import os
import uuid
from shutil import copyfile, make_archive, rmtree
import zipfile
import base64

i = 0
chapters_downloaded = []
chapters_html = {}
fiction_html = ""
running = False
directory = "Error/"

def get_fiction(fiction_id,directory="Fictions/"):
    fiction_object = get_fiction_object(fiction_id)
    get_fiction_info(fiction_object)
    if chapter_links != []:
        get_chapters(chapter_links,directory)
    else:
        print("Fiction {} contains no chapters.".format(fiction_id))

def get_fictions(fiction_id_start=1,fiction_id_end=None,directory="Fictions/"):
    try:
        if fiction_id_end == None:
            fiction_id_end = find_latest_fiction_id()
        fiction_id_start = int(fiction_id_start)
        fiction_id_end = int(fiction_id_end)
        total = (fiction_id_end-fiction_id_start)+1
        if (fiction_id_end >= fiction_id_start):
            for i in range(fiction_id_start,fiction_id_end+1):
                try:
                    get_fiction(i,directory)
                    print("Progress:",str(round((((i-(fiction_id_start))+1)/total)*100,2))+"%")
                    print("Remaining:",str((total-1)-(i-(fiction_id_start))))
                except:
                    print("Fiction {} Not Available.".format(i))
                    print("Progress:",str(round((((i-(fiction_id_start))+1)/total)*100,2))+"%")
                    print("Remaining:",str((total-1)-(i-(fiction_id_start))))
        else:
            print("Invalid Range.")
    except:
        print("Please use valid numbers!")

def get_fiction_object(fiction_id):
    global url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount
    try:
        url = None
        title = None
        cover_image = None
        author = None
        description = None
        genres = None
        ratings = None
        stats = None
        chapter_links = None
        chapter_amount = None
    except:
        pass
    try:
        http_client = httpclient.HTTPClient()
        url = "https://www.royalroad.com/fiction/"+str(fiction_id)
        html = http_client.fetch(url).body.decode('utf-8')
        soup = BeautifulSoup(html, "lxml")
        check_active = check_active_fiction(soup,fiction_id)
        if check_active:
            return soup
        else:
            return None
    except httpclient.HTTPError as e:
        if e.code != 404: #don't know the exact exception code
            get_fiction_object(fiction_id)
    
def get_fiction_info(fiction_obj): #finished
    global url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount
    soup = fiction_obj
    if soup:
        fiction_id = get_fiction_id(soup)
        url = "https://www.royalroad.com/fiction/"+str(fiction_id)
        title = get_fiction_title(soup)
        cover_image = get_fiction_cover_image(soup)
        author = get_fiction_author(soup)
        description = get_fiction_description(soup)
        genres = get_fiction_genres(soup)
        ratings = get_fiction_rating(soup)
        stats = get_fiction_statistics(soup)
        chapter_links = get_chapter_links(soup)
        chapter_amount = len(chapter_links)
        if chapter_amount == 1:
            plural = ""
        elif chapter_amount == 0:
            return None
        else:
            plural = "s"
        print("Downloading ({} chapter".format(chapter_amount) + plural + ") ID {}: ".format(fiction_id) + title + " - " + author + ".epub")
        #print(url,title,cover_image,author,description,ratings,chapter_links,chapter_amount)
        return url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount
    else:
        return None

def get_fiction_id(soup):
    fiction_id = soup.find("input", attrs={"name":"id"}).get("value")
    return fiction_id

def find_latest_fiction_id():
    try:
        http_client = httpclient.HTTPClient()
        url = "https://www.royalroad.com/fictions/new-releases"
        html = http_client.fetch(url).body.decode('utf-8')
        soup = BeautifulSoup(html, "lxml")
        latest_fiction_id = int(soup.find("a",attrs={"class":"font-red-sunglo bold"}).get("href").split("/")[2])
        return latest_fiction_id
    except httpclient.HTTPError as e:
        if e.code != 404: #don't know the exact exception code
            find_latest_fiction_id()

def check_active_fiction(soup,fiction_id):
    not_active = soup.find('div', attrs={'class': 'number font-red-sunglo'})
    if not_active:
        print("No Fiction with ID "+str(fiction_id))
        return False
    else:
        return True

def get_fiction_title(soup): #finished
    title = soup.find('h1', attrs={'property': 'name'}).text.strip()
    return title

def get_fiction_cover_image(soup): #finished
    cover_image = soup.find('img', attrs={'property': 'image'}).get('src')
    if cover_image.lower() == "/Content/Images/rr-placeholder.jpg".lower():
        cover_image = "http://www.royalroadl.com/Content/Images/rr-placeholder.jpg"
    elif cover_image == "undefined":
        cover_image = "http://www.royalroadl.com/Content/Images/rr-placeholder.jpg"
    return cover_image

def get_fiction_author(soup): #finished
    author = soup.find('span', attrs={'property': 'name'}).text.strip()
    if author == "":
        author = "NONE"
    return author

def get_fiction_description(soup): #finished
    description = soup.find('div', attrs={'property': 'description'}).text.strip()
    if description == "":
        description = "No Description"
    return description

def get_fiction_genres(soup):
    genres = []
    genre_tags_part1 = soup.findAll('span', attrs={'class': 'label label-default label-sm bg-blue-hoki'})
    genre_tags_part2 = soup.findAll('span', attrs={'property': 'genre'})
    for tag in genre_tags_part1:
        genres.append(tag.text.strip())
    for tag in genre_tags_part2:
        genres.append(tag.text.strip())
    return genres

def get_fiction_rating(soup): #finished
    overall_rating = soup.find('meta', attrs={'property': 'ratingValue'}).get("content")
    best_rating = soup.find('meta', attrs={'property': 'bestRating'}).get("content")
    rating_count = soup.find('meta', attrs={'property': 'ratingCount'}).get("content")
    style_rating = soup.find('span', attrs={'data-original-title': 'Style Score'}).get("data-content")
    story_rating = soup.find('span', attrs={'data-original-title': 'Story Score'}).get("data-content")
    character_rating = soup.find('span', attrs={'data-original-title': 'Character Score'}).get("data-content")
    grammar_rating = soup.find('span', attrs={'data-original-title': 'Grammar Score'}).get("data-content")
    rating = [overall_rating,best_rating,rating_count,style_rating,story_rating,character_rating,grammar_rating]
    return rating

def get_fiction_statistics(soup):
    total_views = soup.findAll('li', attrs={'class': 'bold uppercase font-red-sunglo'})[0].text.strip()
    average_views = soup.findAll('li', attrs={'class': 'bold uppercase font-red-sunglo'})[1].text.strip()
    followers = soup.findAll('li', attrs={'class': 'bold uppercase font-red-sunglo'})[2].text.strip()
    favorites = soup.findAll('li', attrs={'class': 'bold uppercase font-red-sunglo'})[3].text.strip()
    pages = soup.findAll('li', attrs={'class': 'bold uppercase font-red-sunglo'})[5].text.strip()
    stats = total_views,average_views,followers,favorites,pages
    return stats

def get_chapter_links(soup): #finished
    chapter_links = []
    chapter_links_tag = soup.findAll('tr', attrs={'style': 'cursor: pointer'})
    for tag in chapter_links_tag:
        chapter_link = tag.get("data-url")
        chapter_links.append(chapter_link)
    return chapter_links

def get_chapter_amount(soup):
    chapter_links = []
    chapter_links_tag = soup.findAll('tr', attrs={'style': 'cursor: pointer'})
    for tag in chapter_links_tag:
        chapter_link = tag.get("data-url")
        chapter_links.append(chapter_link)
    return len(chapter_links)

def get_chapters(chapter_links,directory_loc="Fictions/"):
    global chapters_downloaded,chapters_html,fiction_html,directory,http_client
    globals()['directory'] = directory_loc #little dodgy
    chapters_downloaded = []
    chapters_html = {}
    fiction_html = ""
    http_client = httpclient.AsyncHTTPClient(force_instance=True,defaults=dict(user_agent="Mozilla/5.0"),max_clients=20)
    for chapter in chapter_links:
        global i
        i += 1
        url = "https://www.royalroad.com/"+str(chapter)
        http_client.fetch(url.strip(),handle_chapter_response, method='GET',connect_timeout=10000,request_timeout=10000)
    if chapter_links != []:
        ioloop.IOLoop.instance().start()

def get_chapter_content(html):
    soup = BeautifulSoup(html, "lxml")
    chapter_title = soup.find('h1', attrs={'style': 'margin-top: 10px','class': 'font-white'}).text.strip()
    content_html = str(soup.find('div', attrs={'class': 'chapter-inner chapter-content'}))
    #print(chapter_title)
    return content_html,chapter_title

def save_to_hdd(fiction_html,chapters_html,chapters_downloaded,directory="Fictions/"):
    global url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount
    time = datetime.now().strftime("%Y-%m-%d %H:%M")
    genre_html = ""
    for genre in genres:
        if genre_html == "":
            genre_html += genre
        else:
            genre_html += " | " + genre
    stats_html = "</p><p><b>Total Views:</b> " + stats[0] + "<b> | Average Views:</b> " + stats[1] + "<b> | Followers:</b> " + stats[2] + "<b> | Favorites:</b> " + stats[3] + "<b> | Pages:</b> " + stats[4]
    statistics = "<b>Chapters:</b> " + str(chapter_amount) + "<b> | Overall Score:</b> " + ratings[0] + "<b> | Best Score:</b> " + ratings[1] + "<b> | Ratings:</b> " + ratings[2] + "</p><p><b>Style Score:</b> " + ratings[3] + "<b> | Story Score:</b> " + ratings[4] + "<b> | Character Score:</b> " + ratings[5] + "<b> | Grammar Score:</b> " + ratings[6] + stats_html + "</p>"
    data = "<center><img src='../cover.jpg'></img><p><b><h1> \"<a href='" + url + "'>" + str(title) + "</a>\" by \"" + str(author) + "\"</h1></b></p><p><b>" + genre_html + "</b></p><p>" + statistics + "<p><h2>Last updated: " + time + "</h2></p></center><p><h3>Description:</h3> " + str(description) + "</p>"# + fiction_html
    title_clean = re.sub(r'[\\/*?:"<>|]',"",title)
    author_clean = re.sub(r'[\\/*?:"<>|]',"",author)
    if author_clean[-1] == ".":
        author_clean = author_clean.replace(".","dot")
    print("Saving EPUB: " + directory + title_clean + " - " + author_clean + ".epub")
    name = title_clean + " - " + author_clean
    folder_name = name + "/"
    os.makedirs(directory+folder_name+"OEBPS/", exist_ok=True)
    os.makedirs(directory+folder_name+"META-INF/", exist_ok=True)
    file_name = name + ".html"
    full_path = directory + folder_name + file_name
    #with open(full_path, "w", encoding="utf-8") as file_webnovel:
    #    file_webnovel.write(data)
    #print("Saved:",full_path)
    uuid_str = str(uuid.uuid4())
    with open(directory + folder_name + "toc.ncx", "w", encoding="utf-8") as file_toc:
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
##    with open(directory + folder_name + "mimetype", "w", encoding="utf-8") as file_mimetype:
##        file_mimetype.write("application/epub+zip")
    with open(directory + folder_name + "META-INF/container.xml", "w", encoding="utf-8") as file_container:
        file_container.write("""<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
	<rootfiles>
		<rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
	</rootfiles>
</container>""")
    with open(directory + folder_name + "content.opf", "w", encoding="utf-8") as file_content:
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
    <opf:item id="cover-page" href="titlepage.xhtml" media-type="application/xhtml+xml"/>
    <opf:item id="prov_idx_1" href="OEBPS/info.xhtml" media-type="application/xhtml+xml"/>""")
    for i in range(1,len(chapters_downloaded)+1):
        with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content:
            file_content.write("""
    <opf:item id="prov_idx_""" + str(i+1) + """\" href="OEBPS/chapter_""" + str(i) + """.xhtml" media-type="application/xhtml+xml"/>""")
    with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content:
        file_content.write("""
  </opf:manifest>
  <opf:spine toc="ncx">""")
    
    with open(directory + folder_name + "toc.ncx", "a", encoding="utf-8") as file_toc:
            file_toc.write("""
    <navPoint class="chapter" id="navPoint-""" + str(0) + """\" playOrder=\"""" + str(1) + """\">
      <navLabel>
        <text>Information</text>
      </navLabel>
      <content src="OEBPS/info.xhtml"/>
    </navPoint>""")
    full_path = directory + folder_name + "OEBPS/info.xhtml"
    with open(full_path, "w", encoding="utf-8") as file_info:
        file_info.write("""<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
				<head>
					<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
					<title>Information</title>
				</head>
				<body>
					"""+data+"""</body>
			</html>""")
    #("tables.css",directory + folder_name + "tables.css") #not needed
    with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content:
        file_content.write("""
    <opf:itemref idref="prov_idx_1\"/>""")
    chp = 0
    for chp_id in chapters_downloaded:
        chp += 1
        chapter_title = "Chapter " + str(chp) + ": " + chapters_html[chp_id][1]
        chapter_html = "<?xml version='1.0' encoding='utf-8'?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n\t\t\t\t<head>\n\t\t\t\t\t<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/>\n\t\t\t\t\t<title>Chapter " + str(chp) + ": " + chapters_html[chp_id][1] + "</title>\n\t\t\t\t</head>\n\t\t\t\t<body>\n\t\t\t\t\t<h1>Chapter " + str(chp) + ": " + chapters_html[chp_id][1] + "</h1>\n\t\t\t\t\t" + chapters_html[chp_id][0] + "\n\t\t\t\t</body>\n\t\t\t</html>"
        chapter_file_name = "chapter_"+str(chp)+".xhtml"
        full_path = directory + folder_name + "OEBPS/" + chapter_file_name
        with open(full_path, "w", encoding="utf-8") as file_chapter:
            file_chapter.write(chapter_html.replace("&","&#38;"))
        with open(directory + folder_name + "toc.ncx", "a", encoding="utf-8") as file_toc:
            file_toc.write("""
    <navPoint class="chapter" id="navPoint-""" + str(chp) + """\" playOrder=\"""" + str(chp+1) + """\">
      <navLabel>
        <text>""" + chapter_title.replace("&","&#38;") + """</text>
      </navLabel>
      <content src="OEBPS/chapter_""" + str(chp) + """.xhtml"/>
    </navPoint>""")
        with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content:
            file_content.write("""
    <opf:itemref idref="prov_idx_""" + str(chp+1) + """\"/>""")
    with open(directory + folder_name + "content.opf", "a", encoding="utf-8") as file_content:
            file_content.write("""
  </opf:spine>
  <opf:guide>
    <opf:reference href="titlepage.xhtml" title="Cover" type="cover"/>
  </opf:guide>
</opf:package>""")
    with open(directory + folder_name + "toc.ncx", "a", encoding="utf-8") as file_toc:        
        file_toc.write("""
  </navMap>
</ncx>""")
    with open(directory + folder_name + "titlepage.xhtml", "w", encoding="utf-8") as titlepage:
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
    if (cover_image.split(",")[0] != "data:image/jpeg;base64") and (cover_image.split(",")[0] != "data:image/gif;base64") and (cover_image.split(",")[0] != "data:image/png;base64"):
        image_data = download_image_data(cover_image)
    else:
        image_data = base64.b64decode(cover_image.split(",")[1])
        with open('cover.jpg', 'wb') as file:
            file.write(image_data)
    with open(directory + folder_name + "cover.jpg", "wb") as cover_image_file:
        cover_image_file.write(image_data)
    output_location = directory
    folder_location = directory + folder_name
    compress_and_convert_to_epub(directory,folder_location,output_location)

def download_image_data(cover_image):
    try:
        http_client_image = httpclient.HTTPClient()
        image_data = http_client_image.fetch(cover_image).body
        return image_data
    except httpclient.HTTPError as e:
        if e.code != 404: #don't know the exact exception code
            download_image_data(cover_image)

def compress_and_convert_to_epub(directory,folder_location,output_location):
    #print(folder_location)
    new_zip_name = folder_location.split("/")[-2]
    #print(new_zip_name)
    output_location = directory+new_zip_name
    #print(output_location)
    zip_file_epub = zipfile.ZipFile(directory+new_zip_name+".zip", "w")
    zip_file_epub.writestr("mimetype", "application/epub+zip")
    #print(folder_location)
    #zip_file_epub.write(folder_location, folder_location, zipfile.ZIP_DEFLATED)
    addFolderToZip(zip_file_epub, folder_location)
    #make_archive(output_location, 'zip', folder_location)
    zip_file_epub.close()
    remove_dir(folder_location)
    try: #to prevent file exists error
        os.remove(output_location+".epub")
    except:
        pass
    try:
        os.rename(output_location+".zip",output_location+".epub")
    except Exception as e:
        print(output_location,"Error",e)
    print("Saved EPUB:",output_location+".epub")    

def remove_dir(folder_location):
    try:
        rmtree(folder_location)
    except:
        os.listdir(folder_location)
        remove_dir(folder_location)

def addFolderToZip(zip_file_epub, folder_location):
    for file in os.listdir(folder_location):
        full_path = os.path.join(folder_location, file)
        if os.path.isfile(full_path):
            #print('File added: ' + str(full_path))
            zip_file_epub.write(str(full_path), str("/".join(full_path.split("/")[2:])), zipfile.ZIP_DEFLATED)
        elif os.path.isdir(full_path):
            #print('Entering folder: ' + str(full_path))
            addFolderToZip(zip_file_epub, full_path)
def handle_chapter_response(response):
    global i,chapters_downloaded,chapters_html,fiction_html,directory,http_client
    if response.code == 599:
        print(response.effective_url,"error")
        http_client.fetch(response.effective_url.strip(), handle_chapter_response, method='GET',connect_timeout=10,request_timeout=10)
    else:
        html = response.body.decode('utf-8')
        url = response.effective_url
        if "Could not find host | www.royalroad.com | Cloudflare".lower() in html.lower(): #incorrect page
            print("Cloudflare Problem! Retrying")
            http_client.fetch(response.effective_url.strip(), handle_chapter_response, method='GET',connect_timeout=10,request_timeout=10)
        else:
            try:
                chapter_id = int(url.split("/")[-2])
            except:
                chapter_id = int(url.split("?")[0].split("/")[-1])
            chapters_downloaded.append(chapter_id)
            html = get_chapter_content(html)
            chapters_html[chapter_id] = html
            #print(url)
            i -= 1
            if i == 0: #all chapters downloaded for the fiction
                #evoke a function with the complete fiction html
                chapters_downloaded.sort(key=int)
                chp = 0
                for chp_id in chapters_downloaded:
                    chp += 1
                    fiction_html = fiction_html + "<center><h1 style='margin-top: 10px' class='font-white'>(" + str(chp) + ") " + chapters_html[chp_id][1] + "</center></h1>" + chapters_html[chp_id][0]
                save_to_hdd(fiction_html,chapters_html,chapters_downloaded,directory)
                ioloop.IOLoop.instance().stop()

