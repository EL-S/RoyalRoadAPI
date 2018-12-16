from bs4 import BeautifulSoup
from tornado import ioloop, httpclient
from datetime import datetime
import re
import os

i = 0
chapters_downloaded = []
chapters_html = {}
fiction_html = ""
running = False
directory = "Error/"

def get_fiction(fiction_id,directory="Fictions/"):
    fiction = get_fiction_object(fiction_id)
    get_fiction_info(fiction_id)
    chapter_links = get_chapter_links(fiction)
    if chapter_links != []:
        get_chapters(chapter_links,directory)
    else:
        print("Fiction {} contains no chapters.".format(fiction_id))

def get_fictions(fiction_id_start=1,fiction_id_end=23000,directory="Fictions/"):
    try:
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
    http_client = httpclient.HTTPClient()
    url = "https://www.royalroad.com/fiction/"+str(fiction_id)
    html = http_client.fetch(url).body.decode('utf-8')
    soup = BeautifulSoup(html, "lxml")
    check_active = check_active_fiction(soup,fiction_id)
    if check_active:
        return soup
    else:
        return None
    
def get_fiction_info(fiction_id): #finished
    global url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount
    soup = get_fiction_object(fiction_id)
    if soup:
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
        print("Downloading (" + str(chapter_amount) + " chapter" + plural + "): " + title + " - " + author + ".html")
        #print(url,title,cover_image,author,description,ratings,chapter_links,chapter_amount)
        return url,title,cover_image,author,description,genres,ratings,stats,chapter_links,chapter_amount
    else:
        return None

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
    if cover_image == "/Content/Images/nocover.png":
        cover_image = "http://www.royalroadl.com/content/Images/nocover.png"
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
    global chapters_downloaded,chapters_html,fiction_html,directory
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
    stats_html = "<b><br>Total Views:</b> " + stats[0] + "<b> | Average Views:</b> " + stats[1] + "<b> | Followers:</b> " + stats[2] + "<b> | Favorites:</b> " + stats[3] + "<b> | Pages:</b> " + stats[4]
    statistics = "<center><b>Chapters:</b> " + str(chapter_amount) + "<b> | Overall Score:</b> " + ratings[0] + "<b> | Best Score:</b> " + ratings[1] + "<b> | Ratings:</b> " + ratings[2] + "<b><br>Style Score:</b> " + ratings[3] + "<b> | Story Score:</b> " + ratings[4] + "<b> | Character Score:</b> " + ratings[5] + "<b> | Grammar Score:</b> " + ratings[6] + stats_html + "</center></p></b>"
    data = "<link rel='stylesheet' href='styles/tables.css'><center><img src='" + cover_image + "'><b><h1> \"<a href='" + url + "'>" + str(title) + "</a>\" by \"" + str(author) + "\"</h1></b><br>" +"<br><b>" + genre_html + "</b>" + statistics + "<h2>Last updated: " + time + "</h2></center><br><h3>Description: " + str(description) + "</h3><br>" + fiction_html
    title_clean = re.sub(r'[\\/*?:"<>|]',"",title)
    author_clean = re.sub(r'[\\/*?:"<>|]',"",author)
    print("Saving: " + directory + title_clean + " - " + author_clean + ".html")
    name = title_clean + " - " + author_clean
    folder_name = name + "/"
    os.makedirs(directory+folder_name+"OEBPS/", exist_ok=True)
    file_name = name + ".html"
    full_path = directory + folder_name + file_name
    with open(full_path, "w", encoding="utf-8") as file_webnovel:
        file_webnovel.write(data)
    print("Saved:",full_path)
    uid = "test"
    with open(directory + folder_name + "toc.ncx", "w", encoding="utf-8") as file_toc:
        file_toc.write("""<?xml version='1.0' encoding='UTF-8'?>
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
  <head>
    <meta name="dtb:uid" content=\""""+uid+"""\"/>
    <meta name="dtb:generator" content="DumbEpub"/>
    <meta name="dtb:depth" content="2"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>"""+str(title)+"""</text>
  </docTitle>
  <navMap>
    <navPoint class="chapter" id="navPoint-0" playOrder="1">
      <navLabel>
        <text>""")
        
    chp = 0
    for chp_id in chapters_downloaded:
        chp += 1
        chapter_html = "<?xml version='1.0' encoding='utf-8'?>\n<html xmlns=\"http://www.w3.org/1999/xhtml\">\n\t\t\t\t<head>\n\t\t\t\t\t<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/>\n\t\t\t\t\t<title>Chapter " + str(chp) + ": " + chapters_html[chp_id][1] + "</title>\n\t\t\t\t</head>\n\t\t\t\t<body>\n\t\t\t\t\t<h1>Chapter " + str(chp) + ": " + chapters_html[chp_id][1] + "</h1>\n\t\t\t\t\t" + chapters_html[chp_id][0] + "\n\t\t\t\t</body>\n\t\t\t</html>"
        chapter_file_name = "chapter_"+str(chp)+".xhtml"
        full_path = directory + folder_name + "OEBPS/" + chapter_file_name
        with open(full_path, "w", encoding="utf-8") as file_chapter:
            file_chapter.write(chapter_html)
    with open(directory + folder_name + "OEBPS/"+"titlepage.xhtml", "w", encoding="utf-8") as titlepage:
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
    http_client_image = httpclient.HTTPClient()
    if cover_image == "/Content/Images/rr-placeholder.jpg":
        cover_image_absolute = "https://www.royalroad.com"+cover_image
    else:
        cover_image_absolute = cover_image
    print(cover_image_absolute)
    image_data = http_client_image.fetch(cover_image_absolute).body
    with open(directory + folder_name + "cover.jpg", "wb") as cover_image_file:
        cover_image_file.write(image_data)
    

def handle_chapter_response(response):
    if response.code == 599:
        print(response.effective_url,"error")
        http_client.fetch(response.effective_url.strip(), handle_request, method='GET',connect_timeout=10000,request_timeout=10000)
    else:
        global i,chapters_downloaded,chapters_html,fiction_html,directory
        html = response.body.decode('utf-8')
        url = response.effective_url
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

