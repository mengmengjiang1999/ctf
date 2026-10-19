**今天给大家介绍的是一款名叫Wordpress Exploit
Framework的Ruby框架，研究人员可利用该框架来研发或使用其自带某开来对由[WordPress](https://www.kitploit.com/search/label/WordPress)驱动的网站或系统进行[渗透测试](https://www.kitploit.com/search/label/Penetration%20Testing)。**  

![1.png](https://image.3001.net/images/20180618/15293199518566.png!small)

## 工具运行条件

确保你的设备安装了Ruby（版本>=2.4.3），然后切换到WPXF文件夹，并在终端中运行下列命令完成依赖组件的安装：

    
    
    bundle install

如果你的设备没有安装bundler，你还需要运行下列命令进行安装：

    
    
    gem install bundler

## 安装问题

### Debian系统

如果你在安装WPXF依赖组件时遇到了问题，首先需要确保你安装好了编译.c文件的所有工具：

    
    
    sudo apt-get install build-essential patch

除此之外，很可能你的设备中没有安装关键的开发头文件，你可以使用下列命令进行安装：

    
    
    sudo apt-get install ruby-dev zlib1g-dev liblzma-dev

### Windows系统

如果你遇到了问题，很可能是因为libcurl.dll没有加载成功，你需要确保Ruby
bin文件夹中包含了最新版的libcurl库，或者在PATH环境变量中指定代码库的路径。

最新版本libcurl库：【[点我下载](http://curl.haxx.se/download.html)】

下载成功后，将代码库文件提取到Ruby bin目录中，注意不要覆盖任何现有的DLL文件。

## 如何使用？

打开终端并切换到项目目录，使用下列命令运行框架：

    
    
    ruby wpxf.rb

框架加载成功后，你将会看到wpxf的终端窗口，你可以使用search命令搜索模块或使用use命令加载模块。

加载模块后，你可以使用set命令来设置模块选项，或使用info命令查看模块信息。

在下面的例子中，我们加载了symposium_shell_upload漏洞利用模块，并针对目标特征对模块和Payload选项进行了设置，然后运行模块。

![2.png](https://image.3001.net/images/20180618/15293200846612.png!small)

大家可以从【[这里](https://github.com/rastating/wordpress-exploit-framework/wiki/Supported-Commands)】查看该框架所有支持的命令。

## 可用的Payload

> 1\. bind_php：上传一个脚本，并跟特定端口绑定，WPXF将建立一个远程shell连接。
>
> 2\. custom：上传并执行自定义PHP脚本。
>
> 3\. download_exec：下载并运行一个远程可执行文件。
>
> 4\. meterpreter_bind_tcp：使用msfvenom生成一个绑定TCP Payload的Meterpreter模块。
>
> 5\. meterpreter_reverse_tcp：使用msfvenom生成一个绑定了反向TCP Payload的Meterpreter模块。
>
> 6\. Exec：在远程服务器中运行一个shell命令，返回WPXF会话的输出结果。
>
> 7\. reverse_tcp：上传一个能够建立反向TCP Shell的脚本。

### 如何开发自己的模块和Payload

关于如何编写模块和Payload，请大家参考【[这份文档](https://github.com/rastating/wordpress-exploit-framework/wiki)】，完整的API开发文档可以从【[这里](http://www.getwpxf.com/)】找到。

 *** 参考来源：[kitploit](https://www.kitploit.com/2018/05/wordpress-exploit-framework-v192.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

