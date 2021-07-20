#!/usr/bin/env python
# coding: utf-8

from pytube import YouTube
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome, ChromeOptions
import time
import os
import warnings
import glob

warnings.filterwarnings(action='ignore')


# get_ipython().run_line_magic('load_ext', 'watermark')
# get_ipython().run_line_magic('watermark', '-asoyeong -d -n -v -ppytube,bs4,selenium')

# get_driver - 드라이버 가져오기
def get_driver():
    options = ChromeOptions()
    options.add_argument('headless') #창이 뜨지 않게 처리
    options.add_argument('disable-gpu') #창 크기 조절
    # options.add_argument(
    #     'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    driver = Chrome(options=options)
    return driver


# search - 검색 결과 page source 리턴
def search(keyword):
    driver = get_driver()

    url = 'https://www.youtube.com/results?search_query=' + keyword
    driver.get(url)

    # last_page_height = driver.execute_script("return document.documentElement.scrollHeight")
    #
    # pages = 10
    # for i in range(pages):  # 스크롤 100번까지로 제한
    #     driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    #
    #     # time.sleep(3)
    #
    #     new_page_height = driver.execute_script("return document.documentElement.scrollHeight")
    #
    #     if new_page_height*i > last_page_height:
    #         break
    #
    #     last_page_height = new_page_height

    dom = BeautifulSoup(driver.page_source, 'lxml')
    return dom


# get_url - 검색 결과창의 모든 동영상 url 받아오기
def get_url(keyword):
    dom = search(keyword)
    href = [a.attrs['href'] for a in dom.select('a#video-title')]
    url = ['https://www.youtube.com' + h for h in href]
    return url


# chk_cap - 한국어 자막 유무 체크 (없으면 None 리턴)
def chk_cap(yt):
    lang = 'ko'
    yt_cap = yt.captions.get_by_language_code(lang)
    return yt_cap


# get_audio - pytube 라이브러리를 사용하여 오디오 파일 받아오기
def get_audio(keyword):
    path = './audio_data/'
    url = get_url(keyword)
    url = list(set(url))  # 중복 제거
    for _ in url:
        try:
            yt = YouTube(_)
            if chk_cap(yt) != None and yt.length < 1200: # 한글 자막이 있고 20분 이내인 동영상일 경우
                print(yt.streams.filter(only_audio=True))
                out_file=yt.streams.filter(only_audio=True).first().download(output_path=path)
                base, ext = os.path.splitext(out_file)
                # mp3로 변환
                new_file = base + '.mp3'
                os.rename(out_file, new_file)
                print(yt.title + " 다운로드 완료")
        except Exception:
            continue


# get_cap - pytube 라이브러리를 사용하여 자막 파일 받아오기
def get_cap(keyword):
    path = './caption/'
    url = get_url(keyword)
    url = list(set(url))  # 중복 제거
    for _ in url:
        try:
            yt = YouTube(_)
            if chk_cap(yt) is not None and yt.length < 1200:  # 한글 자막이 있고 20분 이내인 동영상일 경우
                print(yt.captions.all())
                out_file = yt.captions['ko'].download(title=yt.title, output_path=path)
                base, ext = os.path.splitext(out_file)
                # txt 파일로 변환
                new_file = base + '.txt'
                os.rename(out_file, new_file)
                print(yt.title + " 다운로드 완료")
        except Exception:
            continue


if __name__ == "__main__":
    f = open("search_keywords.txt", "r") # reading keyword list file
    lines = f.readlines()
    for keyword in lines:
        keyword = keyword.strip()
        print("Searching youtube data about " + keyword)
        get_audio(keyword)
        get_cap(keyword)

    f.close()
