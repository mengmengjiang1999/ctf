许多恶意软件分析人员喜欢使用MS
Word或Excel中的VB编辑器来分析恶意宏代码，因为它提供了一个不错的调试环境。这是一种在其本机上下文中运行VBA代码的便捷解决方案，来取消掩盖严重混淆的宏代码。

## 按住SHIFT键

为此，必须先按“启用内容”按钮，然后按Alt +
F11打开编辑器并访问VBA源代码。众所周知的技巧是在打开文档/工作簿时按住SHIFT键，直到按下“启用内容”。Shift键可禁用自动宏触发器，例如Document_Open或AutoOpen，它们被用作大多数恶意宏中的入口点。

![1620810443_609b9acb86e8a9c470574.png!small?1620810443755](https://image.3001.net/images/20210512/1620810443_609b9acb86e8a9c470574.png!small?1620810443755)

然后可以研究源代码而不被感染，设置断点或用无害的语句替换危险的语句，并逐步运行代码以了解其行为。

## 问题1：SHIFT键仅在按下时才起作用

鲜为人知的是，在打开文件时仅按Shift键是不够的。Shift键被按下时才有效，一旦放开就无效。因此，如果宏使用其他触发器（例如Document_Close），则在关闭文件时它可能会运行其恶意payload，除非分析人员在关闭文件时不会忘记再次按下Shift键......

要对其进行测试，可以简单地使用以下宏创建Word文档，然后将其关闭，在按住Shift键的同时重新打开文件。Document_Open消息不应显示，接着释放Shift键，然后关闭文档将显示Document_Close消息。

    
    
    Private Sub Document_Open()
        MsgBox "Document_Open"
    End Sub
    Private Sub Document_Close()
        MsgBox "Document_Close"
    End Sub

## 问题2：ActiveX触发器

2016年8月，一些恶意软件作者开始在其宏中使用晦涩的ActiveX对象（例如InkPicture）：

<https://twitter.com/joe4security/status/770691099988025345>

<https://twitter.com/_jsoo_/status/771209677191249921>

事实证明，ActiveX对象可以生成触发VBA宏的事件。打开文档/工作簿时一旦按下“启用内容”，就会触发其中某些事件，例如InkPicture_Painted。许多其他ActiveX对象也可以触发各种事件，这些事件可以被利用来运行恶意宏：

<http://www.greyhathacker.net/?p=948>

<http://blogs.cisco.com/security/malicious-microsoft-office-documents-mov>

根据我对MS
Word的最新版本（2016和2013）的测试，当用户按住Shift键时，不会禁用ActiveX对象事件。这意味着使用VB编辑器对其中的恶意宏代码分析很危险，无法保证安全。

底线：不要相信Shift键！

## 解决方案？

首先，我要说的是，在不事先查看VBA源代码的情况下，在MS
Office应用程序中打开可疑文件不是一个好主意。最安全的解决方案是一开始就使用oledump或olevba之类的工具提取VBA代码。然后，查看代码以确定所有潜在的入口点，尤其是那些可能会忽略Shift键技巧的入口点。olevba可以通过显示已知入口点的列表（在下表的第一列中标记为“
AutoExec”）来快速定位分析。

![1620810540_609b9b2cb5f663b8dc1e1.png!small?1620810541058](https://image.3001.net/images/20210512/1620810540_609b9b2cb5f663b8dc1e1.png!small?1620810541058)

如果所有入口点都类似于Document_Open或AutoOpen，则可以在MS
Office中打开文件，然后在按住Shift键的同时按“启用内容”。如果不是，那么可以尝试以下步骤：

1.将VBA宏代码从olevba或oledump保存到文本文件中。

2.在MS Office中打开可疑文件，而无需按“启用内容”。

3.如果处于保护视图中，请单击“启用编辑”。

4.转到“文件”菜单。

5.单击“另存为”，然后以无宏格式保存文件，例如“ Word文档（.docx）”。

6.关闭应用程序。

7.使用olevba或oledump验证新文件不包含任何宏。

8.重新打开刚刚保存的无宏文件。

9.如果有ActiveX对象，则可能需要按“启用内容”。因为宏已被删除，所以它应该是安全的。

10.使用Alt + F11打开VB编辑器。

11.将你在步骤1中提取的VBA代码逐个过程复制并粘贴回文档中。确定宏运行代码，然后将这些语句替换为MsgBox或其他无害的代码。

12.现在可以使用VB编辑器的调试功能对文档进行分析和模糊处理了。

这种方法的另一个不错的副作用是，即使VBA项目受密码保护，该方法仍然有效。

## 参考链接

<https://www.decalage.info/en/vbashift>

<https://twitter.com/joe4security/status/770691099988025345>

<https://twitter.com/_jsoo_/status/771209677191249921>

<http://www.greyhathacker.net/?p=948>

[http://blogs.cisco.com/security/malicious-microsoft-office-documents-mov﻿](http://blogs.cisco.com/security/malicious-microsoft-office-documents-mov)

