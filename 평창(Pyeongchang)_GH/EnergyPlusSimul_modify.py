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

setpoint_df = pd.DataFrame(
        {'times' : ['3:00','6:00','7:00','17:00','19:00','23:00','24:00'],
         'set_values' : ['8', '10', '12', '13', '12', '12','10'],
         'set_values_2' : ['10', '16', '20', '24', '20', '24','20']}
)

#파일들
weather_file = '/home/agtech_eplus/EnergySimulation/KOR_KW_Taebaek.epw' #웨더파일

#paths
eplus_path = '/usr/local/EnergyPlus-8-7-0/energyplus-8.7.0'  #에너지플러스 exe 파일위치
idf_base_path="/home/agtech_eplus/EnergySimulation/Originals.idf"
idf_custom_path="/home/agtech_eplus/EnergySimulation/case2.idf"
eplus_file = ('/home/agtech_eplus/EnergySimulation/case2.idf')   #수정된 에너지플러스파일
out_files = '/home/agtech_eplus/EnergySimulation/'  # 아웃풋 드랍 할 위치

out_name = 'case2' #outputfile이름기반

with open(idf_base_path, 'r') as file:   #idf가 있는 패스
        data = file.readlines()
#        line=data[178]
        data[39] = '  %s;    !new time steps \n'%TS    # 아웃풋 출력주기
        data[56] = '  %s,    !new start month\n' %SM   #시뮬레이션 하고 싶은 시작월
        data[57] = '  %s,    !new start day \n'%SD    #시뮬레이션 하고 싶은 시작일
        data[58] = '  %s,    !new end month \n'%EM    #시뮬레이션 끝내고 싶은 종료 월
        data[59] = '  %s,    !new end day \n'%ED    #시뮬레이션 끝내고 싶은 종료 일

        """
        # C & A온실 Heating setpoints
        data[511]= '     %s,                     !- Field 4\n'%AC_Heating_set_tempUnt7  # A & C온실 자정부터 7시까지 Setpoint
        data[513]= '     %s,                     !- Field 6\n'%AC_Heating_set_tempUnt17 # A & C온실 7시부터 17시까지 Setpoint
        data[515]= '     %s;                     !- Field 8\n'%AC_Heating_set_tempUnt24 # A & C온실 17시부터 24시까지 Setpoint

        # C & A온실 Cooling setpoints
        data[523]= '     %s,                     !- Field 4\n'%AC_Cooling_set_tempUnt7  # A & C온실 자정부터 7시까지 Setpoint
        data[525]= '     %s,                     !- Field 6\n'%AC_Cooling_set_tempUnt20 # A & C온실 7시부터 20시까지 Setpoint
        data[527]= '     %s;                     !- Field 8\n'%AC_Cooling_set_tempUnt24 # A & C온실 20시부터 24시까지 Setpoint  

        # D & B 온실 Heating setpoints_2
        data[551]= '     %s,                     !- Field 4\n'%BD_Heating_set_tempUnt7  # B & D온실 자정부터 7시까지 Setpoint
        data[553]= '     %s,                     !- Field 6\n'%BD_Heating_set_tempUnt17 # B & D온실 7시부터 17시까지 Setpoint
        data[555]= '     %s;                     !- Field 8\n'%BD_Heating_set_tempUnt24 # B & D온실 17시부터 24시까지 Setpoint

        # D & B 온실 Cooling setpoints_2
        data[563]= '     %s,                     !- Field 4\n'%BD_Cooling_set_tempUnt7  # B & D온실 자정부터 7시까지 Setpoint
        data[565]= '     %s,                     !- Field 6\n'%BD_Cooling_set_tempUnt20 # B & D온실 7시부터 20시까지 Setpoint
        data[567]= '     %s;                     !- Field 8\n'%BD_Cooling_set_tempUnt24 # B & D온실 20시부터 24시까지 Setpoint
        """
        ### HEATING SETPOINTS_2, COLLING SETPOINTS_2 대상 setpoint 설정
        start_index = 550  # 가장 먼저 수정할 setpoint의 index
        field_value = 3    # 시간이 수정되는 field 3 부터 시작

        for i, row in setpoint_df.iterrows():
                time = row['times']
                set_value = row['set_values']
                insert_index = start_index + 2 * i

                data.insert(insert_index, '    until: %s,             !- Field %d\n'%(time,field_value))
                field_value += 1

                if i == len(setpoint_df) - 1:
                        data.insert(insert_index + 1, '     %s;                     !- Field %d\n'%(set_value, field_value))
                else:
                        data.insert(insert_index + 1, '     %s,                     !- Field %d\n'%(set_value, field_value))
                field_value += 1

        del_index = start_index + 2 * len(setpoint_df)  # insert 마친 지점
        while data[del_index].strip():            # 공백이 나타날때까지 지우기
                del data[del_index]

        start_index_2 = del_index + 6
        field_value_2 = 3

        for i, row in setpoint_df.iterrows():
                time = row['times']
                set_value_2 = row['set_values_2']
                insert_index = start_index_2 + 2 * i

                data.insert(insert_index, '    until: %s,             !- Field %d\n'%(time,field_value_2))
                field_value_2 += 1

                if i == len(setpoint_df) -1 :
                        data.insert(insert_index + 1, '     %s;                     !- Field %d\n'%(set_value_2, field_value_2))
                else:
                        data.insert(insert_index + 1, '     %s,                     !- Field %d\n'%(set_value_2, field_value_2))
                field_value_2 += 1

        del_index_2 = start_index_2 + 2 * len(setpoint_df)
        while data[del_index_2].strip():
                del data[del_index_2]    
        
  
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
        
        
        
