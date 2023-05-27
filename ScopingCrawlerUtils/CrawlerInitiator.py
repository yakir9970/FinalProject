import os
import uuid
import requests
from time import sleep
from datetime import datetime
from socket import gethostbyname_ex
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

from ScopingCrawlerUtils.CrawlerManager import CrawlerManager
from ScopingCrawlerUtils.CrawlerKeywords import keywordsPerFeature


def link_response_status_checker(link):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0"}
    try:
        link_response = requests.get(link, verify=False, headers=headers, timeout=5)
        link_status = link_response.status_code
        if link_status == 200:
            return True
        elif link_status == 400 or link_status == 403 or link_status == 404 or link_status == 429 or link_status == 500:
            return False
        else:
            return False
    except Exception as link_response_err:
        return False


class CrawlerInitiator:
    features = {'registerForm': False, 'rstPss': False, 'chatBot': False, 'bagCart': False,
                'accountSettings': False, 'couponPromotion': False, 'LoginLogout': False,
                'No Special Features': False, 'LoginLogoutEvidence': [], 'registerFormEvidence': [],
                'rstPssEvidence': [], 'accountSettingsEvidence': [], 'chatBotEvidence': [],
                'chatBotEvidence': [], 'couponPromotionEvidence': [], 'bagCartEvidence': []}

    def __init__(self, targets, request_json):
        self.targets = targets
        self.request_json = request_json
        self.result = None  # Initialize instance variable to store result
        self.scan_folder = self.create_scan_folder()
        output_dir = 'Output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        new_dir = os.path.join(output_dir, self.scan_folder)
        os.mkdir(new_dir)

        # os.mkdir(os.path.join('Output', self.scan_folder))

    def subprocess_main_starter(self):
        returnArgs = {}
        for target in self.targets:
            target = self.prepare_target_for_crawl(target)
            tld = target['tld']
            try:
                featuresCrawled = self.start_crawl(tld)
            except Exception as e:
                featuresCrawled = self.features
            featuresCrawledSorted = {
                "LoginLogout": (featuresCrawled['LoginLogout'] or featuresCrawled['registerForm'] or
                                featuresCrawled['rstPss'] or featuresCrawled['accountSettings']),
                "registration": featuresCrawled['registerForm'],
                "resetPassword": featuresCrawled['rstPss'],
                "waf": False,
                "geoLocation": False,
                "certificatePinning": False,
                "2fa": False,
                "chatBot": featuresCrawled['chatBot'],
                "couponProm": featuresCrawled['couponPromotion'],
                "bagCart": featuresCrawled['bagCart'],
                "profileSettings": (featuresCrawled['LoginLogout'] or featuresCrawled['registerForm'] or
                                    featuresCrawled['rstPss'] or featuresCrawled['accountSettings']),
                "sso": False,
                "retest": False,
                "payment": featuresCrawled['bagCart'],

                # Evidence section
                "LoginLogoutEvidence": (featuresCrawled['LoginLogoutEvidence'] or
                                         featuresCrawled['registerFormEvidence'] or
                                         featuresCrawled['rstPssEvidence'] or
                                         featuresCrawled['accountSettingsEvidence']),
                "registrationEvidence": featuresCrawled['registerFormEvidence'],
                "resetPasswordEvidence": featuresCrawled['rstPssEvidence'],
                "chatBotEvidence": featuresCrawled['chatBotEvidence'],
                "couponPromEvidence": featuresCrawled['couponPromotionEvidence'],
                "bagCartEvidence": featuresCrawled['bagCartEvidence'],
                "profileSettingsEvidence": (featuresCrawled['LoginLogoutEvidence'] or
                                            featuresCrawled['registerFormEvidence'] or
                                            featuresCrawled['rstPssEvidence'] or
                                            featuresCrawled['accountSettingsEvidence']),
                "paymentEvidence": []
            }
            tld_without_protocol = tld.split('://')[1]
            returnArgs[tld_without_protocol] = featuresCrawledSorted
        self.request_json['featuresData'] = returnArgs
        self.result = self.request_json

    def get_result(self):
        return self.result  # Method to retrieve the result from the instance variable

    def start_crawl(self, tld):
        try:
            links = CrawlerManager(tld, os.path.join('Output', self.scan_folder)).run_crawlers()
            features_calculated = self.sort_crawled_results_by_feature(links)
        except Exception as e:
            features_calculated = self.features
        return features_calculated

    def prepare_target_for_crawl(self, target):
        if not target['tld'].startswith('https://'):
            if not target['tld'].startswith('http://'):
                if self.check_if_target_is_alive(target['tld'], 'https'):
                    target['tld'] = "{}://{}".format('https', target['tld'])
                elif self.check_if_target_is_alive(target['tld'], 'http'):
                    target['tld'] = "{}://{}".format('http', target['tld'])
                else:
                    target['tld'] = "{}://{}".format('https', target['tld'])
        return target

    def check_if_target_is_alive(self, tld, protocol):
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0"}
        is_alive = False
        if not self.ip_resolver(tld):
            return is_alive
        try:
            response = requests.get('{}://{}'.format(protocol, tld), verify=False, headers=headers, timeout=20)
            if response.status_code == 200:
                is_alive = True
        except Exception as e:
            is_alive = False
        return is_alive

    def sort_crawled_results_by_feature(self, links):
        features_calculated = self.features
        for link in links:
            # if not link_response_status_checker(link):
            #     sleep(0.5)
            #     continue
            for feature in keywordsPerFeature.keys():
                for keyword in keywordsPerFeature[feature]:
                    if keyword in link:
                        feature_evidence = f'{feature}Evidence'
                        features_calculated[feature] = True

                        # Verify evidence key exist - if not then create it
                        if feature_evidence not in features_calculated.keys():
                            features_calculated[feature_evidence] = [link]
                        # Verify that evidence URL not exist to avoid duplicates
                        else:
                            if link not in features_calculated[feature_evidence]:
                                features_calculated[feature_evidence].append(link)
        # Verify all Evidence keys are in place
        for feature in keywordsPerFeature.keys():
            feature_evidence_name = f'{feature}Evidence'
            if feature_evidence_name not in features_calculated.keys():
                features_calculated[feature_evidence_name] = []
        return features_calculated

    @staticmethod
    def create_scan_folder():
        date = str(datetime.today())
        uuid_suffix = str(uuid.uuid4())
        date = date.split(' ')
        date = '_'.join(date)
        date = date.split('.')[0]
        date = date.replace(':', '_')
        return '{}_{}'.format(date, uuid_suffix)

    @staticmethod
    def ip_resolver(s):
        is_alive = False
        try:
            ip = gethostbyname_ex(s)
            if ip is not None:
                is_alive = True
            return is_alive
        except:
            return is_alive
