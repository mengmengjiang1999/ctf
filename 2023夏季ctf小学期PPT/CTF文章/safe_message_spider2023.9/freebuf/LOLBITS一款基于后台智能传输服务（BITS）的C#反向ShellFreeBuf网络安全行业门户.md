![1.png](https://image.3001.net/images/20200202/1580639797_5e36a6355684c.png!small)

## LOLBITS

**LOLBITS是一款C#反向Shell，它使用了微软后台智能传输服务（BITS）作为传输信道来与后端命令控制服务器进行交互。后台的命令控制服务器基于Flask
Web应用程序构建，并且只能通过包含了有效认证Header的HTTP请求来与之通信。**

### LOLBITS由以下三个部分组成：

> 1、C#代理，它负责在受感染主机中执行控制命令，并在命令执行成功后将输出结果发送回后台命令控制服务器。
>
> 2、Flask Web应用程序，它作为中间的调度程序，该组件可以伪装成合法网站来隐藏后端的C2基础设施，并且能够向客户端发送新的控制命令。
>
> 3、C&C命令行，可以用来控制代理。

为了防止通讯内容被拦截或窃听，代理与C&C服务器之间的通信内容会使用R**（基于预共享密钥）进行加密。LOLBITS的逻辑架构如下图所示：

![2.png](https://image.3001.net/images/20200202/1580639809_5e36a641c7f07.png!small)

为了避免安全研究人员复现命令控制请求来分析和研究C&C基础架构，每个身份验证Header都是随机的，并且只在一个周期内有效。

## 工具依赖

后台的C&C基础设施需要一台Windows Server 2012或以上版本，并安装Python 3.4以及下列Python依赖：

### Colorama：

    
    
    pip install colorama

### Flask：

    
    
    pip install flask

当前版本的C#客户端已在Windows Server 2016、Windows Server 2019、Windows 8.1和Windows
10平台上成功测试。编译环境如下：

> Visual Studio 2017及其以上版本
>
> .NET Framework 4.5及其以上版本

## 工具安装

使用下列命令将项目源码克隆至C&C服务器中：

    
    
    git clone https://github.com/Kudaes/LOLBITS.git

通过Widnwos服务器管理器安装Web Server（IIS），确保安装好CGI、ASP.NET以及.NET Extensibility：

![3.png](https://image.3001.net/images/20200202/1580639832_5e36a65855423.png!small)

并且为IIS安装 .NET Framework和BITS：

![4.png](https://image.3001.net/images/20200202/1580639836_5e36a65cae96e.png!small)

安装wfastcgi并在IIS中配置好Fast CGI设置。这里要求我们的Web应用程序采用Python开发，点击【[
_这里_](https://medium.com/@rajesh.r6r/deploying-a-python-flask-rest-api-on-iis-d8d9ebf886e9)】获取参考教程。

关闭默认网站，并使用IIS管理器创建一个新的站点，并为该站点启用BITS上传服务：

![5.png](https://image.3001.net/images/20200202/1580639841_5e36a661e81a0.png!small)

将本项目中C&C目录下的“the
content”文件拷贝到本地主机中的站点物理目录内，假设我们创建的网站指向的是本地的“C:\inetpub\wwwroot\bits”目录，那么该目录的结构应该如下：

    
    
    C:\inetpub\wwwroot\bits
    
    	    |__ /config            
    
    	         |-- auth.txt
    
    	    |__ /files
    
    	         |-- abcde1234          
    
    	         |-- default
    
    	    |__ /lolbins
    
    	         |-- base64decode.py
    
    	         |-- base64encode.py
    
    	         |-- a lot of other .py files
    
    	    |__ /templates
    
    	    	 |-- index.html
    
    	    |__ /static
    
    	    |__ /payloads
    
    	    |__ -- decrypt.py
    
    	    |__ -- encrypt.py
    
    	    |__ -- myapp.py
    
    	    |__ -- web.config

我建议大家给这个目录“C:\inetpub\wwwroot\bits”提供Everyone的完整访问权限来避免错误发生。

接下来，编辑web.config文件，修改下列两个配置项：

1、针对Web
Handler的scriptProcessor属性，点击IIS管理器，在IIS服务器的根路径选择FastCGI设置，将scriptProcessor属性值修改为“Full
Path|Arguments”：

![6.png](https://image.3001.net/images/20200202/1580639853_5e36a66d33ffa.png!small)

这里，我将scriptProcessor属性设置为了：

    
    
    “c:\python3.4\python.exe|c:\python3.4\lib\site-packages\wfastcgi.py”

2、PYTHONPATH，该参数需要指向我们的站点目录，即“C:\inetpub\wwwroot\bits”。

然后，修改初始安装常量，设置预共享密钥的密码：

    
    
    Program.cs -> Password变量
    
    myapp.py -> Password变量
    
    lawlbin.py -> password变量

选择Flask应用程序需要监听的C#代理URL：

    
    
    Program.cs -> Url变量

在myapp.py中，设置AuthPath、ReadPath和Payloads的值，分别指向Web目录中对应的文件夹。

在lawlbin.py (lolbins目录)中设置baseReadPath和baseWritePath的值，分别指向Web目录中对应的文件夹。

在inject.py (lolbins folder)中设置__payloads的值，这个值需要跟myapp.py中的Payloads值相同。

编译代理，并在受感染的主机中运行。编译完成后，将会生成一个exe文件和一个外部依赖文件(Newtonsoft.Json.dll)。你也可以使用ILMerge来生成一个单独的exe文件，这里请将项目以Windows
Application进行编译：

![7.png](https://image.3001.net/images/20200202/1580639868_5e36a67ca89cd.png!small)

## 工具使用

广大用户可以直接在C&C服务器中的命令行工具中输入下列命令，并在受感染的主机中运行C#代理，即可开始使用LOLBITS了：

    
    
    python lawlbin.py

### 项目地址

LOLBITS：【[ _GitHub传送门_](https://github.com/Kudaes/LOLBITS)】

 ***参考来源：[
_Kudaes_](https://github.com/Kudaes/LOLBITS)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

