import requests
import csv
from datetime import datetime
import os
from dotenv import load_dotenv

# .env에서 ACCESS_TOKEN 불러오기
load_dotenv()
access_token = os.getenv("ACCESS_TOKEN")

# API 호출 헤더
headers = {
    'authority': 'new.land.naver.com',
    'accept': '*/*',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'authorization': f'Bearer {access_token}',  # .env에서 불러온 토큰 사용
    'referer': 'https://new.land.naver.com/complexes/',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}

# 아파트 고유번호와 아파트 이름 매칭
apt_code = {
    483: "대치2단지아파트",
    419: "대청아파트"
}


apt_code_name_mapping = {
    483: "대치2단지아파트",
    419: "대청아파트"
}

# URL 템플릿
URL_TEMPLATE = "https://new.land.naver.com/api/articles/complex/{apt_code}?tradeType=A1&priceMin=0&priceMax=120000&areaMin=44&areaMax=85&minHouseHoldCount=300&page={page}&order=prc"

# 전체 데이터 저장할 리스트
all_data = []

# 각 아파트에 대해 데이터 받아오기
for code in apt_code:

    # 아파트 코드에 해당하는 이름 얻기
    apt_name = apt_code_name_mapping.get(code)
    print(f"### 시작: {apt_name} ###")

    page = 1
    while True:
        # URL에 페이지 번호 추가
        URL = URL_TEMPLATE.format(apt_code=code, page=page)
        
        # API 호출
        response = requests.get(URL, headers=headers)
        
        # 응답 상태 코드 확인
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)  # 응답 본문 출력
            break
        
        # 응답 데이터를 JSON으로 변환
        data = response.json()
        
        # 데이터가 없으면 반복 종료
        if not data.get('articleList'):
            print(f"### 끝: {apt_name} ###")
            break
        
        # 매물 데이터를 추출하여 리스트에 저장
        properties = []
        for article in data['articleList']:
            property_data = {
                '날짜': article['articleConfirmYmd'],
                '매물명': article['articleName'],
                '거래유형': article['tradeTypeName'],
                '면적': f"{article['areaName']}",
                '호가': article['dealOrWarrantPrc'],
                '가격변경': article['priceChangeState'],
                '동': article['buildingName'],
                '층': article['floorInfo'],
                '향': article['direction']
            }
            properties.append(property_data)

        # 응답 데이터 확인
        print(f"{page}번째 페이지에서 {len(properties)}개의 데이터가 수집됐습니다.")
        
        # 받아온 데이터 추가
        all_data.extend(properties)
        
        # 페이지 증가
        page += 1

        # 최대 10페이지까지만 받고 종료
        if page > 10:
            print(f"### 끝: {apt_name} ###")
            break

# 결과 출력
print(f"총 {len(all_data)}개의 데이터가 수집되었습니다.")

# CSV 파일로 저장
def save_to_csv(properties):
    # /data/ 디렉토리 확인 및 생성
    data_dir = './data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 날짜 형식 지정 (YYMMDD)
    date_str = datetime.now().strftime('%y%m%d')
    # 파일 경로: /data/[YYMMDD]_data.csv
    csv_file = f"{data_dir}/{date_str}_data.csv"
    
    # CSV 파일 헤더
    fieldnames = ['날짜', '매물명', '거래유형', '면적', '호가', '가격변경', '동', '층', '향']
    
    # 파일 존재 여부 확인 후 작성
    with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(properties)
    
    print(f"수집된 데이터를 CSV 파일로 저장했습니다: {csv_file}")

# CSV로 저장
save_to_csv(all_data)
