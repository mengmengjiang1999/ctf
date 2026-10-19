最近在测试 Android APP 的时候，发现目标程序做了HTTPS证书校验，而因为 APK 混淆过，因此`xposed`插件（比如`SSL
Unpinning`或者`Just Trust Me`）就失效了，因为要hook的函数名被修改了。因此想到用`Frida`来进行动态查看和Hook。  

​

> Brida是一款Burp Suite扩展，作为一座桥梁连接着Burp Suite以及Frida，以帮助用户修改应用程序与后端服务器之间的通信数据为己任。

​

关于`Brida`，Freebuf上已有介绍，不再赘述，感兴趣的可以看[这里](https://www.freebuf.com/sectool/143360.html)。但是，官方的`Brida`发布于2018年，原生支持的是`python
2.7`，或者说只在`py27`环境下测试过，而`Frida`版本迭代之快，在如今的环境下已经无法再适应`py2.7`的环境了。

尝试在`python3`环境下安装的时候，发现并不能使用，因此才有了本文折腾的全过程，看了无数遍官方文档，慢慢领会了其中的精髓，现在记录下来，与大家分享。

可以说安装的过程中每一步都是坑，接下来慢慢分享~

## 环境准备

第一个坑：`Python`环境。

在安装`Frida`的时候，对于`Python`的版本还是有一定要求的。

### 确定版本

 **Step 1: 确定`Frida`版本**

这一步需要你定下来要用的`Frida`是哪个版本，因为这与整个环境都有着巨大的关系。访问Github的[下载页面](https://github.com/frida/frida/releases)，下载`frida-server-xx.xx.xx-android-xx.tar.gz`并在你的机器上（模拟器或者手机均可）运行。

 **Step2: 确定支持的`Python`版本**

不同版本的`Frida`支持的Python版本是不一样的。把能用的`Frida`版本记下来，比如`12.8.17`，此时访问`Pypi`的Frida下载页，如果你的`pip`用了国内源，就去访问该源的页面，比如我用的清华大学的源，那就访问<https://pypi.tuna.tsinghua.edu.cn/simple/frida/>。

![image-20200331115856690.png](https://image.3001.net/images/20200331/1585644901_5e830565360d6.png!small)

在这个列表中找到相应的版本`12.8.17`，并查看文件名。比如：

![image-20200331120051557.png](https://image.3001.net/images/20200331/1585644917_5e83057523bc7.png!small)

比如你是在Windows 64位平台使用，就下载`frida-12.8.17-py3.7-win-amd64.egg`，Linux平台就下载相应的egg即可。

### 安装Python

根据上面查看到的`egg`文件前标示的`Python`版本，选择安装。

####  **Linux系统（基于`pyenv`）**

 **安装pyenv。**
如果选择在Linux系统下使用`Brida`，比如在`Kali`里使用，推荐使用`pyenv`进行python环境的版本管理，非常的方便，安装方法参见[pyenv的官方Github](https://github.com/pyenv/pyenv#basic-github-checkout)。

 **安装Python。** 安装Python的时候会踩几个坑：

  1. 依赖库

`pyenv`在安装Python时会从其源码进行编译，因此需要有依赖库的支持，否则即使不报错的安装完，在运行的时候也会有问题。以`Kali`为例（`Ubuntu`、`Debian`命令应该是一样的，其他的Linux系统原理类似），需要安装的库可能有：

    
        libbz2-dev  
    librealine-dev  
    zlib1g-dev  
    libffi-dev  
    libsqlite3-dev  
    liblzma-dev

以上库是我在安装的过程中报错信息里提示的，比如`ModuleNotFoundError: No module named '_sqlite3'`

  2. 下载安装

在使用命令`pyenv install 3.6.5`来安装`Python 3.6.5`时，会有如下显示：

    
        pentest@DESKTOP-2AE07FJ:~$ pyenv install 3.6.5  
    Downloading Python-3.6.5.tar.xz...  
    -> https://www.python.org/ftp/python/3.6.5/Python-3.6.5.tar.xz

pyenv会去尝试下载`tar.gz`格式的源码来进行编译，一般情况下国内网络会非常缓慢，让pyenv自己去下载会下到天荒地老，而且还有可能等了半小时之后给你弹一个error，非常讨厌。

这时候可以拿着这个链接手动下载（Linux上可以安装`aria2`，使用方法百度很多）。

下载完毕后，在`~/.pyenv/`路径下新建文件夹`cache`，并把下载好的`tar.xz`文件放进去，再运行`pyenv install
3.6.5`，就会跳过下载直接开始编译安装。

安装完毕后，使用`pyenv versions`查看，如果能看到列表，说明安装成功。使用命令`pyenv global
3.6.5`即可全局切换到`Python 3.6.5`环境下。

 **安装pyenv-virtualenv。**
此时就可以安装`Frida`了，但是推荐安装`pyenv`的插件`virtualenv`，避免因为依赖组件版本冲突导致工具不能安装的问题。`virtualenv`的安装参见[官方Github](https://github.com/pyenv/pyenv-virtualenv#installation)。

安装完毕后，使用命令`pyenv virtualenv 3.6.5 frida`来创建一个基于`Python
3.6.5`版本的、名为`frida`的虚拟环境，并使用`pyenv activate frida`来启用它。

启用成功后，命令行开头会显示一个括号：

![image-20200331142403386.png](https://image.3001.net/images/20200331/1585645059_5e83060352812.png!small)

####  **Windows环境**

Windows环境下，因为`pyenv-win`支持不好，因此直接安装即可：直接去官网下载对应版本的`.msi`的安装包，双击安装。要注意的是，在安装时
**不要勾选** “Add Python 3.x to PATH”的选项，以免对当前系统中的环境造成影响。

![image-20200331143420055.png](https://image.3001.net/images/20200331/1585645067_5e83060bc87b4.png!small)

由于不加入PATH，所以相对来说环境是独立的，也算是比较方便好用了。

记住Python的安装路径，后面需要用到。

### 安装Frida、Frida-tools和Pyro4

Python环境安装完毕，可以开始安装Frida了。此时需要准备阶段下载的`frida-12.8.17-py3.7-xxx-xxx.egg`文件。

理论上来说可以使用pip命令`pip install frida==12.8.17`来进行安装，但是可能会卡在`Running setup.py
install for frida ... -`不动，因此需要`.egg`文件直接安装。

`Pyro4`是`Brida`与`Frida`通信的中间件，需要一并安装。

####  **Linux环境**

在使用virtualenv切换环境后，直接输入`easy_install
~/Downloads/frida-12.8.17-py3.6-linux-x86_64.egg`即可。

使用命令`pip install frida-tools`安装`frida-tools`。

使用命令`pip install pyro4`安装`Pyro4`。

![image-20200331150103543.png](https://image.3001.net/images/20200331/1585645073_5e83061148f04.png!small)

####  **Windows环境**

Windows环境下需要进入安装步骤中的安装路径，如`C:\Users\[用户名]\AppData\Local\Programs\Python\Python37`，在此处打开命令行，输入命令：

    
    
    C:\Users\xx\AppData\Local\Programs\Python\Python37>.\Scripts\easy_install.exe C:\Users\xx\Downloads\frida-12.8.17-py3.7-win-amd64.egg

安装Frida。安装成功后，输入`.\Scripts\pip.exe install frida-tools`来安装Frida-tools。

输入`.\Scripts\pip.exe install pyro4`安装`Pyro4`。

至此，`Frida`和`Frida-tools`均安装完毕。

### 配置Brida

`Brida`需要`Burpsuite`支持，Community版本和Pro均可。安装方法很简单，可以直接在`BApp
Store`中安装，也可以进入[Brida的Releases页面](https://github.com/federicodotta/Brida/releases)下载。这里使用Burpsuite中安装的方式。

####  **适配Python3**

 **大坑预警！大坑预警！大坑预警！** 重要的事情说三遍！

由于`Brida`编写的时候支持`Python2.7`，因此在`3.6` /
`3.7`的环境下无法直接运行。2019年5月就有人在issues中提出[这个问题](https://github.com/federicodotta/Brida/issues/39)，作者在2020年3月才进行了回答，并给出了一个解决方案：修改插件中的`.py`文件，方法如下：

  1. 找到插件`Brida_xxx.jar`文件。插件的根目录：

    * Windows：`C:\Users\xx\AppData\Roaming\BurpSuite`

    * Linux：`~/.BurpSuite`

后面的路径是一致的：`\bapps\2c0def96c5d44e159151b236de766892\build\libs`

  2. 用解压工具打开`brida-all.jar`，将`/res`文件夹下的两个文件（`bridaServicePyro.py`、`scriptBridaDefault.js`）解压出来备用

  3. 编辑`bridaServicePyro.py`，将内容替换成以下代码：
    
        # -*- coding: utf-8 -*-  
    import frida  
    import codecs  
    import Pyro4  
    import sys  
    ​  
    #reload(sys)     
    #sys.setdefaultencoding('utf-8')  
    ​  
    class Unbuffered(object):  
       def __init__(self, stream):  
           self.stream = stream  
       def write(self, data):  
           self.stream.write(data)  
           self.stream.flush()  
       def writelines(self, datas):  
           self.stream.writelines(datas)  
           self.stream.flush()  
       def __getattr__(self, attr):  
           return getattr(self.stream, attr)  
    ​  
    @Pyro4.expose  
    class BridaServicePyro:  
        def __init__(self, daemon):  
            self.daemon = daemon  
        def spawn_application(self,application_id,frida_script,remote):  
    ​  
            self.application_id = application_id  
            self.frida_script = frida_script  
    ​  
            if remote == True:  
                self.device = frida.get_remote_device()  
            else:  
                self.device = frida.get_usb_device()  
    ​  
            self.pid = self.device.spawn([self.application_id])  
    ​  
            self.session = self.device.attach(self.pid)  
    ​  
            with codecs.open(self.frida_script, 'r', 'utf-8') as f:  
                source = f.read()  
    ​  
            self.script = self.session.create_script(source)  
            self.script.load()  
    ​  
            return  
    ​  
        def resume_application(self):  
    ​  
            self.device.resume(self.pid)  
    ​  
            return  
    ​  
        def reload_script(self):  
    ​  
            with codecs.open(self.frida_script, 'r', 'utf-8') as f:  
                source = f.read()  
    ​  
            self.script = self.session.create_script(source)  
            self.script.load()  
    ​  
            return  
    ​  
        def disconnect_application(self):  
    ​  
            self.device.kill(self.pid)  
            return  
    ​  
        def callexportfunction(self, methodName, args):  
            method_to_call = getattr(self.script.exports, methodName)  
    ​  
            # Take the Java list passed as argument and create a new variable list of argument  
            # (necessary for bridge Python - Java, I think)  
            s = []  
            for i in args:  
                s.append(i)  
    ​  
            return_value = method_to_call(*s)  
            return return_value  
    ​  
        @Pyro4.oneway  
        def shutdown(self):  
            print('shutting down...')  
            self.daemon.shutdown()  
    ​  
    # Disable python buffering (cause issues when communicating with Java...)  
    sys.stdout = Unbuffered(sys.stdout)  
    ​  
    host = sys.argv[1]  
    port = int(sys.argv[2])  
    daemon = Pyro4.Daemon(host=host,port=port)  
    ​  
    #daemon = Pyro4.Daemon(host='127.0.0.1',port=9999)  
    bs = BridaServicePyro(daemon)  
    uri = daemon.register(bs,objectId='BridaServicePyro')  
    ​  
    print("Ready.")  
    daemon.requestLoop()

该代码出自Brida原作者，参见：<https://github.com/federicodotta/Brida/issues/39#issuecomment-596064419>

  4. 将`bridaServicePyro.py`重新放回`brida_all.jar`的`/res`文件夹下（覆盖原文件）。

  5. 将`scriptBridaDefault.js`复制出来，并记住路径。

至此，`Brida`的`Python3`适配部分完成。

  

####  **Brida配置**

打开`Burpsuite`，切换到`Brida`选项卡，页面功能和用法可以参考[[原创]Brida操作指南](https://bbs.pediy.com/thread-248977.htm)中的介绍。

“Python binary path”的值填写“环境准备”章节中安装的Python的位置。

Linux系统中，该路径为`~/.pyenv/versions/xxx/bin/python`

Windows系统中，路径为安装的路径，如`C:\Users\xx\AppData\Local\Programs\Python\Python`

此时，点击“Start Server”按钮，会显示绿色的“Server running”，表示`Pyro4`运行成功，可以进行操作了。

 **大坑预警！大坑预警！大坑预警！** 重要的事情 **再说三遍** ！

对于“Frida JS file path”这个选项，各种教程里都没有提及它的含义，如果不管用它的 **默认值** ，或者指向 **自定义脚本**
，都无法“Spawn application”。

![image-20200331160408482.png](https://image.3001.net/images/20200331/1585645098_5e83062aa9aa2.png!small)

如果出现“getplatform”的错误，就说明是这个 JS 文件指定的有误。

在它的[官方说明页面](https://techblog.mediaservice.net/2018/04/brida-a-step-by-step-user-guide/)中，有如下说明：

> “Frida JS file path” is the path of the Frida instrumentation JavaScript
> file, containing all Frida and Brida hooks and exports. To properly use
> Brida you have to insert the path of the JS file supplied with the Brida
> release (named “scriptBrida.js”) because this file contains Frida functions
> used by Brida itself. You can add your own Frida hooks and exports directly
> in this file.

简单翻译一下就是，这个`Frida JS file path`需要指向一个包含Frida和Brida定义的Hook和Export的 JS
文件。这个文件保存在`Brida-all.jar`中，就是上面步骤中保存的`scriptBridaDefault.js`文件。

这里将“Frida JS file path”的地址指向之前保存的`scriptBridaDefault.js`文件的路径。

####  **配置Android设备并Spawn application**

最后一步，在Android设备上启动`frida-server`，在`Brida`中填好包名，“Spawn application”成功！

![image-20200331161726836.png](https://image.3001.net/images/20200331/1585645122_5e830642ca3c9.png!small)

点击`Analyze binary`标签页，选中`Binary`，点击`Load tree`按钮，列出加载的`.so`文件，成功！

![image-20200331164444141.png](https://image.3001.net/images/20200331/1585645135_5e83064fb4216.png!small)

## 总结

`Frida`版本更新很快，因此虽然一两年前的工具，现在用起来也有诸多麻烦。在Linux平台上使用`pyenv` \+
`virtualenv`进行环境的管理配置会使配置简单很多。

另外，根据`Brida`作者的说法，在2020年6月会出一个支持`Python3`的官方版本，可以到时候关注一下Github。

整个过程总结起来就是：

  1. 安装`Python`、`Frida`、`Pyro4`；

  2. 修改`Brida-all.jar`，更改`bridaServicePyro.py`文件；

  3. 提取`scriptBridaDefault.js`，修改`Frida JS file path`指向到提取的文件；

####  **参考文档**

[1] Brida. <https://github.com/federicodotta/Brida>

[2] Frida. <https://github.com/frida/frida>

[3] [原创]Brida操作指南. <https://bbs.pediy.com/thread-248977.htm>

[4] pyenv. <https://github.com/pyenv/pyenv>

[5] virtualenv. <https://github.com/pyenv/pyenv-virtualenv>

[6] Brida – A step-by-step user guide.
<https://techblog.mediaservice.net/2018/04/brida-a-step-by-step-user-guide/>

[7] 《FRIDA操作手册》by @hluwa @r0ysue. <https://github.com/hookmaster/frida-all-in-one>

