from utils import *

# 전체 데이터 저장할 리스트
all_data = []

# 각 아파트에 대해 데이터 받아오기
for apt_code in APT_CODE:
    crawl_data(apt_code, all_data)

# 중복 제거
cleaned_data = remove_duplicates(all_data)

# 결과 출력
print(f"총 {len(cleaned_data)}개의 데이터가 수집되었습니다.")

# CSV로 저장
save_to_csv(cleaned_data)
