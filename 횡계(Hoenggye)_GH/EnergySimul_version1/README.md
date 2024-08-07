## Data
* Validation_ch_ing_2.idf 이용  
## Description
* Eplus를 python 파일로 원하는 setpoint(구동기 schedule)에 맞춰 실행하도록 함  
* 시뮬레이션 날짜는 토마토 생육 중기 중 1월~6월임  
* 월마다의 일출/일몰 시간에 맞춰 온도와 습도 setpoint가 맞춰지도록 설정함  
* 온도를 조절하는 데에는 난방시스템(레일난방 Schedule Day 4), 습도를 조절하는 데에는 Humid Setpoint Schedule을 통해서 조절된다고 가정했음  
* 차광은 일출~일몰 시간 안에서만 작동  
* 포그와 유동팬은 상시가동  