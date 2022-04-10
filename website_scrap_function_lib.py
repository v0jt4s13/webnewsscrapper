from builtins import SystemExit
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
  #print(link)
  try:
    request_object = requests.get(link)
    page = BeautifulSoup(request_object.content,features="lxml")
    
    return page
  except ConnectionError as e:
    
    return 0
  except:
    
    return 1
    
def convert_list_to_dict(l):
   i=iter(l)
   dic=dict(zip(i,i))
   return dic

def convert_urls_list_to_dict(l):
  dic = { el:'url' for el in l}
  return dic

def convert_urls_dict_to_list(d):
  ll = [val for val in d]
  return ll
 
def get_list_links(scrapped_page):
  tmp_href_list = [a.get('href') for a in scrapped_page.find_all('a', href=True)]
  for href in tmp_href_list:
    if href.startswith('http:'):
      tmp_href_list.remove(href)
      
  return tmp_href_list

def clear_links(url,deep_lvl,links_list):
  #print('clear_links START -> ',url)
  # deepl_lvl == front                deepl_lvl == section
  if url in "https://metro.co.uk" or "https://metro.co.uk" in url:
    page_link_list, section_link_list = metro_response_build(url,deep_lvl,links_list)
    
  elif url in "https://bbc.com" or "https://bbc.com" in url:
    page_link_list, section_link_list = bbc_response_build(url,deep_lvl,links_list)
    
  elif url in "https://standard.co.uk" or "https://standard.co.uk" in url:
    page_link_list, section_link_list = standard_response_build(url,deep_lvl,links_list)

  #print('clear_links KONIEC -> ',url,len(page_link_list),len(section_link_list))
  return [page_link_list, section_link_list]

def url_article_scrap(domain,url,scrap_keys_list):
  #print('\n','&'*50,'article_scrap(',domain,',',url,',',SCRAP_KEYS_LIST,')')
  if domain == "metro.co.uk":
    return metro_article_scrap(url,scrap_keys_list)
  elif domain == "standard.co.uk":
    return standard_article_scrap(url,scrap_keys_list)
  elif domain == "bbc.com":
    return bbc_article_scrap(url,scrap_keys_list)

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
  
  short_date = ""
  short_title = ""
  return_json_list = []
  return_short_json_list = []
  return_short_json_list.append({'url':url})
  #return_json_list.append({'url':url})
  for key in keys_list:
    if key == "title":
      post_title = soup.find("h1", class_="post-title")
      post_title = post_title.getText().replace("'","\'")
      return_json_list.append('post_title')
      return_json_list.append(post_title)
      return_short_json_list.append({'post_title':post_title})
      short_title = post_title
    elif key == "author":
      author_container = soup.find("span", class_="author-container")
      try:
        author_container = author_container.getText().replace("'","\'")
        return_json_list.append('author_container')
        return_json_list.append(author_container)
      except:
        pass
    elif key == "date":
      post_date = soup.find("span", class_="post-date")
      post_date = post_date.getText().replace("'","\'")
      formated_post_date = datetime.strptime(post_date,"%A %d %b %Y %I:%M %p")
      return_json_list.append('post_date')
      return_json_list.append(str(formated_post_date))
      return_short_json_list.append({'post_date': str(formated_post_date)})
      short_date = str(formated_post_date)
    elif key == "body":
      article_body = soup.find("div", class_="article-body")
      article_body = article_body.getText().replace("'","\'").replace("\n\n","")
      return_json_list.append('article_body')
      return_json_list.append(article_body)
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
            
      return_json_list.append('images')
      return_json_list.append(img_json_list)

  #print(return_short_json_list)

  #json_short = ','.join(return_short_json_list)
  #print(json_short)
  return [{'url':url,'page_title':short_title,'page_date':short_date},{'url':url,'page_details':convert_list_to_dict(return_json_list)}]
  #return [{'url':url,'page_details':return_short_json_list},{'url':url,'page_details':return_json_list}]
  #return return_json_list # {'url':url, 'post_title':post_title, 'author_container':author_container, 'post_date':post_date, 'article_body':article_body} #, 'images':images}

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
    if link_list[-1].isnumeric() and not link.startswith('/russian') \
          and not link.startswith('/mundo') and not link.startswith('/persian') \
          and not link.startswith('/portuguese'):
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

def get_image_alt_and_src(img_src_list, img_json_list, tmp_img_alt, tmp_img_data_widths, tmp_img_data_src, tmp_img_src_set):
  
  src = tmp_img_data_src
  src_set = tmp_img_src_set
  alt = tmp_img_alt

  if src_set:  
    tmp_img_src_set_list = src_set.split(',')
    if len(tmp_img_src_set_list) > 0:
      src = tmp_img_src_set_list[-2]
      #print('\t======> src_set:',src)
  else:
    width_list = tmp_img_data_widths.replace('[','').replace(']','').split(',')
    if len(width_list) > 0:
      srcl = src.split('width')
      src = str(srcl[0])[:-1]+width_list[-1]+str(srcl[1])[1:]
      #print('\t======> src:',src)

  if src and alt:
    if src not in img_src_list: 
      img_src_list.append(src)
      img_json_list.append({'src':src,'alt':alt})
     
  return img_src_list,img_json_list
  #article_part_json_list.append({'images': img_json_list})  


def extra_articles_to_json_list(s, post_title, formated_post_date):
  #print('extra_articles_to_json_list == '+post_title.getText())
  body_part = ""
  article_part_json_list = []
  img_src_list = []
  img_json_list = []
  article_part_json_list.append('post_date')
  article_part_json_list.append(str(formated_post_date))
  article_part_json_list.append('post_title')
  article_part_json_list.append(post_title.getText())
          
  tmp_tmp_post_body_wrapper = s.find("div", class_="lx-stream-post-body")
  #print('tmp_tmp_post_body_wrapper len=>',len(tmp_tmp_post_body_wrapper))
  licz = 0
  for line in tmp_tmp_post_body_wrapper:
    licz+= 1
    #print('line.select("figure img") len:',len(line.select("figure img")))
    if len(line.select("figure img")) >= 1:
      #print('figure img=>',line.select("figure img"))
      tmp_img = line.select("figure img")[0]
      if tmp_img.has_attr('data-src'):
        tmp_img_alt = tmp_img['alt']
        tmp_img_data_widths = tmp_img['data-widths']
        tmp_img_data_src = tmp_img['data-src']
        tmp_img_src_set = ""
        
        img_src_list, img_json_list = get_image_alt_and_src(img_src_list, img_json_list, tmp_img_alt, tmp_img_data_widths, tmp_img_data_src, tmp_img_src_set)
        
      elif tmp_img.has_attr('data-srcset'):
        tmp_img_alt = tmp_img['alt']
        tmp_img_data_widths = tmp_img['data-widths']
        tmp_img_data_src = ""
        tmp_img_src_set = tmp_img['data-srcset']

        img_src_list, img_json_list = get_image_alt_and_src(img_src_list, img_json_list, tmp_img_alt, tmp_img_data_widths, tmp_img_data_src, tmp_img_src_set)
    else:
      body_part+= ' '+line.getText()
    
  article_part_json_list.append('post_body')
  article_part_json_list.append(str(body_part))
  article_part_json_list.append('post_images')
  article_part_json_list.append(img_json_list)

  return convert_list_to_dict(article_part_json_list)


def bbc_article_scrap(url,keys_list):
  from datetime import date
  
  soup = get_page(url)
  short_date = ""
  short_title = ""
  #print(url)
  today = date.today()
  return_json_list = []
  return_short_json_list = []
  #return_json_list.append({'url':url})
  
  index_page_count = 0
  try:
    site_container = soup.find("div", id="site-container")
  except:
    pass
  
  try:
    index_page = soup.find("div", id="index-page")
    index_page_count = len(index_page)
  except:
    pass
  
  site_container_aside_count = 0
  try:
    site_container_aside = site_container.find("aside").find_all("li")
    site_container_aside_count = len(site_container_aside)
  except:
      pass
  
  site_container_count = 0
  try:
    site_container = soup.find("div", id="site-container")
    site_container_count = len(site_container)
  except:
      pass
  
  #print(url)
  #print('index_page_count:',index_page_count)
  #print('site_container_aside_count:',site_container_aside_count)
  #print('site_container_count:',site_container_count)
  
  if index_page_count == 0 and site_container_aside_count > 0:
    try:
      site_container_summary = site_container.find("aside").find_all("li")
    except:
      print('========================> site_container.find("aside").find_all("li")')
      #site_container_summary = site_container.find("aside").find_all("li")
      #print(url)
      site_container_summary = ""
      return []

    #if site_container_summary and len(site_container_summary) > 0:
    if site_container_aside_count > 0:
      #print('\t\t===>scrapped live report')
      head_post_title = soup.select('head title')[0].getText().replace("'","\'")
      #return_json_list.append({'live_report':1})
      return_json_list.append('live_report')
      return_json_list.append(1)
      #return_json_list.append({'post_title':head_post_title})
      return_json_list.append('post_title')
      return_json_list.append(head_post_title)
      return_short_json_list.append({'post_title':head_post_title})
      short_title = head_post_title
      
      #print("Summary:\n")
      body_part = "Summary:"
      for s in site_container_summary:
        tmp_s = s.getText().replace("'","\'")
        body_part+= '\n- '+tmp_s  
      site_container_summary = site_container.find("ol", class_="lx-stream__feed").find_all("li")
      #print('site_container_summary:',len(site_container_summary))
      if body_part != "Summary:":
        #return_json_list.append({'summary':body_part})
        return_json_list.append('summary')
        return_json_list.append(body_part)
      
      body_part = ""
      articles_json_list = []
      licz = 0
      for s in site_container_summary:
        
        if len(s.select("article")) > 0:
          
          licz+= 1
          #if licz > 10: break
    
          time_div = s.select("article time span")
          formated_post_date = today.strftime("%Y-%m-%d") + ' ' + time_div[1].getText() + ':' + today.strftime("%S.%f") #.select("time") #, class_="qa-post-auto-meta") #[0] #.getText()
          #print('\n',' *'*25,formated_post_date,' *'*25,'\n')
          #print('article time==>',s.select("article time")[0].getText())
          post_title = s.select("article header h3 span")[-1]
          if licz == 1:
            return_short_json_list.append({'post_date':formated_post_date})
            short_date = formated_post_date
            
          articles_json_list.append({'article':extra_articles_to_json_list(s, post_title, formated_post_date)})
          

    #return_json_list.append({'articles':articles_json_list})
    return_json_list.append('articles')
    return_json_list.append(articles_json_list)
      
  elif index_page_count == 0:    
    #print('\t\t===>scrapped website')
    for key in keys_list:
      if key == "title":
        try:
          post_title = soup.find("h1", id="main-heading")
          #print(url, post_title)
          post_title = post_title.getText().replace("'","\'")
          if "Page cannot be found" in post_title:
            return []  
        except AttributeError as e:
          return []
        except:
          print(post_title)
          
        #return_json_list.append({'post_title':post_title})
        return_json_list.append('post_title')
        return_json_list.append(post_title)
        return_short_json_list.append({'post_title':post_title})
        short_title = post_title
      elif key == "author":
        author_container = soup.find("span", class_="author-container")
        try:
          author_container = author_container.getText().replace("'","\'")
          #return_json_list.append({'author_container':author_container})
          return_json_list.append('author_container')
          return_json_list.append(author_container)
        except:
          pass
      elif key == "date":
        #print('Line:501 ==> post_title==>',post_title)
        post_title = soup.find("article") #, id="main-heading")
        post_date = post_title.find("time") #, class_="post-date")
        formated_post_date = datetime.strptime(post_date['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
        #return_json_list.append({'post_date': str(formated_post_date)})
        return_json_list.append('post_date')
        return_json_list.append(str(formated_post_date))
        return_short_json_list.append({'post_date': str(formated_post_date)})
        short_date = str(formated_post_date)
      elif key == "body":
        article_body = soup.find("article") #, class_="article-body")
        article_body_list = article_body.find_all("div", attrs={'data-component':'text-block'})
        article_body_str = ""
        for block in article_body_list:
          article_body_str+= block.getText()+'\n'

        #return_json_list.append({'article_body':article_body_str.replace("'","\'")})
        return_json_list.append('article_body')
        return_json_list.append(article_body_str.replace("'","\'"))
      elif key == "img":
        article_body = soup.find("article") #, class_="article-body")
        article_body_list = article_body.find_all("div", attrs={'data-component':'image-block'})
        img_json_list = []
        for block in article_body_list:
          images = block.find_all("img")
          #print(len(images),block)
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
              
        #return_json_list.append({'images':img_json_list})
        return_json_list.append('images')
        return_json_list.append(img_json_list)
  else:
    pass
  
  if len(return_json_list) > 0:
    #print({'url':url,'page_title':short_title,'page_date':short_date})
    #print({'url':url,'page_details':convert_list_to_dict(return_json_list)})
  
    #input()
    #raise SystemExit
  
    return [{'url':url,'page_title':short_title,'page_date':short_date},{'url':url,'page_details':convert_list_to_dict(return_json_list)}]
    #return [{'url':url,'page_details':return_short_json_list},{'url':url,'page_details':return_json_list}]
    #return return_page_json_list # {'url':url, 'post_title':post_title, 'author_container':author_container, 'post_date':post_date, 'article_body':article_body} #, 'images':images}
  else:
    return []

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
  if not url.startswith('https'):
    url = 'https://standard.co.uk'+url
  soup = get_page(url)

  short_date = ""
  short_title = ""
  return_json_list = []
  return_short_json_list = []
  #print('return_json_list.append({\'url\':',url,'})')
  #return_json_list.append({'url':url})
  for key in keys_list:
    if key == "title":
      #post_title = soup.find("h1", class_="post-title")
      #post_title = (soup.select('head title'))[-1]
      post_title = (soup.select('article header h1'))[-1]
      post_title = post_title.getText().replace("'","\'")
      return_json_list.append('post_title')
      return_json_list.append(post_title)
      return_short_json_list.append({'post_title':post_title})
      short_title = post_title

    elif key == "author":
      #author_container = soup.find("span", class_="author-container")
      author_container = soup.find('div', class_='author')
      #author_container = author_container.replace('\n', '')
      try:
        author_container = author_container.getText(separator=' ').replace("'","\'")
        return_json_list.append('author_container')
        return_json_list.append(author_container)
      except:
        pass

    elif key == "date":
      #post_date = soup.find("span", class_="post-date")
      try:
        post_date = soup.select('amp-timeago')[-1]
        post_date = post_date.attrs['datetime']
        formated_post_date = datetime.strptime(post_date, '%Y-%m-%dT%H:%M:%S.%fZ')
        return_json_list.append('post_date')
        return_json_list.append(str(formated_post_date))
        return_short_json_list.append({'post_date': str(formated_post_date)})
        short_date = str(formated_post_date)
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
        return_json_list.append('article_body')
        return_json_list.append(' '.join(article_body_list))

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

        return_json_list.append('images')
        return_json_list.append(img_json_list)
        
      except:
        pass
  
  return [{'url':url,'page_title':short_title,'page_date':short_date},{'url':url,'page_details':convert_list_to_dict(return_json_list)}]
  #return [{'url':url,'page_details':return_short_json_list},{'url':url,'page_details':return_json_list}]
  #return return_json_list # {'url':url, 'post_title':post_title, 'author_container':author_container, 'post_date':post_date, 'article_body':article_body} #, 'images':images}

def standard_section_links(section_links_list):
  for url in section_links_list:
    scrapped_page = get_page(url)
    links_list = get_list_links(scrapped_page)

  return links_list

##################################################################################
############### end functions for every website ##############################
##################################################################################
