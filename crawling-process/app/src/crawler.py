#크롤링시 필요한 라이브러리 불러오기
from bs4 import BeautifulSoup
import requests
import re
import datetime
from tqdm import tqdm
import sys
import pandas as pd

# ConnectionError방지
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}

# 페이지 url 형식에 맞게 바꾸어 주는 함수 만들기
#입력된 수를 1, 11, 21, 31 ...만들어 주는 함수
def makePgNum(num):
    if num <= 0:
        return 1
    else:
        return 10 * num - 9
    
# 크롤링할 url 생성하는 함수 만들기(검색어, 크롤링 시작 페이지, 크롤링 종료 페이지)
def makeUrl(search, start_pg, end_pg):
    urls = []
    for i in range(start_pg, end_pg + 1):
        page = makePgNum(i)
        url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(page)
        urls.append(url)
    # print("생성url: ", urls)
        
    return urls    
    
# html에서 원하는 속성 추출하는 함수 만들기 (기사, 추출하려는 속성값)
def news_attrs_crawler(articles, attrs):
    attrs_content=[]
    for i in articles:
        attrs_content.append(i.attrs[attrs])
    return attrs_content


#html생성해서 기사크롤링하는 함수 만들기(url): 링크를 반환
def articles_crawler(url):
    #html 불러오기
    original_html = requests.get(url, headers=headers)
    html = BeautifulSoup(original_html.text, "html.parser")

    url_naver = html.select("div.group_news > ul.list_news > li div.news_area > div.news_info > div.info_group > a.info")
    article_urls = news_attrs_crawler(url_naver,'href')
    return article_urls


def start_crawl(search, page, page2):
    #####뉴스크롤링 시작#####

    print("크롤링할 시작 페이지: ",page,"페이지")
    print("크롤링할 종료 페이지: ",page2,"페이지")   

    # naver url 생성
    naver_urls = makeUrl(search,page,page2)

    #뉴스 크롤러 실행
    news_titles = []
    news_urls =[]
    news_contents =[]
    news_dates = []
    
    for naver_url in naver_urls:
        article_urls = articles_crawler(naver_url)
        for article_url in article_urls:
            news_urls.append(article_url)

    #NAVER 뉴스만 남기기
    final_urls = []
    for news_url in news_urls:
        if "news.naver.com" in news_url:
            final_urls.append(news_url)
        else:
            pass

    # 뉴스 내용 크롤링
    for i in tqdm(final_urls):
        #각 기사 html get하기
        news = requests.get(i,headers=headers)
        news_html = BeautifulSoup(news.text,"html.parser")

        # 뉴스 제목 가져오기
        title = news_html.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
        if title == None:
            title = news_html.select_one("#content > div.end_ct > div > h2")
        
        # 뉴스 본문 가져오기
        content = news_html.select("div#dic_area")
        if content == []:
            content = news_html.select("#articeBody")

        # 기사 텍스트만 가져오기
        # list합치기
        content = ''.join(str(content))

        # html태그제거 및 텍스트 다듬기
        pattern1 = '<[^>]*>'
        title = re.sub(pattern=pattern1, repl='', string=str(title))
        content = re.sub(pattern=pattern1, repl='', string=content)
        patterns = ["// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}", "\n", "\t", "[", ']', '=', ',', '/', '\\']
        for pattern in patterns:
            content = content.replace(pattern, '')
            title = title.replace(pattern, '')

        news_titles.append(title)
        news_contents.append(content)

        try:
            html_date = news_html.select_one("div#ct> div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span")
            news_date = html_date.attrs['data-date-time']
        except AttributeError:
            news_date = news_html.select_one("#content > div.end_ct > div > div.article_info > span > em")
            news_date = re.sub(pattern=pattern1,repl='',string=str(news_date))
        # 날짜 가져오기
        news_dates.append(news_date)

    print("검색된 기사 갯수: 총 ",(page2+1-page)*10,'개')
    # print("\n[뉴스 제목]")
    # print(news_titles)
    # print("\n[뉴스 링크]")
    # print(final_urls)
    # print("\n[뉴스 내용]")
    # print(news_contents)

    print('news_title: ',len(news_titles))
    print('news_url: ',len(final_urls))
    print('news_contents: ',len(news_contents))
    print('news_dates: ',len(news_dates))


    #데이터 프레임 만들기
    news_df = pd.DataFrame({'date':news_dates,'title':news_titles,'link':final_urls,'content':news_contents})

    #중복 행 지우기
    news_df = news_df.drop_duplicates(keep='first',ignore_index=True)
    print("중복 제거 후 행 개수: ",len(news_df))

    #데이터 프레임 저장
    now = datetime.datetime.now() 
    news_df.to_csv('saved_csv/{}_{}.csv'.format(search,now.strftime('%Y%m%d_%H%M%S')),encoding='utf-8-sig',index=False)
    
    return news_df