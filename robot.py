#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
import selenium.common.exceptions as Exceptions
import time
import getopt, sys
import timeit


class SeleniumDriver:
    def __init__(self, implict_wait_time=2, headless=True):
        self._options = webdriver.ChromeOptions()

        # Run chromdriver has headless
        if headless:
            self._options.add_argument('headless')

        # set the window size
        self._options.add_argument("--window-size=1920,1200")

        # initialize the driver
        self.driver = webdriver.Chrome(options=self._options)

        # wait up to implict_wait_time seconds for the elements to become available
        self.implicit_wait_time = 0
        if implict_wait_time > 0:
            self.driver.implicitly_wait(implict_wait_time)
            self.implicit_wait_time = implict_wait_time

    # Visit page
    def visit_page(self, uri):
        self.driver.get(uri)

    # Take screenshot
    def screenshot(self, name='screenshot.png'):
        ## save page as screenshot
        self.driver.get_screenshot_as_file(name)

    def get_options(self):
        return { 'args': self._options.arguments,
                 'implicit_wait_time': self.implicit_wait_time
                 }




class TelekomRobot(SeleniumDriver):
    def __init__(self, implict_wait_time=2, headless=True):
        super().__init__(implict_wait_time, headless)

        self.login_uri = 'https://www.telekom.de/kundencenter/login?showCancelButton=false&redirectUrl=%2Fkundencenter%2Fstartseite'

        self.timestamp = int(time.time())
        self.logged_in = False

    @classmethod
    def from_robot(cls, robot):
        options = robot.get_options()

        headless = False
        if 'headless' in options.get('args'):
            headless = True

        implict_wait_time = options.get('implicit_wait_time')
        return cls(implict_wait_time=implict_wait_time, headless=headless)


    ## login into telekom page
    def login(self, email, password, screenshot=False):

        if self.is_logged_in(email):
            return True

        # Visit login page
        self.visit_page(self.login_uri)

        #Take screenshot
        if screenshot:
            # Append timestamp to name
            self.screenshot("%d_%s" % (self.timestamp ,'pre-login.png'))



        # use css selectors to grab the login email input and fill it in
        try:
            email_elem = self.driver.find_element_by_css_selector('input[id="username"]')
            login_button = self.driver.find_element_by_css_selector('button[id="pw_submit"]')
            
            # Fill in login inputs
            email_elem.send_keys(email)


            # click login button
            login_button.click()
        except Exceptions.NoSuchElementException:
            print('Error: Could not find email elements')
            return False
        except Exception as err:
            print('Error:', err)
            return False

        # use css selectors to grab the login password input and fill it in
        try:
            password_elem = self.driver.find_element_by_css_selector('input[id="pw_pwd"]')
            login_button = self.driver.find_element_by_css_selector('button[id="pw_submit"]')
            
            # Fill in login inputs
            password_elem.send_keys(password)


            # click login button
            login_button.click()
        except Exceptions.NoSuchElementException:
            print('Error: Could not find password elements')
            return False
        except Exception as err:
            print('Error:', err)
            return False


        # Take screenshot
        if screenshot:
            # Append timestamp to name
            self.screenshot("%d_%s" % (self.timestamp, 'post-login.png'))

        ## Verify that we actually logged in
        if not self.is_logged_in(email):
            if self.is_incorrect_credentials():
                print('Error: Wrong credentials provided')
            elif self.is_login_session_error_page():
                print('Error: Login session failed. Rety again')

            return False

        self.logged_in = True
        return True


    ## verify if we're logged in or not
    def is_logged_in(self, email):
        try:
            # Get email element after login
            post_login_email_elem = self.driver.find_element_by_css_selector(
                'div[class="navigation_login-box-content"]')

            # Get the actual text in the email element
            post_login_email = post_login_email_elem.get_attribute('innerText').replace('\n', '').strip()

            # Check if logged in
            # assert email == post_login_email, "Login failed"
            if email == post_login_email:
                return True
            else:
                raise Exception("Error: We're on a page that I dont know about although login seems to be successful")

        except Exceptions.NoSuchElementException:
            return False

    ## Check if login error is session error
    def is_login_session_error_page(self):

        error_string = 'Anmeldung nicht möglich'

        try:
            #body_error = self.driver.find_element_by_css_selector('body[class="error_page"]')



            error_elem = self.driver.find_element_by_css_selector('h1[class="error"]')
            error_elem_text = error_elem.get_attribute('innerText').replace('\n', '').strip()

            if error_elem_text == error_string:
                return True
            else:
                return False
        except Exceptions.NoSuchElementException as err:
            # print('Error: Not on login session error page')
            # raise err
            return False

    ## Check if login error is from incorrect credentials
    def is_incorrect_credentials(self):

        error_string = 'Benutzername oder Passwort ist nicht korrekt.'
        try:
            error_elem = self.driver.find_element_by_css_selector('div[class*="info-box error"]')
            error_elem_text = error_elem.get_attribute('innerText').replace('\n', '').strip()

            if error_elem_text == error_string:
                return True
            else:
                return False
        except Exceptions.NoSuchElementException as err:
            # print('Error: Not on login error page')
            # raise err
            return False

    ## Get main phone number of account
    def get_phone_number(self, screenshot=False):
        if not self.logged_in:
            print('Error: Not logged in')
            return None
        try:
            account_elem = self.driver.find_element_by_css_selector('a[tealium-headline-overwrite="vertragsdetails"]')
            contract_id = account_elem.get_attribute('href').replace('\n', '').replace(
                '/kundencenter/vertragsdetails?c=', '')

            account_elem.click()


            phone_num_elem = self.driver.find_element_by_css_selector('h1[class*="page-title"]')
            phone_num = phone_num_elem.get_attribute('innerText').replace('\n', '')
            # Take screenshot
            if screenshot:
                self.screenshot("%d_%s" % (self.timestamp, 'phone-number.png'))
            return phone_num
        except Exceptions.NoSuchElementException as err:
            print('Error: No phone number attached to account')
            return None


class AlphaCommRobot(SeleniumDriver):
    def __init__(self, implict_wait_time=2):
        super().__init__(implict_wait_time)
        self.login_uri = 'https://www.telekomaufladen.de/de/auth/login'

        self.timestamp = int(time.time())

    ## login into telekom page
    def login(self, email, password, screenshot=False):

        # Visit login page
        self.visit_page(self.login_uri)

        # Take screenshot
        if screenshot:
            # Append timestamp to name
            self.screenshot("%d_%s" % (self.timestamp, 'pre-login.png'))

        # use css selectors to grab the login inputs and login
        try:
            email_elem = self.driver.find_element_by_css_selector('input[id="username"]')
            password_elem = self.driver.find_element_by_css_selector('input[id="password"]')
            #login_button = self.driver.find_element_by_css_selector('input[id="submit"]')

            # Fill in login inputs
            email_elem.send_keys(email)
            password_elem.send_keys(password)

            # click login button
            #login_button.click()
            email_elem.submit()
        except Exceptions.NoSuchElementException:
            print('Error: Could not find login elements')
            return False
        except Exception as err:
            print('Error:', err)
            return False

        # Take screenshot
        if screenshot:
            # Append timestamp to name
            self.screenshot("%d_%s" % (self.timestamp, 'post-login.png'))

def usage():
    usage = '''
        -h, --help         Print this help statement
        -s, --screenshot   Take screenshots of pages
        -e, --email        Email to login with
        -p, --pass         Password to login with
    '''
    print(usage)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hse:p:", ["help", "screenshot", "email=", "pass="])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    user_email = None
    user_password = None
    screenshot = False
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-s", "--screenshot"):
            screenshot = True
        elif o in ("-e", "--email"):
            user_email = a
        elif o in ("-p", "--pass"):
            user_password = a
        else:
            assert False, "unhandled option"

    if not user_email:
        assert False, "User email is missing"

    if not user_password:
        assert False, "User password is missing"

    return user_email, user_password, screenshot


def execute_login(user_email, user_password, screenshot=True):
    telekom = TelekomRobot()
    telekom.login(email=user_email, password=user_password, screenshot=screenshot)
    telekom.get_phone_number(screenshot=screenshot)

def time_wrapper(func, *args, **kwargs):
    def wrapped():
        return func(*args, **kwargs)
    return wrapped

if __name__ == '__main__':
    user_email, user_password, screenshot = main()

    print(user_email, user_password, screenshot)
    execute_login(user_email, user_password, screenshot)

    # wrapped = time_wrapper(execute_login, user_email, user_password, screenshot)
    # print(timeit.timeit(wrapped, number=1))


