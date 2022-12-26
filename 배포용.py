# 라이브러리 불러오기 
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from shapely.geometry import Point, Polygon
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

from shapely.geometry import Point, Polygon, LineString
import matplotlib.pyplot as plt
import matplotlib
import math

# 꽉 찬 화면
st.set_page_config(layout="wide")

# 이미지 가져오기
st.image('https://github.com/8900j/BIG_project/blob/main/JH.png?raw=true')

# 데이터 가져오기
dt = pd.read_csv('https://raw.githubusercontent.com/8900j/BIG_project/main/test_predict_complete_undummify.csv')
metro = pd.read_csv('https://raw.githubusercontent.com/8900j/BIG_project/main/subway_re.csv')
bus = pd.read_csv('https://raw.githubusercontent.com/8900j/BIG_project/main/JUNG_BUS.csv')
# --------------------------------------------------------------------------------------------------------------------------------------------

tab1, tab2 = st.tabs(['직원용 웹사이트','고객용 웹사이트'])

with tab1:

    # 직원용 웹사이트
    st.title('[1] 직원용 웹사이트')

    st.markdown('#### 차액 기준 내림차순 고객 리스트 TOP 5')    
    st.dataframe(dt[['단지명','주소','예측월세가격', '기존월세가격', '월수입차액']].head())

    st.markdown('#### 고객 정보 검색')
    a,b,c = st.columns([1,1,1])

    idx = a.text_input(f'index 번호(0~{len(dt)})를 입력하세요') # 유저한테 글자 입력받기

    if idx :
        i=int(idx)

        st.markdown("""<style>[data-testid="stMetricValue"] {font-size: 80px;}</style>""",unsafe_allow_html=True,)
        st.metric(label=f'index {idx}번의 예측월세가격(단위: 만 원)', value=int(dt.iloc[i]['예측월세가격']), delta=int(dt.iloc[i]['월수입차액']))
        tmp=dt.iloc[[i]]

        # 1. 기본 정보(표 / 위경도 지도): 단지명, 전용면적, 주소
        st.markdown('**기본 정보**')
        a,b = st.columns([1,2])
        basic=pd.DataFrame({'단지명':tmp['단지명'],'전용면적(㎡)':tmp['전용면적'],'주소':tmp['주소']})
        a.dataframe(basic)
        #지도
        # 위도
        home_lat = tmp['위도']
        # 경도
        home_lng = tmp['경도']
        
        for k in range(len(metro)):
            if dt.loc[i, '지하철역'] == metro.loc[k, '역명']:
                metro_station = metro.loc[k, '역명']
                # print([metro.loc[i, '역사위치위도'], metro.loc[i, '역사위치경도']])
                metro_lat = metro.loc[k,'역사위치위도']
                metro_lng = metro.loc[k,'역사위치경도']
                break
                
        # 배경지도 map (center 위치)
        baegyeong = folium.Figure(width=400, height=400)
        map = folium.Map(location=[home_lat, home_lng],
                         zoom_start=15).add_to(baegyeong)
        # 지도 map에 Marker 추가하기
        folium.Marker([home_lat, home_lng],
                      tooltip = dt.iloc[i]['단지명'],
                     ).add_to(map)
        # 지하철역 marker 추가
        folium.Marker(location=[metro_lat, metro_lng],
                      tooltip = metro_station,
                      zoom_start=15).add_to(map)

        # 버스정류장 표시
        # folium.Marker([bus_lat, bus_lng],
        #               popup=)
        # 500m 반경 원 추가하기
        folium.Circle(
            location=[home_lat, home_lng],
            radius=500,
            popup="반경 500m",
            color="#3186cc",
            fill=True,
            fill_color="#3186cc",
        ).add_to(map)

        # call to render Folium map in Streamlit
        b.st_data = st_folium(baegyeong, width=400, height=400)
        # 2. 가격 정보(차트): 예측월세가격, 기존월세가격, 월수입차액
        m=['기존월세가격','예측월세가격']
        n=[int(tmp['기존월세가격'][i]),int(tmp['예측월세가격'][i])]
        price=pd.DataFrame({'구분':m,'가격':n})
        fig = px.bar(price, x='구분', y='가격',text_auto=True, width=400, height=400) # text_auto=True 값 표시 여부, title='제목'
        a1,a2,a3=st.columns(3)
        with a1:
            st.markdown('**가격비교 차트**')
            st.plotly_chart(fig)
        with a2:
            st.metric(label='기존월세가(만 원)', value=int(dt.iloc[i]['기존월세가격']))
            st.metric(label='예측월세가(만 원)', value=int(dt.iloc[i]['예측월세가격']))
            st.metric(label='월수입차액(만 원)', value=int(dt.iloc[i]['월수입차액']))

        # 3. 반경 1km 내 관광정보(차트): 맛집, 문화공간, 문화재, 쇼핑
        st.markdown('**반경 1km 내 관광정보 (개수)**')
        ten=tmp[['맛집', '문화공간', '문화재', '쇼핑']]
        st.dataframe(ten)

        # 4. 교통 정보(표): 지하철역, 지하철역까지(m), 버스정류장, 버스정류장까지(m)
        st.markdown('**최단거리 대중교통 정보**')
        ten=tmp[['지하철역', '지하철역까지(m)', '버스정류장', '버스정류장까지(m)']]
        st.dataframe(ten)
        
        st.markdown('**고객 연락수단 (email, sns 등)**')
        a,b,c,d = st.columns([1,1,1,1])
        a.markdown(f'##### [📨e-mail](mailto:ktaivle@kt.com)') # 에이블스쿨 이메일
        insta_url='https://www.instagram.com/aivlestory/?igshid=YmMyMTA2M2Y%3D' # 에이블스쿨 인스타그램
        b.markdown(f'##### [⭐instagram]({insta_url})')

    else:
        txt = '<p style="font-family:Malgun Gothic; color:cornflowerblue; font-size: 15px;">▲ index 번호를 입력해주세요</p>'
        st.markdown(txt, unsafe_allow_html=True)

# st.markdown('#### 고객 연락수단(email 전송, sns 연동 등)')
# a,b = st.columns([1,1])
# a.markdown(f'##### [📨e-mail](mailto:ktaivle@kt.com)') # 에이블스쿨 이메일
# insta_url='https://www.instagram.com/aivlestory/?igshid=YmMyMTA2M2Y%3D' # 에이블스쿨 인스타그램
# b.markdown(f'##### [⭐instagram]({insta_url})')

# --------------------------------------------------------------------------------------------------------------------------------------------

with tab2:

    # 고객용 웹사이트
    st.title('[2] 고객용 웹사이트')

    new_title = '<p style="font-family:Malgun Gothic; color:lightcoral; font-size: 30px;">당신의 공간을 에어비앤비하세요!</p>'
    st.markdown(new_title, unsafe_allow_html=True)

    st.markdown('#### 정보를 입력해주세요.')
    a,b,c,d = st.columns([1,1,1,1])
    a.markdown('**단지명**')
    name=a.text_input('예시) 마이홈') # 유저한테 글자 입력받기
    b.markdown('**전용면적(㎡)**')
    size=b.text_input('예시) 100') # 유저한테 글자 입력받기
    c.markdown('**층수**')
    floor=c.text_input('예시) 1') # 유저한테 글자 입력받기
    d.markdown('**도로명 주소**')
    address=d.text_input('예시) 중구 명동10길 29') # 유저한테 글자 입력받기

    # 입력 정보로 데이터프레임 input_df 만들기
    input_df=pd.DataFrame({'단지명':[name],'전용면적':[size],'층':[floor],'도로명주소':[address]})

    # input_df에 위경도 컬럼 추가
    if address:
        geolocator = Nominatim(user_agent="GTA Lookup")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
        location = geolocator.geocode(address)
        lat = location.latitude
        lon = location.longitude
        input_df['위도']=lat
        input_df['경도']=lon
    else:
        txt = '<p style="font-family:Malgun Gothic; color:cornflowerblue; font-size: 15px;">▲ 주소를 입력해주세요!</p>'
        st.markdown(txt, unsafe_allow_html=True)

    st.dataframe(input_df)

    st.markdown('#### 메인지표 3가지')
    st.metric(label="예측된 일일가격", value="60,000won", delta="20,000won")
    main=dt['예측월세가격'][:10]
    st.bar_chart(main)

    st.markdown('#### 외부지표 6가지')