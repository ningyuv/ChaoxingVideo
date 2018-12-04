from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

from random import randint
import requests
import json
import time

import logging
logFileName = (str(time.ctime() + "_Selenium.log").replace(":","-").replace(" ",""))
logger = logging.getLogger(__name__)
logFormat = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
logHandler = logging.FileHandler(logFileName)
logHandler.setFormatter(logFormat)
logger.addHandler(logHandler)
#Log Level
logger.setLevel(logging.DEBUG)

class AutoVideo:
    def __init__(self):
        self.webDri = webdriver.Chrome()
        self.webDri.get('http://stdu.fanya.chaoxing.com/portal')

    def run(self):
        url = input('URL: ')
        self.webDri.get(url)
        self.getUrlList()
        self.learnVideo()

    def locateVideo(self):
        self.webDri.switch_to.default_content()
        try:
            WebDriverWait(self.webDri, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, 'iframe'))
            )
        except:
            print('Can\'t find frame. By.ID iframe.')
        try:
            WebDriverWait(self.webDri, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, 'iframe'))
            )
            self.webDri.execute_script('javascript:Ext.fly(window.document).un("mouseout");void 0');
            self.video = self.webDri.find_element_by_id('video_html5_api')
            self.webDri.execute_script('arguments[0].volume=0;', self.video);
            return True
        except:
            print('Can\'t find frame. By.TAG_NAME iframe.')
            return False

    def getUrlList(self):
        self.missionList = []
        print('Finding Timeline...')
        try:
            timeLine = self.webDri.find_element_by_class_name('timeline')
            print('Found Timeline')
            units = timeLine.find_elements_by_class_name('units')
            for unit in units:
                print('Found Unit: ' + unit.find_element_by_tag_name('h2').text)
                leveltwo = unit.find_elements_by_class_name('leveltwo')
                for course in leveltwo:
                    print('Found Course: ' + course.find_element_by_tag_name('h3').text)
                    _dict = {}
                    _dict['title'] = course.find_element_by_tag_name('a').get_attribute('title')
                    _dict['point'] = course.find_element_by_tag_name('em').text
                    _dict['href'] = course.find_element_by_tag_name('a').get_attribute('href')
                    self.missionList.append(_dict)
        except:
            print('Dead on Timeline.')

    def learnVideo(self):
        for i in self.missionList:
            if i['point'] == '2':
                print('Learning ' + i['title'])
                logger.info('Learning ' + i['title'])
                self.webDri.get(i['href'])
                try:
                    dct1 = WebDriverWait(self.webDri, 10).until(
                        EC.presence_of_element_located((By.ID, 'dct1'))
                    )
                    if dct1.get_attribute('title') != '视频':
                        dct2 = self.webDri.find_element_by_id('dct2')
                        if dct2.get_attribute('title') == '视频':
                            self.webDri.execute_script('arguments[0].click()', dct2)
                        else:
                            continue
                except:
                    print('Can\'t find dct1.')
                    continue

                try:
                    WebDriverWait(self.webDri, 10).until(
                        EC.frame_to_be_available_and_switch_to_it((By.ID, 'iframe'))
                    )
                    # self.webDri.switch_to_frame('iframe')
                    datas = self.webDri.find_element_by_tag_name('iframe').get_attribute('data')
                    datas = json.loads(datas)
                    self.mid = datas['mid']
                except:
                    print('Dead on iframe.')

                try:
                    WebDriverWait(self.webDri, 10).until(
                        EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, 'iframe'))
                    )
                    # self.webDri.switch_to_frame(self.webDri.find_element_by_tag_name('iframe'))
                except:
                    print('Dead on iframe.')

                try:
                    self.video = WebDriverWait(self.webDri, 10).until(
                        EC.presence_of_element_located((By.ID, 'video_html5_api'))
                    )
                    # self.video = self.webDri.find_element_by_id('video_html5_api')
                    self.webDri.execute_script('javascript:Ext.fly(window.document).un("mouseout");void 0');
                    actions = ActionChains(self.webDri)
                    actions.reset_actions()
                    actions.move_to_element(self.video)
                    actions.click()
                    actions.perform()
                    # firstPlay = self.webDri.find_element_by_class_name('vjs-big-play-button')
                    # self.webDri.execute_script('arguments[0].click()', firstPlay)
                except:
                    print('Dead on Video.')

                print('Question Listener Working...')
                while self.answerQuestion():
                    time.sleep(randint(5,20))
                # i['point'] = '1'
                # time.sleep(1000)

    def answerQuestion(self):
        if not self.locateVideo():
            return False
        ended = self.webDri.execute_script('javascript:return arguments[0].ended;void 0', self.video)
        if ended:
            return False
        paused = self.webDri.execute_script('javascript:return arguments[0].paused;void 0', self.video)
        if not paused:
            return True
        try:
            ul = self.webDri.find_element_by_class_name('ans-videoquiz-opts')
            li = ul.find_elements_by_tag_name('li')
            subm = self.webDri.find_element_by_class_name('ans-videoquiz-submit')
        except:
            self.webDri.execute_script('arguments[0].play();', self.video);
            return True

        # questionUrl = self.webDri.find_element_by_id('questionUrl')
        questionUrl = 'https://mooc1-1.chaoxing.com/richvideo/initdatawithviewer?mid=' + self.mid
        res = self.getHTMLText(url = questionUrl)
        res = json.loads(res)
        print(res)
        logger.info(res)
        currentTime = self.webDri.execute_script('javascript:return arguments[0].currentTime', self.video)
        if res == '':
            return True

        print('AnswerQuestion： ' + res[0]['datas'][0]['description'])

        for index,o in enumerate(res[0]['datas'][0]['options']):
            if o['isRight']:
                print('Will Click: ' + str(o['name']))
                self.webDri.execute_script('arguments[0].click()', li[index].find_element_by_tag_name('input'))
        print('Will Click: submit')
        self.webDri.execute_script('arguments[0].click()', subm)

        return True

    def getHTMLText(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        try:
            # print(url)
            r = requests.get(url, headers = headers)
            print(r.status_code)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except:
            print('Not 200.')
            return ''

robot = AutoVideo()
robot.run()