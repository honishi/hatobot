#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import pymysql

TWEET_STATUS_COMPLETED = 0
TWEET_STATUS_FAILED = 1


class HatoDatabase(object):
    def __init__(self, username, password, database):
        self.connect = pymysql.connect(
            user=username, passwd=password, database=database, charset='utf8')

    def __del__(self):
        self.connect.close()

# save img/tree
    def save_imgs(self, imgs):
        cursor = self.connect.cursor()

        for img in imgs:
            cursor.execute("replace into img "
                           "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", img)
        self.connect.commit()

        cursor.close()

    def save_trees(self, trees):
        cursor = self.connect.cursor()

        for tree in trees:
            cursor.execute("replace into tree values(%s, %s, %s)", tree)
        self.connect.commit()

        cursor.close()

# new heads picker
    def pick_new_head_imgs(self, img_count, freshness, keywords=None):
        """
        returns [(head_img_no, subject, comment), (...), ...].
        """
        picked_new_heads = []
        cursor = self.connect.cursor()

        base_query = ("select tree.head_img_no, img.subject, img.comment"
                      " from img force index(idx_date_no_subject), tree"
                      " where"
                      " (now() - interval {} hour) < img.img_date"
                      " and img.img_no = tree.head_img_no"
                      " and {} <= tree.img_count"
                      .format(freshness, img_count))

        if keywords is None:
            keywords = [None]

        for keyword in keywords:
            logging.debug("keyword:<{}>".format(keyword))

            query = base_query
            if keyword:
                query = base_query + " and img.subject like '%{}%'".format(keyword)

            cursor.execute(query)
            rows = cursor.fetchall()
            picked_new_heads.extend(rows)

        cursor.close()

        # remove duplicates, http://stackoverflow.com/a/7961425
        picked_new_heads = list(set(picked_new_heads))

        return picked_new_heads

# tweet status
    def is_tweeted(self, target_name, head_img_no, img_count):
        cursor = self.connect.cursor()
        cursor.execute("select * from tweet"
                       " where target_name = %s and img_no = %s and img_count = %s and status = %s",
                       (target_name, head_img_no, img_count, TWEET_STATUS_COMPLETED))
        is_tweeted = (0 < cursor.rowcount)
        cursor.close()

        return is_tweeted

    def set_tweet_as_completed(self, target_name, head_img_no, img_count):
        self.set_tweet(target_name, head_img_no, img_count, TWEET_STATUS_COMPLETED)

    def set_tweet(self, target_name, head_img_no, img_count, status):
        cursor = self.connect.cursor()
        cursor.execute("replace into tweet values(%s, %s, %s, %s, %s)",
                       (target_name, head_img_no, img_count, status, 0))
        self.connect.commit()
        cursor.close()
