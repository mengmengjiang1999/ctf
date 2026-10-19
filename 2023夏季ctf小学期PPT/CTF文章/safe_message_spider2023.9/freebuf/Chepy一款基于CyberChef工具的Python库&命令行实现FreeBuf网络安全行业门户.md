**Chepy是一款基于CyberChef工具的Python库 &命令行实现，它是一个Python库/命令行，实现了跟CyberChef工具相同的功能。**

![](https://image.3001.net/images/20200403/1585919765_5e873715cd6d9.png!small)

Chepy是一个带有完整命令行接口的Python库，它完整复制了[CyberChef](https://gchq.github.io/CyberChef/)的大部分功能。开发人员在Chepy上付出了非常多的努力，并使它成功变成了基于CyberChef的Python实现，而且其中所有的代码均采用纯Python开发。Chepy跟CyberChef相比，有很多核心优势，而且Chepy还将CyberChef中对栈的概念以不同模块的形式仍然保留在了Chepy中。

当然了，Chepy还没有达到完美的程度，因此还需要社区中的各位开发人员贡献自己的力量。

##  工具安装

Chepy可以通过下列几个方式来进行安装。

###  Pypi安装

    
    
    pip3 install chepy
    
        # optionally with extra requirements
    
        pip3 install chepy[extras]

###  Git安装

    
    
    git clone --recursive <https://github.com/securisec/chepy.git>
    
        cd chepy
    
        pip3 install -e .
    
        # I use -e here so that if I update later with git pull, I dont have it install it again (unless dependencies have changed)

##  Docker安装

    
    
    docker run --rm -ti -v $PWD:/data securisec/chepy "some string" [somefile, "another string"]

###  独立代码

当然了，我们也可以将Chepy以独立代码的形式进行构建，这里需要涉及到将所有的依赖组件封装整合成一体。

    
    
    git clone <https://github.com/securisec/chepy.git>
    
        cd chepy
    
        pip install .
    
        pip install pyinstaller
    
        pyinstaller cli.py --name chepy --onefile

构建完成的代码将存储在dist/目录下。

##  插件系统-【[参考文档](https://chepy-plugins.readthedocs.io/en/latest/)】

> .. toctree::
>
> :maxdepth: 3
>
> :caption: Contents:
>
> usage.md
>
> examples.md
>
> cli.rst
>
> chepy.md
>
> core.md
>
> modules.rst
>
> extras.rst
>
> plugins.md
>
> pullrequest.md
>
> config.md
>
> faq.md
>
> Indices and tables
>
> ==================
>
> * :ref:`genindex`
>
> * :ref:`modindex`
>
> * :ref:`search`

项目代码库中托管了大量Chepy插件，我们也可以根据自己的需要来用自定义插件扩展Chepy的功能。所有的Chepy插件必须继承ChepyCore类，如需使用插件库，请运行下列命令：

    
    
    git clone https://github.com/securisec/chepy_plugins.git

然后编辑Chepy配置文件，将pluginpath设置为chepy_plugin目录。配置文件位于$User/.chepy/chepy.conf路径下。

###  下面给出的是配置文件样本：

    
    
    [Plugin]
    
        pluginpath = /home/test/chepy_plugins
    
        [Cli]
    
        history_path = /home/test/.chepy/chepy_history
    
        prompt_char = >
    
        prompt_colors = #00ffff #ff0000 #ffd700
    
        show_rprompt = false
    
        prompt_rprompt = #00ff48
    
        prompt_bottom_toolbar = #000000
    
        prompt_toolbar_version = #00ff48
    
        prompt_toolbar_states = #60cdd5
    
        prompt_toolbar_buffers = #ff00ff
    
        prompt_toolbar_type = #ffd700
    
        prompt_toolbar_errors = #ff0000

##  Chepy vs Cyberchef

Chepy所实现的栈机制比CyberChef要简单，并且是以模块化的形式实现的。比如说，CyberChef中的栈概念如下：

![](https://image.3001.net/images/20200403/1585919849_5e8737692a755.png!small)

但在Chepy中的形式如下：

    
    
    from chepy import Chepy
    
        file_path = "/tmp/demo/encoding"
    
        print(
    
            Chepy(file_path)
    
            .load_file()
    
            .reverse()
    
            .rot_13()
    
            .base64_decode()
    
            .base32_decode()
    
            .hexdump_to_str()
    
            .o
    
        )

##  优势

> 1、Chepy以纯Python实现，并且支持各种Python API；
>
> 2、Chepy提供了命令行接口；
>
> 3、Chepy命令行接口支持完整的自动化补全；
>
> 4、支持对PE、ELF和其他特殊文件格式进行解析；
>
> 5、可通过插件系统实现功能扩展；
>
> 6、可利用各种Python库实现不同功能；
>
> 7、Chepy可与CyberChef Web应用程序进行交互；
>
> 8、Chepy Python库的速度比CyberChef Node库要快很多；
>
> 9、支持HTTP/HTTPS请求；

##  劣势

> 1、Chepy不是一个Web应用程序；
>
> 2、Chepy没有100%实现CyberChef的每一个功能；
>
> 3、Chepy目前还不提供magic方法；

##  工具使用样例

![](https://image.3001.net/images/20200403/1585919876_5e87378487d33.gif!small)

##  项目地址

> Chepy：【[GitHub传送门](https://github.com/securisec/chepy)】
>
> 完整使用：【[详细文档](http://chepy.readthedocs.io/en/latest/)】

 ***
参考来源：[securisec](https://github.com/securisec/chepy)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

  

