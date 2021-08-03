import requests
import json
import argparse
import re

# 初始化变量
parser = argparse.ArgumentParser()
parser.add_argument('--username', type=str, default=None)
parser.add_argument('--password', type=str, default=None)
parser.add_argument('--province', type=str, default=None)
parser.add_argument('--city', type=str, default=None)
parser.add_argument('--county', type=str, default=None)
args = parser.parse_args()

def captchaOCR():
    captcha = ''
    token   = '' 
    while len(captcha) != 4:
        token = json.loads(requests.get('https://fangkong.hnu.edu.cn/api/v1/account/getimgvcode').text)['data']['Token']
        data = {
                'image_url': f'https://fangkong.hnu.edu.cn/imagevcode?token={token}',
                'type': 'https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic',
                'detect_direction': 'false'
                }
        captcha = requests.post('https://cloud.baidu.com/aidemo', data=data).json()['data']['words_result'][0]['words']
    print(token, captcha)
    return token, captcha
            
    while len(captcha) != 4:
        token = json.loads(requests.get('https://fangkong.hnu.edu.cn/api/v1/account/getimgvcode').text)['data']['Token']
        captcha = requests.post('https://cloud.baidu.com/aidemo', data=data).json()['data']['words_result'][0]['words']
    return token, captcha

def login():
    login_url = 'https://fangkong.hnu.edu.cn/api/v1/account/login'
    token, captcha = captchaOCR()
    login_info = {"Code":args.username,"Password":args.password,"VerCode":captcha,"Token":token}
    
    set_cookie = requests.post(login_url, json=login_info).headers['set-cookie']
    regex = r"\.ASPXAUTH=(.*?);"
    ASPXAUTH = re.findall(regex, set_cookie)[2]

    headers = {'Cookie': f'.ASPXAUTH={ASPXAUTH}; TOKEN={token}'}
    return headers

def setLocation():
    location = json.loads(requests.get(f'http://api.tianditu.gov.cn/geocoder?ds={{"keyWord":\"{args.province+args.city+args.county}\"}}&tk=2355cd686a32d016021bffbc4a69d880').text)["location"]
    real_address = "胡集镇周岗村" # 在此填写详细地址
    return location["lon"], location["lat"], real_address

def main():
    clockin_url = 'https://fangkong.hnu.edu.cn/api/v1/clockinlog/add'
    headers = login()
    lon, lat, real_address = setLocation()
    clockin_data = {"Temperature":"null",
                    "RealProvince":args.province,
                    "RealCity":args.city,
                    "RealCounty":args.county,
                    "RealAddress":real_address,
                    "IsUnusual":"0",
                    "UnusualInfo":"",
                    "IsTouch":"0",
                    "IsInsulated":"0",
                    "IsSuspected":"0",
                    "IsDiagnosis":"0",
                    "tripinfolist":[{"aTripDate":"","FromAdr":"","ToAdr":"","Number":"","trippersoninfolist":[]}],
                    "toucherinfolist":[],
                    "dailyinfo":{"IsVia":"0","DateTrip":""},
                    "IsInCampus":"1",
                    "IsViaHuBei":"0",
                    "IsViaWuHan":"0",
                    "InsulatedAddress":"",
                    "TouchInfo":"",
                    "IsNormalTemperature":"1",
                    "Longitude":lon,
                    "Latitude":lat
                    }

    clockin = requests.post(clockin_url, headers=headers, json=clockin_data)

    if clockin.status_code == 200:
        if '成功' in clockin.text or '已提交' in clockin.text:
            isSucccess = 0
        else:
            isSucccess = 1
            print(json.loads(clockin.text)['msg'])
    else:
        isSucccess = 1
    print(json.loads(clockin.text)['msg'])

    return isSucccess

for i in range(10):
    try:    
        main()
        break
    except:
        continue
