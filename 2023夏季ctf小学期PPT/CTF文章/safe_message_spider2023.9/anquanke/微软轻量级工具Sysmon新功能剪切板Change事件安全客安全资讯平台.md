# 微软轻量级工具Sysmon新功能剪切板Change事件

阅读量 **214069**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-04-21 10:30:39

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t0137f9ad6730b4c509.jpg)

Sysmon的最新版本增加一个事件id： 24 剪切板事件，sysmon的官网描述如下  
<https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon>

![](https://p0.ssl.qhimg.com/t014f52488e256a3372.png)

如果要开启这个功能可以进行简单的配置文件，内容如下:

![](https://p4.ssl.qhimg.com/t01a22d6ab06cea31d0.png)

`<EventFiltering>`  
`<!-- Log all drivers except if the signature -->`  
`<!-- contains Microsoft or Windows -->`  
`<!-- Do not log process termination -->`  
`<ClipboardChange onmatch="exclude" />`  
`</EventFiltering>`

输入命令行：

**Sysmon64.exe -c “new 1.xml”** 打开更新规则

![](https://p2.ssl.qhimg.com/t0105aa2548876b4e20.png)

然后我们打开windows事件日志记录就可以看到剪切板的记录事件了,事件id值是24

![](https://p2.ssl.qhimg.com/t016e4009897e02924e.png)

查看详细信息

![](https://p3.ssl.qhimg.com/t0108768fefc0834d9a.png)

SYSMONSCHEMA.XML描述该事件的进程参数

![](https://p3.ssl.qhimg.com/t01250a02b0597a68fe.png)

多两条参数配置信息

`<option switch="z" name="ClipboardInstance" argument="required"
noconfig="true" exclusive="true" />`  
`<option name="CaptureClipboard" argument="none" />`

SYSMONSCHEMA.XML描述该事件规则上报结构  
`<event name="SYSMONEVENT_CLIPBOARD" value="24" level="Informational"
template="Clipboard changed" rulename="ClipboardChange" version="5">`  
`<data name="RuleName" inType="win:UnicodeString" outType="xs:string" />`  
`<data name="UtcTime" inType="win:UnicodeString" outType="xs:string" />`  
`<data name="ProcessGuid" inType="win:GUID" />`  
`<data name="ProcessId" inType="win:UInt32" outType="win:PID" />`  
`<data name="Image" inType="win:UnicodeString" outType="xs:string" />`  
`<data name="Session" inType="win:UInt32" />`  
`<data name="ClientInfo" inType="win:UnicodeString" outType="xs:string" />`  
`<data name="Hashes" inType="win:UnicodeString" outType="xs:string" />`  
`<data name="Archived" inType="win:UnicodeString" outType="xs:string" />`  
`</event>`

上报事件id: 24, 事件字段：UtcTime、ProcessGuid、ProcessId、Image、Session、Hashes、ClientInfo

了解了该事件的大概的情况的后，我们就要开始分析sysmon监测该事件的原理方法。

## 1\. 开关打开剪切板开关后就会运行Start函数

![](https://p5.ssl.qhimg.com/t01edd2eae1fb4f5cf3.png)

## 2\. StartClipboardListening

###
**（1）先获取两个与剪切板监控相关的函数AddClipboardFormatListener、RemoveClipboardFormatListener的函数地址**

![](https://p4.ssl.qhimg.com/t0126e59af83b4fdad7.png)

###  **（2）创建一个窗口来监控剪切板**

窗口的类名: L”smclip”;  
窗口函数WinMonitorClipBoard

![](https://p4.ssl.qhimg.com/t013260671ccbf2e24e.png)

### **（3）窗口回调函数WinMonitorClipBoard的逻辑**

**1> WM_CREATE消息**

![](https://p3.ssl.qhimg.com/t0148cbbce34e2b54cc.png)

WM_CREATE是窗口的创建消息，sysmon在WM_CREATE的时候会调用AddClipboardFormatListener(HWND),该函数的作用是指定哪个窗口有资格去捕捉剪贴板内容更新的消息。然后调用hWndNewNext
= SetClipboardViewer(a1); SetClipboardViewer()也是监控剪切板事件的设置函数，把当前窗口假如的监控队列里。

**2> WM_DRAWCLIPBOARD 剪切板内容变化事件**

当发生这个消息的时候，sysmon
就回调用GetClipboardSequenceNumber函数获取当前窗体在剪切板链下的序列号,调用GetPriorityClipboardFormat获取在一个列表下某个索引的剪切板格式

![](https://p1.ssl.qhimg.com/t01ba5a39cb59deb36e.png)

它要获取的是三种格式： CF_TEXT 、 CF_WAVE 、CF_OEMTEXT  
接下来就尝试打开剪切板并且获取剪切板里的数据

![](https://p3.ssl.qhimg.com/t0152d6471f01456d35.png)

获要获取的就是上述三种格式的数据，获取数据后就计算数据的hash。  
为了补充信息，sysmon还会通过GetClipboardOwner获取当前剪切板改变的窗口句柄，然后通过GetWindowThreadProcessId函数获取该窗口的线程以及进程。

![](https://p3.ssl.qhimg.com/t010ddb3eaf7e05c39e.png)

**3 > WM_CHANGECBCHAIN 监控链改变的消息**

这个消息是当有新的监控程序加入或移出，那么就会给这个链表中每个程序发送一个消息WM_CHANGECBCHAIN,
sysmon遇到有这个发生的时候会判断是否是自己的消息被移除,了,就把自己再加回来了。

**4> WM_CLIPBOARDUPDATE 剪切板更新消息**

这个消息是AddClipboardFormatListener消息带来的，Sysmon的处理逻辑与WM_DRAWCLIPBOARD一样。

**5> WM_QUIT 退出消息**

![](https://p0.ssl.qhimg.com/t019cc9aed2a3115d09.png)

退出就销毁当前监控。

sysmon的监控逻辑就这么简单，下面可以自己尝试写一个demo，可以建立一个MFC的窗口程序，窗口初始化的时候调用AddClipboardFormatListener

![](https://p3.ssl.qhimg.com/t01cf282c3d4be47b30.png)

窗体里继承映射WM_DRAWCLIPBOARD 和 消息

`afx_msg void OnDrawClipboard();`  
`afx_msg void OnClipboardUpdate();`

`BEGIN_MESSAGE_MAP(CForbidCapDlg, CDialogEx)`  
`ON_WM_DRAWCLIPBOARD()`  
`ON_WM_CLIPBOARDUPDATE()`  
`END_MESSAGE_MAP()`

当我在其他进程鼠标右键复制操作一下，监控程序就会进入OnClipboardUpdate

![](https://p5.ssl.qhimg.com/t010570f388dc8e9d43.png)

Demo实例成功，至此，这篇文章就分析到这里，剪切板的监控就这么简单，大家有兴趣可以自行研究的更深入。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **浪子_三少** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/238360](/post/id/238360)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Sysmon](/tag/Sysmon)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t0174a6724d592adb88.jpg) 浪子_三少

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

