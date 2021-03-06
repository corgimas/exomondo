import splinter
import requests
import logging
import re
from time import sleep

class Browser(object):
    def __init__(self, webdriver, email = None,password = None, user_agent = None, cookies = None):

        self.browser = splinter.Browser(webdriver,user_agent=user_agent)

        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})

        if (not cookies):
            if not (email and password):
                raise Exception('you should specify email and password or cookies')
            self.cookies = self.login(email,password)
        else:
            self.cookies = cookies

    def login(self,email,password):
        b = self.browser

        b.visit('http://www.endomondo.com')
        b.find_link_by_href('login').first.click()

        b.fill('email',email)
        b.fill('password',password)
        b.find_by_css('div.signInButton').first.click()
        cookies = dict(map(lambda cookie: (cookie['name'],cookie['value']), b.cookies.all()))

        return cookies

    def download_track(self,workout_id):
        url = 'http://www.endomondo.com/workouts/%d' % workout_id
        logging.debug('exploring workout %d' % workout_id)
        
        b = self.browser
        b.visit(url)
        try:
            b.find_by_css('span.more').first.mouse_over()
        except NotImplementedError:
            b.find_by_css('span.more').first.click()
        
        try:
            b.find_by_css('a.export').first.click()
        except splinter.exceptions.ElementDoesNotExist:
            logging.info('There is no track available for workout %d' % workout_id)
            return None

        for i in range(0,20):
            if b.is_text_present('CHOOSE EXPORT DESTINATION'):
                logging.debug('it took %d s for ajax to finish' % 0.2*i)
                break
            sleep(0.2)
        else: 
            raise Exception('Export dialog was not loaded')

        m = re.search('<a href="\.\./(.+?exportGpxLink.+?)">',b.html)
        
        url = 'http://www.endomondo.com/'+m.group(1)
        r = self.session.get(url, cookies = self.cookies)
        return r.text


    def get_cookies(self):
        return self.session.cookies
