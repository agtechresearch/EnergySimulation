# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import subprocess
import pandas as pd
import numpy as np
import json
import os

SM = 9
SD = 1
EM = 9
ED = 5
TS = 1 # 1: 시간별, 2, 30분별, 4: 15분별, 6: 10분별
"""
with open("C:\EP_dev\mindgnd\mindsgnd2.idf", 'r') as file:   #idf가 있는 패스
        data = file.readlines()
#        line=data[178]
        data[39] = '  %s;    !new time steps \n'%TS    # 아웃풋 출력주기
        data[56] = '  %s,    !new start month\n' %SM   #시뮬레이션 하고 싶은 시작월
        data[57] = '  %s,    !new start day \n'%SD    #시뮬레이션 하고 싶은 시작일
        data[58] = '  %s,    !new end month \n'%EM    #시뮬레이션 끝내고 싶은 종료 월
        data[59] = '  %s,    !new end day \n'%ED    #시뮬레이션 끝내고 싶은 종료 일      
  
with open("C:\EP_dev\mindgnd\mindsgnd5.idf", 'w') as file:  #
        file.writelines(data)
        file.close()
        eplus_path = "C:\EnergyPlusV8-7-0\energyplus"  #에너지플러스 exe 파일위치
        eplus_file = ('C:\EP_dev\mindgnd\mindsgnd2.idf')   #신규작성된 에너지플러스파일
        weather_file = 'C:\EP_dev\mindgnd\KOR_KW_Taebaek.epw' #웨더파일
        out_files = 'C:\EP_dev\mindgnd'  # 아웃풋 드랍 할 위치
        out_name = 'mindgnd2' #결과파일이름 (최종 outname+out.csv파일로 저장됨)
# df = subprocess.call([eplus_path, "-w", weather_file, "-d", out_files, "-p", out_name, eplus_file])
        df = subprocess.Popen([eplus_path, "-w", weather_file, "-d", out_files, "-p", out_name, "-r", eplus_file], stdout=subprocess.PIPE, shell =False)
        output, err = df.communicate()
#        print (output.decode('utf-8'))
#        if not err is None:
#            print(err.decode('utf-8'))
        depout = pd.read_csv("C:\EP_dev\mindgnd\mindgnd2out.csv") #결과값 읽기

       
        
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
        
        #depout['Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)'] #출력하기 외기온도 예시
        #depout['Environment:Site Outdoor Air Relative Humidity [%](TimeStep)'] #출력하기 외부습도 예시
        #depout['Environment:Site Direct Solar Radiation Rate per Area [W/m2](TimeStep)'] #출력하기 일사량


        #Sol_Rad_A = depout['A_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 A온실 일사량
        #Sol_Rad_B = depout['B_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 B온실 일사량
        Sol_Rad_C = depout['C_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 C온실 일사량
        #Sol_Rad_D = depout['D_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 D온실 일사량


        #In_Temp_A = depout['A_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 A온실 내부온도
        #In_Temp_B = depout['B_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 B온실 내부온도
        #In_Temp_C = depout['C_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 C온실 내부온도
        #In_Temp_D = depout['D_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 D온실 내부온도

        #In_Hum_A = depout['A_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 A온실 내부습도
        #In_Hum_B = depout['B_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 B온실 내부습도
        #In_Hum_C = depout['C_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 C온실 내부습도
        #In_Hum_D = depout['D_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 D온실 내부습도


        #Elac_Light_A = depout['A_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 A온실
        #Elac_Light_B = depout['B_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 B온실
        Elac_Light_C = depout['C_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 C온실
        #Elac_Light_D = depout['D_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 D온실


        #E_Heat_A = depout['ZONE3AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 A온실 난방에너지
        #E_Cool_A = depout['ZONE3AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 A온실 냉방에너지

        #E_Heat_B = depout['ZONE4AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 B온실 난방에너지
        #E_Cool_B = depout['ZONE4AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 B온실 냉방에너지

        E_Heat_C = depout['ZONE1AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 C온실 난방에너지
        E_Cool_C = depout['ZONE1AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 C온실 냉방에너지

        #E_Heat_D = depout['ZONE2AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 D온실 난방에너지
        #E_Cool_D = depout['ZONE2AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 D온실 냉방에너지

        # 전체기간 합산 결과
        Total_sum = depout.sum()
        #일사량
        Total_GH_Sol = Total_sum['C_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #우선 C온실을 기준으로함
        #난방에너지
        Total_GH_Heat = Total_sum['ZONE1AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #우선 C온실을 기준으로함
        #냉방에너지
        Total_GH_Cool = Total_sum['ZONE1AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #우선 C온실을 기준으로함
        # 조명에너지
        Total_GH_Light = Total_sum['C_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #우선 C온실을 기준으로함

        #일별 에너지 총 사용량 (N일 => N개의 인덱스)
        # 24개씩 값을 평균내어 리스트에 저장
        Daily_GH_Sol = []
        Daily_GH_Heat = []
        Daily_GH_Cool = []
        Daily_GH_Light = []

        for i in range(0, len(Elac_Light_C), 24):
                Daily_GH_Sol.append(Sol_Rad_C[i:i+24].mean())
                Daily_GH_Heat.append(E_Heat_C[i:i+24].mean())
                Daily_GH_Cool.append(E_Cool_C[i:i+24].mean())
                Daily_GH_Light.append(Elac_Light_C[i:i+24].mean())

        result = {
                "Total_GH_Sol[J]": Total_GH_Sol,
                "Total_GH_Heat[J]": Total_GH_Heat, 
                "Total_GH_Cool[J]": Total_GH_Cool,
                "Total_GH_Light[W]": Total_GH_Light,
                "Daily_GH_Sol[J]": Daily_GH_Sol,
                "Daily_GH_Heat[J]": Daily_GH_Heat,
                "Daily_GH_Cool[J]": Daily_GH_Cool,
                "Daily_GH_Light[W]": Daily_GH_Light,
        }

result_json = json.dumps(result)

print(result_json)



        
 
#print(y_out)
        
        
        """

#아래는 지정 필요
idf_path = "C:\EP_dev\mindgnd\mindsgnd2.idf" # idf 파일이 있는 위치
eplus_file = ('C:\EP_dev\mindgnd\mindsgnd_modi.idf')   #신규작성된 에너지플러스파일
eplus_path = "C:\EnergyPlusV8-7-0\energyplus"  #에너지플러스 exe 파일위치
weather_file = 'C:\EP_dev\mindgnd\KOR_KW_Taebaek.epw' #웨더파일
#out_path = 'C:\EP_dev\mindgnd'  # 아웃풋 드랍 할 위치
#out_name = 'sfram_energy_simul' #결과파일이름 (최종 outname+out.csv파일로 저장됨)

SM = 9
SD = 1
EM = 9
ED = 5
TS = 1 # 1: 시간별, 2, 30분별, 4: 15분별, 6: 10분별

    

def ep_set_run(df, out_path, out_name): # 값 설정 및 수정된 파일 기반 에너지플러스 실행

    df["date"] = pd.to_datetime(df["date"]) 

    #df 날짜순으로 정렬
    #df.sort_values('date')

    # 시작일, 마지막날 저장
    SM = df.iloc[0]["date"].month #month
    SD = df.iloc[0]["date"].day #day
    EM = df.iloc[-1]["date"].month#.split('-')[1] #month
    ED = df.iloc[-1]["date"].day#.split('-')[2] #day
 
    with open(idf_path, 'r') as file:   #idf가 있는 패스
            data = file.readlines()

            data[39] = '  %s;    !new time steps \n'%TS    # 아웃풋 출력주기
            data[56] = '  %s,    !new start month\n' %SM   #시뮬레이션 하고 싶은 시작월
            data[57] = '  %s,    !new start day \n'%SD    #시뮬레이션 하고 싶은 시작일
            data[58] = '  %s,    !new end month \n'%EM    #시뮬레이션 끝내고 싶은 종료 월
            data[59] = '  %s,    !new end day \n'%ED    #시뮬레이션 끝내고 싶은 종료 일      

    with open(eplus_file, 'w') as file:  #
            file.writelines(data)
            file.close()

            df = subprocess.Popen([eplus_path, "-w", weather_file, "-d", out_path, "-p", out_name, "-r", eplus_file], stdout=subprocess.PIPE, shell =False)
            output, err = df.communicate()
    #        print (output.decode('utf-8'))
    #        if not err is None:
    #            print(err.decode('utf-8')) 



def get_ep_result_json(out_path, out_name):

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


    output_path = os.path.join(out_path,out_name+"out.csv")
    print("get_ep",output_path)
    EP_out = pd.read_csv(output_path) #결과값 읽기

    #EP_out['Environment:Site Outdoor Air Drybulb Temperature [C](TimeStep)'] #출력하기 외기온도 예시
    #EP_out['Environment:Site Outdoor Air Relative Humidity [%](TimeStep)'] #출력하기 외부습도 예시
    #EP_out['Environment:Site Direct Solar Radiation Rate per Area [W/m2](TimeStep)'] #출력하기 일사량

    #Sol_Rad_A = EP_out['A_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 A온실 일사량
    #Sol_Rad_B = EP_out['B_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 B온실 일사량
    Sol_Rad_C = EP_out['C_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 C온실 일사량
    #Sol_Rad_D = EP_out['D_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #출력하기 D온실 일사량

    #In_Temp_A = EP_out['A_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 A온실 내부온도
    #In_Temp_B = EP_out['B_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 B온실 내부온도
    #In_Temp_C = EP_out['C_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 C온실 내부온도
    #In_Temp_D = EP_out['D_BOT:Zone Mean Air Temperature [C](TimeStep)'] #출력하기 시간별 D온실 내부온도

    #In_Hum_A = EP_out['A_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 A온실 내부습도
    #In_Hum_B = EP_out['B_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 B온실 내부습도
    #In_Hum_C = EP_out['C_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 C온실 내부습도
    #In_Hum_D = EP_out['D_BOT:Zone Air Relative Humidity [%](TimeStep)'] #출력하기 시간별 D온실 내부습도

    #Elac_Light_A = EP_out['A_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 A온실
    #Elac_Light_B = EP_out['B_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 B온실
    Elac_Light_C = EP_out['C_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 C온실
    #Elac_Light_D = EP_out['D_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #출력하기 조명 전기사용 D온실

    #E_Heat_A = EP_out['ZONE3AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 A온실 난방에너지
    #E_Cool_A = EP_out['ZONE3AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 A온실 냉방에너지

    #E_Heat_B = EP_out['ZONE4AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 B온실 난방에너지
    #E_Cool_B = EP_out['ZONE4AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 B온실 냉방에너지

    E_Heat_C = EP_out['ZONE1AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 C온실 난방에너지
    E_Cool_C = EP_out['ZONE1AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 C온실 냉방에너지

    #E_Heat_D = EP_out['ZONE2AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #출력하기 시간별 D온실 난방에너지
    #E_Cool_D = EP_out['ZONE2AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #출력하기 시간별 D온실 냉방에너지

    # 전체기간 합산 결과
    Total_sum = EP_out.sum()
    #일사량
    Total_GH_Sol = Total_sum['C_TOP:Zone Exterior Windows Total Transmitted Beam Solar Radiation Energy [J](TimeStep)'] #우선 C온실을 기준으로함
    #난방에너지
    Total_GH_Heat = Total_sum['ZONE1AIR:Zone Ideal Loads Zone Total Heating Energy [J](TimeStep)'] #우선 C온실을 기준으로함
    #냉방에너지
    Total_GH_Cool = Total_sum['ZONE1AIR:Zone Ideal Loads Zone Total Cooling Energy [J](TimeStep)'] #우선 C온실을 기준으로함
    # 조명에너지
    Total_GH_Light = Total_sum['C_BOT LIGHTS:Lights Electric Power [W](TimeStep)'] #우선 C온실을 기준으로함

    #일별 에너지 총 사용량 (N일 => N개의 인덱스)
    # 24개씩 값을 평균내어 리스트에 저장
    Daily_GH_Sol = []
    Daily_GH_Heat = []
    Daily_GH_Cool = []
    Daily_GH_Light = []

    for i in range(0, len(Elac_Light_C), 24):
            Daily_GH_Sol.append(Sol_Rad_C[i:i+24].mean())
            Daily_GH_Heat.append(E_Heat_C[i:i+24].mean())
            Daily_GH_Cool.append(E_Cool_C[i:i+24].mean())
            Daily_GH_Light.append(Elac_Light_C[i:i+24].mean())

    result = {
            "Total_GH_Sol[J]": Total_GH_Sol,
            "Total_GH_Heat[J]": Total_GH_Heat, 
            "Total_GH_Cool[J]": Total_GH_Cool,
            "Total_GH_Light[W]": Total_GH_Light,
            "Daily_GH_Sol[J]": Daily_GH_Sol,
            "Daily_GH_Heat[J]": Daily_GH_Heat,
            "Daily_GH_Cool[J]": Daily_GH_Cool,
            "Daily_GH_Light[W]": Daily_GH_Light,
    }

    result_json = json.dumps(result)

    print(result_json)

    return result_json

        
dfs = [
    "2022-01-01",
    "2022-01-02",
    "2022-01-09",
    "2022-01-16",
    "2022-01-23",
    "2022-01-30",
    "2022-02-06",
    "2022-02-13",
    "2022-02-20",
    "2022-02-27",
    "2022-03-06",
    "2022-03-13",
    "2022-03-20",
]

# DataFrame 생성
dfs = pd.DataFrame({"date": dfs})

out_path = "C:\EP_dev\mindgnd"
out_name = "test_simul"
ep_set_run(dfs, out_path, out_name) #ep파일 설정 셋팅 및 energyplus 실행

EP_result_json = get_ep_result_json(out_path, out_name) #결과파일 읽기 및 json결과 가져오기

print(EP_result_json)