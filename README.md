# EnergySimulation

# Originals.idf파일 수정 금지

# Version
EnergyPlus 8.7.0

https://github.com/NREL/EnergyPlus/releases/tag/v8.7.0

```
wget https://github.com/NREL/EnergyPlus/releases/download/v8.7.0/EnergyPlus-8.7.0-78a111df4a-Linux-x86_64.sh
sudo sh https://github.com/NREL/EnergyPlus/releases/download/v8.7.0/EnergyPlus-8.7.0-78a111df4a-Linux-x86_64.sh
```
* 첫번째 동의y 외 설치중 모두 enter

# Variables
#수정할 수 있는 변수들
* SM = 9 #시작월
* SD = 1 #시작일
* EM = 9 #종료월
* ED = 5 #종료일
* TS = 4 #타임스텝(결과출력주기)  1: 시간별, 2, 30분별, 4: 15분별, 6: 10분별

* 그 외 idf파일 참조(온도설정 등)

