# 【技术分享】拦截密码用于提升OSX权限的分析

阅读量 **93800**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2016-09-19 14:35:15

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

原文地址：<https://www.scriptjunkie.us/2016/09/intercepting-passwords-to-escalate-privileges-on-os-x/>

译文仅供参考，具体内容表达以及含义原文为准。

**前言**

几周前，Dropbox
的“黑客”委员会受到了广泛关注。安装Dropbox之后会要求用户输入管理员密码，然后它就会在以后的运行中为自己启用访问权限，就算用户禁用这些权限也无法阻止。尽管互联网用户对此表示了强烈的不满、Dropbox也十分无礼，但是它事实上并没有利用任何漏洞、也没有攻击任何安全保护；一旦用户交出了自己的管理员密码，这就意味着它可以为所欲为。

**不管你相不相信，这都是一个真实存在的安全问题！OSX上的Dropbox不是这样的，它不会询问用户密码，在用户更改管理员信息的时候它会直接获取密码。**

这是之前一篇文章《安全伪装游戏》的后续。那篇文章主要内容是现在主要的桌面操作系统是如何在默认有限权限情况下运行用户程序，以及操作系统需要某些特定权限运行特定程序时用户是如何提升权限的。虽然这足以让用户避免无意中破坏重要的保护措施，但是这些“安全”措施完全不够用来阻止黑客；在同一个登陆界面中未经授权的程序拥有足够的权限来检测、拦截、更改或控制权限提升过程。

  

**拦截用于升级OSX权限的密码分析**

上一次我利用命令行工具截获密码，这次我使用的是标准的OSX GUI，部分[
**源代码**](https://github.com/scriptjunkie/kcap) 如下：

    
    
    +<?xml version="1.0" encoding="UTF-8"?>
    +<!-- You may freely edit this file. See commented blocks below for -->
    +<!-- some examples of how to customize the build. -->
    +<!-- (If you delete it and reopen the project it will be recreated.) -->
    +<!-- By default, only the Clean and Build commands use this build script. -->
    +<!-- Commands such as Run, Debug, and Test only use this build script if -->
    +<!-- the Compile on Save feature is turned off for the project. -->
    +<!-- You can turn off the Compile on Save (or Deploy on Save) setting -->
    +<!-- in the project's Project Properties dialog box.-->
    +<project name="kcap" default="default" basedir=".">
    +    <description>Builds, tests, and runs the project kcap.</description>
    +    <import file="nbproject/build-impl.xml"/>
    +    <!--    +
    +    There exist several targets which are by default empty and which can be 
    +    used for execution of your tasks. These targets are usually executed 
    +    before and after some main targets. They are: 
    +
    +      -pre-init:                 called before initialization of project properties
    +      -post-init:                called after initialization of project properties
    +      -pre-compile:              called before javac compilation
    +      -post-compile:             called after javac compilation
    +      -pre-compile-single:       called before javac compilation of single file
    +      -post-compile-single:      called after javac compilation of single file
    +      -pre-compile-test:         called before javac compilation of JUnit tests
    +      -post-compile-test:        called after javac compilation of JUnit tests
    +      -pre-compile-test-single:  called before javac compilation of single JUnit test
    +      -post-compile-test-single: called after javac compilation of single JUunit test
    +      -pre-jar:                  called before JAR building
    +      -post-jar:                 called after JAR building
    +      -post-clean:               called after cleaning build products
    +
    +    (Targets beginning with '-' are not intended to be called on their own.)
    +
    +    Example of inserting an obfuscator after compilation could look like this:
    +
    +        <target name="-post-compile">
    +            <obfuscate>
    +                <fileset dir="${build.classes.dir}"/>
    +            </obfuscate>
    +        </target>
    +
    +    For list of available properties check the imported 
    +    nbproject/build-impl.xml file. 
    +
    +
    +    Another way to customize the build is by overriding existing main targets.
    +    The targets of interest are: 
    +
    +      -init-macrodef-javac:     defines macro for javac compilation
    +      -init-macrodef-junit:     defines macro for junit execution
    +      -init-macrodef-debug:     defines macro for class debugging
    +      -init-macrodef-java:      defines macro for class execution
    +      -do-jar:                  JAR building
    +      run:                      execution of project 
    +      -javadoc-build:           Javadoc generation
    +      test-report:              JUnit report generation
    +
    +    An example of overriding the target for project execution could look like this:
    +
    +        <target name="run" depends="kcap-impl.jar">
    +            <exec dir="bin" executable="launcher.exe">
    +                <arg file="${dist.jar}"/>
    +            </exec>
    +        </target>
    +
    +    Notice that the overridden target depends on the jar target and not only on 
    +    the compile target as the regular run target does. Again, for a list of available 
    +    properties which you can use, check the target you are overriding in the
    +    nbproject/build-impl.xml file. 
    +
    +    -->
    +</project>

**  
**

**其余代码详见：** **<https://github.com/scriptjunkie/kcap>**

OSX试图通过阻断程序用于运行密码提示的非特权注入/调试过程来避免这种不安全事件的发生。它还通过击键记录功能添加了阻止非特权代码检测键盘，并且阻止程序弹出密码提示窗口。但是这些限制都很容易绕过。

程序只需要使用屏幕截图功能，并且以编程方式生成按键和鼠标内容，就可以在本地以图片方式打破OSX的这些努力。

相比于WINDOWS的UAC提示允许非特权进程进行交互并弹出窗口骗取密码，OSX的这个拦截十分简单。请看视频：

**骗取密码的工作原理：**

1、不断弹出窗口检测系统身份验证提示，直到用户做出回应；

2、对弹出窗口提示进行截屏；

3、关闭真实的身份验证提示；

4、创建一个克隆版本并在桌面显示；

5、在用户输入密码时保存密码；

6、再次打开原始的身份验证窗口；

7、将其移到屏幕以外；

8、将密码输入真实的身份验证；

9、将原始窗口移动回原始位置；

10、点击输入，将输入的密码发送到原始的身份验证窗口。

这些过程听起来似乎十分繁琐，但是实际情况是这些过程只要一瞬间就可以全部完成，甚至不会有人注意到。

可能会有吹毛求疵的人指出在运行这一程序的时候会创建一个空的停驻，所以这一攻击发生的时候是可以在角落看出有几个可疑像素的。但是我从来没有编写过任何OSX
GUI程序，只是花了几个小时时间在JAVA上编写了一个程序。如果写一个本地程序，应该可以同时达到这两点要求。

我在Macbook
Air上进行了测试，默认分辨率是1440*900，阻止绝大多数系统应用程序的密码输入提示。使用其他系统可能会出现一些偏差，所以如果想要在其他系统中进行测试，需要测试和修改一些偏移量。

如果苹果通过阻止未经授权程序进行交互“修复”了这一问题，这不算什么；未经授权的程序只要简单地修改启动系统设置应用程序的快捷方式，并让其启用程序的克隆版本，密码就又一次无处躲藏了。

普遍观点是当你输入密码时只是在一个时间点赋予一个命令一个特定权限。但是事实是，只要你曾经赋予黑客一个特权，他就可以在任何时间在你的账户中运行任何代码，并决定任何他们想要提升的特权。

阻止非特权桌面程序提升权限永远也不会成为一个真正有效的安全屏障。有效的做法就是用户将账户管理任务和日常任务分开管理，在使用管理员账户登录电子邮件的时候不要浏览互联网网页，登陆日常账户的时候不要输入自己的管理员密码。

本文翻译自安全客 [原文链接](https://www.scriptjunkie.us/2016/09/intercepting-passwords-to-escalate-privileges-on-os-x/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **默白** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/84589](/post/id/84589)

安全客 - 有思想的安全新媒体

本文转载自: [安全客](https://www.scriptjunkie.us/2016/09/intercepting-passwords-to-escalate-privileges-on-os-x/)

如若转载,请注明出处： <https://www.scriptjunkie.us/2016/09/intercepting-passwords-to-escalate-privileges-on-os-x/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p4.ssl.qhmsg.com/dm/200_200_100/t011edf3404f95091e3.jpg) 默白

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

