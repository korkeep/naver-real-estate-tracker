import csv
from datetime import datetime
import os
from collections import defaultdict

# parse_date: 주어진 날짜(또는 오늘 날짜)를 YYMMDD 형식으로 반환
def parse_date(input=None):
    # 인자가 없으면 오늘날짜를 YYMMDD 형식으로 반환
    if input is None:
        return datetime.now().strftime('%y%m%d')
    
    # 인자가 있으면 해당날짜를 YYMMDD 형식으로 변환
    else:
        date_str = str(input)
        return date_str[2:]  # YYMMDD 형식으로 자르기


# parse_price: '호가'를 숫자 형식으로 변환하는 함수
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


# remove_duplicates: 동과 층을 기준으로 중복을 판단하고, 가장 최근에 올라온 항목을 선택
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


# save_to_csv: list 형식의 data를 CSV 파일로 저장
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
