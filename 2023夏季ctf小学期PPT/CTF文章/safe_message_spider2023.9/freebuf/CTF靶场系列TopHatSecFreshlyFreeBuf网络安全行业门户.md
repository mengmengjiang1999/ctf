# 下载地址

注：只能使用vmbox打开，新增一张网卡修改为桥接模式

    
    
    https://download.vulnhub.com/tophatsec/Freshly.ova
    

# 实战演练

查找靶机IP

![image.png](https://image.3001.net/images/20191114/1573727579_5dcd2d5bcc864.png!small)  

扫描靶机开放了那些端口？开放了80，443，8080端口

![image.png](https://image.3001.net/images/20191114/1573727796_5dcd2e3435671.png!small)首先，我们先看看80端口，浏览器打开，只有一张gif图片

![image.png](https://image.3001.net/images/20191114/1573727846_5dcd2e66321a4.png!small)查看页面源代码

![image.png](https://image.3001.net/images/20191114/1573727920_5dcd2eb047974.png!small)爆破一下目录，找到了login.php页面，抓包，用sqlmap跑一下

![image.png](https://image.3001.net/images/20191114/1573728297_5dcd3029e7519.png!small)![image.png](https://image.3001.net/images/20191114/1573730238_5dcd37bef3762.png!small)看到有个8080数据库，跑一下，找到了一个用户名和密码

![image.png](https://image.3001.net/images/20191114/1573731112_5dcd3b28c1b3b.png!small)  

浏览器打开8080端口，发现是个wordpress系统

![image.png](https://image.3001.net/images/20191114/1573731180_5dcd3b6ce7ebf.png!small)上传webshell

![image.png](https://image.3001.net/images/20191114/1573731386_5dcd3c3a7dc48.png!small)连接成功

![image.png](https://image.3001.net/images/20191114/1573731432_5dcd3c680c065.png!small)切换成root用户，密码就是wordpress密码

  

