import csv
from datetime import datetime
import os

# parse_date: 주어진 날짜(또는 오늘 날짜)를 YYMMDD 형식으로 반환
def parse_date(input=None):
    # 인자가 없으면 오늘날짜를 YYMMDD 형식으로 반환
    if input is None:
        return datetime.now().strftime('%y%m%d')
    
    # 인자가 있으면 해당날짜를 YYMMDD 형식으로 변환
    else:
        date_str = str(input)
        return date_str[2:]  # YYMMDD 형식으로 자르기

# save_to_csv: CSV 파일로 저장
def save_to_csv(properties):
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
        writer.writerows(properties)
    
    print(f"수집된 데이터를 CSV 파일로 저장했습니다: {csv_file}")

# '호가'를 숫자 형식으로 변환하는 함수
def convert_price_to_numeric(price_str):
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
