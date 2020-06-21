import math
import re
import time
import requests
from bs4 import BeautifulSoup as BS
import dbase
import random

session = requests.Session()

main_adress = 'https://www.rusprofile.ru/'

okved = [429110, 89220] # список для ввода ОКВЭД, по кот. будет поиск


com_name = [] # данные о названии организации
com_ogrn = [] # данные об ОГРН организации
com_okpo = [] # данные об ОКПО  организации
com_status = [] # данные о действующем статусе организации
com_reg_date = [] # данные о дате регистрации организации
com_capital = [] # данные об уставном капитале  организации


def get_html(proxy = None, user_agent = None):
    '''
    Составления списка страниц для парсинга
    '''
    html_list = []

    for i in okved:
        status_code = 200
        page = 1
    
        while status_code != 404:
            response = session.get(main_adress+'codes/'+str(i), headers = user_agent, proxies = proxy)
            soup = BS(response.content, 'lxml')
            a = soup.find('span', class_='okved-company-tools__label').text.strip().replace(' ','').replace('\n','').split('из')
            a_1 = a[1].split('–')[1]
            a_2 = a[2]
            a_3 = math.ceil(int(a_2) % int(a_1))
            if a_3 == 0:
                html_list.append(main_adress+'codes/'+str(i)+'/'+str(page))
            else:
                for k in range(a_3):
                    html_list.append(main_adress+'codes/'+str(i)+'/'+str(page+k))
            
            status_code = 404
            
    return html_list          

def parser(html, proxy = None, user_agent = None):
    '''
    Поиск основных данных организации
    '''

    # список "супа" всех страниц, по которым будет поиск
    soup_all = [] 

    # добавляем все страницы по ОКВЕД в список soup_all
    for j in html:
        response = session.get(j, headers = user_agent, proxies = proxy)
        soup_all.append(BS(response.content, 'lxml'))

    for next_soup in soup_all:
        
        # поиск названия организации
        find_name = next_soup.find_all('div', class_='company-item__title')

        for i in find_name:
            com_name.append(i.text.strip())
        
        # поиск ОГРН
        find_ogrn = next_soup.find_all('div', class_='company-item-info')
        
        count_ogrn = 1
        while count_ogrn <= len(find_ogrn): 
            b = find_ogrn[count_ogrn].text.strip().replace(' ', '').replace('\n','')
            com_ogrn.append(b.split('ОГРН')[1].split('Датарегистрации')[0])
            count_ogrn = count_ogrn + 3
        
        # поиск статуса организации
        find_status = next_soup.find_all('div', class_='company-item')
        
        for i in find_status:
            if i.find('div', class_='company-item-status') != None:
                com_status.append(i.find('div', class_='company-item-status').text)
            else:
                com_status.append('Действующая организация')
        
        # поиск даты регистрации
        count_reg_date = 1
        while count_reg_date <= len(find_ogrn): 
            
            b = find_ogrn[count_reg_date].text.strip().replace(' ', '').replace('\n','')
        
            c = b.split('Датарегистрации')[1].split('г.')[0]
        
        # перевод текста даты в формат БД (YYYY-MM-DD)
            if re.search('января',c) != None:
                e = c.split('января')
                com_reg_date.append('{}''-01-''{}'.format(e[1],e[0]))
            elif re.search('февраля',c) != None:
                e = c.split('февраля')
                com_reg_date.append('{}''-02-''{}'.format(e[1],e[0]))
            elif re.search('марта',c) != None:
                e = c.split('марта')
                com_reg_date.append('{}''-03-''{}'.format(e[1],e[0]))
            elif re.search('апреля',c) != None:
                e = c.split('апреля')
                com_reg_date.append('{}''-04-''{}'.format(e[1],e[0]))
            elif re.search('мая',c) != None:
                e = c.split('мая')
                com_reg_date.append('{}''-05-''{}'.format(e[1],e[0]))
            elif re.search('июня',c) != None:
                e = c.split('июня')
                com_reg_date.append('{}''-06-''{}'.format(e[1],e[0]))
            elif re.search('июля',c) != None:
                e = c.split('июля')
                com_reg_date.append('{}''-07-''{}'.format(e[1],e[0]))
            elif re.search('августа',c) != None:
                e = c.split('августа')
                com_reg_date.append('{}''-08-''{}'.format(e[1],e[0]))
            elif re.search('сентября',c) != None:
                e = c.split('сентября')
                com_reg_date.append('{}''-09-''{}'.format(e[1],e[0]))
            elif re.search('октября',c) != None:
                e = c.split('октября')
                com_reg_date.append('{}''-10-''{}'.format(e[1],e[0]))
            elif re.search('ноября',c) != None:
                e = c.split('ноября')
                com_reg_date.append('{}''-11-''{}'.format(e[1],e[0]))
            elif re.search('декабря',c) != None:
                e = c.split('декабря')
                com_reg_date.append('{}''-12-''{}'.format(e[1],e[0]))

            count_reg_date = count_reg_date + 3

        # поиск уставного капитала
        count_capital = 1
        while count_capital <= len(find_ogrn): 
            b = find_ogrn[count_capital].text.strip().replace(' ', '').replace('\n','')
            if b.find('Уставныйкапитал') != -1:
                com_capital.append(b.split('Уставныйкапитал')[1].split('руб.')[0])
                count_capital = count_capital + 3
            else:
                com_capital.append('0')
                count_capital = count_capital + 3

        # ищем страницы для парсинга ОКПО
        for find_link in find_name: 
            okpo_find_html = find_link.find('a')['href']

            # заходим в найденые страницы и забираем ОКПО
            if okpo_find_html != 0: 
                response_okpo = session.get('https://www.rusprofile.ru' + str(okpo_find_html), headers = user_agent, proxies = proxy)
                soup_okpo = BS(response_okpo.content, 'lxml')
                
                # если ОКПО указано на странице, добавляем его в список
                if soup_okpo.find('span', {'id': 'clip_okpo'}) != None: 
                    com_okpo.append(soup_okpo.find('span', {'id': 'clip_okpo'}).text)
                    time.sleep(random.randint(3,5))
                else:
                    com_okpo.append(0)
                    time.sleep(random.randint(3,5))


def benchmark(func):
    import time
    
    def wrapper():
        start = time.time()
        func()
        end = time.time()
        print('[?] Время выполнения: {:.3f} секунд.'.format(end-start))
    return wrapper


@benchmark
def main():
    
    try:
        with open('proxies.txt') as proxies:
            proxy = proxies.read().split()
            print(proxy)
            one_proxy = random.choice(proxy)
            print('choose proxy: ', one_proxy)
            proxy_param = {'http': 'http://' + one_proxy}


        with open('user_agents.txt') as agents:
            agent = agents.read().split('\n')
            print(agent)
            one_agent = random.choice(agent)
            agent_param = {'User-Agent': one_agent}
    except:
        print('ERROR: files proxy.txt and user-agents.txt not found')
        proxy_param = None
        agent_param = None

    main_get_html = get_html(proxy_param, agent_param)

    parser(main_get_html, proxy_param, agent_param)
    
    dbase.wr_data(com_name, com_ogrn, com_okpo, com_status, com_reg_date, com_capital)


if __name__ == "__main__":
    main()