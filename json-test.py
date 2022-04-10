

import json
from scrap_url import prepare_list_used_urls, download_file_from_s3, get_urls_from_page


def prepare_list_used_urls1(url_domain):
  #print('def prepare_list_used_urls:',url_domain)
  domain = 'https://'+url_domain
  #with open('allwebsite.json', 'r') as f:
  with open('json/allwebsite.json', 'r') as file:
    try: 
      read_dict = json.load(file)
      websites_dict = read_dict.get('websites')
      website_nr = -1
      #pidx = 0
      print('\n\t\t\t\t==> websites_dict len',len(websites_dict))
      for pidx,tmp_page in enumerate(websites_dict):
        print('\n\n\t\t\t\t==>',domain,'==',tmp_page['website']['page'],' <==')
        if domain == tmp_page['website']['page']: #['website']['page']:
          website_nr = pidx
          break  
        #pidx+= 1
      
      print('\n\n','* '*20,'website_nr:',website_nr,'* '*20,'\n\n')
      
      if website_nr >= 0:
        website_page_urls_list = read_dict.get('websites')[website_nr]['website']['urls_list']
        website_urls_list = []
        for url in website_page_urls_list:
          website_urls_list.append(prep_url(domain,url['url'])) #url[:20]+'(...)'+url[-10:])
          #website_urls_list.append(url['url']) #.replace(domain,''))

      return website_urls_list

    except: 
      #read_dict = dict({'websites':[]})
      return []

def prep_url(d,u):
  url = d+u
  return url[:20]+'(...)'+url[-10:]
  

if 1 == 1:

  domain = 'bbc.com'
  domain = 'metro.co.uk'
  domain = 'standard.co.uk'
  domain_url = 'https://'+domain
  #get_url_list(domain_url)
  allwebsite_save_file_name = 'allwebsite.json'
  path = 'json/'
  domain_save_file_name = 'test-'+domain+'-full.json'

  ############################### used_urls_list from allwebsite.json
  used_urls_list = []
  used_urls_list = prepare_list_used_urls1(domain)
  print('\n allwebsite.json \t\t==> used_urls_list \t==>',len(used_urls_list),used_urls_list)

  ############################### error_page_urls_list
  error_page_list = download_file_from_s3('errorwebsite.text').decode("utf-8")
  tmp_list = []
  if type(error_page_list) == str: error_page_list = error_page_list.split('\n')
  for url in error_page_list:
    tmp_list.append(prep_url(domain_url,url)) #url[:20]+'(...)'+url[-10:])
  error_page_list = tmp_list
  print('\n errorwebsite.text \t\t==> error_page_list \t==>',len(error_page_list),error_page_list)

  used_urls_list.extend(error_page_list)
  print('\n\t\t\t\t==> used urls list count:',len(used_urls_list))

    
    
  ############################### get_urls_from_page - pobranie linkow ze strony
  tmp_new_urls_list = get_urls_from_page(domain_url,'front')
  new_urls_list = [prep_url(domain_url,url) for url in tmp_new_urls_list[0]]
  #print(new_urls_list)
  print('\t\t\t\t==> Usuwanie duplikatów z nowych linków: przed:',len(new_urls_list), end=' po: ')
  ############################### usuwanie duplikatow z nowo pobranych plikow
  [new_urls_list.remove(l) for l in used_urls_list if l in new_urls_list]
  print(len(new_urls_list))
  #print(used_urls_list)


  ############################### scrapowanie stron z listy url -> new_urls_list
  print('\n\n\t\t\t\t','* '*40,'\n\t\t\t\t  * * * * * * * * *  Koniec przygotowywania linkow do obrobki * * * * * * * * * \n\t\t\t\t','* '*40,'\n')
  print('\t\t\t\t==> Scrapowanie stron - lista 3pierwsze i 3ostatnie z',len(new_urls_list))
  for i,link in enumerate(new_urls_list):
    if i < 3 or i > len(new_urls_list)-3:
      print('\t\t\t\t',i,'scrap:',link)
  print('\t\t\t\t==> Scrapowanie - KONIEC ',len(new_urls_list))
  ############################### zapis zescrapowanych stron do pliku domain_save_file_name




############################### articles_url_list from domain_save_file_name
with open(path+domain_save_file_name, 'r') as file:
  read_dict = json.load(file)

articles_url_list = []
pages_json_list = read_dict.get('websites')[0]['urls_list']
for i,w in enumerate(read_dict.get('websites')[0]['urls_list']):
  articles_url_list.append(prep_url(domain_url,w['url'])) #url[:20]+'(...)'+url[-10:])
print('\n',domain_save_file_name,'\t==> articles_url_list \t==>',len(articles_url_list),articles_url_list)  
print('\n\n')




#{"websites": 
# [
  # {
    # "page": "https://bbc.com", 
    # "urls_list": [
      # {
        # "url": "https://bbc.com/news/world-europe-61030090", 
        # "page_details": [
          # {"post_title": "Ukraine war: Sharing space with the dead - horror outside Chernihiv"}, 
          # {"post_date": "2022-04-07 19:18:26"}, 
          # {"article_body": "On the white, damp wall of the Yahidne school basement is a crude calendar, drawn ...."}, 
          # {"images": [
            # {"src": "https://ichef.bbci.co.uk/news/976/cpsprodpb/20F6/production/_124083480_mykola.jpg", "alt": "Mykola Klymchuk"}, 
            # {"src": "https://ichef.bbci.co.uk/news/976/cpsprodpb/0030/production/_124084000_mediaitem124083999.jpg", "alt": "basement in yahidne"}, 
            # {"src": "https://ichef.bbci.co.uk/news/976/cpsprodpb/10200/production/_124084066_mediaitem124084005.jpg", "alt": "anastasia"}, 
            # {"src": "https://ichef.bbci.co.uk/news/976/cpsprodpb/13842/production/_124083997_mediaitem124083996.jpg", "alt": "destroyed building in chernihiv"}, 
            # {"src": "https://ichef.bbci.co.uk/news/976/cpsprodpb/130E0/production/_124084087_mediaitem124084086.jpg", "alt": "chernihiv"}, 
            # {"src": "https://ichef.bbci.co.uk/news/976/cpsprodpb/112C2/production/_124083307_nina.jpg", "alt": "Nina"}, 
            # {"src": "https://ichef.bbci.co.uk/news/624/cpsprodpb/1FCD/production/_105914180_line976-nc.png", "alt": "line"}, 
            # {"src": "https://ichef.bbci.co.uk/news/624/cpsprodpb/1FCD/production/_105914180_line976-nc.png", "alt": "line"}
          # ]}
        # ]
      # }, {
        # "url": "https://bbc.com/news/world-europe-61028380", "page_details": [
          # {"post_title": "Bucha murders: German report says Russian troops discussed killings"}, 
          # {"post_date": "2022-04-07 16:46:46"}, 
          # {"article_body": "Russian troops were heard discussing killing civilians in the Ukrainian town of Bucha, in messages intercepted"}, 
          # {"images": [
            # {"src": "https://ichef.bbci.co.uk/news/976/cpsprodpb/E588/production/_124006785_gettyimages-1239714286.jpg", "alt": "Body bags in Bucha"}, 
            # {"src": "https://ichef.bbci.co.uk/news/624/cpsprodpb/1FCD/production/_105914180_line976-nc.png", "alt": "line"}, 
            # {"src": "https://ichef.bbci.co.uk/news/624/cpsprodpb/1FCD/production/_105914180_line976-nc.png", "alt": "line"}
          # ]}
        # ]}
      # }
    # ] 
  # }
# ]
#}


#{'websites':
#[
  # {'website': 
    # {'page': 'https://bbc.com', 
    # 'urls_list': [
      # {'url': 'https://bbc.com/news/world-us-canada-61005388', 'page_title': "Ukraine ...", 'page_date': '2022-04-06 17:52:06'}, 
      # {'url': 'https://bbc.com/news/business-61013908', 'page_title': 'Oil bosses vow to boost output and deny profiteering', 'page_date': '2022-04-06 17:40:00'}
    # ]
    # }
  # }, 
  # {'website': 
    # {'page': 'https://metro.co.uk', 
    # 'urls_list': [
      # {'url': 'https://metro.co.uk/2022/04/06/first-pictures-inside-chernobyl-since-russians-retreated-after-falling-ill-16416170/', 'page_title': 'First pictures from inside Chernobyl since Russians retreated after falling ill', 'page_date': '2022-04-06 13:20:00'}, 
      # {'url': 'https://metro.co.uk/2022/04/06/brit-accused-of-spying-for-russia-charged-under-official-secrets-act-16418649/', 'page_title': 'Brit security guard accused of spying for Russia extradited from Germany', 'page_date': '2022-04-06 16:42:00'}
    # ]
    # }
  # } 
#]
#}








#print('\n\n\t\t',len(read_dict['websites']),len(read_dict.get('websites')),len(read_dict.get('websites')[0]['website']['page']),'\n\n')
#print(read_dict.get('websites')[0]['website']['page'])
#print(read_dict.get('websites')[1]['website']['page'])
#print(read_dict.get('websites')[2]['website']['page'])
#c = len(read_dict.get('websites'))
#for i,u in enumerate(read_dict.get('websites')):
#i = 0
#print(i,'\t',type(u),read_dict.get('websites')[i]['website']['urls_list'][0]['url'][:100])
#i+= 1

#print('\n0\t',read_dict.get('websites')[0]['website'])
#print('\n1\t',read_dict.get('websites')[1]['website']['page'])
#print('\n2\t',read_dict.get('websites')[2]['website']['urls_list'])
#print('\n3\t',read_dict.get('websites')[3]['website']['urls_list'][0])
#print('\n4\t',read_dict.get('websites')[4]['website']['urls_list'][0]['url'])

#pages_url_from_file_list = read_dict['websites'][1]['website']['page']
#scrapped_site_urls_from_file_list = read_dict['websites'][1]['website']['urls_list'][0]['url']

#print('scrapped_site_urls_from_file_list:',scrapped_site_urls_from_file_list)
#print('pages_url_from_file_list:',pages_url_from_file_list)





#website_url_list_json = set()
#with open(path+save_file_name, 'r') as file:
#      json.dump(website_url_list_json, file)

#print('website_url_list_json:',website_url_list_json)







if 1 == 2:
  pass

# allwebsite_save_file_name = 'json/allwebsite.json'
# #allwebsite_save_file_name = 'allwebsite.json'
# #allwebsite_url_list.append({'website': short_website_json_list})
# with open(allwebsite_save_file_name, 'r') as f:
#   read_dict = json.load(f)


# f = open(local_path+allwebsite_save_file_name, 'r')
#     # To read the whole file
#     read_dict = json.load(f)
#     data_from_file = read_dict['websites']
    
    
    
    
# job_page = 'https://bbc.com'
# for pidx,tmp_page in enumerate(read_dict.get('websites')):
#   if job_page == read_dict.get('websites')[pidx]['website']['page']:
#     website_nr = pidx
#     break    

# print('All websites:',len(read_dict.get('websites')))

# website_page = read_dict.get('websites')[website_nr]['website']['page']
# website = read_dict.get('websites')[website_nr]['website']['urls_list']
# print(website_nr,' ',website_page,' urls list',len(website),':')
# for url in website:
#   print(url['url'])
# print('\n')


# # {"websites": [
#   # {"website": {
#     # "page": "https://bbc.com", 
#     # "urls_list": [
#     # {
#       # "url": "https://bbc.com/news/live/world-europe-60991746", 
#       # "page_title": "Ukraine war latest: Russians trying to cover up war crimes - Zelensky - BBC News", 
#       # "page_date": "2022-04-05 3:17:00.000000"
#     # }, {
#       # "url": "https://bbc.com/news/world-europe-60990934", 
#       # "page_title": "Ukraine war: International outrage grows over civilian killings in Bucha", 
#       # "page_date": "2022-04-04 22:31:19"
#     # }
    
    
# json = read_dict.get('websites') #[1]['website']['urls_list']
# print(len(json),json) # 7 
# print('*'*50)
# page = read_dict.get('websites')[0]['website']['page']
# website = read_dict.get('websites')[0]['website'] #[0]['website']['page']
# print('website 0 ================> :',page,'\n','*'*50)
# print('.get(\'websites\')[0][\'website\'] ==> ',website)
# print('*'*50)
# page = read_dict.get('websites')[1]['website']['page']

# website = read_dict.get('websites')[1]['website']['urls_list']
# print('website 1 ================> :',page,'\n','*'*50)
# print('.get(\'websites\')[1][\'website\'][\'url_list\'] ==> ',len(website))
# print('\twebsite[0]:',website[0],'\n\twebsite[1][\'url\']:',website[1]['url'],'\n\twebsite[6][\'page_date\']:',website[6]['page_date'])
# print('*'*50)
# page = read_dict.get('websites')[2]['website']['page']
# website = read_dict.get('websites')[2]['website']['urls_list'][1]
# print('website 2 ================> :',page,'\n','*'*50)
# print('.get(\'websites\')[2][\'website\'][\'url_list\'][1] ==> ',website)
# print('*'*50)







# print('=+'*50)
# page = read_dict.get('websites')['website'] #[0]['website']['page']
# print('page:',page)

# urls_list = read_dict.get('websites')[0]['website']['urls_list'][0]
# print('urls_list:',type(urls_list),len(urls_list))

# for url in urls_list:
#   print('url.keys():',url.keys()) #,url.get('url'))



# website_json_list = []
# urls_list =['https://url-0-1-link','https://url-0-2-link']
# url_json_list = []
# for val in urls_list:
#   url_json_list.append({'url':val})

# website_json_list.append({'page':'website0_url','urls_list': url_json_list})
# website_json_list.append({'page':'website1_url','urls_list': [
#   {'url':'https://url-1-1-link', 'title':'jakis tytul 1 1'}, 
#   {'url':'https://url-1-2-link','title': 'jakis tytul 1 2'}
# ]})
# website_json_list.append({'page':'website2_url','urls_list': [
#   {'url':'https://url-2-1-link','title':'tytul 2 1'}, 
#   {'url':'https://url-2-2-link','title':'tutul 2 2'}
# ]})
# json = {'websites':website_json_list}
# print('\n******************************************************\n')
# print(json.get('websites')[0])

# # To read the whole file
# #print('+++++++++++++++++++++++++')
# #read_dict = json.dumps(f.read())

# #print(read_dict)

# #[{'website': {
#   # 'page': 'https://bbc.com', 
#   # 'urls_list': [{
#     # 'url': 'https://bbc.com/news/live/world-europe-60991746', 
#     # 'page_title': 'Ukraine war latest: Russians trying to cover up war crimes - Zelensky - BBC News', 
#     # 'page_date': '2022-04-05 8:18:00.000000'}
    
# #data_from_file = read_dict['websites']
# print(read_dict.get('website')) #[0]['urls_list'][0])


# #for idx,w in enumerate(data_from_file):
# #  print(data_from_file[idx]['urls_list'])
  

    
# if 1 == 2:
#   l1 = []
#   l1.append({'tutul': 'title1', 'date': '2022-04-02'})
#   l1.append({'tutul': 'title2', 'date': '2022-04-03'})

#   short_website_json_list = []
#   short_website_json_list.append({'url': 'website1.url', 'pages': l1})

#   allwebsite_url_list_json = {'websites': 
#     {'website': short_website_json_list}
#   }

#   js = json.dumps(allwebsite_url_list_json)
#   print(js)


# #with open(allwebsite_save_file_name, 'w') as file:
# #  json.dump(allwebsite_url_list_json, file)
