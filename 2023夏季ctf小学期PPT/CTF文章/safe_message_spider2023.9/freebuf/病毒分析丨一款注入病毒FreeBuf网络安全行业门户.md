# **作者丨黑蛋**

#  **一、病毒简介**

SHA256:  
de2a83f256ef821a5e9a806254bf77e4508eb5137c70ee55ec94695029f80e45  
MD5:  
6e4b0a001c493f0fcf8c5e9020958f38  
SHA1:  
bea213f1c932455aee8ff6fde346b1d1960d57ff  
云沙箱检测：

![](https://image.3001.net/images/20230601/1685596608_647829c0ed5c09b1cae6c.png!small)

#  **二、环境准备**

系统  
  
---  
  
Win7x86Sp1  
  
#  **三、行为监控**

打开火绒剑，打开样本：![](https://image.3001.net/images/20230601/1685596609_647829c1eb3af631c66b6.png!small)

可以看到这里释放了部分隐藏文件，以及进行了网络链接，但是网站关闭了，没有成功：  
![](https://image.3001.net/images/20230601/1685596610_647829c2b0d75dca3d077.png!small)其次就是入侵了explorer.exe。最后进行自我删除。

#  **四、调试分析**

由于其中有很多需要解密部分，所以这次动静结合分析。首先在IDA中，打开start函数：

![](https://image.3001.net/images/20230601/1685596611_647829c34e377c4563aa7.png!small)

这里有IsProcessorFeaturePresent反调试，直接用OD插件过掉：  
![](https://image.3001.net/images/20230601/1685596612_647829c4100910d3f78d4.png!small)一直走下去，函数sub_402A10是关键函数

![](https://image.3001.net/images/20230601/1685596612_647829c4d49683f54349b.png!small)

![](https://image.3001.net/images/20230601/1685596613_647829c58661dbe6b03e1.png!small)

前面是设置窗口属性，对部分杀软进行遍历强杀：  
![](https://image.3001.net/images/20230601/1685596614_647829c625fd4d7323af5.png!small)

跟进sub_402190：

![](https://image.3001.net/images/20230601/1685596614_647829c6e48eaa5d97c2d.png!small)

继续向下走：

![](https://image.3001.net/images/20230601/1685596615_647829c79003b588ebfaa.png!small)

![](https://image.3001.net/images/20230601/1685596616_647829c81dbda03bce71d.png!small)

  
继续拼接路径：

![](https://image.3001.net/images/20230601/1685596616_647829c8ae32ae2e9267e.png!small)

![](https://image.3001.net/images/20230601/1685596617_647829c93a2f4f499cb1b.png!small)

接下来是解密网址：

![](https://image.3001.net/images/20230601/1685596617_647829c9bb385c47d684f.png!small)

![](https://image.3001.net/images/20230601/1685596618_647829ca670bcdf120634.png!small)

  
然后进行文件下载，设置文件属性，随后又是一堆路径的拷贝：

![](https://image.3001.net/images/20230601/1685596618_647829caede47089c2dbf.png!small)

随后又是网址解密，下载文件，设置属性：

![](https://image.3001.net/images/20230601/1685596619_647829cb8fd82dfbf3fbc.png!small)

![](https://image.3001.net/images/20230601/1685596620_647829cc38c0619df3bc1.png!small)

![](https://image.3001.net/images/20230601/1685596620_647829cca41f67d3bb40a.png!small)

继续走，走过一大堆函数后，来到标记函数：

![](https://image.3001.net/images/20230601/1685596621_647829cd28614771af317.png!small)

进去：

![](https://image.3001.net/images/20230601/1685596621_647829cda97afad2b1e6d.png!small)

![](https://image.3001.net/images/20230601/1685596622_647829ce807a260af000f.png!small)

  
这里是创建了一个文件，并进行一个注入操作

![](https://image.3001.net/images/20230601/1685596623_647829cf30ce7a68b86f2.png!small)

注意这里这个函数：

![](https://image.3001.net/images/20230601/1685596623_647829cfae2ca87fd359a.png!small)

![](https://image.3001.net/images/20230601/1685596624_647829d04ac5138e14cd3.png!small)

  
这里设置了dll创建时间=C:\Windows\notepad.exe创建时间。  
在最后，启动了cmd，ping了127.0.0.1并进行删除操作：

  
![](https://image.3001.net/images/20230601/1685596625_647829d12ee0ed020c9ee.png!small)随后看看释放的dll，进入主函数：

![](https://image.3001.net/images/20230601/1685596625_647829d1eab8dd65ab934.png!small)

  
第一个函数是获取系统时间，着重看第二个函数：  
![](https://image.3001.net/images/20230601/1685596626_647829d26ccb3dc6de406.png!small)进入标记函数，他创建了一个线程，跟进回调函数：

![](https://image.3001.net/images/20230601/1685596627_647829d326ebfe434e371.png!small)

解密了一个网站，进行了访问：

![](https://image.3001.net/images/20230601/1685596627_647829d3d35b9b868ee71.png!small)

函数1188简单的追了一下，猜测是根据服务器返回信息进行不同操作

![](https://image.3001.net/images/20230601/1685596628_647829d4a6077a8073432.png!small)

这几个函数没有看出是干啥的。总体思路就这样。

