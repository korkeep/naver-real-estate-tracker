import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib.dates as mdates
import glob
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 폰트 경로를 .env에서 불러오기
FONT_PATH = os.getenv("FONT_PATH")

# 한글 폰트 설정 (Windows에서 '맑은 고딕' 폰트를 사용)
def set_font():
    font_prop = font_manager.FontProperties(fname=FONT_PATH)
    plt.rcParams['font.family'] = font_prop.get_name()

# 데이터 로드 함수
def load_data(file_path_pattern):
    # file_path_pattern에 맞는 CSV 파일들을 모두 읽어들인다.
    file_paths = glob.glob(file_path_pattern)
    
    # 모든 데이터를 하나의 DataFrame으로 합치기
    data = pd.concat([pd.read_csv(file) for file in file_paths], ignore_index=True)
    
    # '호가' 컬럼을 숫자로 변환
    data['호가'] = pd.to_numeric(data['호가'], errors='coerce')
    
    # '수집날짜'를 datetime 형식으로 변환
    data['수집날짜'] = pd.to_datetime(data['수집날짜'], format='%y%m%d')
    
    return data

# 가격 변동 시각화 함수
def plot_price_change(data):
    # 가격변경이 'SAME'인지 여부는 중요하지 않으므로 모든 데이터를 사용
    # 아파트별로 데이터를 그룹화
    grouped_by_apt = data.groupby('매물명')
    
    # 아파트별로 그룹화된 데이터 확인
    #for apt, group in grouped_by_apt:
    #    print(f'--- {apt} 아파트 ---')
    #    print(group.head())  # 각 아파트별 데이터의 처음 5개 행 출력
    #    print("\n")  # 구분을 위해 줄바꿈 추가
    
    # 아파트별로 시각화
    for apt, group in grouped_by_apt:
        plt.figure(figsize=(12, 6))
        
        # 면적별로 그룹화
        grouped_by_area = group.groupby('면적')

        # 면적별로 그룹화된 데이터 확인
        #for area, area_group in grouped_by_area:
        #    print(f'--- {area} 면적 ---')
        #    print(area_group.head())  # 각 면적별 데이터의 처음 5개 행 출력
        #    print("\n")  # 구분을 위해 줄바꿈 추가
        
        # 면적별로 가격을 시각화
        for area, area_group in grouped_by_area:
            # 최저 가격, 최고 가격, 평균 가격 계산
            min_price = area_group['호가'].min()
            max_price = area_group['호가'].max()
            mean_price = area_group['호가'].mean()

            # 면적별 색상 설정
            if area == 46:
                color = 'blue'
            elif area == 56:
                color = 'green'
            elif area == 69:
                color = 'orange'
            elif area == 81:
                color = 'red'
            else:
                color = 'gray'

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


# 주요 실행 함수
if __name__ == '__main__':
    
    # 한글 폰트 설정
    set_font()
    
    # CSV 파일 패턴에 맞는 파일을 로드 (data 폴더에 있는 모든 CSV 파일)
    data = load_data('./data/*_data.csv')
    
    # 가격 변동 시각화
    plot_price_change(data)