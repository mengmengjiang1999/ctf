## 一、背景

最近在GitHub看到一个新的开源安全工具，可以把工具都集成到一个平台里，觉得挺有意思，但是平台现有的工具不是太全，我想把自己的工具也集成进去，所以研究了一番

>
> 蜻蜓安全工作台是一个安全工具集成平台，集成市面上主流的安全工具，并按照工作场景进行编排，目前主要预制了四个场景：信息收集、黑盒扫描、POC批量验证、代码审计；  
>
> 最大特点就是集成的工具多、种类全，你可以将你想要的工具编排成任意一个场景，快速打造属于自己的安全工作台~`https://github.com/StarCrossPortal/QingTing`

在这篇文章中主要讲解将自己喜欢的工具集成到平台里面来，下面说下工具如何封装。

## 二、学习工具使用

在将工具集成到平台中之前，你需要了解工具的下载方式、依赖安装、使用方法；只有满足这几个条件你才有可能集成到平台中去。

我以弱口令检测工具WebCrack为例,讲解如何在蜻蜓安全工作台中提交工具。

### 2.1 工具下载

首先需要你从工具的官方网站，或者GitHub将工具下载下来

    
    
    git clone https://github.com/yzddmr6/WebCrack
    

返回内容如下

    
    
    Cloning into 'WebCrack'...
    remote: Enumerating objects: 104, done.
    remote: Counting objects: 100% (31/31), done.
    remote: Compressing objects: 100% (25/25), done.
    remote: Total 104 (delta 9), reused 17 (delta 3), pack-reused 73
    Receiving objects: 100% (104/104), 138.12 KiB | 867.00 KiB/s, done.
    Resolving deltas: 100% (30/30), done.
    

### 2.2 安装工具的依赖

接着对照工具的文档，我安装依赖，安装命令如下所示

    
    
    cd WebCrack && pip3 install -r requirements.txt
    

返回结果

    
    
    Defaulting to user installation because normal site-packages is not writeable
    Requirement already satisfied: bs4 in /Users/tangqingsong/Library/Python/3.8/lib/python/site-packages (from -r requirements.txt (line 1)) (0.0.1)
    Requirement already satisfied: lxml in /Users/tangqingsong/Library/Python/3.8/lib/python/site-packages (from -r requirements.txt (line 2)) (4.8.0)
    Requirement already satisfied: requests in /Users/tangqingsong/Library/Python/3.8/lib/python/site-packages (from -r requirements.txt (line 3)) (2.27.1)
    Requirement already satisfied: beautifulsoup4 in /Users/tangqingsong/Library/Python/3.8/lib/python/site-packages (from bs4->-r requirements.txt (line 1)) (4.11.1)
    Requirement already satisfied: charset-normalizer~=2.0.0 in /Users/tangqingsong/Library/Python/3.8/lib/python/site-packages (from requests->-r requirements.txt (line 3)) (2.0.12)
    Requirement already satisfied: urllib3<1.27,>=1.21.1 in /Users/tangqingsong/Library/Python/3.8/lib/python/site-packages (from requests->-r requirements.txt (line 3)) (1.26.9)
    Requirement already satisfied: certifi>=2017.4.17 in /Users/tangqingsong/Library/Python/3.8/lib/python/site-packages (from requests->-r requirements.txt (line 3)) (2021.10.8)
    Requirement already satisfied: idna<4,>=2.5 in /Users/tangqingsong/Library/Python/3.8/lib/python/site-packages (from requests->-r requirements.txt (line 3)) (3.3)
    Requirement already satisfied: soupsieve>1.2 in /Users/tangqingsong/Library/Python/3.8/lib/python/site-packages (from beautifulsoup4->bs4->-r requirements.txt (line 1)) (2.3.2.post1)
    

### 2.3 学习使用方法

现在学习工具使用方法，为后续接入做准备

    
    
    ➜  WebCrack git:(master) python3 webcrack.py 
    
    +---------------------------------------------------+
    | __          __  _      _____                _     |
    | \ \        / / | |    / ____|              | |    |
    |  \ \  /\  / /__| |__ | |     _ __ __ _  ___| | __ |
    |   \ \/  \/ / _ \ '_ \| |    | '__/ _' |/ __| |/ / |
    |    \  /\  /  __/ |_) | |____| | | (_| | (__|   <  |
    |     \/  \/ \___|_.__/ \_____|_|  \__,_|\___|_|\_\ |
    |                                                   |
    |                 code by @yzddmr6                  |
    |                  version: 2.2                     |
    +---------------------------------------------------+
    
    File or Url:
    

### 2.4 改造工具

在上没使用的体验中，发现还需要进行交互，这非常不方便，我想执行一条命令就可以让他工作，所以需要改动代码

改动代码之前，需要分析主入口文件,其中有一个变量名`url_file_name`

    
    
    url_file_name = input('File or Url:\n')
    
        if '://' in url_file_name:
            CrackTask().run(1, url_file_name)
        else:
            url_list = []
            if os.path.exists(url_file_name):
    

我把他的修改成这个从参数中获取即可

    
    
    url_file_name = sys.argv[1]
    

![](https://image.3001.net/images/20220510/1652150721_6279d1c154d6cc18320d9.png!small)

接下来我用permeate搭建一个靶场，然后将登录地址放进去

    
    
    python3 webcrack.py http://*.*.*/home/index.php?m=user&a=login
    

返回结果如下，可以看到接收参数成功了，并且已经运行成功。

    
    
    ➜  WebCrack git:(master) ✗ python3 webcrack.py http://xx.xx.xx/home/index.php\?m\=user\&a\=login
    2022-05-09 19:36:53  id: 1 [*] Start: http://xx.xx.xx/home/index.php?m=user&a=login
    2022-05-09 19:36:53  id: 1 [*] http://xx.xx.xx/home/index.php?m=user&a=login 进度: (1/27) checking: admin admin
    .....中间过程删减....
    2022-05-09 19:36:53  id: 1 [*] http://xx.xx.xx/home/index.php?m=user&a=login 进度: (2/27) checking: admin 123456
    2022-05-09 19:36:56  id: 1 [*] http://xx.xx.xx/home/index.php?m=user&a=login 启动万能密码爆破模块
    2022-05-09 19:36:56  id: 1 [*] http://xx.xx.xx/home/index.php?m=user&a=login 进度: (1/25) checking: admin' or 'a'='a admin' or 'a'='a
    2022-05-09 19:36:56  id: 1 [*] Rechecking... http://xx.xx.xx/home/index.php?m=user&a=login admin' or 'a'='a admin' or 'a'='a
    2022-05-09 19:36:56  id: 1 [+] Success: http://xx.xx.xx/home/index.php?m=user&a=login  admin' or 'a'='a/admin' or 'a'='a
    ➜  WebCrack git:(master) ✗ 
    

从反馈的结果来看,工具使用了万能密码暴力破解成功了。

## 三、学习镜像制作方法

现在我们已经知道工具如何接入,只需要让程序执行他就行了，所以我们需要学习蜻蜓安全工作台插件的一些基本规则，学习规则很简单。

我们只需要将蜻蜓已经写好的插件下载下来，看看之前的插件怎么写的就可以了。

### 3.1 案例分析

如下图是蜻蜓安全工作台已经编写好的插件，  
![](https://image.3001.net/images/20220510/1652150722_6279d1c21a2f6deec10e6.png!small)

我们随意挑选一个案例，以长亭的`xray`工具接入为例,

![](https://image.3001.net/images/20220510/1652150723_6279d1c3d44332cf59020.png!small)

可以看到工具一共有三个目录：`code`、`tools`、`Dockerfile`

我们先分析一下 dockerfile 文件

    
    
    FROM daxia/qingting:base
    
    COPY ./code /root/code
    COPY ./tools /data/tools
    
    CMD ["php","/root/code/index.php"]
    

从Dockerfile文件中可以看到其实镜像制作，只需要把两个目录复制到镜像就可以了，然后让他启动执行一个主入口文件；

我们接下来再继续看主入口文件所在的`code`目录,打开文件查看，`index.php`内容如下

![](https://image.3001.net/images/20220510/1652150724_6279d1c43af5e67bf3e09.png!small)

从这个图中可以看到,插件的流程其实是读取要扫描的目标,然后将目标丢给工具去扫描,然后将扫描的结果存储到数据库

## 四、制作工具镜像

现在我们开始尝试自己写插件，首先将xray的整个文件夹复制一份，新的文件夹名字叫做`webcrack`，然后把tools里面的内容删除

接着将最开始下载的webcrack代码复制过来，如下图所示

![](https://image.3001.net/images/20220510/1652150724_6279d1c4a5a666c882720.png!small)

接下来我们再分析`index.php`的具体逻辑,这里剧透一下，我们只看index.php就行，其他地方不用看了，用之前的配置就行了。

然后我们开始替换文件内容，直接将文件内容的xray改成webcrack,如下图所示  
![](https://image.3001.net/images/20220510/1652150725_6279d1c559941b53690b3.png!small)

再剧透一个地方，我们只需要改这两个函数就行了。

![](https://image.3001.net/images/20220510/1652150725_6279d1c586396ea39691a.png!small)

### 4.1 调用工具

首先我们需要关注执行工具的函数，这里面我们只需要关注CMD 这个命令

![](https://image.3001.net/images/20220510/1652150725_6279d1c5ca5c22690c9d0.png!small)

把这个命令改成webcrack的调用命令就行了

![](https://image.3001.net/images/20220510/1652150726_6279d1c616c7f799b63c7.png!small)

### 4.2 录入数据

然后再看下一个导入数据的函数`writeData`

![](https://image.3001.net/images/20220510/1652150726_6279d1c642214c87c476a.png!small)

在这个方法里可以看到只做了三件事,首先读取工具的结果，然后将结果的JSON字符串转换为数组,之后插入数据库即可。

* * *

作者：汤青松

日期：2022年05月09日

