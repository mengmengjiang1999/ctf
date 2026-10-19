***本文原创作者：艾登——皮尔斯，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 前言

 **本篇文章主要以图文教程和视频演示详细地教你如何快速学会使用SpyNote
5.0图形化工具来穿透内网远程控制Android手机。本教程有一定的攻击性，请各位Freebuf小粉合理使用。(切勿用于违法，否则因用于违法产生的一切法律纠纷，由使用者自行承担，与本文作者无关)**

![图片.png](https://image.3001.net/images/20180304/15200935222671.png!small)

Freebuf之前相关SpyNote的介绍文章

>
> [小心，Android木马工具SpyNote免费啦！远程监听就是这么简单](http://www.freebuf.com/news/110776.html)  
>
>
> [当心，安卓远控（spynote）升级了……](http://www.freebuf.com/news/110776.html)

##  **所需环境:**

> Windows 7/8/10系统
>
> Java环境
>
> Microsoft .NET Framework 4.0框架
>
> SpyNote 5.0 （[ __]()[百度云传送门提取码nhq6](https://pan.baidu.com/s/1BkMm-> iEs__f7wZALMOZztg),[官方下载地址](http://www.iq-team.org/spy-note/))
>
> 网络通(用于端口映射到公网来达到穿透内网[传送门](http://www.youtusoft.com))

##  **教程开始:**  

1.下载并且安装Java[ __](https://www.java.com/zh_CN/)，已经安装了Java可以跳过

![图片.png](https://image.3001.net/images/20180304/15200939462033.png!small)  

2.如果你的计算机没有安装Microsoft .NET Framework 4.0框架，请去百度搜索下载安装，已经安装了Microsoft .NET
Framework 4.0可以跳过。  

![图片.png](https://image.3001.net/images/20180304/1520094006786.png!small)  

3.下载安装网络通给接下来的内网穿透做铺垫

![图片.png](https://image.3001.net/images/20180304/15200940816393.png!small)  

下载进行安装，如果你没有网络通的帐号就去注册一个帐号，并且登录。

![图片.png](https://image.3001.net/images/20180304/15200940953023.png!small)  

然后打开CMD输入ipconfig,我的内网IP地址是:192.168.1.152  

![图片.png](https://image.3001.net/images/20180304/15200941052071.png!small)  

然后点击添加映射,免费用户线路就选择美国1，名称你可以随便输入，内网IP就输入自己的内网IP地址，内网端口可以任意，但是不能冲突。  

![图片.png](https://image.3001.net/images/20180304/15200941182056.png!small)  

点击确定后，鼠标移到线路，右击选择复制外网地址  

![图片.png](https://image.3001.net/images/20180304/15200941285574.png!small)  

由上图可以得知，我的外网端口是29035  

4\. 打开SpyNote5.0点击Listen Port(监听端口)  

![图片.png](https://image.3001.net/images/20180304/1520094164414.png!small)  

输入2222添加监听端口--->Add,再输入29035添加上线地址的端口--->Add，再点击OK  

![图片.png](https://image.3001.net/images/20180304/15200941838867.png!small)  

当如下图所示时，控制端就已经处于监听状态。  

![图片.png](https://image.3001.net/images/20180304/15200942433507.png!small)  

5\. 点击BuildClient生成木马。  

(1)Client Info设置木马的图标，版本号，名称：  

![图片.png](https://image.3001.net/images/20180304/15200942745615.png!small)  

(2)Dynamic DNS设置上线地址：

![图片.png](https://image.3001.net/images/20180304/15200942909320.png!small)  

(3)Properties设置对生成的木马进行一些特殊设置  

![图片.png](https://image.3001.net/images/20180304/15200943915101.png!small)

> Hide application是隐藏应用程序
>
> Wi-fi Wakelock是锁定WIF
>
> CPU WakelockI是常驻后台
>
> Permission Root SuperSu是主动申请Root权限
>
> Device Administration是请求激活设备管理器(防普通方式卸载)
>
> Accessibility(Keylogger)是用于键盘记录
>
> Set a Repeating Alarm是设置报警(应该是上线提示)

这里我就全选  

(4)Merging App(捆绑APK)，就是和其他apk安装包进行捆绑

![图片.png](https://image.3001.net/images/20180304/15200944851208.png!small)  

因为捆绑有几率会因为被捆绑文件加固而捆绑失败，所以这里我就不捆绑。

(5)设置好一切后点击左上角的Build--->Build APK创建木马,会弹出一个这个  

![图片.png](https://image.3001.net/images/20180304/15200946165776.png!small)  

(6)我们就找到你SpyNote5.0的所在路径的根目录有个Patch的文件夹  

![图片.png](https://image.3001.net/images/20180304/1520094638552.png!small)  

(7)点击进入选择Patch-StaminaMode-release，然后点击打开  

![图片.png](https://image.3001.net/images/20180304/15200946504028.png!small)  

(8)你点击打开之后下面就会出现一个绿色的进度条  

![图片.png](https://image.3001.net/images/20180304/15200946597939.png!small)  

(9)生成完毕会自动打开一个文件夹里面有一个名字为client的apk文件就是你刚刚生成的木马。  

![图片.png](https://image.3001.net/images/20180304/15200946716679.png!small)  

(10)现在我用我的手机(魅蓝5)安装刚刚生成木马，然后等待上线，安装打开后控制端这边就已经提示上线了，接下来就可以对这个手机进行一个远程的控制了。

![图片.png](https://image.3001.net/images/20180304/15200947299988.png!small)  

## **主要功能:**

> File Manager：读取手机文件
>
> SMS Manager：读取手机SMS短信
>
> Calls Manager：读取手机通讯录
>
> Contacts Manager：读取联系人
>
> Location Manager：读取GPS位置
>
> Account Manager：不详
>
> Camera Manager：利用摄像头进行拍照
>
> Audio Recorder：录音
>
> Shell Terminal：不详
>
> Applications：应用管理
>
> Keylogger：键盘记录
>
> Settings：设置
>
> Phone：手机管理
>
> Client：客户端管理
>
> Chat：进行文本对话

下面是SpyNote5.0生成教程和演示视频:

  

##  **防范方法：**

> (1)安装个手机杀毒软件，定期更新病毒库，定期杀毒
>
> (2)提高自身的安全意识
>
> (3)不下载安装第三方来历不明的文件，下载应用最好去应用商店下载
>
> (4)对于不必要的权限建议你禁止其APP获取权限

##  **小结：**

这款工具因为其功能强大而闻名，且上线是比Metasploit生成的payload上线要稳定很多，还会自动弹出激活设备管理器窗口，来提升自身的权限，以防被普通卸载方式卸载，但是没有提及如何地详细使用，所以鄙人就弄了一个详细的图文+视频的教学献给忠实的Freebuf小粉，就当作是元宵节鄙人送给你们的礼物吧！希望Freebuf小粉们喜欢！

![图片.png](https://image.3001.net/images/20180304/15200975192932.png!small)

 ***本文原创作者：艾登——皮尔斯，本文属FreeBuf原创奖励计划，未经许可禁止转载**

