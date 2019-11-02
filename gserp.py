#!/usr/bin/python

import json
import time
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
# chrome_options.add_argument('--headless')


class Website:
  """Represents a Website with its URL and its keywords"""
  
  def __init__(self, url, keywords, per_page=10, delay_min=0, delay_max=3):
    self.url = url
    self.keywords = keywords
    self.per_page = per_page
    self.delay_min = delay_min
    self.delay_max = delay_max

    self.statistics = {
      'site': self.url,
      'date': None,
      'keywords': {kw: [] for kw in self.keywords}
    }

    print(self.statistics)
  
  def scrape(self, callback=None):
    # start driver
    d = webdriver.Chrome('/opt/webdrivers/chromedriver78', options=chrome_options)
    d.implicitly_wait(10)

    self.statistics['date'] = int(round(time.time() * 1000))

    for keyword in self.keywords:
      print('================== %s ==================' % keyword)
      d.get('https://google.com')
      search_bar = d.find_element_by_name('q')
      search_bar.clear()

      # search for keyword
      search_bar.send_keys(keyword)
      search_bar.send_keys(Keys.RETURN)

      # serp_cache = d.find_element_by_id('rso')

      try:
        d.execute_script("document.getElementsByClassName('g kno-kp mnr-c g-blk')[0].remove()")
      except:
        pass
      
      # get keyword position from serp
      results = d.find_element_by_id('rso')
      results = results.find_elements_by_class_name('g')

      # site position
      pos = 0

      for result in results:
        # if len(result.get_attribute('class').split(' ')) > 1: continue
        pos += 1
        title = result.find_element_by_tag_name('h3').text
        link = self.__parse_link(result.find_element_by_tag_name('cite'))
        print("[%d] - %s - %s" % (pos, title, link))

        # if found
        if self.url in link:
          # update statistics
          self.statistics['keywords'][keyword].append(pos)
      
      print('\n\nKeyword: %s - Encontrado: %d vezes.\n\n' % (keyword, len(self.statistics['keywords'][keyword])))

    d.close()
    callback(self.statistics)

  def get_results(self):
    return self.statistics
  
  def __parse_link(self, link):
    cl = link.get_attribute('class')
    link = urlparse(link.text.split(' › ')[0]) if 'bc' in cl else urlparse(link.text)

    return link.path if link.scheme == '' else link.hostname


def load_keywords(filename):
  keywords = []
  
  with open(filename) as f:
    for line in f.readlines():
      if line.endswith('\n'):
        keywords.append(line[:-1])
      else:
        keywords.append(line)

  return keywords

def save_statistics(statistics):
  print(statistics)

  with open('%s-%d.txt' % (statistics['site'], statistics['date']), 'w+') as f:
    json.dump(statistics, f)


if __name__ == '__main__':
  import sys

  if len(sys.argv) < 3:
    print('Usage: ./gserp <domain> <keywords_file>')
    sys.exit()

  keywords = load_keywords(sys.argv[2])
  url = sys.argv[1]
  # per_page = sys.argv[3] if len(sys.argv) >= 3 else 10

  site = Website(url, keywords)

  site.scrape(save_statistics)
