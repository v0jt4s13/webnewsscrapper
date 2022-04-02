from logging import exception
from bs4 import BeautifulSoup
from website_scrap_function_lib import *
from rich import print
import json
from secret import access_key, secret_access_key
import boto3
import os

def article_scrap(domain,url):
  
  #print('\n','&'*50,'article_scrap(',domain,',',url,',',SCRAP_KEYS_LIST,')')
  if domain == "metro.co.uk":
    return metro_article_scrap(url,SCRAP_KEYS_LIST)
  elif domain == "standard.co.uk":
    return standard_article_scrap(url,SCRAP_KEYS_LIST)
  elif domain == "bbc.com":
    return bbc_article_scrap(url,SCRAP_KEYS_LIST)
  

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


def get_urls_from_page(url,deep_lvl,page_links_list=[]):
  
  if deep_lvl == 'front':
    sect_links_list = []
    scrapped_page = get_page(url)
    if len(scrapped_page) > 0:
      links_list = get_list_links(scrapped_page)
  
    if len(links_list) > 0:
      print('\t\t ** Funkcje: get_page i get_list_links zwrocily: %i linków do obróbki.' %len(links_list))
      #print('\n'.join(links_list))
      clear_links_output = clear_links(url,deep_lvl,links_list)
      
      page_links_list = clear_links_output[0]
      sect_links_list = clear_links_output[1]
      
      #print('get_urls_from_page -> page_links_list:',len(page_links_list),' sect_links_list:',len(sect_links_list),sect_links_list)
      print('\t\t ** \n\t\t ** Linki z głównej strony zebrane:',len(page_links_list),' w tym linków do działów: %i \n' %len(sect_links_list))
    
    return [page_links_list, sect_links_list]

  else:
    # ##### section ######
    
    scrapped_page = get_page(url)
    if len(scrapped_page) > 0:
      links_list = get_list_links(scrapped_page)
  
    if len(links_list) > 0:
      tmp_page_links_list = page_links_list+links_list
      print(url,' ===> get_page i get_list_links zwrocil links_list:',len(links_list),'+',len(page_links_list),'=',len(tmp_page_links_list))
      #print('\n'.join(links_list))
      clear_links_output = clear_links(url,deep_lvl,tmp_page_links_list)
      
      page_links_list = clear_links_output[0]
      #sect_links_list = clear_links_output[1]
      
      print('get_urls_from_page -> page_links_list:',len(page_links_list))
    
    return page_links_list 
    

def get_domain_from_url(url):
  if url.startswith('http'):
    tmp_list = url.split('/')
    domain = tmp_list[2].replace('www.','')
  else:
    tmp_list = url.split('/')
    domain = tmp_list[0].replace('www.','')
  
  return domain

def get_url_list(url):
  #{'websites': [
    # {'page': 'https://newspage-url', 
    # 'urls_list': [
      # {'url': 'https://newspage-url/page', 
      # 'post_title': 'Post title', 
      # 'author_container': 'Article author', 
      # 'post_date': 'Friday 25 Mar 2022 10:15 am', 
      # 'article_body': 'Article body', 
      # 'images': [images_list]
      # }
    # ]}
  # ]}
  time_point_list = calculate_execution_time()
 
  if url == "":
    urls_list = ACTIVE_DOMAINS_LIST
  else:
    urls_list = []
    urls_list.append(url)
  
  print('\n\n\t\t * Rozpoczęcie przetwarzania listy domen:', end='\n\t\t * ')
  print(urls_list)

  website_json_list = []
  json_output_list = []
  
  for url in urls_list:
    url = 'https://'+url
    domain = get_domain_from_url(url)
    print('\n\n')
    print('\t\t','*'*50)
    print('\t\t **','\n\t\t ** Domena:',domain,'\n\t\t **')
    print('\t\t','*'*50)
    # Pierwsze pobranie linkow ze strony glownej
    url_list = get_urls_from_page(url,'front')
    # zwrocone linki do stron z artykulami oraz do stron kategorii
    page_links_list = url_list[0]
    sect_links_list = url_list[1]

    #print('*'*50,'\n','Mamy zwrócone',len(page_links_list),'stron oraz',len(sect_links_list),' sekcji.\n'+'*'*50)
    
    if INPUT_ON: 
      print(INPUT_STR.center(80))
      while input():
        break

    all_tmp_links_list = []
    if SECTION:
      for section_url in sect_links_list:
        # Przegladanie stron kategorii i pobranie z nich linkow do artykułów
        print('!'*50,'Zabieramy',len(page_links_list),' stron.','!'*50)
        tmp_links_list = get_urls_from_page(url+''+section_url,'section',page_links_list)
        if len(tmp_links_list) > 0:
          print('!'*50,'Kolejne zwrócone',len(tmp_links_list),' stron z ',len(page_links_list),'.','!'*50)
          page_links_list = tmp_links_list
          all_tmp_links_list+= tmp_links_list
          
        if INPUT_ON: 
          print(INPUT_STR.center(80))
          input()
        # zwrocone linki do stron z artykulami
  
    time_point_list = calculate_execution_time(time_point_list)
    print('\t\t ** Statystyki wstępne. Czas przygotowania:',calculate_execution_time(time_point_list,end=1))
    all_found_links_len = len(all_tmp_links_list+page_links_list)
    finally_links_list = list(set(all_tmp_links_list+page_links_list))
    finally_links_len = len(finally_links_list)
    print('\t\t ** Ilość wszystkich znalezionych linków:',all_found_links_len)
    print('\t\t ** Ilość niepowtarzających się linków:',finally_links_len)
    print('\t\t ** \n\t\t ** \n\t\t ** Teraz będziemy scrapować ....')

    url_list = page_links_list
    url_json_list = []
    
    for licz,link in enumerate(url_list):
      link = url+link
      scrapped_page_part_list = article_scrap(domain,link)
      url_json_list.append(scrapped_page_part_list)
      if EARLY_BREAK:
        if licz > 10: 
          domain = 'test-'+domain
          break
  
    if len(url_json_list) > 0:
      website_json_list.append({'page':url,'urls_list':url_json_list})
      print('\t\t ** %i przetworzonych linków\n' %licz)
    
    #raise SystemExit  
    #input('dalej')
    
    website_url_list_json = dict()
    website_url_list_json = {'websites': website_json_list}
    #print('get_url_list -> url_list_json len:',len(website_url_list_json.keys()))
    #print(website_url_list_json)
    #print('*'*50)
    
    path = "json/"
    save_file_name = domain+'-full.json'
    #print(website_url_list_json)
    
    with open(path+save_file_name, 'w') as file:
      json.dump(website_url_list_json, file)
    
    print('\t\t ** >>>>> Utworzono plik:',save_file_name,'. Całkowity czas:',calculate_execution_time(time_point_list,end=1))
    upload_files_to_s3(save_file_name)
    
    website_url_list_json.clear()
    website_json_list.clear()
    
    json_output_list.append({'website':url, 'filename':save_file_name, 'url_count':finally_links_len})
    
    # jq .websites[] json/metro.co.uk-full.json
    # jq .websites[].urls_list[] json/metro.co.uk-full.json
    # jq .websites[].urls_list[][0] json/metro.co.uk-full.json
    # jq .websites[].urls_list[][1] json/metro.co.uk-full.json

  return json_output_list

def upload_files_to_s3(file_name):
  import stat
  import logging
  from botocore.exceptions import ClientError
  
  client = boto3.client('s3',
                        aws_access_key_id = access_key, 
                        aws_secret_access_key = secret_access_key)
  
  #https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ec2-example-managing-instances.html
  #ec2 = boto3.client('ec2')
  #response = ec2.describe_instances()
  #print(response)
  
  try:
    f = file_name
  except:
    file_name = ""
    
  if file_name:
    pathname = 'json/'+file_name
    date_now = datetime.now().isoformat()
    upload_file_key = S3_PATH + str(file_name)
    try:
      client.upload_file(pathname, S3_BUCKET_NAME, upload_file_key,
                        ExtraArgs={'Metadata': {'filename': str(file_name),'data': str(date_now)}})
      print('\t\t ** >>>>> Plik',file_name,'zapisany na AWS S3 <<<<< **')
    except ClientError as e:
      logging.error(e)
      return False
    return True  
  else:
    for file in os.listdir('json/'):
      if file.endswith('.json'):
        pathname = 'json/'+file
        #print('file=',file,os.stat(pathname))
        #mode = os.stat(pathname).st_mode
        date_now = datetime.now().isoformat()
        upload_file_key = S3_PATH + str(file)
        try:
          client.upload_file(pathname, S3_BUCKET_NAME, upload_file_key,
                            ExtraArgs={'Metadata': {'filename': str(file),'data': str(date_now)}})
          print('\t\t ** >>>>> Plik',file,'zapisany na AWS S3 <<<<< **')
        except ClientError as e:
          logging.error(e)
          return False
        return True

def start_settings():
  #########################################################
  #########################################################
  ######## ustawienia #####################################
  #########################################################
  #########################################################
  global INPUT_STR, SCRAP_KEYS_LIST, ACTIVE_DOMAINS_LIST
  INPUT_STR = '-'*15+'>>> dalej >>>'+'-'*15+''
  keys_list = []
  active_keys = 5 # max=5
  tmp_keys_list = ['title','author','date','body','img']
  [keys_list.append(key) for idx, key in enumerate(tmp_keys_list) if idx < active_keys]
  # lista kluczy dla wyjściowego pliku .json z danymi
  SCRAP_KEYS_LIST = keys_list
  # lista domen do scrapowania
  ACTIVE_DOMAINS_LIST = ["metro.co.uk", "standard.co.uk", "bbc.com"]

  # test settings toolbox
  testenv_on = False
  testenv_on = turn_on_testing_toolbox('bbc.com',test_nr=1,active_keys=4,input_on=0,section=0)
  
  if not testenv_on:
    global INPUT_ON, EARLY_BREAK, SECTION, TEST, ACTIVE_DOMAIN_NR, S3_BUCKET_NAME, S3_PATH
    ######################################################################################
    INPUT_ON    = False   # True - zatrzymuje proces po wykonaniu partii kodu 
                          # False - leci bez opamiętania
    EARLY_BREAK = False   # True - zakoncz skanowanie po przetworzeniu 10ciu linków
                          # False - pełne scrapowanie

    TEST        = 0       # 0 - skrypt uruchamiany na wszystkie domeny z tablicy; 
                          # 1 - dla wybranej domeny; 
                          # 9 - scrapowanie wybranej strony w domenie
    ACTIVE_DOMAIN_NR = 0  # dla test==9 wybór z tablicy domeny do skrapowania

    SECTION     = 0       # 0 - scrapowanie tylko strony głównej
                          # 1 - scrapowanie dodatkowo stron sekcji/działów
  
  # ustawienia dla S3
  S3_BUCKET_NAME = "xd-test-bucket-for-lambda"
  S3_PATH = "website-scrap-json/"
  #########################################################
  #########################################################
  ######## ustawienia #####################################
  #########################################################
  #########################################################

def turn_on_testing_toolbox(domain,test_nr=9,active_keys=3,input_on=1,section=0):
  global TEST, SCRAP_KEYS_LIST, INPUT_ON, SECTION, EARLY_BREAK, ACTIVE_DOMAIN_NR, ACTIVE_DOMAINS_LIST
  keys_list = [key for idx, key in enumerate(SCRAP_KEYS_LIST) if idx < active_keys]
  SCRAP_KEYS_LIST = keys_list
  ACTIVE_DOMAIN_NR = int([idx for idx,d in enumerate(ACTIVE_DOMAINS_LIST) if d==domain][0])
  INPUT_ON = [False if input_on==1 else True][0]
  EARLY_BREAK = True
  TEST = test_nr
  SECTION = section
  
  #print(TEST, SCRAP_KEYS_LIST, INPUT_ON, SECTION, EARLY_BREAK, ACTIVE_DOMAIN_NR, ACTIVE_DOMAINS_LIST)
  
  return True
    
def main():    
  
  start_settings()
  
  if TEST == 0:

    scrap_resp = get_url_list(url="")
    print('\n\n *'+' *'*60)
    tmp_str = 'TEST=0 => '
    print(' *',tmp_str.center(120))
    print(' *',url)
    print(' *\n *'+' *'*60)
    print(scrap_resp)
    print('\n\n')

  elif TEST == 1:
    
    # get_url_list(url="https://standard.co.uk")
    url = ACTIVE_DOMAINS_LIST[ACTIVE_DOMAIN_NR]
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

    if ACTIVE_DOMAIN_NR == 0:
      #url = 'https://metro.co.uk/2022/03/29/jada-pinkett-smith-speaks-out-on-oscars-drama-between-will-smith-and-chris-rock-16366198/'
      url = 'https://metro.co.uk/2022/03/29/queen-elizabeth-arrives-at-memorial-service-for-prince-philip-16362851/'
    elif ACTIVE_DOMAIN_NR == 1:
      #url = 'https://www.standard.co.uk/news/world/vladimir-putin-defeat-volodymyr-zelensky-ukraine-russia-war-b990869.html'
      url = 'https://www.standard.co.uk/news/world/joe-biden-russia-ukraine-invasion-latest-regime-change-vladimir-putin-b990815.html'
      #url = 'https://www.standard.co.uk/news/world/donald-trump-likely-committed-crime-joe-biden-election-victory-us-capitol-commitee-b991038.html'
    elif ACTIVE_DOMAIN_NR == 2:
      url = 'https://www.bbc.com/news/entertainment-arts-60952358'

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
    main()
  except:
    console.print_exception()
    
