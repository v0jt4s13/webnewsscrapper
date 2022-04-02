import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.traceback import install
from datetime import datetime

install()
console = Console()

def calculate_execution_time(time_point_list=[],end=0):
  import time
  if end == 0:
    time_point_list.append(time.time())
    return time_point_list
  else:
    end_time = time.time()
    time_taken = end_time - time_point_list[0]
    #print("\nTime: ", time_taken)
    return time_taken

def get_date_time(show_part):
  import datetime
  
  currentDateTime = datetime.datetime.now()
  date = currentDateTime.date()
  year = ""
  month = ""
  day = ""
  if "Y" in show_part:
    year = date.strftime("%Y")
  if "M" in show_part:
    month = date.strftime("%m")
  if "D" in show_part:
    day = date.strftime("%d")
  
  return (int(year),month,day)

def get_page(link):
  # get page from link
  request_object = requests.get(link)
  page = BeautifulSoup(request_object.content,features="lxml")
  return page

def get_list_links(scrapped_page):
  return [a.get('href') for a in scrapped_page.find_all('a', href=True)]


#####################################################
############### metro.co.uk #########################
#####################################################
def metro_response_build(url,deep_lvl,links_list):
  page_link_list = []
  section_link_list = []
  #print(links_list)
  #print('\n\t\t'+'*'*100)
  #print('\t\t  _response_build -> go to metro_clear_links(',url,', links_list len:',len(links_list),')\n\t\t','*'*100)
  new_links_list = metro_clear_links(url,links_list)
  #print('\t\t'+'*'*100,'\n\t\t  _response_build -> new_links_list len:',len(new_links_list),'\n\t\t','*'*100,'\n')
  #print(new_links_list)
  
  for type,page_url in new_links_list:
    if type == "page":
      page_link_list.append(page_url)
    elif type == "section":
      section_link_list.append(page_url)

  #print(' _response_build -> section_link_list len:',len(section_link_list),' ===> page_link_list len:',len(page_link_list),'\n')
  if deep_lvl == 'front':
    #print('\t\t _response_build',len(page_link_list),'->',deep_lvl,'END ',url,'\n')
    return [page_link_list, section_link_list]

  else:
    #print('\t\t\t _response_build',len(page_link_list),' ->',deep_lvl,'END\n')
    return [page_link_list, []]

def metro_clear_links(url,links_list):
  new_links_list = []
  website_new_links_list = []
  #print('metro_clear_links START -> links_list len:',len(links_list))
  tmp_set = set()
  for link in links_list:
    link = link.replace('https://metro.co.uk','').replace('https://www.metro.co.uk','')

    if link.startswith('/') and link.endswith('/'):
      url_to_list = link.split('/')
      #print(url_to_list)
      if url_to_list[1].isnumeric():
        ####################################################
        ############# data do poprawy po testach ###########
        ####################################################
        ####################################################
        url_today_date = (int(url_to_list[1]),url_to_list[2],'') #,url_to_list[5])
        today_date = get_date_time('YM')
        if today_date == url_today_date:
          tmp_set.add(link)
          if link not in new_links_list:
            #print(today_date,' == ',url_today_date,link)    
            new_links_list.append(link)
            website_new_links_list.append(['page',link])
          
        else:
          pass
        #/sport/, /tag/premier-league/, /tag/transfer-news-and-rumours/, /sport/tennis/, /sport/cricket/, /sport/boxing/, /tag/snooker/, /tag/darts/, /entertainment/, /lifestyle/, /puzzles/, /blogs/, 
      elif link in ("/news/","/news/uk/","/video/","/tag/coronavirus/", "/news/us/", "/news/world/", "/tag/royal-family/", "/news/weird/", "/news/tech/", "/tag/russia-ukraine-conflict/", "/rush-hour-crush/", "/trending/"):
        tmp_set.add(link)
        if link not in new_links_list:
          new_links_list.append(link)
          website_new_links_list.append(['section',link])
      else:
        pass #print(link)
          
    elif link.startswith('#') or link.startswith('http://') or link.startswith('httpsify') or link.startswith('javascript'):
      tmp_set.add(link)
      continue
    elif "/video/" in link:
      tmp_set.add(link)
      if link not in new_links_list:
        new_links_list.append(link)
        website_new_links_list.append(['page',link])
    else:
      pass
          #print(today_date,' == ',url_today_date, link)
  #print(list(set(section_links_list)))
  #print(len(links_list),len(new_links_list))
  #print('metro_clear_links END -> website_new_links_list len:',len(website_new_links_list))

  #print(tmp_set.difference(set(links_list)))

  return website_new_links_list

def metro_article_scrap(url,keys_list):
  soup = get_page(url)
  
  return_json_list = []
  return_json_list.append({'url':url})
  for key in keys_list:
    if key == "title":
      post_title = soup.find("h1", class_="post-title")
      post_title = post_title.getText().replace("'","\'")
      return_json_list.append({'post_title':post_title})
    elif key == "author":
      author_container = soup.find("span", class_="author-container")
      try:
        author_container = author_container.getText().replace("'","\'")
        return_json_list.append({'author_container':author_container})
      except:
        pass
    elif key == "date":
      post_date = soup.find("span", class_="post-date")
      post_date = post_date.getText().replace("'","\'")
      formated_post_date = datetime.strptime(post_date,"%A %d %b %Y %I:%M %p")
      return_json_list.append({'post_date': str(formated_post_date)})
    elif key == "body":
      article_body = soup.find("div", class_="article-body")
      article_body = article_body.getText().replace("'","\'").replace("\n\n","")
      return_json_list.append({'article_body':article_body})
    elif key == "img":
      images_article = soup.find("div", class_="article-body")
      images_article_str = ""
      img_json_list = []
      #print(len(images_article),images_article)
      images = images_article.find_all("img")
      if images is not None and len(images) > 0:
        if images_article_str == "":
          #print(len(images),type(images),'++++')
          for img in images:
            try:
              src = img['data-src']
            except:
              try:
                src = img['src']
              except:
                pass
            try:
              alt = img['alt']
            except:
              alt = ""

            if src and alt:
              img_json_list.append({'src':src,'alt':alt})
            
      return_json_list.append({'images':img_json_list})
          
  return return_json_list # {'url':url, 'post_title':post_title, 'author_container':author_container, 'post_date':post_date, 'article_body':article_body} #, 'images':images}

def metro_section_links(section_links_list):
  for url in section_links_list:
    scrapped_page = get_page(url)
    links_list = get_list_links(scrapped_page)

  return links_list

#####################################################
################# bbc.com ###########################
#####################################################
def bbc_response_build(url,deep_lvl,links_list):
  page_link_list = []
  section_link_list = []
  #print(links_list)
  #print('\n\t\t'+'*'*100)
  #print('\t\t  _response_build -> go to metro_clear_links(',url,', links_list len:',len(links_list),')\n\t\t','*'*100)
  new_links_list = bbc_clear_links(url,links_list)
  #print('\t\t'+'*'*100,'\n\t\t  _response_build -> new_links_list len:',len(new_links_list),'\n\t\t','*'*100,'\n')
  #print(new_links_list)
  
  for type,page_url in new_links_list:
    if type == "page":
      page_link_list.append(page_url)
    elif type == "section":
      section_link_list.append(page_url)

  #print(' _response_build -> section_link_list len:',len(section_link_list),' ===> page_link_list len:',len(page_link_list),'\n')
  if deep_lvl == 'front':
    #print('\t\t _response_build',len(page_link_list),'->',deep_lvl,'END ',url,'\n')
    return [page_link_list, section_link_list]

  else:
    #print('\t\t\t _response_build',len(page_link_list),' ->',deep_lvl,'END\n')
    return [page_link_list, []]

def bbc_clear_links(url,links_list):
  new_links_list = []
  website_new_links_list = []
  #print('bbc_clear_links START -> links_list len:',len(links_list))
  tmp_set = set()
  for link in links_list:
    link = link.replace('https://bbc.com','').replace('https://www.bbc.com','')
    link = link.replace('https://bbc.co.uk','').replace('https://www.bbc.co.uk','')
    link_list = link.split('-')
    if link_list[-1].isnumeric():
      tmp_set.add(link)
      if link not in new_links_list:
        #print(today_date,' == ',url_today_date,link)    
        new_links_list.append(link)
        website_new_links_list.append(['page',link])
    elif link.startswith('/') and link in ("/news","/sport"):
        tmp_set.add(link)
        if link not in new_links_list:
          new_links_list.append(link)
          website_new_links_list.append(['section',link])
    else:
      pass
  #print(today_date,' == ',url_today_date, link)
  #print(list(set(section_links_list)))
  #print(len(links_list),len(new_links_list))
  #print('\n\t\t -----> bbc_clear_links END -> website_new_links_list len:',len(website_new_links_list))
  #print('\nDifference: ')
  #print(tmp_set.difference(set(links_list)))
  #print('\nWebsite new links list:')
  #for p,u in website_new_links_list: print(p,u)
  
  #raise SystemExit
  return website_new_links_list

def bbc_article_scrap(url,keys_list):
  soup = get_page(url)
  print(url)
  return_json_list = []
  return_json_list.append({'url':url})
  site_container = soup.find("div", id="site-container")
  if len(site_container) > 0:
    site_container_summary = site_container.find("aside").find_all("li")
    if len(site_container_summary) > 0:
      post_title = soup.select('head title')[0].getText().replace("'","\'")
      return_json_list.append({'post_title':post_title})
      body_part = "Summary:\n"
      for s in site_container_summary:
        tmp_s = s.getText().replace("'","\'")
        body_part+= '- '+tmp_s+'\n'  
      site_container_summary = site_container.find("ol", class_="lx-stream__feed").find_all("li")
      print('site_container_summary:',len(site_container_summary))
      
      for s in site_container_summary:
        if len(s.select("article")) > 0:
          print('article time==>',s.select("article time")[0].getText())
        
      print(len(site_container_summary))
      print('site_container_summary[0].getText():\n',site_container_summary[0])
      print('site_container_summary[5].getText():\n',site_container_summary[5])
      print('site_container_summary[10].getText():\n',site_container_summary[10])
      
  for key in keys_list:
    if key == "title":
      post_title = soup.find("h1", id="main-heading")
      #print(url, post_title)
      post_title = post_title.getText().replace("'","\'")
      return_json_list.append({'post_title':post_title})
    elif key == "author":
      author_container = soup.find("span", class_="author-container")
      try:
        author_container = author_container.getText().replace("'","\'")
        return_json_list.append({'author_container':author_container})
      except:
        pass
    elif key == "date":
      post_title = soup.find("article") #, id="main-heading")
      post_date = post_title.find("time") #, class_="post-date")
      formated_post_date = datetime.strptime(post_date['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
      return_json_list.append({'post_date': str(formated_post_date)})
    elif key == "body":
      article_body = soup.find("article") #, class_="article-body")
      article_body_list = article_body.find_all("div", attrs={'data-component':'text-block'})
      article_body_str = ""
      for block in article_body_list:
        article_body_str+= block.getText()+'\n'

      return_json_list.append({'article_body':article_body_str.replace("'","\'")})
    elif key == "img":
      article_body = soup.find("article") #, class_="article-body")
      article_body_list = article_body.find_all("div", attrs={'data-component':'image-block'})
      img_json_list = []
      for block in article_body_list:
        images = block.find_all("img")
        print(len(images),block)
        if images is not None and len(images) > 0:
          #print(len(images),type(images),'++++')
          for img in images:
            try:
              src = img['data-src']
            except:
              try:
                src = img['src']
              except:
                pass
            try:
              alt = img['alt']
            except:
              alt = ""

            if src and alt:
              img_json_list.append({'src':src,'alt':alt})
            
      return_json_list.append({'images':img_json_list})
          
  return return_json_list # {'url':url, 'post_title':post_title, 'author_container':author_container, 'post_date':post_date, 'article_body':article_body} #, 'images':images}

def bbc_section_links(section_links_list):
  for url in section_links_list:
    scrapped_page = get_page(url)
    links_list = get_list_links(scrapped_page)

  return links_list

#####################################################
############### www.standard.co.uk ##################
#####################################################
def standard_response_build(url,deep_lvl,links_list):
  page_link_list = []
  section_link_list = []
  #print(links_list)
  #print('\n\t\t'+'*'*100)
  #print('\t\t  _response_build -> go to standard_clear_links(',url,', links_list len:',len(links_list),')\n\t\t','*'*100)
  new_links_list = standard_clear_links(url,links_list)
  #print('\t\t'+'*'*100,'\n\t\t  _response_build -> new_links_list len:',len(new_links_list),'\n\t\t','*'*100,'\n')
  #print(new_links_list)
  
  for type,page_url in new_links_list:
    if type == "page":
      page_link_list.append(page_url)
    elif type == "section":
      section_link_list.append(page_url)

  #print(' _response_build -> section_link_list len:',len(section_link_list),' ===> page_link_list len:',len(page_link_list),'\n')
  if deep_lvl == 'front':
    #print('\t\t _response_build',len(page_link_list),'->',deep_lvl,'END ',url,'\n')
    return [page_link_list, section_link_list]

  else:
    #print('\t\t\t _response_build',len(page_link_list),' ->',deep_lvl,'END\n')
    return [page_link_list, []]

def standard_clear_links(url,links_list):
  new_links_list = []
  website_new_links_list = []
  #print('standard_clear_links START -> links_list len:',len(links_list))
  tmp_set = set()
  for link in links_list:
    link = link.replace('https://standard.co.uk','').replace('https://www.standard.co.uk','')

    if link.endswith('.html') or '.html?' in link:
      tmp_set.add(link)
      if link not in new_links_list:
        new_links_list.append(link)
        website_new_links_list.append(['page',link])
    elif "/news/" in link or "/business/" in link:
      tmp_set.add(link)
      if link not in new_links_list:
        new_links_list.append(link)
        website_new_links_list.append(['section',link])
    elif link.startswith('#') or link.startswith('http://') or link.startswith('httpsify') or link.startswith('javascript'):
      continue
    elif "/video/" in link:
      tmp_set.add(link)
      if link not in new_links_list:
        new_links_list.append(link)
        website_new_links_list.append(['page',link])
    elif "/video" in link:
      tmp_set.add(link)
      if link not in new_links_list:
        new_links_list.append(link)
        website_new_links_list.append(['section',link])
        
    #print(today_date,' == ',url_today_date, link)
  #print(list(set(section_links_list)))
  #print(len(links_list),len(new_links_list))
  #print('standard_clear_links END -> website_new_links_list len:',len(website_new_links_list))

  #print(tmp_set.difference(set(links_list)))

  return website_new_links_list

def standard_article_scrap(url,keys_list):
  soup = get_page(url)

  return_json_list = []
  #print('return_json_list.append({\'url\':',url,'})')
  return_json_list.append({'url':url})
  for key in keys_list:
    if key == "title":
      #post_title = soup.find("h1", class_="post-title")
      #post_title = (soup.select('head title'))[-1]
      post_title = (soup.select('article header h1'))[-1]
      post_title = post_title.getText().replace("'","\'")
      return_json_list.append({'post_title':post_title})
    elif key == "author":
      #author_container = soup.find("span", class_="author-container")
      author_container = soup.find('div', class_='author')
      #author_container = author_container.replace('\n', '')
      try:
        author_container = author_container.getText(separator=' ').replace("'","\'")
        return_json_list.append({'author_container':author_container})
      except:
        pass
    elif key == "date":
      #post_date = soup.find("span", class_="post-date")
      try:
        post_date = soup.select('amp-timeago')[-1]
        post_date = post_date.attrs['datetime']
        formated_post_date = datetime.strptime(post_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        return_json_list.append({'post_date': str(formated_post_date)})
      except:
        pass
    elif key == "body":
      article = soup.find("div", id='frameInner') #.next_element
      article_body = article.find("div", id="polarArticle")
      article_body_list = []
      
      try:
        article_body = article_body.previous_element
        article_body_list_error = []

        for idx,art_part in enumerate(list(article_body)):
          art_part_str = art_part.string
          if art_part_str is None:
            try:
            #if 1 == 1:
              tmp_art_part = ""
              for s in art_part.contents:
                tmp_art_part+= str(s)
                
              if "<svg" not in tmp_art_part \
                and "<figcaption " not in tmp_art_part:
                ssoup = BeautifulSoup(tmp_art_part, 'html.parser')
                tmp_art_part = ssoup.text
                if len(tmp_art_part) > 0 \
                  and not tmp_art_part.startswith('READ MORE'):
                  #print('\n\n\t===>',len(tmp_art_part),tmp_art_part,'\n\n',art_part.contents)
                  article_body_list.append(tmp_art_part+'\n')
            #else:
            except:
              print('------ ERROR ------'.center(60))
              article_body_list_error.append(art_part)
            continue
          else:
            article_body_list.append(art_part_str+'\n')

      except:
        pass
      
      if len(article_body_list) > 0:
        return_json_list.append({'article_body':' '.join(article_body_list)})

    elif key == "img":
      article = soup.find("div", id='frameInner') #.next_element
      article_body = article.find("div", id="polarArticle")

      try:
        article_body = article_body.previous_element
        img_json_list = []
        images_article_str = ""
        for tmp_art_part in article_body:
          images_article = tmp_art_part.find_all("img")
          if len(images_article) == 0:
            images_article = tmp_art_part.find_all("amp-img")
            #images_article = soup.find("div", class_="article-body")
            if images_article is not None and len(images_article) > 0:
              if images_article_str == "":
                #print(len(images_article),type(images_article),'++++')
                for img in images_article:
                  src = img['src']
                  try:
                    alt = img['alt']
                  except:
                    alt = ""
                    #print(img)
                  img_json_list.append({'src':src,'alt':alt})

        return_json_list.append({'images':img_json_list})
        
      except:
        pass
          
  return return_json_list # {'url':url, 'post_title':post_title, 'author_container':author_container, 'post_date':post_date, 'article_body':article_body} #, 'images':images}

def standard_section_links(section_links_list):
  for url in section_links_list:
    scrapped_page = get_page(url)
    links_list = get_list_links(scrapped_page)

  return links_list

##################################################################################
############### end functions for every website ##############################
##################################################################################
