# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import subprocess
import pandas as pd
import numpy as np

#수정할 변수들
SM = 9 #시작월
SD = 1 #시작일
EM = 9 #종료월
ED = 5 #종료일
TS = 4 #타임스텝(결과출력주기)  1: 시간별, 2, 30분별, 4: 15분별, 6: 10분별

#파일들
weather_file = '/home/egtechlab/EnergySimulation/KOR_KW_Taebaek.epw' #웨더파일

#paths
eplus_path = '/usr/local/EnergyPlus-8-7-0/energyplus-8.7.0'  #에너지플러스 exe 파일위치
idf_base_path="/home/egtechlab/EnergySimulation/mindsgnd2.idf"
idf_custom_path="/home/egtechlab/EnergySimulation/mindsgnd2.idf"
eplus_file = ('/home/egtechlab/EnergySimulation/mindsgnd2.idf')   #수정된 에너지플러스파일
out_files = '/home/egtechlab/EnergySimulation/'  # 아웃풋 드랍 할 위치

out_name = 'mindgnd2' #outputfile이름기반


with open(idf_base_path, 'r') as file:   #idf가 있는 패스
        data = file.readlines()
#        line=data[178]
        data[39] = '  %s;    !new time steps \n'%TS    # 아웃풋 출력주기
        data[56] = '  %s,    !new start month\n' %SM   #시뮬레이션 하고 싶은 시작월
        data[57] = '  %s,    !new start day \n'%SD    #시뮬레이션 하고 싶은 시작일
        data[58] = '  %s,    !new end month \n'%EM    #시뮬레이션 끝내고 싶은 종료 월
        data[59] = '  %s,    !new end day \n'%ED    #시뮬레이션 끝내고 싶은 종료 일      
  
with open(idf_custom_path, 'w') as file:  #
        file.writelines(data)
        file.close()
        
        # df = subprocess.call([eplus_path, "-w", weather_file, "-d", out_files, "-p", out_name, eplus_file])
        df = subprocess.Popen([eplus_path, "-w", weather_file, "-d", out_files, "-p", out_name, "-r", eplus_file], stdout=subprocess.PIPE, shell =False)
        output, err = df.communicate()
        #print (output.decode('utf-8'))
        #if not err is None:
                #print(err.decode('utf-8'))
        depout = pd.read_csv("/home/egtechlab/EnergySimulation/"+out_name+"out.csv") #결과값 읽기
        
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
        
        
        y_out = depout['Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)'] #출력하기 외기온도 예시
        
 
print(y_out)
        
        
        
