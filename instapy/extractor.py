"""Methods to extract the data for the given usernames profile"""
from time import sleep
from re import findall
import math
from langdetect import detect
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import requests
from datetime import datetime
import json
import re
from elasticsearch import Elasticsearch


def difference_between_two_list(list_1, list_2):
    index = 0
    if list_1 and list_2:
        if list_2[0] in list_1:
            first_element = list_2[0]
            for idx,item in enumerate(list_1):
                if item == first_element:
                    index = idx
                    break
            return list_1[:index]
        else:
            return list_1
    else:
        return list_1

def get_user_info(browser):
    """Get the basic user info from the profile screen"""
    sleep(2)
    data = browser.execute_script("return window._sharedData;")
    # print(data)
    # data = json.loads(data)
    alias_name = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["full_name"]
    bio = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["biography"]
    prof_img = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["profile_pic_url"]
    num_of_posts = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["count"]
    followers = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_followed_by"]["count"]
    following = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_follow"]["count"]
    user_id = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["id"]
    return alias_name, bio, prof_img, num_of_posts, followers, following, user_id


def all_extract_post_info(browser, _id, count):
    """
    Get the information from the current post
    """
    _hash = None
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    script = """return window.performance.getEntries({entryType: "resource"});"""
    sleep(2)
    for req in browser.execute_script(script):
        if 'query_hash' in req['name']:
            _hash = req['name']
    if count > 12:
        _hash = re.findall('ash=.*&vari', str(_hash))
        print(_hash)
        _hash = _hash[0][4:]
        _hash = _hash[:-5]
        req = "https://www.instagram.com/graphql/query/?query_hash=" + str(_hash) +\
              '&variables={\"id\":' + str(_id) + ',\"first\":' + str(count) + "}"
        #print(req)
        browser.get(req)
        data  = json.loads(browser.find_element_by_tag_name("pre").text)
        nodes = data["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
    else:
        data = browser.execute_script("return window._sharedData;")
        data = json.loads(browser.find_element_by_tag_name("pre").text)
        nodes = data["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
    return nodes

def extract_information(browser, username, limit_amount, logger):
    """Get all the information for the given username"""

    browser.get('https://www.instagram.com/' + username)
    num_of_posts = 0
    user_id = 0
    alias_name = ''
    bio = ''
    followers = 0
    following = 0
    prof_img = ''
    links2 = []
    try:
        alias_name, bio, prof_img, num_of_posts, followers, following, user_id = get_user_info(browser)
        browser.get('https://www.instagram.com/' + username)
        nodes = all_extract_post_info(browser, user_id, num_of_posts)
        if limit_amount < 1:
            limit_amount = 999999
        num_of_posts = min(limit_amount, num_of_posts)
    except:
        print ("\nError: Couldn't get user profile.")
        return None

    #prev_divs = browser.find_elements_by_class_name('_70iju')

    #posts - array of dicts all posts
    posts = []
    time = datetime.now()

    for node in nodes:
        try:
            language = detect(node["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"])
        except:
            language = 'en'
        title = ""
        if node["node"]["edge_media_to_caption"]["edges"]:
            text = node["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"]
            k = 0
            text = text.split(' ')
            for word in text:
                title = title + word + ' '
                k += 1
                if k == 11:
                    break
        post = {
            'id': node["node"]["id"],
            'display_url': node["node"]["display_url"],
            'is_video': node["node"]["is_video"] if "is_video" in node["node"] else False,
            'text': node["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"] if node["node"]["edge_media_to_caption"]["edges"] else "",
            'title': title,
            'language': language,
            'shortcode': node["node"]["shortcode"],
            'comments_count': node["node"]["edge_media_to_comment"]["count"],
            'timestamp': node["node"]["taken_at_timestamp"],
            'foundtime': int(time.timestamp()),
            'like_count': node["node"]["edge_media_preview_like"]["count"],
            'owner': node["node"]["owner"]["id"],
            'url': "https://www.instagram.com/p/" + node["node"]["shortcode"]

        }
        #print(post)
        posts.append(post)

    #end

    information = {
        'id':user_id,
        'full_name': alias_name,
        'username': username,
        'bio': bio,
        'prof_img': prof_img,
        'num_of_posts': num_of_posts,
        'followers': followers,
        'following': following,
        'timestamp': int(time.timestamp())
    }
    posts.append(information)

    return posts

def instaimport(searchindex,thisdoctype,newsbody):
    # Index by Elastic
    es = Elasticsearch(
        ['media-audit.com'],
        http_auth=('elastic', 'changeme'), #TODO - config.py
        port=9200
    )
    
    if newsbody:
        searchindex = 'instagram'
        try:
            es.create(index=searchindex, doc_type=thisdoctype, body=newsbody, id=newsbody['id'])

        except:
            es.delete(index=searchindex, doc_type=thisdoctype, id=newsbody['id'])
            print('Delete Id =' + newsbody['id'])
            try:
                es.create(index=searchindex, doc_type=thisdoctype, body=newsbody, id=newsbody['id'])
                print('Id = ' + newsbody['id'] + ' was upload \n')
            except:
                es.delete(index=searchindex, doc_type=thisdoctype, id=newsbody['id'])
                print("Skip")

    return 'ok'
