import requests
from bs4 import BeautifulSoup
import time
from random import randint
import urllib

def login(username,password):
    set_cookies,soup,cookie = establish_first_connection() #establish the first connection and get the required cookies and values from the dom and headers

    set_cookies,cookie = send_login_request(soup,username,password,cookie) #send a post request with all the information

    headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "accept-encoding": "gzip, deflate",
                "accept-language": "en-US,en;q=0.9",
                "cookie": cookie,
                "referrer": "https://www.royalroad.com/account/loginsuccess?returnUrl=https%3A%2F%2Fwww.royalroad.com%2Fhome",
                "upgrade-insecure-requests": "1",
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"}

    user_id = get_logged_in_users_id(headers)

    print("Logged In.")
    
    return [headers,user_id] #return the working login information

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

    set_cookies = login_response_headers["Set-Cookie"].split(";")

    cookie += "; "+set_cookies[0]+";"
    
    return set_cookies,cookie

def get_logged_in_users_id(login_details):
    req = requests.get("https://www.royalroad.com/home", headers=login_details)
    html = req.text
    soup = BeautifulSoup(html, "lxml")
    user_id = soup.find("ul", attrs={"class":"dropdown-menu dropdown-menu-default"}).find("a").get("href").split("/")[-1].strip()
    return user_id

def request_secure_page(url,login_object):
    req = requests.get(url, headers=login_object[0])
    html = req.text
    soup = BeautifulSoup(html, "lxml")
    return soup

def send_message(login_object,recipients,subject,message,replyto=""):
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
        print("Message Sent.")
    else:
        status = False
        print("Message failed to send.")
    
    return status

login_object = login("","")

status = send_message(login_object,"userid","subject","message")
    



