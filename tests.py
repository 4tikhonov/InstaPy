import os
import sys
import time
import arrow
import unittest
from instapy import InstaPy
from quickstart import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from elasticsearch import Elasticsearch

insta_username = 'zeusfsx'
insta_password = 'instagrambot'


class PythonInstagram(unittest.TestCase):

    test_session = None
    test_usernames = ['art_didus']

    def test_acreating_chromedriver(self):
        PythonInstagram.test_session = InstaPy(username=insta_username, password=insta_password, nogui=True)
        utc = arrow.utcnow()
        if PythonInstagram.test_session:
            print("\nTest 'InstaPy()' PASS at " + str(utc))
        else:
            print("\nTest 'InstaPy()' FAIL at " + str(utc))
            send_email("Test 'InstaPy()' FAIL at " + str(utc))

    def test_blogin(self):
        loginner = PythonInstagram.test_session.login()
        utc = arrow.utcnow()
        if isinstance(loginner, InstaPy):
            print("\nTest 'login' PASS at " + str(utc))
        else:
            print("\nTest 'login' FAIL at " + str(utc))
            send_email("Test 'login' FAIL at " + str(utc))

    def test_caccounts_to_json(self):
        id_news = ['1738744946298415600', '1788357238303626994']
        PythonInstagram.test_session.accounts_to_json(PythonInstagram.test_usernames)
        res = check_Elastic(id_news)
        utc = arrow.utcnow()
        if res == 2:
            print("\nTest 'accounts_to_json' PASS at " + str(utc))
        else:
            print("\nTest 'accounts_to_json' FAIL at " + str(utc))
            send_email("Test 'accounts_to_json' FAIL at " + str(utc))

    def test_dend(self):
        PythonInstagram.test_session.end()
        brouwser = PythonInstagram.test_session.get_browser()
        utc = arrow.utcnow()
        try:
            brouwser.get('https://www.google.com.ua')
            print("\nTest 'InstaPy()' FAIL at " + str(utc))
            send_email("Test 'InstaPy()' FAIL at " + str(utc))
        except:
            print("\nTest 'InstaPy()' PASS at " + str(utc))





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
