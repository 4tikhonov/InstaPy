import os
import sys
import time
import arrow
import unittest
from instapy import InstaPy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from elasticsearch import Elasticsearch

insta_username = 'zeusfsx'
insta_password = 'instagrambot'


class PythonInstagram(unittest.TestCase):

    test_session = None
    test_usernames = []
    test_usernames[0] = 'art_didus'

    def test_creating_chromedriver(self):
        test_session = InstaPy(username=insta_username, password=insta_password, nogui=True)
        utc = arrow.utcnow()
        if test_session:
            print("Test 'InstaPy()' PASS at " + str(utc))
        else:
            print("Test 'InstaPy()' FAIL at " + str(utc))

    def test_login(self):
        loginner = test_session.login()
        utc = arrow.utcnow()
        if isinstance(loginner, InstaPy):
            print("Test 'login' PASS at " + str(utc))
        else:
            print("Test 'login' FAIL at " + str(utc))

    def test_accounts_to_json(self):
        id_news = ['1738744946298415600', '1788357238303626994']
        test_session.accounts_to_json(test_usernames)
        res = check_Elastic(id_news)
        utc = arrow.utcnow()
        if res == 2:
            print("Test 'accounts_to_json' PASS at " + str(utc))
        else:
            print("Test 'accounts_to_json' FAIL at " + str(utc))

    def test_end(self):
        brouwser = test_session.get_browser()
        utc = arrow.utcnow()
        try:
            brouwser.get('https://www.google.com.ua')
            print("Test 'InstaPy()' FAIL at " + str(utc))
        except:
            print("Test 'InstaPy()' PASS at " + str(utc))





def check_Elastic(id_news: list)->int:
    es = Elasticsearch(
        ['media-audit.com'],
        http_auth=('elastic', 'changeme'),
        port=9200
    )
    
    res = es.search('instagram', 'local', body={"query": {
                                                "ids" : {
                                                    "values" : id_news
                                                }
                                            }
                                        })
    return res['hits']['total']

if __name__ == "__main__":
    unittest.main()