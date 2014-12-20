#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import logging.config
import re
import time

import requests
from twython import Twython

from hato.database import HatoDatabase
from hato.exception import HatoException

HATORODA_BASE = "http://up.subuya.com/"
HATORODA_TREE = HATORODA_BASE + "tree.cgi"
HATORODA_IMG = HATORODA_BASE + "img.cgi"
HATORODA_PAGE = HATORODA_BASE + "siokara.php?res="

USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/37.0.2062.124 Safari/537.36")

NO_TITLED_SUBJECT = "無題"
# use '[0-9A-Za-z_]' instead of '\w', cause it matches full-width characters like 'あ'
REGEXP_URL = r"https?://[0-9A-Za-z_/:%#\$&\?\(\)~\.0=\+\-]+"
COMMENT_LENGTH_IN_NO_TITLED_SUBJECT = 50


class HatoCore(object):
    def __init__(self, username, password, database, freshness_threshold, img_count_thresholds,
                 polling_interval, target_configs):
        self.username = username
        self.password = password
        self.database = database
        self.freshness_threshold = freshness_threshold
        self.img_count_thresholds = img_count_thresholds
        self.polling_interval = polling_interval
        self.target_configs = target_configs

# public interface
    def start(self):
        while True:
            try:
                # raise Exception("dummy exception.")
                self.hatodb = HatoDatabase(self.username, self.password, self.database)
                self.monitor()
            except Exception as error:
                logging.error("caught exception:{}".format(error))

            logging.info("*** sleeping for {} seconds...".format(self.polling_interval))
            time.sleep(self.polling_interval)

# main sequence
    def monitor(self):
        self.process_img()
        self.process_tree()
        self.process_tweet()

    def process_img(self):
        logging.info("*** processing img.")

        raw_img = self.fetch_hatoloda(HATORODA_IMG)
        imgs = self.parse_img(raw_img)
        logging.debug("fetched {} imgs.".format(len(imgs)))

        self.hatodb.save_imgs(imgs)
        logging.debug("saved {} imgs.".format(len(imgs)))

    def process_tree(self):
        logging.info("*** processing tree.")

        raw_tree = self.fetch_hatoloda(HATORODA_TREE)
        trees = self.parse_tree(raw_tree)
        logging.debug("fetched {} trees.".format(len(trees)))

        self.hatodb.save_trees(trees)
        logging.debug("saved {} trees.".format(len(trees)))

    def process_tweet(self):
        logging.info("*** processing tweet.")

        for target_config in self.target_configs:
            target_name = target_config['target_name']
            keywords = target_config['keywords']

            logging.info("target:<{}>".format(target_name))

            for img_count_threshold in self.img_count_thresholds:
                logging.info("img_count_threshold:<{}>".format(img_count_threshold))
                picked_new_heads = self.hatodb.pick_new_head_imgs(
                    img_count_threshold, self.freshness_threshold, keywords)

                for new_head in picked_new_heads:
                    (head_img_no, subject, comment) = new_head
                    logging.debug("({},{},{})".format(head_img_no, subject, img_count_threshold))

                    if not self.hatodb.is_tweeted(target_name, head_img_no, img_count_threshold):
                        logging.debug("updating twitter status...")

                        tweet_prefix = target_config['tweet_prefix']
                        consumer_key = target_config['consumer_key']
                        consumer_secret = target_config['consumer_secret']
                        access_key = target_config['access_key']
                        access_secret = target_config['access_secret']

                        subject = self.adjust_subject(subject, comment)

                        self.tweet(tweet_prefix, subject, head_img_no, img_count_threshold,
                                   consumer_key, consumer_secret, access_key, access_secret)
                        self.hatodb.set_tweet_as_completed(
                            target_name, head_img_no, img_count_threshold)

                        logging.info("updated twitter status.")
                        time.sleep(5)

# internal methods
    def fetch_hatoloda(self, url):
        request = requests.get(url, headers={"User-Agent": USER_AGENT})
        if request.status_code != 200:
            raise HatoException()
        # logging.debug(request.content)

        request.encoding = 'shift_jis'
        text = request.text

        return text

    def parse_img(self, text):
        """
        returns img array. img quote from original source:
        list($no,$now,$name,$email,$sub,$com,$url,$host,$pw,$ext,$w,$h,$tim,$chk) = ...
        """
        imgs = []

        for line in text.splitlines():
            if line is None:
                continue

            columns = line.split(',')
            # print("{}: {}".format(len(columns), line))
            if len(columns) != 15:
                continue

            img_no = int(columns[0])
            img_date = self.convert_datetime_string(columns[1])
            img_name = columns[2]
            mail = columns[3]
            subject = columns[4]
            comment = columns[5]
            url = columns[6]
            host = columns[7]
            password = columns[8]
            ext = columns[9]
            width = (0 if columns[10] == "" else int(columns[10]))
            height = (0 if columns[11] == "" else int(columns[11]))
            img_time = int(columns[12])
            checksum = columns[13]

            img = (img_no, img_date, img_name, mail, subject, comment, url, host, password, ext,
                   width, height, img_time, checksum)
            imgs.append(img)

        return imgs

    def parse_tree(self, text):
        trees = []

        for line in text.splitlines():
            if line is None:
                continue

            imgs = line.split(',')

            head_img_no = imgs[0]
            img_nos = line
            img_count = len(imgs)

            tree = (head_img_no, img_nos, img_count)
            trees.append(tree)

        return trees

    def adjust_subject(self, subject, comment):
        # decode unicode references
        subject = self.decode_unicode_references(subject)
        comment = self.decode_unicode_references(comment)

        # cleansing text
        subject = self.replace_special_characters(subject)
        comment = self.replace_special_characters(comment)

        # adjust subject
        if subject != NO_TITLED_SUBJECT or (subject == NO_TITLED_SUBJECT and len(comment) == 0):
            return subject

        if len(comment) < COMMENT_LENGTH_IN_NO_TITLED_SUBJECT:
            pass
        else:
            comment = comment[0:COMMENT_LENGTH_IN_NO_TITLED_SUBJECT] + "…"

        return subject + "（" + comment + "）"

    def tweet(self, tweet_prefix, subject, img_no, img_count,
              consumer_key, consumer_secret, access_key, access_secret):
        status = "{}{} [{}+] {}".format(
            tweet_prefix, subject, img_count, HATORODA_PAGE + str(img_no))

        try:
            twitter = Twython(consumer_key, consumer_secret, access_key, access_secret)
            twitter.update_status(status=status)
        except Exception as error:
            logging.error("caught exception in tweet:{}".format(error))

# miscellaneous utility methods
    def convert_datetime_string(self, string):
        # convert datetime string like '14/10/01(水)13:45:40' to datetime object.
        cleansed = re.sub(r"\(.\)", " ", string)
        datetime_object = datetime.datetime.strptime(cleansed, "%y/%m/%d %H:%M:%S")

        return datetime_object

    # based on http://stackoverflow.com/a/1208931
    def decode_unicode_references(self, string):
        def _callback(matches):
            value = int(matches.group(1))
            try:
                return chr(value)
            except:
                return value

        return re.sub("&#(\d+)(;|(?=\s))", _callback, string)

    def replace_special_characters(self, string):
        replaced = re.sub(r"[@＠]", "%", string)
        replaced = re.sub(r"<br />", "", replaced)
        replaced = re.sub(REGEXP_URL, "", replaced)

        return replaced
