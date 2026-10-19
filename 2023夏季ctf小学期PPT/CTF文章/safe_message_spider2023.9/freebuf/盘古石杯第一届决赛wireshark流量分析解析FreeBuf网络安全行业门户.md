容器密码：2ej)!,[JN-U;wm19J=d9sZt_L6#bf+}[  
题目链接：https://pan.baidu.com/s/1iThyL6YCEM0vIRg9wvCgQg  
提取码：7179

# 流量分析

首先导入key.log进行解密，如下图所示编辑-首选项-TLS：  
![image](https://image.3001.net/images/20230613/1686588180_64874b149e4b57e16d8f6.png!small)

  1. 计算流量包文件的SHA256值是？[答案：字母小写]  
我这里用的hashmyfile计算的。2d689add281b477c82b18af8ab857ef5be6badf253db1c1923528dd73b3d61a9

  2. 流量包长度在“640-1279”之间的的数据包总共有多少？[答案：100]  
![image](https://image.3001.net/images/20230613/1686588265_64874b69a77d5bab1e35b.png!small)  
流量包的长度需要进行统计分析，通过writeshark中的统计->分组长度可以确定

  3. 黑客使用的计算机操作系统是？[答案：windows7 x32]  
一般可以在http流中的User-Agent看到，要注意判断是不是伪造的User-Agent。  
![image](https://image.3001.net/images/20230613/1686588333_64874badb4a4820e3b14c.png!small)  
如果在整个数据包中没有http流。可以通过mss属性和sack属性值来观察推断，mss属性（Maximum segment
size）TCP报文段中的最大段大小，通常该值为1460。还可以观察SACK属性，如果存在可能是windows操作系统，如果不存在可能是linux操作系统，SACK选项在Windows中默认启用，而在Linux中默认禁用。  
![image](https://image.3001.net/images/20230613/1686588348_64874bbce51963edd7b37.png!small)

  4. 黑客上传文件到哪个网盘？[答案：xx网盘]  
通过http.request.method ==
POST过滤请求包，发现几乎都是pan.baidu.com，有个别post请求不是百度网盘的。是请求的其他百度地址。(文件上传是以post进行请求)  
![image](https://image.3001.net/images/20230613/1686588377_64874bd9e812a30cf13d8.png!small)

  5. 黑客上传网盘的中间件是？[答案：xxxx]  
这个题目的问题一直不太明天它到底要找什么中间件，比较迷惑。直到在后续过程中找到关于百度网盘上传的图片的时候，才理解如果是问黑客上传的网盘中间件应该按照ip.dst_host
== 192.168.100.141去过滤，且是百度网盘又过滤http，即通过ip.dst_host ==
192.168.100.141&&http过滤找到图片image/jpeg的上传信息，发现server是nginx，这个在比赛的时候只考虑到目标地址，过滤出来填的apache，错了。  
![image](https://image.3001.net/images/20230613/1686588448_64874c20454ce9b0d6b86.png!small)  
找到server为nginx中间件。  
![image](https://image.3001.net/images/20230613/1686588476_64874c3c11728e35f71a2.png!small)

  6. 黑客首次登陆网盘时间是？[答案：2000-01-01 01:00:33]  
第一次登录肯定是post请求，且存在pan.baidu.com的关键字，则使用http contains "pan.baidu.com" &&
http.request.method == "POST"进行过滤，如下图所示：  
![image](https://image.3001.net/images/20230613/1686588503_64874c57ba38a20ad3342.png!small)  
这里得到结果UTC+8为12：03：55。不知道答案为什么给12：03：52。如有问题还请留言。  
![image](https://image.3001.net/images/20230613/1686588531_64874c735896a5fcefc3a.png!small)

  7. 黑客上传到网盘的txt文件的md5值是？[答案：字母小写]  
在wireshark数据包中会有pan.baidu.com的cookie信息，如下图所示：![image](https://image.3001.net/images/20230613/1686588627_64874cd38b141b141c79c.png!small)  
这里只需要替换BDUSS，BIDUPSID，BAIDUID将百度网盘的cookie值进行替换即可，进入百度网盘，可获取到上传百度网盘3个文件分别是：dic.txt，flag.rar，pass.jpg。计算dic.txt文件md5值为：6a5aff7bec78dd1e4fc23e571b664b50

  8. 黑客上传到网盘的txt文件第8行的内容是？[答案：XXX]  
打开txt文件可以看到第八行是：$$  
![image](https://image.3001.net/images/20230613/1686588668_64874cfc6cfc775f89bcb.png!small)

  9. 被入侵主机的计算机名是？[答案：XXXXXXXXXXX]  
发现是找计算机名，一般思路而言需要先分析哪个是攻击IP地址，要根据统计流量，排除进行分析才能找到计算机主机名，但是在wireshark中通常nbns协议才会携带主机名，所以这里我不知道哪个是被攻击机器的情况下，直接过滤nbns协议，发现只有192.168.100.141和192.168.100.139的请求，确定了192.168.100.141，则192.168.100.139必然是，所有WIN-BFA1TO8PTNP必然是。（这里需要了解nbns协议）如下图所示：![image](https://image.3001.net/images/20230613/1686588703_64874d1fbcffa3f778aa0.png!small)

  10. 被入侵电脑的数据回传端口是？[答案：11]  
既然我们确定了黑客IP和被攻击IP，则可以使用ip.dst==192.168.100.141&&ip.src==192.168.100.139进行过滤，如下图所示：  
![image](https://image.3001.net/images/20230613/1686588730_64874d3a2175a96ac7e07.png!small)  
21端口是ftp数据传输端口。追踪下8888发现是断链的请求排除。在追踪下62292发现是请求目录setup.exe；![image](https://image.3001.net/images/20230613/1686588795_64874d7bd7200e2ec0194.png!small)在请求下63762，通过保存原始数据，发现是伪造的360木马文件的内容；![image](https://image.3001.net/images/20230613/1686588834_64874da24d8ade10325b7.png!small)![image](https://image.3001.net/images/20230613/1686588870_64874dc65057eaee1c21f.jpg!small)  
在请求下49536发现hex是MZ开头的HEX文件，可能是windows可执行文件，保存原始数据发现还是伪造的360木马文件的内容![image](https://image.3001.net/images/20230613/1686588992_64874e4024447daeda15e.png!small)  
那么此时在ip.dst==192.168.100.141&&ip.src==192.168.100.139过滤中只剩下8000端口。发现在hex记录中是以ghost开头的内容，因为Gh0st开头的文件可能是Gh0st远程控制软件的客户端或服务器端程序可以用于远程控制计算机，窃取敏感信息，以及进行其他恶意活动，所有判断应该是8000端口为数据回传端口，如下图所示：  
![image](https://image.3001.net/images/20230613/1686589043_64874e73d8fae7e66ca5e.png!small)

  11. 流量包中ftp服务器的用户密码是？[答案：abcd]  
过滤ftp数据包，在tcp流中可以看见登录用户名和密码：![image](https://image.3001.net/images/20230613/1686589069_64874e8d8acf9049733ea.png!small)

  12. 流量包中ftp服务器中的木马文件的md5值是？[答案：字母小写]  
通过判断ftp服务器ip为192.168.100.139，可以过滤该ip地址：ip.addr ==
192.168.100.139。找到setup.exe流信息，也可按照上面题目分析的内容找到，其实这个文件在过滤的时候已经发现了，就是HEX文件以MZ开头的那个文件，如下图所示：  
![image](https://image.3001.net/images/20230613/1686589105_64874eb154f41d5d433bd.png!small)  
在追踪流中选择原始数据，另存为1.exe，可以获得图标为360图标的木马文件，如图所示：  
![image](https://image.3001.net/images/20230613/1686589141_64874ed5d737720a831e7.png!small)  
另存出来的文件为:  
![image](https://image.3001.net/images/20230613/1686589167_64874eef2c0c6f8729d59.jpg!small)  
计算md5为：2a49a00a1f0b898074be95a5bbc436e3  
13\. 木马文件伪造的软件版本是？[答案：0.0.0.0]  
在详细信息中找到伪造的版本信息如下图所示：7.5.0.1039  
![image](https://image.3001.net/images/20230613/1686589201_64874f118e9b05b0bc597.png!small)

  13. 黑客上传到网盘的压缩包解压密码是？[答案：XXXXXXXXXXX]  
由上述可知压缩包为：flag.rar。通过stegseek进行解密：  
stegseek --crack pass.jpg dic.txt -xf output.txt  
![image](https://image.3001.net/images/20230613/1686589232_64874f30aa5603e38f151.png!small)  
通过摩斯进行解密获取到的明文密码为：今天天气不错  
15\. 黑客上传到网盘的压缩包内文件的内容是？[答案：xxxxxxx]  
使用上述题目解压flag.rar，打开找到内容为：![image](https://image.3001.net/images/20230613/1686589272_64874f58c247171b56e09.png!small)

  
  

