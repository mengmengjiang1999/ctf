# 下载地址

    
    
    https://download.vulnhub.com/tr0ll/Tr0ll.rar
    

# 实战演练

查找靶机的IP

![image.png](https://image.3001.net/images/20191004/1570198017_5d975201c6363.png)  

查看靶机开放的端口

![image.png](https://image.3001.net/images/20191004/1570198066_5d975232b4eb0.png)浏览器打开80端口

![image.png](https://image.3001.net/images/20191004/1570198087_5d97524760d22.png)  

查看页面源代码，没发现什么东西

![image.png](https://image.3001.net/images/20191004/1570198111_5d97525f9664a.png)爆破一下目录

![image.png](https://image.3001.net/images/20191004/1570198145_5d97528129284.png)查看robots文件，找到了一个目录

![image.png](https://image.3001.net/images/20191004/1570198204_5d9752bcb44a4.png)![image.png](https://image.3001.net/images/20191004/1570198233_5d9752d9deca2.png)没发现什么东西

![image.png](https://image.3001.net/images/20191004/1570198258_5d9752f2152cd.png)现在就转战FTP端口，使用匿名登录，下载数据包

使用wireshark打开数据包，找到了隐藏目录

![image.png](https://image.3001.net/images/20191004/1570201180_5d975e5c752e4.png)  

查看文件信息

![image.png](https://image.3001.net/images/20191004/1570201146_5d975e3a44a5e.png)

找到了一个目录  
![image.png](https://image.3001.net/images/20191004/1570201226_5d975e8aa5caa.png)![image.png](https://image.3001.net/images/20191004/1570201265_5d975eb1c7d83.png)  

文件夹分别是账号，密码文件，使用这两个进行爆破ssh  
![image.png](https://image.3001.net/images/20191004/1570201538_5d975fc271a73.png)爆破之后，发现不行，后来看到目录的提示，说不定文件名就是密码(Pass.txt)

![image.png](https://image.3001.net/images/20191004/1570201594_5d975ffa6a7ca.png)

登录进去  
![image.png](https://image.3001.net/images/20191004/1570201733_5d976085e9119.png)找提权exp

![image.png](https://image.3001.net/images/20191004/1570201825_5d9760e130bf9.png)提权成功

![image.png](https://image.3001.net/images/20191004/1570202022_5d9761a68d442.png)  

  

  

