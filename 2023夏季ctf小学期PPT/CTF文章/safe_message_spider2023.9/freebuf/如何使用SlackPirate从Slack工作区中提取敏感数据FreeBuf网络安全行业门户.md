![](https://image.3001.net/images/20210428/1619592362_608904aaa21a7e5e4f949.jpg!small)

## SlackPirate

SlackPirate是一款Slack信息枚举和提取工具，可以帮助广大研究人员从Slack工作区中提取敏感信息。该工具基于Python开发，并使用了原生Slack
API来从给定访问令牌的Slack工作区中提取“有意思”的信息。

截止至2018年5月，Slack拥有超过800万的客户，而且这个数字还在迅速上升。在不同的工作场景下，Slack等工具会在不同的信息安全治理/政策雷达下运行，这最终会导致不稳定的情况，即敏感和机密信息最终会出现在不该出现的地方。

## 工具用途

此工具有两个用途：

>
> 红队研究人员可以利用低权限Slack账号从组织的工作区中提取和提取敏感信息，文件，凭证等。这可能使攻击者以其他系统为入口点获取目标组织系统/应用程序更深入的了解和内部工作机制。
>
>
> 蓝队研究人员可以使用它来识别和检测工作区中的敏感信息，这些信息在第一时间可能不应该存在于工作区中。蓝队研究人员可以通过演示工具的输出以及（内部和外部）攻击者可能使用和滥用的“实体”类型，并将此信息用于内部员工安全意识培训。

该工具允许广大研究人员方便地收集敏感信息，以便脱机查看。

## 信息收集

该工具使用了原生的Slack API来提取敏感信息或搜索下列信息：

> 查询允许注册的工作区域名；
>
> S3 bucket链接；
>
> 密码；
>
> AWS访问/密钥；
>
> 私钥；
>
> 跨信道消息；
>
> 引用的链接和地址，可以访问更多敏感信息；
>
> 其他可能包含敏感信息的文件，例如.key、.sh、文档中嵌入的“密码”或“密钥”等；

## Slack Cookie

Slack web应用程序使用了许多cookie，其中有一个特殊的cookie，即d
cookie。这个cookie对于目标用户可以访问的所有工作区来说都是相同的，这也就意味着，盗取d
cookie之后，将允许攻击者访问目标用户登录的所有工作区。

## 项目构建

### Linux + virtualenv

    
    
    git clone https://github.com/emtunc/SlackPirate
    
    pip install virtualenv
    
    virtualenv SlackPirate
    
    source SlackPirate/bin/activate
    
    pip install -r requirements.txt
    
    ./SlackPirate.py --help

### Linux

    
    
    git clone https://github.com/emtunc/SlackPirate
    
    chmod +x SlackPirate.py
    
    pip install -r requirements.txt
    
    ./SlackPirate.py --help

### Windows + virtualenv

    
    
    git clone https://github.com/emtunc/SlackPirate
    
    pip install virtualenv
    
    virtualenv SlackPirate
    
    SlackPirate\Scripts\activate.bat
    
    pip install -r requirements.txt
    
    python SlackPirate.py --help

### Windows

    
    
    git clone https://github.com/emtunc/SlackPirate
    
    pip install -r requirements.txt
    
    python SlackPirate.py --help

## 工具使用

显示帮助菜单，其中包含所有的扫描模块：

    
    
    python3 SlackPirate.py --help

交互模式可以允许我们提供自定义令牌和cookie，并选择需要执行的扫描任务：

    
    
    python3 SlackPirate.py --interactive

下列命令可以寻找能够使用cookie访问的关联工作区、连接至返回的任意工作区、寻找返回工作区的API令牌：

    
    
    python3 SlackPirate.py --cookie <cookie>

下列命令可以寻找各种令牌、密码、私钥和引用链接：

    
    
    python3 SlackPirate.py --token <token>

下列命令仅执行S3扫描：

    
    
    python3 SlackPirate.py --token <token> --s3-scan

下列命令将执行除了S3扫描之外的其他所有扫描任务：

    
    
    python3 SlackPirate.py --token <token> --no-s3-scan

开启Verbose模式并将输出存储至.CSV文件中：

    
    
    python3 SlackPirate.py --token <token> --verbose

## 工具运行截图

![](https://image.3001.net/images/20210428/1619592434_608904f2d4a8fc9194395.png!small)

![](https://image.3001.net/images/20210428/1619592442_608904fa07c34df7ceb04.png!small)

## 项目地址

 **SlackPirate：** https://github.com/emtunc/SlackPirate

