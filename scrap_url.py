from logging import exception
from bs4 import BeautifulSoup
from website_scrap_function_lib import *
from rich import print
import json

def article_scrap(domain,url,keys_list):
  
  #print('\n','&'*50,'article_scrap(',domain,',',url,',',keys_list,')')
  
  if domain == "metro.co.uk":
    return metro_article_scrap(url,keys_list)
  elif domain == "standard.co.uk":
    return standard_article_scrap(url,keys_list)
  elif domain == "bbc.co.uk":
    return bbc_article_scrap(url,keys_list)
  

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
  tmp_list = url.split('/')
  domain = tmp_list[2]
  
  return domain

def get_url_list(url,section=0):
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

  #########################################################
  #########################################################
  ######## ustawienia #####################################
  #########################################################
  #########################################################
  input_on = False
  early_break = True
  scrap_keys_list = ['title','author','date'] #,'body','img']
  #########################################################
  #########################################################
  ######## ustawienia #####################################
  #########################################################
  #########################################################
  
  if url == "":
    # https://www.bbc.com
    urls_list = ['https://metro.co.uk','https://standard.co.uk'] #, 'http://pp.marzec.eu/newspage']
  else:
    urls_list = []
    urls_list.append(url)
    
  website_json_list = []
  
  for url in urls_list:
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
    if input_on: input('-'*20,'dalej','-'*20)

    all_tmp_links_list = []
    if section:
      for section_url in sect_links_list:
        # Przegladanie stron kategorii i pobranie z nich linkow do artykułów
        print('!'*50,'Zabieramy',len(page_links_list),' stron.','!'*50)
        tmp_links_list = get_urls_from_page(url+''+section_url,'section',page_links_list)
        if len(tmp_links_list) > 0:
          print('!'*50,'Kolejne zwrócone',len(tmp_links_list),' stron z ',len(page_links_list),'.','!'*50)
          page_links_list = tmp_links_list
          all_tmp_links_list+= tmp_links_list
          
        if input_on: input('-'*20,'dalej','-'*20)
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
      scrapped_page_part_list = article_scrap(domain,link,scrap_keys_list)
      url_json_list.append(scrapped_page_part_list)
      if early_break:
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

    save_file_name = domain+'-full.json'
    path = "json/"
    with open(path+save_file_name, 'w') as file:
      json.dump(website_url_list_json, file)
    
    
    website_url_list_json.clear()
    website_json_list.clear()
    
    print('Plik',save_file_name,'zapisany. Całkowity czas: ',calculate_execution_time(time_point_list,end=1))
    
    

# jq .websites[] json/metro.co.uk-full.json
# jq .websites[].urls_list[] json/metro.co.uk-full.json
# jq .websites[].urls_list[][0] json/metro.co.uk-full.json
# jq .websites[].urls_list[][1] json/metro.co.uk-full.json

def main():
  
  test = 0
  section = 0
  
  if test == 0:
    
    url_list = get_url_list(url="",section=section)
      
  elif test == 1:

    #url_list = get_url_list(url="https://standard.co.uk",section=section)
    url_list = get_url_list(url="https://metro.co.uk",section=section)
      
  elif test == 9:
    keys_list = ['title','author','date','body','img']
    url = 'https://www.standard.co.uk/news/world/vladimir-putin-defeat-volodymyr-zelensky-ukraine-russia-war-b990869.html'
    url = 'https://www.standard.co.uk/news/world/joe-biden-russia-ukraine-invasion-latest-regime-change-vladimir-putin-b990815.html'
    url = 'https://www.standard.co.uk/news/world/donald-trump-likely-committed-crime-joe-biden-election-victory-us-capitol-commitee-b991038.html'
    #print(standard_article_scrap(url,keys_list))
    #standard_article_scrap(url,keys_list)
    url = 'https://metro.co.uk/2022/03/29/jada-pinkett-smith-speaks-out-on-oscars-drama-between-will-smith-and-chris-rock-16366198/'
    #url = 'https://metro.co.uk/2022/03/29/queen-elizabeth-arrives-at-memorial-service-for-prince-philip-16362851/'
    print(metro_article_scrap(url,keys_list))
    
 

if __name__ == "__main__":
  
  try:
    main()
  except:
    console.print_exception()
    
  
	
