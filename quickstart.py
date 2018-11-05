from instapy import InstaPy
import os
import sys
from daemonize import Daemonize

insta_username = 'art_didus'
insta_password = 'veyron1111'

# if you want to run this script on a server,
# simply add nogui=True to the InstaPy() constructor

usernames = []

def scrapping():
    #Read instagram_accounts from file
    with open('insta.csv','r') as file:
        temp = file.readlines()
        for user in temp:
            usernames.append(user.replace("\n",'').replace('http://instagram.com/', ""))

    print(usernames[:5])
    session = InstaPy(username=insta_username, password=insta_password, nogui=False)
    session.login()
    # session.follow_by_list(usernames,times = 1,sleep_delay = 4743, interact = False)
    session.accounts_to_json(usernames)
    #session.feeds_to_json()

    # end the bot session
    session.end()

if __name__ == "__main__":
    instapy_scr = os.path.basename(sys.argv[0])
    pidfile='/tmp/instapy.pid' # any name
    daemon = Daemonize(app=instapy_scr, pid=pidfile, action=scrapping())
    daemon.start()
