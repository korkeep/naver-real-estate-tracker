import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# 시각화 스타일 설정
sns.set(style="whitegrid")

# CSV 파일 불러오기
def load_data(file_path):
    data = pd.read_csv(file_path, encoding='utf-8')
    
    # 날짜 형식으로 변환
    data['날짜'] = pd.to_datetime(data['날짜'], format='%Y%m%d')
    
    # '호가' 컬럼을 숫자 형식으로 변환
    data['호가'] = data['호가'].apply(lambda x: convert_price_to_numeric(x))
    
    return data

# '호가'를 숫자 형식으로 변환하는 함수
def convert_price_to_numeric(price_str):
    try:
        # 예: "10억 2,000" -> 1020000000
        price_str = price_str.replace("억", "00000000").replace(",", "")
        return int(price_str)
    except:
        return None

# 데이터 불러오기 (파일 경로는 해당하는 CSV 파일로 수정)
file_path = './data/250128_data.csv'
data = load_data(file_path)

# 날짜별 평균 호가 계산
average_prices = data.groupby('날짜')['호가'].mean().reset_index()

# 시계열 그래프 그리기
plt.figure(figsize=(10, 6))
plt.plot(average_prices['날짜'], average_prices['호가'], marker='o', color='b', label='평균 호가')

# 그래프에 제목과 레이블 추가
plt.title('시간에 따른 평균 호가 변화', fontsize=16)
plt.xlabel('날짜', fontsize=12)
plt.ylabel('평균 호가 (원)', fontsize=12)
plt.xticks(rotation=45)  # 날짜가 겹치지 않도록 회전
plt.grid(True)
plt.tight_layout()

# 그래프 출력
plt.show()

# 가격 변동을 더 잘 보여주기 위한 히트맵 (가격변경 상태별로 색깔 변동)
price_change_pivot = data.pivot_table(index='날짜', columns='가격변경', values='호가', aggfunc='mean')

plt.figure(figsize=(10, 6))
sns.heatmap(price_change_pivot, cmap='coolwarm', annot=True, fmt=".0f", cbar_kws={'label': '호가 (원)'})
plt.title('가격변경 상태에 따른 평균 호가', fontsize=16)
plt.xlabel('가격변경 상태', fontsize=12)
plt.ylabel('날짜', fontsize=12)
plt.tight_layout()
plt.show()
