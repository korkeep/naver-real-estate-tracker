import csv
from datetime import datetime
import os
from collections import defaultdict
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates as mdates
import glob
import requests
import re
import pandas as pd


# load_dotenv(): .env에서 필요한 환경변수 가져오기
load_dotenv()

# ACCESS_TOKEN: 네이버 부동산 로그인 후, HTTP Header의 'authorization' 값을 입력
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# FONT_PATH: 한글 폰트를 지원하는 폰트 파일의 로컬 경로 입력
FONT_PATH = os.getenv("FONT_PATH")

# HEADERS: API 호출 헤더
HEADERS = {
    'authority': 'new.land.naver.com',
    'authorization': f'Bearer {ACCESS_TOKEN}',  # .env에서 불러온 토큰 사용
    'referer': 'https://new.land.naver.com/complexes/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

# APT_CODE: 아파트 고유번호와 아파트 이름 매칭
APT_CODE = {
    483: "대치2단지",
    419: "개포대청",
    668: "수서삼익",
    671: "수서신동아",
    827: "수서1단지"
}

# URL_TEMPLATE: URL 템플릿
'''
 apt_code: 아파트 고유번호
 tradetype=A1: 거래유형 매매
 areaMin=44: 최소면적 44
 areaMax=85: 최대면적 85
 minHouseHoldCount=300: 최소세대수 300세대
 page: 화면 구분, 1페이지당 최대 20개 데이터
 order=prc: 낮은가격순 정렬
'''
URL_TEMPLATE = "https://new.land.naver.com/api/articles/complex/{apt_code}?" + \
                "tradeType=A1&areaMin=44&areaMax=85&minHouseHoldCount=300&page={page}&order=prc"


# set_font(): 한글 폰트 설정 (Windows에서 '맑은 고딕' 폰트를 사용)
def set_font():
    font_prop = font_manager.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.family'] = font_prop.get_name()


# parse_date(): 주어진 날짜(또는 오늘 날짜)를 YYMMDD 형식으로 반환
def parse_date(input=None):
    # 인자가 없으면 오늘날짜를 YYMMDD 형식으로 반환
    if input is None:
        return datetime.now().strftime('%y%m%d')
    
    # 인자가 있으면 해당날짜를 YYMMDD 형식으로 변환
    else:
        date_str = str(input)
        return date_str[2:]  # YYMMDD 형식으로 자르기


# parse_price(): '호가'를 숫자 형식으로 변환하는 함수
def parse_price(price_str):
    try:
        # 쉼표 제거
        price_str = price_str.replace(",", "")
        
        # '억' 단위 처리
        if "억" in price_str:
            price_str = price_str.replace("억", "")
            parts = price_str.split(" ")  # 공백으로 나누기
            if len(parts) == 1:  # 예: "11억"
                price_value = float(parts[0])  # 그대로 float로 변환
            elif len(parts) == 2:  # 예: "10억 7,000"
                price_value = float(parts[0]) + (int(parts[1]) / 10000)  # 억 + 만 단위로 변환
            return price_value
        
        else:
            return None
    
    except Exception as e:
        print(f"Error: {e}")
        return None


# remove_duplicates(): 동과 층을 기준으로 중복을 판단하고, 가장 최근에 올라온 항목을 선택
def remove_duplicates(data):
    grouped = defaultdict(list)
    
    for row in data:
        building, floor, registration_date = row['동'], row['층'], row['등록날짜']
        grouped[(building, floor)].append((registration_date, row))  # building, floor을 key로 registration_date와 행을 tuple로 저장

    # 중복 제거된 결과를 저장할 리스트
    result = []
    
    for (building, floor), rows in grouped.items():
        # 같은 building, floor의 중복들 중에서 registration_date가 가장 큰 항목을 선택
        latest_row = max(rows, key=lambda x: x[0])  # registration_date 기준으로 최신 항목 선택
        result.append(latest_row[1])  # 최신 항목의 행만 저장

    return result


# save_to_csv(): list 형식의 data를 CSV 파일로 저장
def save_to_csv(data):
    # /data/ 디렉토리 확인 및 생성
    data_dir = './data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 수집날짜 형식 지정 (YYMMDD)
    date_str = parse_date()
    
    # 파일 경로: /data/[YYMMDD]_data.csv
    csv_file = f"{data_dir}/{date_str}_data.csv"
    
    # CSV 파일 헤더
    fieldnames = ['수집날짜', '등록날짜', '매물명', '거래유형', '면적', '호가', '가격변경', '동', '층', '향']
    
    # 파일 존재 여부 확인 후 작성
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"수집된 데이터를 CSV 파일로 저장했습니다: {csv_file}")


# load_from_csv(): CSV 파일 로드
def load_from_csv(file_path_pattern):
    # file_path_pattern에 맞는 CSV 파일들을 모두 읽어들인다.
    file_paths = glob.glob(file_path_pattern)
    
    # 모든 데이터를 하나의 DataFrame으로 합치기
    data = pd.concat([pd.read_csv(file) for file in file_paths], ignore_index=True)
    
    # '호가' 컬럼을 숫자로 변환
    data['호가'] = pd.to_numeric(data['호가'], errors='coerce')
    
    # '수집날짜'를 datetime 형식으로 변환
    data['수집날짜'] = pd.to_datetime(data['수집날짜'], format='%y%m%d')
    
    return data


# crawl_data(): 아파트 코드에 해당하는 전체 데이터 크롤링
def crawl_data(apt_code, all_data):
    
    # 아파트 코드에 해당하는 이름 얻기
    apt_name = APT_CODE.get(apt_code)
    print(f"### {apt_name} ###")
    page = 1
    
    while True:
        # URL에 페이지 번호 추가
        URL = URL_TEMPLATE.format(apt_code=apt_code, page=page)
        
        # API 호출
        response = requests.get(URL, headers=HEADERS)
        
        # 응답 상태 코드 확인
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)  # 응답 본문 출력
            break
        
        # 응답 데이터를 JSON으로 변환
        data = response.json()
        
        # 데이터가 없으면 반복 종료
        if not data.get('articleList'):
            break
        
        # 매물 데이터를 추출하여 리스트에 저장
        properties = []
        for article in data['articleList']:
            property_data = {
                '수집날짜': parse_date(), # YYMMDD
                '등록날짜': parse_date(article['articleConfirmYmd']), # YYYYMMDD → YYMMDD
                '매물명': apt_name,
                '거래유형': article['tradeTypeName'],
                '면적': article['areaName'],
                '호가': parse_price(article['dealOrWarrantPrc']), # Ex: 10.0, 10.2
                '가격변경': article['priceChangeState'], # SAME, INCREASE, DECREASE
                '동': article['buildingName'],
                '층': article['floorInfo'],
                '향': article['direction']
            }
            properties.append(property_data)
        
        # 받아온 데이터 추가
        all_data.extend(properties)
        
        # 페이지 증가
        page += 1
        
        # 최대 10페이지까지만 받고 종료
        if page > 10:
            break


# plot_price_change(): 가격 변동 시각화 함수
def plot_price_change(data):
    
    # 아파트별로 데이터를 그룹화
    grouped_by_apt = data.groupby('매물명')
    
    # 아파트별로 시각화
    for apt, group in grouped_by_apt:
        plt.figure(figsize=(12, 6))
        
        # 면적별로 그룹화
        grouped_by_area = group.groupby('면적')

        # 면적별로 가격을 시각화
        for area, area_group in grouped_by_area:
            
            # 45A, 45B 등 숫자가 아닌 부분은 제거하고 정수형으로 변환
            area = int(re.sub(r'\D', '', str(area))) 

            # 최저 가격, 최고 가격, 평균 가격 계산
            min_price = area_group['호가'].min()
            max_price = area_group['호가'].max()
            mean_price = area_group['호가'].mean()

            # 면적별 색상 설정
            if area < 50:
                color = 'lightblue'  # 15평 이하
            elif area < 66:
                color = 'lightgreen'  # 20평 이하
            elif area < 82:
                color = 'lightyellow'  # 25평 이하
            else:
                color = 'lightcoral'  # 이외

            # 면적별 가격 영역 표시 (최저, 최고 가격)
            plt.fill_between([area_group['수집날짜'].min(), area_group['수집날짜'].max()], min_price, max_price, 
                             color=color, alpha=0.3, label=f'{area} 면적 범위')

            # 면적별 평균 가격을 점선으로 표시
            plt.axhline(mean_price, color=color, linestyle='--', label=f'{area} 면적 평균')

        # 그래프 제목 및 레이블 설정
        plt.title(f'{apt} 아파트 가격 변동 - 면적별 가격 범위 및 평균')
        plt.xlabel('날짜')
        plt.ylabel('호가 (억원)')
        
        # 날짜 포맷 설정: 월/일 (MM/DD)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        
        # X축 라벨 회전
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.legend(title="면적별 가격 범위 및 평균", loc='upper left', bbox_to_anchor=(1, 1))
        plt.show()