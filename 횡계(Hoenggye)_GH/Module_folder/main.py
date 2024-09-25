import subprocess
import pandas as pd
from datetime import datetime, timedelta
from Schedule_setting import write_idf_setpoints, run_simulation
import warnings
warnings.filterwarnings(action='ignore')

"""
** main.py - GH_Simulation_ver2.2 사용
- 최종 출력이 되는 파일값들이 달라짐. 환경결과파일만 출력. 에너지출력은 mtr 파일에서 보면되지만 정리한 파일 업로드 예정중.
"""

# RunPeriod
SM = 1 #시작월
SD = 1 #시작일
EM = 6 #종료월
ED = 30 #종료일
TS = 6 #타임스텝(결과출력주기)  1: 시간별, 2, 30분별, 4: 15분별, 6: 10분별

# file and path
weather_file = "/home/agtech_eplus/eplus_KIST_GH/KOR_KW_Daegwallyeong.471000_TMYx.2007-2021.epw"

eplus_path = "/usr/local/EnergyPlus-23-1-0/energyplus-23.1.0"
idf_base_path = "/home/agtech_eplus/eplus_KIST_GH/idf_world/Eplus_HG_kist_SetpointVer(KIST_HG_ver3).idf"
idf_custom_path = "/home/agtech_eplus/eplus_KIST_GH/heatS_up8_VentS_up14.idf"
eplus_file = "/home/agtech_eplus/eplus_KIST_GH/heatS_up8_VentS_up14.idf"
out_files = "/home/agtech_eplus/eplus_KIST_GH/"

out_name = 'heatS_up8_VentS_up14'

# 온실 세팅값 설정
write_idf_setpoints(idf_base_path, idf_custom_path, SM, SD, EM, ED, TS)

# 시뮬레이션 실행
output_csv, output_mtr = run_simulation(eplus_path, weather_file, eplus_file, out_files, out_name)

### 결과값 처리
def make_EnvResultsFile(output_csv,TS,out_name): # 환경값 정리
    depout = pd.read_csv(output_csv)
    depout['Date/Time'] = depout['Date/Time'].str.strip() # 공백 제거 및 형식 확인

    # timestep에 따른 filter 걸기
    time_filter = {
        1: '01/01  01:00:00',
        2: '01/01  00:30:00',
        4: '01/01  00:15:00',
        6: '01/01  00:10:00'
    }

    filter_time = time_filter.get(TS, 'None')
    filter_idx = depout[depout['Date/Time'] == filter_time].index
    
    # drop
    first_idx = filter_idx[0]
    filtered_df = depout.loc[first_idx:]
    filtered_df.reset_index(drop=True,inplace=True)

    # 환경값 파일에 필요한 컬럼들만 골라내기
    need_column = ['Date/Time','Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)'
                ,'Environment:Site Outdoor Air Relative Humidity [%](TimeStep)','Environment:Site Wind Speed [m/s](TimeStep)'
                ,'Environment:Site Diffuse Solar Radiation Rate per Area [W/m2](TimeStep)'
                ,'Environment:Site Direct Solar Radiation Rate per Area [W/m2](TimeStep)'
                ,'THERMAL ZONE BOTTOM:Zone Air Temperature [C](TimeStep)'
                ,'THERMAL ZONE BOTTOM:Zone Air Relative Humidity [%](TimeStep)'
                ,'SPACE TOP:Zone Windows Total Transmitted Solar Radiation Rate [W](TimeStep)']
    envio = filtered_df[need_column]

    # 이름 바꾸기
    envio.columns = ['date','Out_Temp[C]','Out_Humid[%]','WindSP[m/s]','Diffuse_Radiation[W/m2]','Direct_Radiation[W/m2]','In_Temp[C]','In_Humid[%]','In_Radiation[W/m2]']
    envio["Radiation[W/m2]"] = envio['Diffuse_Radiation[W/m2]'] + envio['Direct_Radiation[W/m2]']
    envio = envio.drop(columns=['Diffuse_Radiation[W/m2]','Direct_Radiation[W/m2]'])

    envio_file = 'trial_'+out_name+'_envdata.csv'
    envio.to_csv(envio_file, index=False)

    return envio_file

def Calculate_Energy(output_mtr): # 에너지값 정리
    mtrout = pd.read_csv(output_mtr)

    idx = 228
    mtr_engy = mtrout.iloc[idx:]
    mtr_engy.reset_index(drop=True,inplace=True)

    pd.options.display.float_format = '{:.3f}'.format # 지수표기로 된 숫자를 변환한다.
    mtr_engy.columns = ['date','Fan_elecE(J)','Pumps_elecE(J)','FuelOilE(J)']

    # 1KJ = 1000J, 1MJ = 1000000J
    mtr_engy.loc[:,'Fan_elecE(MJ)'] = mtr_engy['Fan_elecE(J)'] / 1000000
    mtr_engy.loc[:,'Pumps_elecE(MJ)'] = mtr_engy['Pumps_elecE(J)'] / 1000000
    mtr_engy.loc[:,'FuelOilE(MJ)'] = mtr_engy['FuelOilE(J)'] / 1000000

    electricity = (mtr_engy['Fan_elecE(MJ)'].sum() + mtr_engy['Pumps_elecE(MJ)'].sum()).round(2)
    fuelOilE = mtr_engy['FuelOilE(MJ)'].sum().round(2)

    return electricity, fuelOilE

envio_file = make_EnvResultsFile(output_csv,TS,out_name)
electricity, fuelOilE = Calculate_Energy(output_mtr)

### 에너지값, 환경 온도 비교를 위한 처리
def Calculate_Envio_Temp(envio_file): # 구간별(1~2월/3~6월) 평균온도 계산하는 타임
    # 시뮬레이션 환경 계산 결과 파일 가져오기
    envio = pd.read_csv(envio_file).round(2)
    sim_file = envio[['date','In_Temp[C]','In_Humid[%]','In_Radiation[W/m2]']]

    # 데이터 가공 시작
    def from24tozero(datetime_str, _format): # 환경 데이터는 24시 형식으로 나오는데, datetime은 이를 감당할 수 없다고 한다. 이런!

        '''
            * datetime_str: 변환할 날짜/시간 문자열
            * _format: 형식을 지정하는 포맷 문자열
        '''

        datetime_str = str(datetime_str).strip() # 원본에 양쪽 공백이 있었으므로 공백 제거
        try:
            change_datetime = datetime.strptime(datetime_str, _format) # strptime: 문자열을 datetime 객체로 변환
            return change_datetime.strftime(_format) # strftime: 다시 문자열로 고침
        except ValueError:   # datetime 함수가 감당할 수 없는 날짜 문자열(24시)를 만났을 때.
            adj_datetime = datetime_str.replace('24:','00:')
            change_datetime = datetime.strptime(adj_datetime, _format) + timedelta(days=1) # 변환후에 하루 더하여 다음날의 시간으로
            return change_datetime.strftime(_format)
        
    def add_year(date): # datetime은 년도도 있어야 계산할 수 있다고 한다.
        if len(date.split()) == 2:
            month_day, time = date.split()
            month, day = month_day.split('/')
            return f'2024-{month}-{day} {time}'
        else:
            return date
    
    sim_file['date'] = sim_file['date'].map(lambda x:from24tozero(x, "%m/%d %H:%M:%S")) # 24시간을 00시간으로 바꿔준다.

    sim_file['date'] = sim_file['date'].apply(add_year) # 계산을 위해 연도를 붙인것
    sim_file['date'] = pd.to_datetime(sim_file['date'], format='%Y-%m-%d %H:%M:%S')
    sim_file['hour'] = sim_file['date'].dt.hour # 시간별로 바꿈

    winter = sim_file[(sim_file['date'].dt.month == 1) | (sim_file['date'].dt.month == 2)]  # 겨울기간(1~2월) 묶어서 계산
    spr_summ = sim_file[(sim_file['date'].dt.month == 3) | (sim_file['date'].dt.month == 4) | (sim_file['date'].dt.month == 5)| (sim_file['date'].dt.month == 6)] # 따뜻기간(3~6월)

    def DayandNight(hour):
        if 6 <= hour < 18:
            return 'Day'
        else:
            return 'Night'
    
    winter['Day_Night'] = winter['hour'].apply(DayandNight)
    winter_avg_temp = winter.groupby('Day_Night')['In_Temp[C]'].mean().round(1)
    winter_day = winter_avg_temp[0]
    winter_night = winter_avg_temp[1]
    
    spr_summ['Day_Night'] = spr_summ['hour'].apply(DayandNight)
    spr_summ_avg_temp = spr_summ.groupby('Day_Night')['In_Temp[C]'].mean().round(1)
    spr_summ_day = spr_summ_avg_temp[0]
    spr_summ_night = spr_summ_avg_temp[1]

    return winter_day, winter_night, spr_summ_day, spr_summ_night

winter_day, winter_night, spr_summ_day, spr_summ_night = Calculate_Envio_Temp(envio_file)
print(winter_day)
print(winter_night)
print(spr_summ_day)
print(spr_summ_night)
print(electricity)
print(fuelOilE)

# ### 에너지값 확인: 설정 구간(최소 에너지~최대 에너지)에 포함되는지?
# std_min_elecity = 45719.43
# std_max_elecity = 51073.57
# std_min_oil = 141027.81
# std_max_oil = 440702.04

# if (std_min_elecity <= electricity <= std_max_elecity) or (std_min_oil <= fuelOilE <= std_max_oil):