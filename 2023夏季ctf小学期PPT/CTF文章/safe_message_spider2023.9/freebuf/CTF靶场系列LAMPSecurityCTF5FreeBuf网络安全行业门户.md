# 下载地址

    
    
    https://download.vulnhub.com/lampsecurity/ctf5.zip

#  **实战演练**

使用netdiscover命令查找靶机的IP。

![image.png](https://image.3001.net/images/20190820/1566287941_5d5ba845dfe37.png)  

使用nmap查看靶机开放的端口

![image.png](https://image.3001.net/images/20190820/1566288126_5d5ba8fee69be.png)

打开浏览器![image.png](https://image.3001.net/images/20190820/1566288141_5d5ba90d2eb8d.png)

使用awvs，发现很多漏洞

![image.png](https://image.3001.net/images/20190820/1566288496_5d5baa704e7a2.png)注入也成功

![image.png](https://image.3001.net/images/20190820/1566288528_5d5baa9078c97.png)不过我们使用另外一种方法，注意到这个系统是nanocms

![image.png](https://image.3001.net/images/20190820/1566288551_5d5baaa762c02.png)![image.png](https://image.3001.net/images/20190820/1566288578_5d5baac2d3195.png)![image.png](https://image.3001.net/images/20190820/1566288610_5d5baae21025c.png)![image.png](https://image.3001.net/images/20190820/1566288708_5d5bab444057c.png)使用admin，shannon登录，并且创建木马

![image.png](https://image.3001.net/images/20190820/1566288801_5d5baba17b24e.png)![image.png](https://image.3001.net/images/20190820/1566288880_5d5babf09d775.png)  

