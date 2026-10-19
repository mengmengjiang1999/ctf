**近期 Fortinet 研究专家发现臭名昭著的间谍软件 Agent Tesla 出现了全新的变种，而变种传播是通过特制的 Microsoft
Word文件进行的。**  

Agent Tesla
是一种用来收集系统键击记录、剪贴板内容、屏幕截图、身份凭证的间谍软件，很多用户使用这款软件窥探受害者。为了实现这些功能，这款间谍软件在主函数中创建了不同的线程和定时函数。

![34.png](https://image.3001.net/images/20180409/15232418987067.png!small)  

专家首先在去年 6 月份就发现了这款恶意软件变种。当时他们观察到威胁样本中，黑客通过 VBA
宏的自动执行进行软件的传播。一旦用户启用了文档中包含的宏，间谍软件就会在受害者机器上成功安装。

![Agent-Tesla-document.png](https://image.3001.net/images/20180409/15232421384461.png!small)  

但在最新发现的行动中，黑客将附件文档的内容被制作成模糊的样子，这样用户会遵循文档上的说明，双击文档来得到更清晰的视图。

而如果用户照做了，这个文档就会提取可执行文件，在本地系统的临时文件中运行。

![image_302840596.img.png](https://image.3001.net/images/20180409/15232428277686.png!small)  

这个可执行文件名为“POM.exe”。运行的 POM.exe 即开始了恶意软件的最终安装程序。

使用分析软件查看这个可执行文件，可以看到黑客使用的是 MS Visual basic 进行编写。

![image_1342029953.img.png](https://image.3001.net/images/20180409/1523242842417.png!small)  

> 根据我的分析，这是一种安装程序。
>
> 运行时，它将两个文件“filename.exe”和“filename.vbs”放入“％temp％\子文件夹”中。
>
> 然后在执行文件“filename.vbs”后退出进程。下面中，就是“filename.vbs”的内容。

![image_945116478.img.png](https://image.3001.net/images/20180409/15232429843364.png!small)  

而为了使这个间谍软件在系统启动的时候就开始自动运行，它还会在系统注册表中添加自己（filename.vbs）。

![image_1603394154.img.png](https://image.3001.net/images/20180409/15232431295257.png!small)

目前看来，新变种的 C＆C服务器提交数据的方式已经改变。研究员表示，过去的攻击行动中使用的都是 HTTP POST
来发送收集的数据。但在观测到的最新变体中，它会使用 SMTPS 将收集到的数据发送到攻击者的邮箱。

更详细的 Agent Tesla 变种研究结果请见 [Blog 原文](https://www.fortinet.com/blog/threat-research/analysis-of-new-agent-tesla-spyware-variant.html)。

***参考资料：[securityaffairs](https://securityaffairs.co/wordpress/71154/breaking-news/agent-tesla-campaign.html)，kylin编译，转载请注明FreeBuf.COM**

