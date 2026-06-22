import streamlit as st

# 1. 사이드바: 모드 선택
mode = st.sidebar.radio("모드 선택", ["시험 모드", "실무 모드"])

st.title("건축사 시험 지문 분석기")

if mode == "실무 모드":
    st.warning("🚧 현재 개발 중인 기능입니다. 시험 모드를 이용해 주세요.")
else:
    # 2. 시험 모드 입력 템플릿
    st.header("입력창 (시험 문제지 조건)")
    
    col1, col2 = st.columns(2)
    with col1:
        site_area = st.number_input("대지면적 (㎡)", value=500.0)
        coverage_limit = st.number_input("건폐율 제한 (%)", value=60.0)
    with col2:
        floor_area_limit = st.number_input("용적률 제한 (%)", value=200.0)
        parking_required = st.number_input("필요 주차대수", value=8)

    # 3. [핵심] 알고리즘/로직 (이곳을 체크해 보세요!)
    def calculate_results(site_area, coverage_limit, floor_area_limit, parking_required):
        """
        건축사님! 이 함수가 프로그램의 '뇌'입니다.
        시험 지문 조건이 법규보다 우선하도록 설계되어 있습니다.
        """
        
        # --- 규칙 1: 건폐율 계산 ---
        # 지문에서 건폐율을 건드리면 즉시 반영됩니다.
        max_building_area = site_area * (coverage_limit / 100)
        
        # --- 규칙 2: 용적률 계산 ---
        max_total_floor_area = site_area * (floor_area_limit / 100)
        
        # --- 규칙 3: 주차장 ---
        # 지문에서 주차 조건을 바꾸면 계산 결과가 바로 바뀝니다.
        parking_lot_area = parking_required * 12.5 # 일반형 2.5 * 5.0
        
        return {
            "max_building_area": max_building_area,
            "max_total_floor_area": max_total_floor_area,
            "parking_lot_area": parking_lot_area
        }

    # 4. 결과 출력
    if st.button("분석 실행"):
        results = calculate_results(site_area, coverage_limit, floor_area_limit, parking_required)
        
        st.subheader("분석 결과")
        st.write(f"- 최대 건축면적: {results['max_building_area']} ㎡")
        st.write(f"- 최대 연면적: {results['max_total_floor_area']} ㎡")
        st.write(f"- 주차장 필요 면적: {results['parking_lot_area']} ㎡")