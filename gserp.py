#!/usr/bin/python

from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')


class Website:
  """Represents a Website with its URL and its keywords"""
  
  def __init__(self, url, keywords, per_page=10, delay_min=0, delay_max=3):
    self.url = url
    self.keywords = keywords
    self.per_page = per_page
    self.delay_min = delay_min
    self.delay_max = delay_max
    
    self.results = []
  
  def scrape(self, callback=None):
    # start driver
    # chrome_options=chrome_options
    d = webdriver.Chrome('/opt/webdrivers/chromedriver78')
    d.implicitly_wait(10)

    for keyword in self.keywords:
      print('================== %s ==================' % keyword)
      # open google
      # TODO: Open serp with keyword in q param
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
      found = 0

      for result in results:
        # if len(result.get_attribute('class').split(' ')) > 1: continue

        pos += 1
        title = result.find_element_by_tag_name('h3').text
        link = self.__parse_link(result.find_element_by_tag_name('cite'))
        print("[%d] - %s - %s" % (pos, title, link))
        # and put position in self.results
        if self.url in link:
          found += 1
          self.results.append({ keyword: pos })
      
      print('\n\nKeyword: %s - Encontrado: %d vezes.\n\n' % (keyword, found))

    d.close()
    callback(self.results)

  def get_results(self):
    return self.results
  
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


if __name__ == '__main__':
  import sys

  if len(sys.argv) < 3:
    print('Usage: ./gserp <domain> <keywords_file>')
    sys.exit()

  keywords = load_keywords(sys.argv[2])
  url = sys.argv[1]
  # per_page = sys.argv[3] if len(sys.argv) >= 3 else 10

  site = Website(url, keywords)

  site.scrape(lambda results: print(results))

  # TODO: Statistics format
  # TODO: Save to file (csv, json)
  # TODO: Dynamic delay
  # TODO: Dynamic per_page