import subprocess
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# RunPeriod
SM = 1 #시작월
SD = 1 #시작일
EM = 6 #종료월
ED = 30 #종료일
TS = 1 #타임스텝(결과출력주기)  1: 시간별, 2, 30분별, 4: 15분별, 6: 10분별

## 월마다 바뀌는 일출/일몰 및 setpoint 값 적용 ##
# 각 월별 일출/일몰 시간
sunrise_times = {1: '7:30', 2: '7:00', 3: '6:30', 4: '6:00', 5: '5:30', 6: '5:00'}
sunset_times = {1: '17:30', 2: '18:00', 3: '18:30', 4: '19:00', 5: '19:30', 6: '20:00'}

# 각 구간(계절별) setpoint 값
setpoint_values = {
        '1-2': [['14.6','14.8','17.3','21.9','17.9','15.4','14.6'],['0','1','0'],['87.3','87.5','85.5','80.0','86.5','88.6','87.3']],
        '3-5': [['16.2','16.0','19.8','24.3','20.6','17.5','16.2'],['0','1','0'],['88.6','89.6','81.0','68.7','78.7','85.3','88.6']],
        '6': [['22.2','21.3','25.5','30.4','26.7','24.1','22.2'],['0','1','0'],['90.6','92.5','80.4','67.1','75.8','85.3','90.6']]
}
# month to str
def MonthToName(mon):
        month_names = ['Jan','Feb','Mar','Apr','May','Jun']
        return month_names[mon - 1]

# time to datetime
def TimeToDatetime(time_str):
        return datetime.strptime(time_str,"%H:%M")

# datetime to str
def DatetimeToStr(time_obj):
        return time_obj.strftime("%H:%M")

# calculate datetime
def CalculateDatetime(time_str, hours):
        time_obj = TimeToDatetime(time_str)
        new_time_obj = time_obj - timedelta(hours=hours)
        return DatetimeToStr(new_time_obj)

# file and path
weather_file = "/home/agtech_eplus/eplus_KIST_GH/KOR_KW_Daegwallyeong.471000_TMYx.2007-2021.epw"

eplus_path = "/usr/local/EnergyPlus-23-1-0/energyplus-23.1.0"
idf_base_path = "/home/agtech_eplus/eplus_KIST_GH/Validation_ch_ing_2.idf"
idf_custom_path = "/home/agtech_eplus/eplus_KIST_GH/trial_one.idf"
eplus_file = "/home/agtech_eplus/eplus_KIST_GH/trial_one.idf"
out_files = "/home/agtech_eplus/eplus_KIST_GH/"

out_name = 'trial_time60'

with open(idf_base_path, 'r') as file:   #idf가 있는 패스
        data = file.readlines()
#        line=data[178]
        data[78] = 'Timestep,%s; \n'%TS    # 아웃풋 출력주기
        data[3524] = '  %s,    !- Begin Month\n' %SM   #시뮬레이션 하고 싶은 시작월
        data[3525] = '  %s,    !- Begin Day of Month \n'%SD    #시뮬레이션 하고 싶은 시작일
        data[3527] = '  %s,    !- End Month \n'%EM    #시뮬레이션 끝내고 싶은 종료 월
        data[3528] = '  %s,    !- End Day of Month \n'%ED    #시뮬레이션 끝내고 싶은 종료 일

        def Modify_ScheduleDay(obj_name, inform_df):  # Schedule:Day:Interval의 값을 수정할 수 있는 함수
                # Schedule:Day:Interval가 포함된 줄 찾기
                for i, line in enumerate(data):
                        if "Schedule:Day:Interval," in line:
                                next_index = i + 1      # Schedule:Day:Interval, 다음 줄 field로 name이 오기 때문에 i + 1

                                # 원하는 이름(!- Name) 찾기
                                if obj_name in data[next_index]:
                                        start_index = i + 4   # 수정할 setpoint의 index
                                        field_value = 1    # 시간이 수정되는 Time 1 부터 시작
                                        value_col = obj_name.split(',')[0]

                                        # 데이터프레임 내 setting value를 삽입하기
                                        for j, row in inform_df.iterrows():
                                                if row['schedule_name'] == value_col:
                                                        if row['schedule_name'] == value_col:
                                                                count_line = 0
                                                                for idx, (time,set_value) in enumerate(zip(row['times'], row['setpoint'])):
                                                                        insert_index = start_index + count_line   # 들어가야 할 위치를 찾는다

                                                                        data.insert(insert_index, '    %s,                   !- Time %d {hh:mm}\n'%(time,idx + 1))
                                                                        count_line += 1

                                                                        if idx == len(row['times']) - 1:    # field값 마지막에는 ;이 들어가기 때문에 마지막 줄이면 다른 양식(;)을 쓰도록 지시
                                                                                data.insert(insert_index + 1, '    %s;                      !- Value Until Time %d\n'%(set_value,idx + 1))
                                                                        else:
                                                                                data.insert(insert_index + 1, '    %s,                      !- Value Until Time %d\n'%(set_value,idx + 1))
                                                                        count_line += 1

                                                                # 기존값 삭제하기
                                                                del_index = start_index + count_line  # insert 마친 지점
                                                                while data[del_index].strip():            # 공백이 나타날때까지 지우기
                                                                        del data[del_index]

        for mon in range(SM,EM+1):
                sunrise = sunrise_times[mon]
                sunset = sunset_times[mon]

                # select setpoint with month
                if 1<= mon <=2:
                        setpoint = setpoint_values['1-2']
                elif 3<= mon <=5:
                        setpoint = setpoint_values['3-5']
                else:
                        setpoint = setpoint_values['6']

                month_end = MonthToName(mon)

                # 변경할 값을 위한 데이터프레임
                setpoint_df = pd.DataFrame({
                        'schedule_name' : [f'Schedule Day 4_{month_end}',f'Schedule Day 7_{month_end}',f'Humid Setpoint Schedule_{month_end}'],
                        'times' : [[CalculateDatetime(sunrise,2),sunrise,'12:00',CalculateDatetime(sunset,2),sunset,CalculateDatetime(sunset,-2),'24:00'],[sunrise,sunset,'24:00'],[CalculateDatetime(sunrise,2),sunrise,'12:00',CalculateDatetime(sunset,2),sunset,CalculateDatetime(sunset,-2),'24:00']],
                        'setpoint' : setpoint
                })

                Modify_ScheduleDay(f"Schedule Day 4_{month_end},", setpoint_df)
                Modify_ScheduleDay(f"Schedule Day 7_{month_end},", setpoint_df)
                Modify_ScheduleDay(f"Humid Setpoint Schedule_{month_end},", setpoint_df)

with open(idf_custom_path, 'w') as file:  #
        file.writelines(data)
        file.close()
        
        # df = subprocess.call([eplus_path, "-w", weather_file, "-d", out_files, "-p", out_name, eplus_file])
        df = subprocess.Popen([eplus_path, "-w", weather_file, "-d", out_files, "-p", out_name, "-r", eplus_file], stdout=subprocess.PIPE, shell =False)
        output, err = df.communicate()
        #print (output.decode('utf-8'))
        #if not err is None:
                #print(err.decode('utf-8'))
        depout = pd.read_csv("/home/agtech_eplus/eplus_KIST_GH/"+out_name+"out.csv") #결과값 읽기

        # y_out = {
        #         'Out_temp': depout['Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)'],
        #         'Out_humid': depout['Environment:Site Outdoor Air Relative Humidity [%](TimeStep)'],
        #         'In_A_temp': depout['A_BOT:Zone Mean Air Temperature [C](TimeStep)'],
        #         'In_A_humid': depout['A_BOT:Zone Air Relative Humidity [%](TimeStep)'],
        #         'A_light_E': depout['A_BOT LIGHTS:Lights Electric Power [W](TimeStep)'],
        #         'A_heatingE': depout['ZONE3AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'],
        #         'A_coolingE': depout['ZONE3AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'],
        # }

        # result_output = pd.DataFrame(y_out)
        # result_output.to_csv('eplus_case1.csv', index=False)

        # 공백 제거 및 형식 확인
        depout['Date/Time'] = depout['Date/Time'].str.strip()

        # timestep에 따른 filter 걸기
        time_filter = {
                1: '01/01  01:00:00',
                2: '01/01  00:30:00',
                4: '01/01  00:15:00',
                6: '01/01  00:10:00'
        }

        filter_time = time_filter.get(TS, 'None') 
        filter_idx = df[df['Date/Time'] == filter_time].index

        # drop
        first_idx = filter_idx[0]
        filtered_df = depout.loc[first_idx:]
        filtered_df.reset_index(drop=True,inplace=True)

        ## 환경값과 에너지값 분리 전 컬럼 이름 정의하고 바꾸기
        """
        환경값(Timestep)
        * Environment:Site Outdoor Air Drybulb Temperature [C] - Out_Temp
        * Environment:Site Outdoor Air Relative Humidity [%] - Out_Humid
        * Environment:Site Wind Speed [m/s] - WindSP
        * Environment:Site Diffuse Solar Radiation Rate per Area [W/m2] - Diffuse_Radiation
        * Environment:Site Direct Solar Radiation Rate per Area [W/m2] - Direct_Radiation
        * THERMAL ZONE BOTTOM:Zone Air Temperature [C] - In_Temp
        * THERMAL ZONE BOTTOM:Zone Air Relative Humidity [%] - In_Humid
        * THERMAL ZONE TOP:Zone Air Temperature [C] - x
        * THERMAL ZONE TOP:Zone Air Relative Humidity [%] - x

        에너지값(Hourly)
        * EXHAUST FAN 1~7:Fan Electricity Energy [J] - Fan_elecE
        * FOG SYSTEM:Water Use Equipment Heating Energy [J] - x(여기서는 0만 나옴, 확인 후 값이 NaN이거나 0이면 지우라고 해야할 듯)
        * Whole Building:Facility Total Electricity Demand Rate [W] - 전력수요, Tot_Elec_Demand
        * HW BOILER:Boiler Heating Energy [J] - Boiler_HeatE
        * VAR SPD PUMP:Pump Electricity Energy [J] - x

        Meter(Monthly) - 이거는 meter.csv에 나와있으니 삭제?
        * Electricity:Facility [J](Monthly)
        * FuelOilNo2:Facility [J](Monthly)
        * EnergyTransfer:Facility [J](Monthly)
        """
        # 불필요한 컬럼 삭제
        drop_list = filtered_df.columns[[7, 8, 9, 10, 11, 12, 15, 16, 17, 20, 21, 22, 23]]
        filtered_df = filtered_df.drop(drop_list,axis=1)

        # 이름 바꾸기
        filtered_df.columns = ['date','Out_Temp','Out_Humid','WindSP','Diffuse_Radiation','Direct_Radiation','Fan_elecE','In_Temp','In_Humid','Tot_Elec_Demand','Boiler_HeatE']
        
        # 환경값 분리
        envio = filtered_df.iloc[:,[0,1,2,3,4,5,7,8]]
        envio["Radiation"] = envio['Diffuse_Radiation'] + envio['Direct_Radiation']
        envio = envio.drop(columns=['Diffuse_Radiation','Direct_Radiation'])

        envio.to_csv('trial_'+out_name+'_envdata.csv', index=False)

# print(result_output)

### 에너지 정보 출력
def find_index(data, report_name, energy_type): # 원하는 energy_type의 Monthly report를 찾을 수 있도록 인덱스 제공
    for idx, item in enumerate(data):
        if item[0] == report_name and any(energy_type in sublist for sublist in item[1]):
            return idx
    return -1

report_name = 'Custom Monthly Report'
energy_types = ['FAN ELECTRICITY ENERGY [kWh]','BASEBOARD TOTAL HEATING ENERGY [kWh]','BOILER HEATING ENERGY [kWh]']

from eppy.results import readhtml
import pprint
pp = pprint.PrettyPrinter()

fname = "/home/agtech_eplus/eplus_KIST_GH/"+out_name+"tbl.htm" # output인 html 파일의 table을 읽을 것임
html_doc = open(fname, 'r').read()
htables = readhtml.titletable(html_doc)

results = {}
for energy_type in energy_types:
    index = find_index(htables, report_name, energy_type)
    if index != -1: # find_index에서 값을 찾을 수 없으면 -1을 반환하므로
        results[energy_type] = htables[index]
        firstitem = htables[index]

# 각각의 monthly report 추출
baseboard_heatE = results['BASEBOARD TOTAL HEATING ENERGY [kWh]']
boiler_heatE = results['BOILER HEATING ENERGY [kWh]']
fan_elecE = results['FAN ELECTRICITY ENERGY [kWh]']

def Period_Energy_value(data_list, target_value): # report에서 에너지 값 가져오기
    for index, row in enumerate(data_list):
        if row[0] == target_value:
            return data_list[index][1]
        
data_lists = [baseboard_heatE[1], boiler_heatE[1], fan_elecE[1]]
target_value = 'Annual Sum or Average'

energy_results = []
for data_list in data_lists:
    energy_result = Period_Energy_value(data_list, target_value)
    energy_results.append(energy_result)

# print(f'Sum or Average of BaseBoeard Heat Energy:{energy_results[0]}')
# print(f'Sum or Average of Boiler Heat Energy:{energy_results[1]}')
# print(f'Sum or Average of Fan Electricity Heat Energy:{energy_results[2]}')

# Annual Building Utility Performance Summary
for title, table in htables:
    if title == "Site and Source Energy":
        Tot_energy = table[1][1]

# 에너지결과값 저장하는 데이터프레임
Energy_data = {
    'Description':[
        'Sum or Average of BaseBoeard Heat Energy(kWh)',
        'Sum or Average of Boiler Heat Energy(kWh)',
        'Sum or Average of Fan Electricity Heat Energy(kWh)',
        'Total Use Energy(kWh)',
    ],
    'Value':[
        energy_results[0],
        energy_results[1],
        energy_results[2],
        Tot_energy
    ]
}

Energy_df = pd.DataFrame(Energy_data)

# End Uses
columns = htables[3][1][0]
data = htables[3][1][1:]

End_uses_table = pd.DataFrame(data,columns=columns)
End_uses_table.drop(index=14,inplace=True)
End_uses_table.set_index('', inplace=True)

idx_list = list(End_uses_table.index)
col_list = list(End_uses_table.columns)

additional_data = []
for i, idx in enumerate(idx_list):
    for j, col in enumerate(col_list):
        if End_uses_table.loc[idx, col] != 0.0:
            additional_data.append({
                'Description':f"Uses: {col} - {idx}:",
                'Value': End_uses_table.loc[idx, col]
            })

add_df = pd.DataFrame(additional_data)
Energy_df = pd.concat([Energy_df, add_df], ignore_index=True)

# 최종 에너지값 저장
Energy_df.to_csv('trial_'+out_name+'_energy.csv', index=False)