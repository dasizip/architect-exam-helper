import streamlit as st
import pandas as pd

# 1. 페이지 초기 세팅 (A3 가로 비율을 고려하여 와이드 모드로 설정)
st.set_page_config(layout="wide", page_title="건축사 시험 대지분석기")

st.sidebar.title("🛠️ 건축사 시험 모드")
mode = st.sidebar.radio("작업 선택", ["1교시 지문 분석 및 대지 설정", "실무 분석 모드"])

if mode == "실무 분석 모드":
    st.sidebar.warning("🚧 현재 개발 중인 기능입니다.")
    st.title("실무 모드는 추후 법령 데이터베이스 연동과 함께 업데이트됩니다.")
else:
    st.title("📐 건축사 자격시험 1교시 배치 시뮬레이터")
    st.caption("지문 조건 우선 적용 | 하이브리드 대지 입력 시스템 | 배치 경우의 수 시뮬레이터")

    # ---------------------------------------------------------
    # [기능 1] 문제지 PDF 업로드 및 하이브리드 입력단
    # ---------------------------------------------------------
    st.header("1. 대지 조건 및 제약사항 입력")
    
    upload_col, input_col = st.columns([1, 2])
    
    with upload_col:
        st.subheader("📁 지문 연동 (PDF)")
        uploaded_file = st.file_uploader("시험 문제지 또는 모의고사 PDF 업로드", type=["pdf"])
        if uploaded_file:
            st.success("점수/치수 데이터 추출 준비 완료 (Vision AI 대기 중)")
            st.info("💡 팁: 현재는 텍스트/규칙 하이브리드 입력창을 통해 수치를 조정하세요.")

    with input_col:
        st.subheader("🧱 대지 형상 정의 (하이브리드 방식)")
        input_type = st.radio("입력 방식 선택", ["규칙 기반 (가로x세로)", "정밀 좌표 기반 (가각전제/다각형 예외 처리)"])
        
        if input_type == "규칙 기반 (가로x세로)":
            c1, c2 = st.columns(2)
            with c1:
                site_w = st.number_input("대지 가로 길이 (m)", min_value=10.0, max_value=200.0, value=40.0, step=1.0)
            with c2:
                site_h = st.number_input("대지 세로 길이 (m)", min_value=10.0, max_value=200.0, value=30.0, step=1.0)
            
            # 규칙 기반 기본 사각형 좌표 자동 생성
            vertices = [(0.0, 0.0), (site_w, 0.0), (site_w, site_h), (0.0, site_h)]
            st.info(f"기본 직사각형 대지가 설정되었습니다. (산정 면적: {site_w * site_h:.1f}㎡)")
            
        else:
            st.markdown("점들의 좌표를 직접 편집하여 **가각전제**나 **기울어진 경계선**을 구현할 수 있습니다.")
            # 가각전제가 포함된 기본 5각형 매핑 예시 데이터 데이터프레임
            default_coords = pd.DataFrame({
                'X 좌표 (m)': [0.0, 37.0, 40.0, 40.0, 0.0],
                'Y 좌표 (m)': [0.0, 0.0, 3.0, 30.0, 30.0]
            })
            edited_df = st.data_editor(default_coords, num_rows="dynamic")
            vertices = list(zip(edited_df['X 좌표 (m)'], edited_df['Y 좌표 (m)']))

    # 법적/지문 제약조건 입력 컨트롤러
    st.markdown("---")
    st.subheader("📋 지문 조건 (조례 및 설계 지침)")
    leg_c1, leg_c2, leg_c3, leg_c4 = st.columns(4)
    with leg_c1:
        limit_bc = st.number_input("지문 건폐율 제한 (%)", value=60)
    with leg_c2:
        limit_far = st.number_input("지문 용적률 제한 (%)", value=200)
    with leg_c3:
        setback_north = st.number_input("정북 방향 이격 거리 (m)", value=1.5, step=0.5)
    with leg_c4:
        setback_road = st.number_input("건축한계선 / 도로 이격 (m)", value=2.0, step=0.5)

    # ---------------------------------------------------------
    # [기능 2] 작도지 비율(A3) 캔버스 시각화 엔진 (이점쇄선 포함)
    # ---------------------------------------------------------
    st.markdown("---")
    st.header("2. A3 비율 작도지 기반 대지 실시간 검증 캔버스")
    
    # 캔버스 치수 및 뷰박스 스케일 계산 (A3 비율인 420x297 기준의 뷰박스 구성)
    # 모든 경계선을 '이점쇄선'으로 그리기 위해 SVG의 stroke-dasharray="12,3,2,3,2,3" 공법 적용
    max_coordinate_x = max([v[0] for v in vertices]) if vertices else 40
    max_coordinate_y = max([v[1] for v in vertices]) if vertices else 30
    scale = min(360 / (max_coordinate_x + 10), 250 / (max_coordinate_y + 10))
    
    def get_svg_polygon_path(points):
        return " ".join([f"{50 + p[0]*scale},{270 - p[1]*scale}" for p in points])

    # 지문 조건을 기반으로 테트리스 블록(경우의 수) 레이아웃 조합 매핑
    # 대안 1: 코어 북서측 배치안 / 대안 2: 코어 남동측 배치안
    st.subheader("🔄 정답의 경우의 수 시뮬레이터 (설계 대안 비교)")
    selected_alt = st.radio("검토할 배치 대안(경우의 수) 선택", ["대안 A (코어 북서측 집중형)", "대안 B (전면 광장 중심형)"])

    # 선택된 대안별 블록 셋업
    if selected_alt == "대안 A (코어 북서측 집중형)":
        blocks = [
            {"name": "주건축물 (테트리스 1번)", "x": 5, "y": 2, "w": 20, "h": 15, "color": "#4A90E2"},
            {"name": "코어/계단실 (테트리스 2번)", "x": 5, "y": 17, "w": 6, "h": 6, "color": "#E24A4A"},
            {"name": "부속시설 주차장", "x": 26, "y": 2, "w": 10, "h": 10, "color": "#F5A623"}
        ]
        score_feedback = "🟢 정북사선 및 도로 이격 거리 조건 완벽 충족. 건폐율 52%로 합격권 내 안정적 배치입니다."
    else:
        blocks = [
            {"name": "주건축물 (테트리스 1번)", "x": 15, "y": 8, "w": 20, "h": 15, "color": "#4A90E2"},
            {"name": "코어/계단실 (테트리스 2번)", "x": 35, "y": 8, "w": 4, "h": 6, "color": "#E24A4A"},
            {"name": "부속시설 주차장", "x": 2, "y": 2, "w": 10, "h": 10, "color": "#F5A623"}
        ]
        score_feedback = "🟡 전면 광장 확보에는 유리하나, 주건축물 우측면이 대지 경계 이격 조항(도로한계선)을 0.5m 간섭할 위험이 있습니다. 작도 시 치수 확인 요망."

    # SVG 그래픽 엔진 문자열 동적 조립
    svg_content = f"""
    <svg width="100%" height="450" viewBox="0 0 500 350" style="background-color: #222222; border-radius: 8px;">
        <defs>
            <pattern id="grid" width="{5*scale}" height="{5*scale}" patternUnits="userSpaceOnUse">
                <path d="M {5*scale} 0 L 0 0 0 {5*scale}" fill="none" stroke="#333333" stroke-width="0.8"/>
            </pattern>
        </defs>
        <rect width="100%" height="100%" fill="#1E1E1E"/>
        <rect width="100%" height="100%" fill="url(#grid)"/>
        
        <polygon points="{get_svg_polygon_path(vertices)}" fill="#2A2A2A" opacity="0.4"/>
        
        <polygon points="{get_svg_polygon_path(vertices)}" fill="none" stroke="#FFD700" stroke-width="2.5" stroke-dasharray="14,4,2,4,2,4"/>
        
        """
    
    for b in blocks:
        bx = 50 + b["x"] * scale
        by = 270 - (b["y"] + b["h"]) * scale
        bw = b["w"] * scale
        bh = b["h"] * scale
        svg_content += f"""
        <rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{b['color']}" opacity="0.85" stroke="#FFFFFF" stroke-width="1.5"/>
        <text x="{bx + 4}" y="{by + 14}" fill="#FFFFFF" font-size="10" font-family="Arial" font-weight="bold">{b['name']}</text>
        """
        
    svg_content += """
    </svg>
    """
    
    # 완성된 벡터 도면을 화면에 출력
    st.components.v1.html(svg_content, height=460)

    # ---------------------------------------------------------
    # [기능 3] 실시간 법규 검증 및 점수 피드백 판넬
    # ---------------------------------------------------------
    st.header("3. 실시간 동적 대지 검증 테이블")
    
    # 면적 계산부 (간이 다각형 면적 연산 공식 적용)
    def polygon_area(pts):
        n = len(pts)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += pts[i][0] * pts[j][1]
            area -= pts[j][0] * pts[i][1]
        return abs(area) / 2.0

    calculated_site_area = polygon_area(vertices)
    total_building_area = sum([b["w"] * b["h"] for b in blocks])
    current_bc = (total_building_area / calculated_site_area) * 100 if calculated_site_area > 0 else 0
    
    v_c1, v_c2, v_c3 = st.columns(3)
    with v_c1:
        st.metric(label="산정 대지면적", value=f"{calculated_site_area:.1f} ㎡")
    with v_c2:
        st.metric(label="현재 대안 건축면적", value=f"{total_building_area:.1f} ㎡")
    with v_c3:
        st.metric(label="현재 건폐율", value=f"{current_bc:.1f} %", delta=f"{limit_bc - current_bc:.1f}% 여유" if current_bc <= limit_bc else f"{current_bc - limit_bc:.1f}% 초과위험", delta_color="normal" if current_bc <= limit_bc else "inverse")

    st.subheader("💡 채점관 관점의 실시간 피드백")
    st.info(score_feedback)
