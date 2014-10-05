#!/usr/bin/env python
# -*- coding: utf-8 -*-

import configparser
import logging
import logging.config
import os
import re

import hato

CONFIG_FILE = os.path.dirname(os.path.realpath(__file__)) + "/main.configuration"


# main sequence
def main():
    init_logger()
    (database_name, username, password, freshness_threshold, img_count_threshold,
        polling_interval, target_configs) = get_configuration()

    hatocore = hato.HatoCore(username, password, database_name, freshness_threshold,
                             img_count_threshold, polling_interval, target_configs)
    hatocore.start()


def init_logger():
    logging.config.fileConfig(CONFIG_FILE)
    logging.info("logger initialized.")


def get_configuration():
    logging.info("using config file: " + CONFIG_FILE)
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    database_section = config['database']
    database_name = database_section['database_name']
    username = database_section['username']
    password = database_section['password']

    application_section = config['application']
    freshness_threshold = int(application_section['freshness_threshold'])
    img_count_threshold = int(application_section['img_count_threshold'])
    polling_interval = int(application_section['polling_interval'])

    target_configs = []

    for section_name in config.sections():
        matched = re.search(r"target-(.+)", section_name)
        if not matched:
            continue

        target_config = {}

        target_section = config[section_name]
        target_config['target_name'] = matched.group(1)
        target_config['keywords'] = extract_keywords(target_section.get('keywords'))
        target_config['tweet_prefix'] = target_section.get('tweet_prefix')
        target_config['consumer_key'] = target_section.get('consumer_key')
        target_config['consumer_secret'] = target_section.get('consumer_secret')
        target_config['access_key'] = target_section.get('access_key')
        target_config['access_secret'] = target_section.get('access_secret')

        target_configs.append(target_config)

    return (database_name, username, password, freshness_threshold, img_count_threshold,
            polling_interval, target_configs)


def extract_keywords(keywords=None):
    if keywords:
        keywords = keywords.split(',')

    return keywords


if __name__ == '__main__':
    main()
