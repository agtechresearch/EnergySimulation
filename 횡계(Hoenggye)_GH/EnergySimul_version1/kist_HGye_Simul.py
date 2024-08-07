import subprocess
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# RunPeriod
SM = 1 #시작월
SD = 1 #시작일
EM = 6 #종료월
ED = 30 #종료일
TS = 6 #타임스텝(결과출력주기)  1: 시간별, 2, 30분별, 4: 15분별, 6: 10분별

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
idf_custom_path = "/home/agtech_eplus/eplus_KIST_GH/test.idf"
eplus_file = "/home/agtech_eplus/eplus_KIST_GH/test.idf"
out_files = "/home/agtech_eplus/eplus_KIST_GH/"

out_name = 'test'

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

# print(result_output)