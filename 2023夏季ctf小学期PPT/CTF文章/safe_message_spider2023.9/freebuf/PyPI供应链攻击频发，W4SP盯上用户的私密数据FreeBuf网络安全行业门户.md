## **恶意文件分析**

###  **1.恶意文件描述**

近期，深信服深盾终端实验室捕获到一起针对 PyPI 库的投毒事件，此次投毒的库名为 Ascii2txt， **该投毒库的代码采用了 Hyperion
对源码进行混淆，此次事件中还有其它库被投毒，** **如pyquest、ultrarequests。**
**目前官方已经将相关库下架，国内源仍有部分缓存。**

###  **2.恶意文件分析**

经调查，在本次攻击事件中，攻击者通过上传具有迷惑性库名的 Python 库至
PyPI，受害者使用该库时会自动从远程服务器加载用于后续攻击的载荷：![图片](https://image.3001.net/images/20220921/1663749862_632acee67e330f3072560.png!small)

经过对下载内容进行解混淆分析，发现如下内容，从远程服务器加载文件，在本地生成一个伪随机的路径和文件名：

![图片](https://image.3001.net/images/20220921/1663749872_632acef0d483b1874032f.png!small)

![图片](https://image.3001.net/images/20220921/1663749885_632acefdd971c5cf67106.png!small)

下载完成之后运行该文件，并将其加入到注册表的启动项中：

![](https://image.3001.net/images/20220921/1663749903_632acf0fcc90299ea51f4.png!small)

![](https://image.3001.net/images/20220921/1663749919_632acf1fcd529427c9a32.png!small)

第二次下载的文件内容如下：

![](https://image.3001.net/images/20220921/1663749936_632acf30612c939379a8d.png!small)

收集如下浏览器的信息：

![](https://image.3001.net/images/20220921/1663749949_632acf3d84a6190afc8f5.png!small)

收集 discord 信息：

![](https://image.3001.net/images/20220921/1663749961_632acf49ec71fcad9d370.png!small)  
![](https://image.3001.net/images/20220921/1663749974_632acf5668e03c3305179.png!small)

获取浏览器密码、Cookie：

![](https://image.3001.net/images/20220921/1663749987_632acf636aa31f4cb2c5e.png!small)

![](https://image.3001.net/images/20220921/1663749997_632acf6de03f906666948.png!small)  
![](https://image.3001.net/images/20220921/1663750010_632acf7a1eea9b6f8bc90.png!small)

压缩特定目录的文件并发送至服务器：

![](https://image.3001.net/images/20220921/1663750026_632acf8ae37cc9f401289.png!small)

注入 discord，首先判断是否存在与 discord 相关的路径，如果存在则从 http://zerotwo-best-waifu.online/778112985743251/wap/dsc_injection 下载一个文件，并写入到 discord 的 index.js
中，然后终止discord.exe，注入的脚本会监控受害主机的行为，包括更改邮件地址、密码、账单信息等，并将这个信息发送到discord 频道。

![](https://image.3001.net/images/20220921/1663750037_632acf9530e92cd9deeb2.png!small)

如果 Cookie 不存在，则根据关键字搜索特定路径下的文件：

![](https://image.3001.net/images/20220921/1663750048_632acfa01d2ea5b313bdd.png!small)  
![](https://image.3001.net/images/20220921/1663750060_632acfac6295df0cd9df2.png!small)

收集到的信息若不为空，则发送到 Discord
频道https://discord.com/api/webhooks/1001296979948740648/4wqCErLU3BVeKWnxDA70Gns5vcfxh5OCb3YDIFZaFujqfSRIwHH4YIu3aLOVWjCDeO1H上。

##  **IOCs**

d7b6df674690c2e81c72ea031ed44a6f  
f0c16b9c0a37d7a23a756616826d1c41  
42f0f3b4d5a2be7f09d1c02668cb2c08  
4d571644fa4f94f65bfb82b6c672803a

https://zerotwo-best-waifu.online/778112985743251/wap/enner/stealer  
http://zerotwo-best-waifu.online/778112985743251/wap/dsc_injection  
https://zerotwo-best-waifu.online/778112985743251/mawl.txt  
http://zerotwo-best-waifu.online/778112985743251/colorgood.txt

##  **​处置建议**

1\. 服务器定期升级服务或安装最新的安全补丁。

2\. 谨慎安装未知开源库。

3\. 安装杀毒软件实时保护设备。

