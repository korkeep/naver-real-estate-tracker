import requests
from dotenv import load_dotenv
from utils import *

# .env에서 ACCESS_TOKEN 불러오기
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# HEADERS: API 호출 헤더
HEADERS = {
    'authority': 'new.land.naver.com',
    'accept': '*/*',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
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
    827: "수서1단지",
    348: "가락우성"
}

# URL 템플릿
# apt_code: 고유번호
# tradetype=A1: 거래유형 매매
# areaMin=44: 최소면적 44
# areaMax=85: 최대면적 85
# minHouseHoldCount=300: 최소세대수 300세대
# page: 화면에 출력되는 페이지, 1페이지당 20개 데이터
# order=prc: 낮은가격순 정렬
URL_TEMPLATE = "https://new.land.naver.com/api/articles/complex/{apt_code}?tradeType=A1&areaMin=44&areaMax=85&minHouseHoldCount=300&page={page}&order=prc"

# 전체 데이터 저장할 리스트
all_data = []

# 각 아파트에 대해 데이터 받아오기
for code in APT_CODE:

    # 아파트 코드에 해당하는 이름 얻기
    apt_name = APT_CODE.get(code)
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
                '수집날짜': parse_date(),
                '등록날짜': parse_date(article['articleConfirmYmd']),
                '매물명': apt_name,
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

# CSV로 저장
save_to_csv(all_data)
