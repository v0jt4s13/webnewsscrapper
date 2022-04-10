#from threading import enumerate
from logging import exception
from bs4 import BeautifulSoup
from rich import print
import json
from secret import access_key, secret_access_key
import boto3
import os
from rich.console import Console
from rich.traceback import install
from website_scrap_function_lib import calculate_execution_time, get_page, get_list_links, clear_links, url_article_scrap, convert_urls_list_to_dict, convert_urls_dict_to_list
from datetime import datetime

install()
console = Console()



def article_scrap(domain,url):
  #print('\n','&'*50,'url_article_scrap(',domain,',',url,',',SCRAP_KEYS_LIST,')')
  return url_article_scrap(domain,url,SCRAP_KEYS_LIST)




def prep_url(d,u):
  url = d+u
  return url #url[:20]+'(...)'+url[-10:]

def remove_duplicates_from_dict(json_dict):
  unique_dict = [k for j, k in enumerate(json_dict) if k not in json_dict[j + 1:]]
  return unique_dict






def prepare_error_urls_list_from_file():
  
  #print('prepare_error_urls_list_from_file prepare_error_urls_list_from_file') 
  file_name = 'errorwebsite.json'
  if os.path.exists('json/'+file_name):
    with open('json/'+file_name, 'r') as file:
      try: 
        read_dict = json.load(file)
        return convert_urls_dict_to_list(read_dict)
      except:
        return []
      
  else:
    return []

def save_error_urls_dict_to_file(dict):
  
  print('prepare_error_urls_list_from_file():',prepare_error_urls_list_from_file())
  print('save_error_urls_dict_to_file:',type(dict),len(dict),dict)
  
  file_name = 'errorwebsite.json'
  path = 'json/'
  try:
    with open(path+file_name, 'w') as file:
      json.dump(dict, file)
    return True
  except:
    return False

def save_dict_to_file(file_name,dicts_list,local_path='json/'):
  try:
    print(local_path)
    print(file_name)
    print(len(dicts_list))
    with open(local_path+file_name, 'w') as file:
      json.dump(dicts_list, file)

    return True

  except:
    return False
  





def prepare_articles_in_domain_json(url_domain,domain_save_file_name,get=""):
  
  #print('&+&+&+&+&+&+& prepare_articles_in_domain_json 0:',url_domain) 
  url_domain = get_domain_from_url(url_domain)
  domain = 'https://'+url_domain
  if os.path.exists('json/'+domain_save_file_name):
    with open('json/'+domain_save_file_name, 'r') as file:
      try: 
        read_dict = json.load(file)
        
        #print('read_dict:',type(read_dict),len(read_dict),read_dict.keys()) #,read_dict.get('websites')) #[0]['page'])
        #input()
        
        websites_dict = read_dict.get('websites')

        if get == 'articles':
          #print('get articles =====>',type(websites_dict),len(websites_dict))
          urls_list = websites_dict[0]['urls_list']
          #print('type(urls_list):',type(urls_list),len(urls_list))
          return urls_list
          
        if get == 'full':
          return websites_dict
          
        website_nr = -1
        for pidx,tmp_page in enumerate(websites_dict):
          if domain == tmp_page['website']['page']: #['website']['page']:
            website_nr = pidx
            break  
        
        if website_nr >= 0:
          website_page_urls_list = read_dict.get('websites')[website_nr]['website']['urls_list']
          website_urls_list = []
          for url in website_page_urls_list:
            url = url['url']
            website_urls_list.append(url[:20]+'(...)'+url[-10:])
        return website_urls_list
      except: 
        return []
  else:
    return []


def update_articles_list_in_domain_file(domain,domain_save_file_name,url_json_list):
  #print('url_json_list => Przyszlo:',len(url_json_list),type(url_json_list))
  live_articles_to_save_list = []
  articles_to_save_list = []
  articles_to_remove_url_list = []
  for article_details in url_json_list:
    try:
      #print('type(article_details), len(article_details):',type(article_details))
      #print(len(article_details))
      #print(article_details)
      #['page_details'][0]['post_title'])
      #input()
      
      post_title = article_details.get('page_details').get('post_title')
      
      post_date = article_details.get('page_details').get('post_title')
      article_body = article_details.get('page_details').get('article_body')
      images = article_details.get('page_details').get('images')
      page_details_json = {'post_title': post_title, 'post_date': post_date, 'article_body': article_body, 'images': images}
      
      live_report = 0
      article_body_len = len(article_details.get('page_details').get('article_body'))
      #print(article_body_len,type(article_details.get('page_details'))) #article_details['page_details'].keys())
      if article_body_len > 10:
        articles_to_save_list.append(article_details)
      else:
        articles_to_remove_url_list.append(article_details.get('url'))
    except:
      #print(type(article_details), len(article_details))
      #print(article_details.get('page_details').get('live_report'))
      live_post_title = article_details.get('page_details').get('post_title')

      live_post_articles = article_details.get('page_details').get('articles').get('article')
      post_date = live_post_articles.get('post_date')
      post_title = live_post_articles.get('post_title')
      post_body = live_post_articles.get('post_body')
      post_images = live_post_articles.get('post_images')
      page_details_json = {'post_date': post_date, 'post_title': post_title, 'post_body': post_body, 'post_images': post_images}

      live_report = 1
      live_articles_to_save_list = article_details.get('page_details').get('articles')

    #input()
  
  #print('articles_to_remove_url_list:',len(articles_to_remove_url_list),type(articles_to_remove_url_list))
  #print('articles_to_save_list:',len(articles_to_save_list),type(articles_to_save_list))
  #print('live_articles_to_save_list:',len(live_articles_to_save_list),type(live_articles_to_save_list))
  
  try:

    #print('\t\t\t\t==> Aktualizuje plik ',domain_save_file_name)
    domain_url = 'https://'+domain
    
    from_domain_file_articles_list = prepare_articles_in_domain_json(domain,domain_save_file_name,get='articles')
    
    #print('from_domain_file_articles_list:',type(from_domain_file_articles_list),len(from_domain_file_articles_list))
    #print('articles_to_save_list:',type(articles_to_save_list),len(articles_to_save_list))
    #input()

    articles_to_save_list.extend(from_domain_file_articles_list)
    #print('extend articles_to_save_list:',type(articles_to_save_list),len(articles_to_save_list))
    #input()
    
    websites_json_list = []
    websites_json_list.append({'page':domain,'urls_list':articles_to_save_list})
    #print('websites_json_list:',type(websites_json_list),len(websites_json_list))
    #print(websites_json_list)
    #input()
    
    websites_list_dict = {'websites': websites_json_list}
    #print('websites_list_dict:',type(websites_list_dict),len(websites_list_dict))
    
    #print('websites_list_dict:',websites_list_dict)

    if not save_dict_to_file(domain_save_file_name,websites_list_dict):
      print('saved fail')
      return False
    else:
      print('saved ok')
    
    #live_articles_to_save_list = []
    #print('articles_to_remove_url_list len:',len(articles_to_remove_url_list))
    if articles_to_remove_url_list:
      print('articles_to_remove_url_list:',type(articles_to_remove_url_list),len(articles_to_remove_url_list),articles_to_remove_url_list)
      input()
      save_error_urls_dict_to_file(articles_to_remove_url_list)
      
      #if upload_files_to_s3(error_url_list_file):
      #  print('\t\t ** >>>>> Plik:',error_url_list_file,'zapisany poprawnie na AWS S3')
      #else:
      #  print('\t\t ** >>>>> Wystąpił błąd podczas zapisu pliku:',error_url_list_file,'na AWS S3')
        

    return True
  except:
    return False    


def _from_domaindict(domain,return_field='sections'):
  try:
    d_len = len(DOMAINS_DICT['domains'])
  except:
    DOMAINS_DICT = {"domains": [
      {"domain": "bbc.com", "sections": [{"/news","/news/coronavirus","/news/uk"}]},
      {"domain": "metro.co.uk", "sections": [{"/news"}]}, #{"/news/","/metro/"}
      {"domain": "standard.co.uk", "sections": [{"/news/london","/news/uk","/news/mayor","/news/transport"}]} #{"/news/","/standard/"}
    ]}
    d_len = len(DOMAINS_DICT['domains'])
  
  xx = 0
  sections_list = []
  while xx < d_len:
    if DOMAINS_DICT['domains'][xx]['domain'] == domain:
      if len(DOMAINS_DICT['domains'][xx][return_field]) > 0:
        sections_list = list(DOMAINS_DICT['domains'][xx][return_field][0])
      break
    xx+= 1
  
  return sections_list


def get_domain_from_url(url):
  if url.startswith('http'):
    tmp_list = url.split('/')
    domain = tmp_list[2].replace('www.','')
  else:
    tmp_list = url.split('/')
    domain = tmp_list[0].replace('www.','')
  
  return domain


def get_list_used_urls(domain_save_file_name):
  
  if os.path.exists('json/'+domain_save_file_name):
    with open('json/'+domain_save_file_name, 'r') as file:
      read_dict = json.load(file)
      websites_dict = read_dict.get('websites')
      urls_list = websites_dict[0].get('urls_list')
      print(type(urls_list),len(urls_list))
      l = []
      for url in urls_list: 
        l.append(url.get('url'))
      return l
      
  else:
    return []
    

def get_urls_from_page(url,deep_lvl,page_links_list=[]):
  
  if deep_lvl == 'front':
    sect_links_list = []
    scrapped_page = get_page(url)
    if len(scrapped_page) > 0:
      links_list = get_list_links(scrapped_page)
  
    if len(links_list) > 0:
      #print('\t\t ** Funkcje: get_page i get_list_links zwrocily: %i linków do obróbki.' %len(links_list))
      #print('\n'.join(links_list))
      clear_links_output = clear_links(url,deep_lvl,links_list)
      
      page_links_list = clear_links_output[0]
      sect_links_list = clear_links_output[1]
      
      #print('get_urls_from_page -> page_links_list:',len(page_links_list),' sect_links_list:',len(sect_links_list),sect_links_list)
      print('\t\t ** \n\t\t ** Linki z głównej strony zebrane:',len(page_links_list),' w tym linków do działów: %i \n' %len(sect_links_list))
      
      #for idx,w in enumerate(page_links_list):
      #  print(idx,w)
      
    return [page_links_list, sect_links_list]

  else:
    # ##### section ######
    
    scrapped_page = get_page(url)
    if len(scrapped_page) > 0:
      links_list = get_list_links(scrapped_page)
  
    if len(links_list) > 0:
      tmp_page_links_list = page_links_list+links_list
      clear_links_output = clear_links(url,deep_lvl,tmp_page_links_list)
      page_links_list = clear_links_output[0]
    return page_links_list 
    


def get_url_list(url):
  
  time_point_list = calculate_execution_time()
  if url == "":
    urls_list = DOMAINS_LIST
  else:
    urls_list = []
    urls_list.append(url)
  print('\n\n\t\t * Rozpoczęcie przetwarzania listy domen:\n\t\t *',urls_list,'\n\t\t *',SCRAP_KEYS_LIST)
  
  website_json_list = []
  json_output_list = []
  
  errorwebsite_save_file_name = 'errorwebsite.json'
  path = 'json/'
  
  url_licz = 0
  for url in urls_list:
    url_licz+= 1
    domain = get_domain_from_url(url)
    url = 'https://'+url
    domain_url = 'https://'+domain

    ############################### used_urls_list from domain-full.json
    used_urls_list = []
    domain_save_file_name = domain+'-full.json'
    used_urls_list = get_list_used_urls(domain)
    print('\n\t\t * from file:'+domain_save_file_name+' ==> used_urls_list \t==>',len(used_urls_list),used_urls_list)

    ############################### error_page_urls_list from errorwebsite.text
    try:
      error_page_list = prepare_error_urls_list_from_file()
      print('error_page_list:',type(error_page_list),len(error_page_list))
      #input()
      # #error_page_list = download_file_from_s3(errorwebsite_save_file_name).decode("utf-8")
      # tmp_list = []
      # if type(error_page_list) == str: error_page_list = error_page_list.split('\n')
      # for url in error_page_list:
      #   tmp_list.append(prep_url(domain_url,url)) #url[:20]+'(...)'+url[-10:])
      # error_page_list = tmp_list
      # print('\n '+errorwebsite_save_file_name+' \t\t==> error_page_list \t==>',len(error_page_list),error_page_list)
    except:
      error_page_list = []
      
    dont_scrap_url_list = used_urls_list+error_page_list
    #print('\n\t\t * used urls list count ==>dont_scrap_url_list:',len(dont_scrap_url_list))
    #input()
    
    ############################### get_urls_from_page - pobranie linkow ze strony
    tmp_new_urls_list = get_urls_from_page(domain_url,'front')
    # zwrocone linki do stron z artykulami oraz do stron kategorii
    page_links_list = tmp_new_urls_list[0]
    sect_links_list = tmp_new_urls_list[1]
    tmp_to_scrap_urls_list = [prep_url(domain_url,url) for url in page_links_list]

    # #print(tmp_to_scrap_urls_list)
    # print('\t\t\t\t==> Usuwanie duplikatów z nowych linków: przed:',len(tmp_to_scrap_urls_list), end=' po: ')
    # ############################### usuwanie duplikatow z nowej listy url
    # [tmp_to_scrap_urls_list.remove(l) for l in dont_scrap_url_list if l in tmp_to_scrap_urls_list]
    # print(len(tmp_to_scrap_urls_list))
    # to_scrap_urls_list = tmp_to_scrap_urls_list
    # #print(dont_scrap_url_list)
    #input_pause()

    if SECTION:
      #tmp_to_scrap_urls_list = []
      sect_links_list = _from_domaindict(domain,return_field='sections')
      for section_url in sect_links_list:
        # Przegladanie stron kategorii i pobranie z nich linkow do artykułów
        #print('!'*50,'Zabieramy',len(page_links_list),' stron.','!'*50)
        tmp_links_list = get_urls_from_page(url+''+section_url,'section') #,page_links_list)
        
        for tmpp_link in tmp_links_list:
          if tmpp_link.startswith('http'):
            print('0. tmpp_link.startwith:',tmpp_link)
            input()
            
        #print(tmp_links_list)
        if len(tmp_links_list) > 0:
          #print('!'*50,'Kolejne zwrócone',len(tmp_links_list),' stron z ',len(page_links_list),'.','!'*50)
          #page_links_list = tmp_links_list
          tmp_to_scrap_urls_list.extend(tmp_links_list)
        #input_pause()  
        # zwrocone linki do stron z artykulami

    print('\t\t\t\t==> Usuwanie duplikatów z nowych linków: przed:',len(tmp_to_scrap_urls_list), end=' po: ')
    ############################### usuwanie duplikatow z nowej listy url
    [tmp_to_scrap_urls_list.remove(l) for l in dont_scrap_url_list if l in tmp_to_scrap_urls_list]
    print(len(tmp_to_scrap_urls_list))
    #print(dont_scrap_url_list)
    to_scrap_urls_list = tmp_to_scrap_urls_list
    #input_pause()
  
    time_point_list = calculate_execution_time(time_point_list)
    print('\t\t ** Statystyki wstępne. Czas przygotowania:',calculate_execution_time(time_point_list,end=1))
    to_scrap_urls_list_len = len(to_scrap_urls_list)      
      
    finally_links_list = list(set(to_scrap_urls_list))
    finally_links_len = len(finally_links_list)
    print('\t\t ** Ilość wszystkich przefiltrowanych linków:',to_scrap_urls_list_len)
    print('\t\t ** Ilość niepowtarzających się linków:',finally_links_len)
    print('\t\t ** \n\t\t ** \n\t\t ** Scrapujemy strony ....')

      
    ############################### scrapowanie stron z listy url -> new_urls_list
    print('\n\n\t\t\t\t','* '*40,'\n\t\t\t\t  * * * * * * * * *  Koniec przygotowywania linkow do obrobki * * * * * * * * * \n\t\t\t\t','* '*40,'\n')
    print('\t\t\t\t==> Scrapowanie stron - lista 3pierwsze i 3ostatnie z',len(finally_links_list))
    
    url_json_list = []
    for lidx,link in enumerate(finally_links_list):
      link = link.replace('https://'+domain,'')
      if link.startswith('http'):
        print('1. link.startwith:',link)
        input()
        
      scrapped_page_part_list = []
      if lidx < 3 or lidx > len(finally_links_list)-3:
        print('\t\t\t\t',lidx,'scrap:',link)
        list_scrapped_page_part_list = article_scrap(domain,link)
        #input('po article_scrap')
        #print('list_scrapped_page_part_list:',list_scrapped_page_part_list)
        #input()
        
        if list_scrapped_page_part_list in (0,1):
          dont_scrap_url_list.append(prep_url(domain_url,link))
          print(url,'Scrapped error:',list_scrapped_page_part_list)
          break
        
        scrapped_page_body_str = ""
        try:
          scrapped_page_part_list = list_scrapped_page_part_list[1]
          scrapped_page_body_str = scrapped_page_part_list.get('page_details').get('article_body')
          #print('scrapped_page_part_list:',scrapped_page_part_list)
          #print('scrapped_page_part_list:',scrapped_page_part_list.get('page_details').get('article_body'))
          #'page_details': {'post_title': "'Devil wheel' rider: It makes me happy", 'post_date': '2017-06-21 23:14:12', 'article_body'
          #input()
          
        except:
          #print('\t\t\t\tlidx:',lidx,'==>link:',link)
          if int(lidx) >= 330:
            #print(type(list_scrapped_page_part_list),len(list_scrapped_page_part_list))
            scrapped_page_part_list = list_scrapped_page_part_list[1]
            scrapped_page_body_str = scrapped_page_part_list.get('page_details').get('article_body')
            #print('*****************************************************************************')
          #print('\t\t\t\tError:',list_scrapped_page_part_list)
          dont_scrap_url_list.append(prep_url(domain_url,link))
        
        
        if type(scrapped_page_body_str) is None or len(scrapped_page_body_str) < 10:
          try:
            #print('\t\t\t\tadd to error_page:',len(dont_scrap_url_list))
            #print('\t\t\t\tscrapped_page_part_list.get(\'url\'):',type(scrapped_page_part_list))
            #print('\t\t\t\tscrapped_page_part_list:',scrapped_page_part_list)
            #print('\t\t\t\tlist_scrapped_page_part_list:',list_scrapped_page_part_list)
            #print('\t\t\t\t',len(scrapped_page_part_list.get('url')),scrapped_page_part_list.get('url'))
            #input()
            scrapped_page_url = scrapped_page_part_list.get('url')
          except:
            scrapped_page_url = link
            
          dont_scrap_url_list.append(prep_url(domain_url,scrapped_page_url))
          #print('\t\t\t\tafter added to error_page:',len(dont_scrap_url_list))
          #input()
                
        else:
          url_json_list.append(scrapped_page_part_list)
        
        if EARLY_BREAK:
          if lidx > 10: 
            break
    
    if len(url_json_list) > 0:
      website_json_list.append({'page':url,'urls_list': url_json_list})

      #print(' ===================> url_json_list <===================')
      #print(website_json_list)

      print('\t\t ** %i przetworzonych linków\n' %lidx)

    #input()
    #raise SystemExit
      
    print('\t\t\t\t==> Scrapowanie - KONIEC ',lidx)
    ############################### zapis zescrapowanych stron do pliku domain_save_file_name


    
    tmp_link = []
    for tmpp_link in dont_scrap_url_list:
      tmpp_link = tmpp_link.replace('https://'+domain,'')
      if tmpp_link.startswith('http'):
        print('2. tmpp_link.startwith:',tmpp_link)
        input()
      tmp_link.append(tmpp_link)
    dont_scrap_url_list = tmp_link
      
    #print('dont_scrap_url_list:',type(dont_scrap_url_list),len(dont_scrap_url_list),dont_scrap_url_list)
    dont_scrap_url_list = remove_duplicates_from_dict(dont_scrap_url_list)
    #print('dont_scrap_url_list:',type(dont_scrap_url_list),len(dont_scrap_url_list),dont_scrap_url_list)
    #input_pause
    dont_scrap_url_dict = convert_urls_list_to_dict(dont_scrap_url_list)
    
    print('dont_scrap_url_dict:',len(dont_scrap_url_dict))
    save_error_urls_dict_to_file_resp = save_error_urls_dict_to_file(dont_scrap_url_dict)
    if save_error_urls_dict_to_file_resp:
      print('\t\t\t\t==> Save errorwebsite.json - OK ')
    else:
      print('\t\t\t\t==> Save errorwebsite.json - fail ')
    
    domain_save_file_name = domain+'-full.json'
    if EARLY_BREAK: domain_save_file_name = domain+'-full.json'
    
    print('url_json_list:',len(url_json_list))
    save_article_file_resp = update_articles_list_in_domain_file(domain,domain_save_file_name,url_json_list)

    if save_article_file_resp:
      print('\t\t\t\t==> Update domain_file - OK ')
      
    else:
      print('\t\t\t\t==> Update domain_file - Fail ')
          
    
    input()
    raise SystemExit
    #input('dalej')
    website_url_list_json = dict()
    website_url_list_json = {'websites': website_json_list}

    #print('get_url_list -> url_list_json len:',len(website_url_list_json.keys()))
    #print(website_url_list_json)
    #print('*'*50)
    
    
    
    #print('Zapisuje plik ',domain_save_file_name)
    
    # dopisywanie do pliku json - filelock ????
    #with open(path+domain_save_file_name, 'w') as file:
    #  json.dump(website_url_list_json, file)
    
    
    print('\t\t ** >>>>> Utworzono plik:',domain_save_file_name,'. Całkowity czas:',calculate_execution_time(time_point_list,end=1))
    if upload_files_to_s3(domain_save_file_name):
      print('\t\t ** >>>>> Plik:',domain_save_file_name,'zapisany poprawnie na AWS S3')
    else:
      print('\t\t ** >>>>> Wystąpił błąd podczas zapisu pliku:',domain_save_file_name,'na AWS S3')

    website_url_list_json.clear()
    website_json_list.clear()
    
    json_output_list.append({'website':url, 'filename':save_file_name, 'url_count':finally_links_len})
    


def start_settings():
  #########################################################
  #########################################################
  ######## ustawienia #####################################
  #########################################################
  #########################################################
  global INPUT_STR, SCRAP_KEYS_LIST, DOMAINS_DICT, DOMAINS_LIST, ACTIVE_DOMAIN_NR
  INPUT_STR = '-'*15+'>>> dalej >>>'+'-'*15+''
  keys_list = []
  active_keys = 5 # max=5
  tmp_keys_list = ['title','author','date','body','img']
  idx = 0
  for key in tmp_keys_list:
    if idx < active_keys:
      keys_list.append(key)
    idx+= 1
  # lista kluczy dla wyjściowego pliku .json z danymi
  SCRAP_KEYS_LIST = keys_list
  # lista domen do scrapowania
  #DOMAINS_LIST = ["metro.co.uk", "standard.co.uk", "bbc.com"]
  DOMAINS_DICT = {"domains": [
    {"domain": "bbc.com", "sections": [{"/news","/news/coronavirus","/news/uk"}]},
    {"domain": "metro.co.uk", "sections": [{"/news"}]},
    {"domain": "standard.co.uk", "sections": [{"/news/london","/news/uk","/news/mayor","/news/transport"}]}
  ]}
  d_len = len(DOMAINS_DICT['domains'])
  xx = 0
  domains_list = []
  while xx < d_len:
    domains_list.append(DOMAINS_DICT['domains'][xx]['domain'])
    xx+= 1
  DOMAINS_LIST = domains_list
  
  # test settings toolbox
  testenv_on = False
  #testenv_on = turn_on_testing_toolbox('bbc.com',test_nr=1,active_keys=4,input_on=0,section=0)
  #testenv_on = turn_on_testing_toolbox('metro.co.uk',test_nr=1,active_keys=4,input_on=0,section=0)
  #testenv_on = turn_on_testing_toolbox('standard.co.uk',test_nr=9,active_keys=4,input_on=0,section=0)
  
  if not testenv_on:
    global INPUT_ON, EARLY_BREAK, SECTION, TEST, ACTIVE_DOMAIN_NR, S3_BUCKET_NAME, S3_PATH
    ######################################################################################
    INPUT_ON    = False   # True - zatrzymuje proces po wykonaniu partii kodu 
                          # False - leci bez opamiętania
    EARLY_BREAK = True   # True - zakoncz skanowanie po przetworzeniu 10ciu linków
                          # False - pełne scrapowanie

    TEST        = 0       # 0 - skrypt uruchamiany na wszystkie domeny z tablicy; 
                          # 1 - dla wybranej domeny; 
                          # 9 - scrapowanie wybranej strony w domenie
    ACTIVE_DOMAIN_NR = 0  # dla test==9 wybór z tablicy domeny do skrapowania

    SECTION     = 1       # 0 - scrapowanie tylko strony głównej
                          # 1 - scrapowanie dodatkowo stron sekcji/działów
  
  # ustawienia dla S3
  S3_BUCKET_NAME = "xd-test-bucket-for-lambda"
  S3_PATH = "website-scrap-json/"
  #########################################################
  #########################################################
  ######## ustawienia #####################################
  #########################################################
  #########################################################

def main():    
  global TEST, SCRAP_KEYS_LIST, INPUT_ON, SECTION, EARLY_BREAK, ACTIVE_DOMAIN_NR, DOMAINS_DICT, DOMAINS_LIST
  
  start_settings()

  if TEST == 0:

    scrap_resp = get_url_list(url="")
    print('\n\n *'+' *'*60)
    tmp_str = 'TEST=0 => '
    print(' *',tmp_str.center(120))
    #print(' *',url)
    print(' *\n *'+' *'*60)
    print(scrap_resp)
    print('\n\n')

  elif TEST == 1:
    
    # get_url_list(url="https://standard.co.uk")
    url = DOMAINS_DICT['domains'][ACTIVE_DOMAIN_NR]['domain'] #DOMAINS_DICT[ACTIVE_DOMAIN_NR]
    #print('url=',url)
    domain = get_domain_from_url(url)
    scrap_resp = get_url_list(url)
    print('\n\n *'+' *'*60)
    tmp_str = 'TEST=1 => '+domain
    print(' *',tmp_str.center(120))
    print(' *',url)
    print(' *\n *'+' *'*60)
    print(scrap_resp)
    print('\n\n')
    
  elif TEST == 9:
    
    print('ACTIVE_DOMAIN_NR:',ACTIVE_DOMAIN_NR)
    if ACTIVE_DOMAIN_NR == 0:
      url = 'https://www.bbc.com/news/entertainment-arts-60952358'
      url = 'https://bbc.com/news/business-15521824'
    elif ACTIVE_DOMAIN_NR == 1:
      #url = 'https://metro.co.uk/2022/03/29/jada-pinkett-smith-speaks-out-on-oscars-drama-between-will-smith-and-chris-rock-16366198/'
      url = 'https://metro.co.uk/2022/03/29/queen-elizabeth-arrives-at-memorial-service-for-prince-philip-16362851/'
    elif ACTIVE_DOMAIN_NR == 2:
      #url = 'https://www.standard.co.uk/news/world/vladimir-putin-defeat-volodymyr-zelensky-ukraine-russia-war-b990869.html'
      #url = 'https://www.standard.co.uk/news/world/joe-biden-russia-ukraine-invasion-latest-regime-change-vladimir-putin-b990815.html'
      #url = 'https://www.standard.co.uk/news/world/donald-trump-likely-committed-crime-joe-biden-election-victory-us-capitol-commitee-b991038.html'
      url = 'https://standard.co.uk/news/london/naked-man-greggs-crouch-end-b991747.html'

    domain = get_domain_from_url(url)
    scrap_resp = article_scrap(domain,url)
    print('\n\n *'+' *'*60)
    tmp_str = 'TEST=9 => '+domain
    print(' *',tmp_str.center(120))
    print(' *',url)
    print(' *\n *'+' *'*60)
    print(scrap_resp)
    print('\n\n')

if __name__ == "__main__":
  
  try:
    #qq = download_file_from_s3('errorwebsite.text').decode("utf-8")
    #return bytearray(list(f.getvalue())).decode("utf-8")
    #qq1 = qq
    #print(type(qq1),qq1)

    main()
  except:
    console.print_exception()
    
