# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.

원본 코드: EnergyPlusSimul.py
"""
import subprocess
import pandas as pd
import numpy as np

# 수정할 변수들
SM = 9 #시작월
SD = 1 #시작일
EM = 9 #종료월
ED = 5 #종료일
TS = 4 #타임스텝(결과출력주기)  1: 시간별, 2, 30분별, 4: 15분별, 6: 10분별

# AC_Heating_set_tempUnt7=10 # 0시-7시 Heating setpoint
# AC_Heating_set_tempUnt17=10 # 7시-17시 Heating setpoint
# AC_Heating_set_tempUnt24=10 # 17시-24시 Heating setpoint
# AC_Cooling_set_tempUnt7=25 # 0시-7시 Cooling setpoint
# AC_Cooling_set_tempUnt20=30 # 7시-20시 Cooling setpoint
# AC_Cooling_set_tempUnt24=15# 20시-24시 Cooling setpoint

# 해당 데이터프레임은 Schedule:Compact field 값 수정용
setpoint_df = pd.DataFrame(
        {'schedule_name' : ['HEATING SETPOINTS','COOLING SETPOINTS','HEATING SETPOINTS_2','COOLING SETPOINTS_2'],
         'times' : [['3:00','6:00','7:00','14:00','17:00','24:00'],['3:00','6:00','7:00','14:00','17:00','24:00'],['6:00','14:00','24:00'],['6:00','14:00','24:00']],
         'setpoint' : [['12','10','10','10','12','12'],['15','16','20','23','24','20'],['8','15','20'],['10','20','30']]
}
)
#파일들
weather_file = '/home/agtech_eplus/EnergySimulation/KOR_KW_Taebaek.epw' #웨더파일

#paths
eplus_path = '/usr/local/EnergyPlus-8-7-0/energyplus-8.7.0'  #에너지플러스 exe 파일위치
idf_base_path="/home/agtech_eplus/EnergySimulation/Originals.idf"
idf_custom_path="/home/agtech_eplus/EnergySimulation/test.idf"
eplus_file = ('/home/agtech_eplus/EnergySimulation/test.idf')   #수정된 에너지플러스파일
out_files = '/home/agtech_eplus/EnergySimulation/'  # 아웃풋 드랍 할 위치

out_name = 'test' #outputfile이름기반

with open(idf_base_path, 'r') as file:   #idf가 있는 패스
        data = file.readlines()
#        line=data[178]
        data[39] = '  %s;    !new time steps \n'%TS    # 아웃풋 출력주기
        data[56] = '  %s,    !new start month\n' %SM   #시뮬레이션 하고 싶은 시작월
        data[57] = '  %s,    !new start day \n'%SD    #시뮬레이션 하고 싶은 시작일
        data[58] = '  %s,    !new end month \n'%EM    #시뮬레이션 끝내고 싶은 종료 월
        data[59] = '  %s,    !new end day \n'%ED    #시뮬레이션 끝내고 싶은 종료 일

        def Modify_ScheduleCompact(obj_name, inform_df):  # Schedule:Compact의 값을 수정할 수 있는 함수
                # Schedule:Compact가 포함된 줄 찾기
                for i, line in enumerate(data):
                        if "Schedule:Compact," in line:
                                next_index = i + 1      # Schedule:Compact, 다음 줄 field로 name이 오기 때문에 i + 1

                                # 원하는 이름(!- Name) 찾기
                                if obj_name in data[next_index]:
                                        start_index = i + 5   # 수정할 setpoint의 index
                                        field_value = 3    # 시간이 수정되는 field 3 부터 시작
                                        value_col = obj_name.split(',')[0]

                                        # 데이터프레임 내 setting value를 삽입하기
                                        for j, row in inform_df.iterrows():
                                                if row['schedule_name'] == value_col:
                                                        if row['schedule_name'] == value_col:
                                                                count_line = 0
                                                                for idx, (time,set_value) in enumerate(zip(row['times'], row['setpoint'])):
                                                                        insert_index = start_index + count_line   # 들어가야 할 위치를 찾는다

                                                                        data.insert(insert_index, '    until: %s,             !- Field %d\n'%(time,field_value))
                                                                        field_value += 1   # field 값이 +1씩 커져야하기 때문
                                                                        count_line += 1

                                                                        if idx == len(row['times']) - 1:    # field값 마지막에는 ;이 들어가기 때문에 마지막 줄이면 다른 양식(;)을 쓰도록 지시
                                                                                data.insert(insert_index + 1, '     %s;                     !- Field %d\n'%(set_value, field_value))
                                                                        else:
                                                                                data.insert(insert_index + 1, '     %s,                     !- Field %d\n'%(set_value, field_value))
                                                                        field_value += 1
                                                                        count_line += 1

                                                                # 기존값 삭제하기
                                                                del_index = start_index + count_line  # insert 마친 지점
                                                                while data[del_index].strip():            # 공백이 나타날때까지 지우기
                                                                        del data[del_index]


        Modify_ScheduleCompact("HEATING SETPOINTS,", setpoint_df)
        Modify_ScheduleCompact("COOLING SETPOINTS,", setpoint_df)
        Modify_ScheduleCompact("HEATING SETPOINTS_2,", setpoint_df)
        Modify_ScheduleCompact("COOLING SETPOINTS_2,", setpoint_df)


with open(idf_custom_path, 'w') as file:  #
        file.writelines(data)
        file.close()
        
        # df = subprocess.call([eplus_path, "-w", weather_file, "-d", out_files, "-p", out_name, eplus_file])
        df = subprocess.Popen([eplus_path, "-w", weather_file, "-d", out_files, "-p", out_name, "-r", eplus_file], stdout=subprocess.PIPE, shell =False)
        output, err = df.communicate()
        #print (output.decode('utf-8'))
        #if not err is None:
                #print(err.decode('utf-8'))
        depout = pd.read_csv("/home/agtech_eplus/EnergySimulation/"+out_name+"out.csv") #결과값 읽기
        
        #온실위치 C_Bot, B_bot, A_bot, D_bot
        #출력값
        #Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy 타입스텝별 온실의 일사량  
        #Zone Mean Air Temperature : 타임스텝별 온실 온도
        #Site Outdoor Air Drybulb Temperature: 외기온도
        #Site Direct Solar Radiation Rate per Area: 천공일사량
        # Site Outdoor Air Relative Humidity: 외기상대습도
        # Zone Ideal Loads Zone Total Heating Energy: 난방에너지량(J)
        # Zone Ideal Loads Zone Total Cooling Energy: 냉방에너지량
        # Lights Electric Power: 조명
        # Zone Air Relative Humidity: 온실내 상대습도

        """ 2/20 추가
        #depout['Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)'] #출력하기 외기온도 예시
        #depout['Environment:Site Outdoor Air Relative Humidity [%](TimeStep)'] #출력하기 외부습도 예시
        #depout['Environment:Site Direct Solar Radiation Rate per Area [W/m2](TimeStep)'] #출력하기 일사량

        #depout['A_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 A온실 일사량
        #depout['B_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 B온실 일사량
        #depout['C_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 C온실 일사량
        #depout['D_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 D온실 일사량

        #depout['A_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 A온실 내부온도
        #depout['B_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 B온실 내부온도
        #depout['C_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 C온실 내부온도
        #depout['D_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 D온실 내부온도

        #depout['A_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 A온실 내부습도
        #depout['B_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 B온실 내부습도
        #depout['C_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 C온실 내부습도
        #depout['D_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 D온실 내부습도

        #depout['A_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 A온실
        #depout['B_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 B온실
        #depout['C_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 C온실
        #depout['D_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 D온실

        #depout['ZONE3AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 A온실 난방에너지
        #depout['ZONE3AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 A온실 냉방에너지

        #depout['ZONE4AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 B온실 난방에너지
        #depout['ZONE4AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 B온실 냉방에너지

        #depout['ZONE1AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 C온실 난방에너지
        #depout['ZONE1AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 C온실 냉방에너지

        #depout['ZONE2AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 D온실 난방에너지
        #depout['ZONE2AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 D온실 냉방에너지
        """
        
        y_out = {
                'Out_temp': depout['Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)'],
                'Out_humid': depout['Environment:Site Outdoor Air Relative Humidity [%](TimeStep)'],
                'In_A_temp': depout['A_BOT:Zone Mean Air Temperature [C](TimeStep)'],
                'In_A_humid': depout['A_BOT:Zone Air Relative Humidity [%](TimeStep)'],
                'A_light_E': depout['A_BOT LIGHTS:Lights Electric Power [W](TimeStep)'],
                'A_heatingE': depout['ZONE3AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'],
                'A_coolingE': depout['ZONE3AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'],
        }

        result_output = pd.DataFrame(y_out)
        result_output.to_csv('eplus_case1.csv', index=False)  # 원하는 출력값만 csv 파일로 만들기(전체 출력결과 중 원하는 결과값이 소수일때)
        
        # y_out = depout['Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)'] #출력하기 외기온도 예시
 
print(result_output)
        
        
        
