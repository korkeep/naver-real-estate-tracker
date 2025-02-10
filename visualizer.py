from utils import *

# 한글 폰트 설정
set_font()

# CSV 파일 패턴에 맞는 파일을 로드 (data 폴더에 있는 모든 CSV 파일)
data = load_from_csv('./data/*_data.csv')

# 가격 변동 시각화
plot_price_change(data)