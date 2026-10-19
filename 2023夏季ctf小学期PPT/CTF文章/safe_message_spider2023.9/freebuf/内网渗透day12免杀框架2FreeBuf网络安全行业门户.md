## 免杀框架2

### 1\. IPC管道连接

命名管道，可以通过ipc进行主机远程管理和文件传输，基于139和445端口的开放

前提:服务端的administrator是开放的并且有设计密码

首先将win10作为客户端向win7的发送ipc连接

[![wps154](https://image.3001.net/images/20201116/1605508843.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112432765-541758769.jpg)

net use \\\192.168.227.128\IPC$ "123123" /user:administrator  
  
---  
  
通过命令行的方式开启管理员cmd

[![wps155](https://image.3001.net/images/20201116/1605508843.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112433463-1640830046.jpg)

runas /noprofile /user:administrator cmd  
  
---  
  
查看会话（显示物理机已经成功连接到win7上）

[![wps156](https://image.3001.net/images/20201116/1605508844.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112434152-2101305081.jpg)

查看C盘目录

[![wps157](https://image.3001.net/images/20201116/1605508844.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112435060-2013015429.jpg)

dir \\\192.168.227.128\c$  
  
---  
  
从win7上下载文件到win10上

[![wps158](https://image.3001.net/images/20201116/1605508845.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112435740-63310416.jpg)

[![wps159](https://image.3001.net/images/20201116/1605508846.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112436335-617943866.jpg)

copy \\\192.168.227.128\c$ nc.exe  
  
---  
  
上传文件

[![wps160](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112436940-204810128.jpg)

[![wps161](https://image.3001.net/images/20201116/1605508846.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112437535-771073168.jpg)

copy useruid.ini \\\192.168.227.128\c$  
  
---  
  
从win10上将连接删除

[![wps162](https://image.3001.net/images/20201116/1605508847.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112438103-1924312081.jpg)

[![wps163](https://image.3001.net/images/20201116/1605508847.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112438733-1105663720.jpg)

net use \\\192.168.227.128\IPC$ /del  
  
---  
  
### 2\. 查看wifi密码

查看连过的所有wifi

[![wps164](https://image.3001.net/images/20201116/1605508848.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112439391-1892564711.jpg)

netsh wlan show profiles  
  
---  
  
查看某个所连wifi的密码

[![wps165](https://image.3001.net/images/20201116/1605508848.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112440130-269339678.jpg)

netsh wlan show profiles wifi名 key=clear  
  
---  
  
[回到顶部](https://www.cnblogs.com/caihon/p/13957822.html#_labelTop)

### 3\. Phantom-Evasion免杀框架的运用

安装依赖python3 phantom-evasion.py --setup

./phantom-evasion.py进入后选择1.windows模块

[![wps166](https://image.3001.net/images/20201116/1605508849.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112440882-294051480.jpg)

选择payload（选择2作为测试）

[![wps167](https://image.3001.net/images/20201116/1605508849.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112441482-1331098646.jpg)

除了ip和端口其他随便填默认就可以了

[![wps168](https://image.3001.net/images/20201116/1605508850.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112442156-1627313860.jpg)

成功签名

[![wps169](https://image.3001.net/images/20201116/1605508850.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112442896-341132428.jpg)

这边注意最新的openssl中的crypto中的类PKCS12Type改成了PKCS12

所以需要在phantom中改对应代码

[![wps170](https://image.3001.net/images/20201116/1605508851.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112443517-1767631078.jpg)

将这个文件中对应的PKCS12Type的改成PKCS12就OK了

### 4\. 自解压（sfx）

首先先准备好三个东西（木马，图片，ico）

[![wps171](https://image.3001.net/images/20201116/1605508851.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112444083-1599785924.jpg)[![wps172](https://image.3001.net/images/20201116/1605508852.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112444596-468194273.jpg)[![wps173](https://image.3001.net/images/20201116/1605508852.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112445116-1080359430.jpg)

用winrar压缩选择自解压的木马（这里是右键木马不是图片）

[![wps174](https://image.3001.net/images/20201116/1605508853.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112445731-319677843.jpg)

然后点高级->自解压选项

[![wps175](https://image.3001.net/images/20201116/1605508854.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112446367-566404735.jpg)

在更新选项中选中解压并替换文件和覆盖所有文件

[![wps176](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112447059-2116936242.jpg)

选择文本和图标选项，加载自解压的文件图标（一开始准备的那个ico）

[![wps177](https://image.3001.net/images/20201116/1605508855.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112447673-1280377818.jpg)

在设置选项中，设置提取后运行的东西（运行一开始准备的jpg文件和木马文件）

[![wps178](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112448349-1340658128.jpg)

在模式选项中的静默模式选择全部隐藏

[![wps179](https://image.3001.net/images/20201116/1605508855.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112448931-2040381100.jpg)

点确定生成laohu.exe()

[![wps180](https://image.3001.net/images/20201116/1605508856.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112449588-989905422.jpg)

连接成功

[![wps181](https://image.3001.net/images/20201116/1605508856.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112450187-1686777763.jpg)

### 5\. 数字签名

利用数字签名添加器为木马添加数字签名

[![wps182](https://image.3001.net/images/20201116/1605508857.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112450794-420509177.jpg)

[![wps183](https://image.3001.net/images/20201116/1605508857.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112451563-851618255.jpg)

木马文件成功获得数字签名

[![wps184](https://image.3001.net/images/20201116/1605508859.jpg!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112452278-645596859.jpg)

### 6\. 资源替换

使用资源编辑器(Resource Hacker)对木马文件的资源进行替换

可以替换掉一些元素使其拥有免杀的效果

[![wps185](https://image.3001.net/images/20200701/1593550745.png!small)](https://img2020.cnblogs.com/blog/2209303/202011/2209303-20201111112452876-726206775.jpg)

