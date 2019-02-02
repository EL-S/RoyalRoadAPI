import requests
from bs4 import BeautifulSoup
import time
from random import randint
import urllib

def login(username,password):
    set_cookies,soup,cookie = establish_first_connection() #establish the first connection and get the required cookies and values from the dom and headers

    response = send_login_request(soup,username,password,cookie) #send a post request with all the information

    if response != None:
        set_cookies,cookie = response
        headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "accept-encoding": "gzip, deflate",
                    "accept-language": "en-US,en;q=0.9",
                    "cookie": cookie,
                    "referrer": "https://www.royalroad.com/account/loginsuccess?returnUrl=https%3A%2F%2Fwww.royalroad.com%2Fhome",
                    "upgrade-insecure-requests": "1",
                    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

        user_id = get_logged_in_users_id(headers)

        print("Successfully Logged In.")
        
        return [headers,user_id] #return the working login information
    else:
        return None

def establish_first_connection():
    url = "https://www.royalroad.com/account/login"

    headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-US,en;q=0.9",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

    req = requests.get(url, headers=headers)

    response_headers = req.headers
    html = req.text

    soup = BeautifulSoup(html, "lxml")

    set_cookies = response_headers["Set-Cookie"].split(";")
    timestamp = str(round(time.time()))
    client_id = str(randint(100000000,999999999))
    client_id2 = str(randint(100000000,999999999))
    royalroad_session_id = "372508318544cb51a44a490a91a69ff4" #actually get this value somewhere
    
    cookie = set_cookies[0]+";"+" _ga=GA1.2."+client_id+"."+timestamp+"; _gid=GA1.2."+client_id2+"."+timestamp+"; visited=1; RoyalRoad.SessionId="+royalroad_session_id+"; "+set_cookies[-4].strip().split()[-1]
    
    return set_cookies,soup,cookie

def send_login_request(soup,username,password,cookie):

    url = "https://www.royalroad.com/account/login"
    rememberme = "false"
    requesttoken = soup.find("input", attrs={"name":"__RequestVerificationToken"}).get("value")
    returnurl = soup.find("input", attrs={"id":"ReturnUrl"}).get("value")

    urlencoded = "ReturnUrl="+returnurl+"&Username="+username+"&Password="+password+"&__RequestVerificationToken="+requesttoken+"&Remember="+rememberme

    content_length = str(len(urlencoded))

    headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "max-age=0",
                "content-length": content_length, #the string length of the post data url encoded
                "content-type": "application/x-www-form-urlencoded",
                "cookie": cookie,
                "origin": "https://www.royalroad.com",
                "referer": "https://www.royalroad.com/account/login",
                "upgrade-insecure-requests": "1",
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

    data = {"ReturnUrl":returnurl,
            "Username":username,
            "Password":password,
            "_RequestVerificationToken":requesttoken,
            "Remember":rememberme}

    login_request = requests.post(url, headers=headers, data=data, allow_redirects=False)

    login_response_headers = login_request.headers
    try:
        set_cookies = login_response_headers["Set-Cookie"].split(";")
        cookie += "; "+set_cookies[0]+";"
        return [set_cookies,cookie]
    except:
        print("Failed to Login.")

def get_logged_in_users_id(login_details):
    req = requests.get("https://www.royalroad.com/home", headers=login_details)
    html = req.text
    soup = BeautifulSoup(html, "lxml")
    user_id = soup.find("ul", attrs={"class":"dropdown-menu dropdown-menu-default"}).find("a").get("href").split("/")[-1].strip()
    return user_id

def request_secure_page(url,login_object): #implement retry logic
    req = requests.get(url, headers=login_object[0])
    html = req.text
    soup = BeautifulSoup(html, "lxml")
    return soup

def send_message(login_object,recipients,subject,message,replyto=""):
    if login_object == None:
        print("Failed to Send Message: Not Logged In.")
        status = False
        return status
    else:
        cookie = login_object[0]['cookie'][:-1]
        url_compose = "https://www.royalroad.com/private/send"
        soup = request_secure_page(url_compose, login_object)

        requesttoken = soup.find("input", attrs={"name":"__RequestVerificationToken"}).get("value")
        
        cfuid = cookie.split(";")[0].split("=")[1]
        ga = cookie.split(";")[1].split("=")[1]
        visited = cookie.split(";")[3].split("=")[1]
        notif_dismiss = "1"
        royalroad_sessionid = cookie.split(";")[4].split("=")[1]
        gid = cookie.split(";")[2].split("=")[1]
        
        antiforgery = cookie.split(";")[5].split("=")[1]
        identity_application = cookie.split(";")[6].split("=")[1]
        
        cookie_new = "__cfduid="+cfuid+"; _ga="+ga+"; visited="+visited+"; notif_dismiss-987973="+notif_dismiss+"; RoyalRoad.SessionId="+royalroad_sessionid+"; .AspNetCore.Antiforgery.w5W7x28NAIs="+antiforgery+"; _gid="+gid+"; .AspNetCore.Identity.Application="+identity_application

        url = "https://www.royalroad.com/private/send/"
        action = "send"

        data = {"__RequestVerificationToken": requesttoken,
                "replyto": replyto, #the messageid of the message being quick replied to
                "Uid": recipients,
                "Subject": subject,
                "content": message,
                "action": action}
        url_encoded = urllib.parse.urlencode(data) #maybe this is wrong
        content_length = str(len(url_encoded))
        headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                    "accept-encoding": "gzip, deflate",
                    "accept-language": "en-US,en;q=0.9",
                    "cache-control": "max-age=0",
                    "content-length": content_length, #can be anything
                    "content-type": "application/x-www-form-urlencoded",
                    "cookie": cookie_new, #must be correct
                    "origin": "https://www.royalroad.com",
                    "referer": url_compose, #can be anything?
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

        req = requests.post(url, data=data, headers=headers)

        soup = BeautifulSoup(req.text, "lxml")
        title = soup.find("title").text
        if "pm sent".lower() in title.lower():
            status = True
            print("Message sent.")
        else:
            status = False
            print("Message failed to send.")
        
        return status

def request_message_like_list(login_object,message_type):
    url = "https://www.royalroad.com/private/"
    if message_type == "received":
        url_suffix = "1"
    elif message_type == "sent":
        url_suffix = "2"
    elif message_type == "drafts":
        url_suffix = "3"
    elif message_type == "deleted":
        url_suffix = "4"
    else:
        url_suffix = "1"
    url = url+url_suffix
    soup = request_secure_page(url,login_object)
    try:
        pages = int(soup.find("ul", attrs={"class":"pagination"}).findAll("a")[-1].get("href").split("=")[-1])
    except:
        pages = 1
    messages = []
    messages = extract_messages_from_soup(soup,messages)
    if pages > 1:
        for i in range(2,pages+1):
            url_page = str(url)+"?page="+str(i)
            print(url_page)
            soup = request_secure_page(url_page,login_object)
            messages = extract_messages_from_soup(soup,messages)
    return messages

def extract_messages_from_soup(soup,messages):
    message_listings = soup.find("tbody").findAll("tr", recursive=False)
    for message_listing in message_listings:
        data = message_listing.findAll("td", recursive=False)
        data2 = data[1]
        data3 = data[2]
        time_data = data[3].find("time")

        message_id = data2.find("a").get("href").split("/")[-1].strip()
        author_id = data3.find("a").get("href").split("/")[-1].strip()
        author = data3.text.strip()
        title = data2.text.strip()
        status = data[0].find("i").get("title").strip()
        time = [time_data.get("unixtime").strip(),time_data.text.strip()]
        messages.append([message_id,author_id,author,title,status,time])
    return messages

def read_messages(login_object):
    if login_object == None:
        print("Failed to Read Messages: Not Logged In.")
        return
    else:
        message_type = "received"
        received_messages = request_message_like_list(login_object,message_type)
        return received_messages

def read_sent_messages(login_object):
    if login_object == None:
        print("Failed to Read Sent Messages: Not Logged In.")
        return
    else:
        message_type = "sent"
        sent_messages = request_message_like_list(login_object,message_type)
        return sent_messages

def read_draft_messages(login_object):
    if login_object == None:
        print("Failed to Read Draft Messages: Not Logged In.")
        return
    else:
        message_type = "drafts"
        draft_messages = request_message_like_list(login_object,message_type)
        return draft_messages

def read_deleted_messages(login_object):
    if login_object == None:
        print("Failed to Read Deleted Messages: Not Logged In.")
        return
    else:
        message_type = "deleted"
        deleted_messages = request_message_like_list(login_object,message_type)
        return deleted_messages

def get_message_content(login_object,message_id):
    if login_object == None:
        print("Failed to Read Message: Not Logged In.")
        return
    else:
        url = "https://www.royalroad.com/private/read/"+message_id
        soup = request_secure_page(url,login_object)
        content_data = extract_message_content(soup)
        if content_data != None:
            content = [message_id,content_data[0],content_data[1],content_data[2],content_data[3],content_data[4],content_data[5],content_data[6]]
            return content

def extract_message_content(soup):
    try:
        data = soup.find("div", attrs={"class":"pm-users"}).findAll("a")
        time_data = soup.find("time")
        title = soup.find("h3", attrs={"class":"margin-top-0 margin-bottom-10"}).text.strip()
        content = soup.find("div", attrs={"class":"pm-body"}).text.strip()
        author = data[0].text.strip()
        author_id = data[0].get("href").split("/")[-1].strip()
        recipient = data[1].text.strip()
        recipient_id = data[1].get("href").split("/")[-1].strip()
        time = [time_data.get("unixtime"),time_data.text.strip()]
        return [author_id,recipient_id,author,recipient,title,content,time]
    except:
        print("That message has been deleted, it does not exist, or you do not have permission to view it.")

def do_secure_post(login_object,token_url,post_url,message_id): #only deletes at the moment
    cookie = login_object[0]['cookie'][:-1]
    soup = request_secure_page(token_url, login_object)

    requesttoken = soup.find("input", attrs={"name":"__RequestVerificationToken"}).get("value")
    
    cfuid = cookie.split(";")[0].split("=")[1]
    ga = cookie.split(";")[1].split("=")[1]
    visited = cookie.split(";")[3].split("=")[1]
    notif_dismiss = "1"
    royalroad_sessionid = cookie.split(";")[4].split("=")[1]
    gid = cookie.split(";")[2].split("=")[1]
    
    antiforgery = cookie.split(";")[5].split("=")[1]
    identity_application = cookie.split(";")[6].split("=")[1]
    
    cookie_new = "__cfduid="+cfuid+"; _ga="+ga+"; visited="+visited+"; notif_dismiss-987973="+notif_dismiss+"; RoyalRoad.SessionId="+royalroad_sessionid+"; .AspNetCore.Antiforgery.w5W7x28NAIs="+antiforgery+"; _gid="+gid+"; .AspNetCore.Identity.Application="+identity_application

    action = "delete" #maybe

    data = {"__RequestVerificationToken": requesttoken,
            "pmid": message_id}
    url_encoded = urllib.parse.urlencode(data) #maybe this is wrong
    content_length = str(len(url_encoded))
    headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "max-age=0",
                "content-length": content_length, #can be anything
                "content-type": "application/x-www-form-urlencoded",
                "cookie": cookie_new, #must be correct
                "origin": "https://www.royalroad.com",
                "referer": token_url, #can be anything?
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

    req = requests.post(post_url, data=data, headers=headers)

    soup = BeautifulSoup(req.text, "lxml")
    title = soup.find("title").text
    return title

def delete_message(login_object,message_id):
    if login_object == None:
        print("Failed to Delete Message: Not Logged In.")
        status = False
        return status
    else:
        token_url = "https://www.royalroad.com/private/read/"+message_id
        post_url = "https://www.royalroad.com/private/delete"
        title = do_secure_post(login_object,token_url,post_url,message_id)
        if "pm deleted".lower() in title.lower():
            status = True
            print("Message deleted.")
        else:
            status = False
            print("Message failed to delete.")
        return status

login_object = login("username","password")

#status = delete_message(login_object,"message_id")

#status = send_message(login_object,"user_id","subject","message")
