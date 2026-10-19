![](https://image.3001.net/images/20201105/1604564623_5fa3b68fe1b5e2c8b4f05.jpg!small)  

## Safety

Safety是一款功能强大的漏洞检测工具，可以帮助广大研究人员检测设备上已安装依赖组件中存在的已知安全漏洞。默认配置下，Safety使用的是开放Python漏洞数据库-[
_Safety DB_](https://github.com/pyupio/safety-db)，但是大家也可以使用--key选项来更新工具，并使用pyup.io的[ _Safety
API_](https://github.com/pyupio/safety/blob/master/docs/api_key.md)。

## 工具安装

我们可以使用pip来安装Safety，不过请大家记住，当前版本的Safety仅支持Python 3.5及其更高版本的环境：

    
    
    pip install safety

## 工具使用

运行下列命令，即可判断当前以选择的安装了依赖组件的虚拟环境，并检测已知的安全漏洞：

    
    
    safety check

运行之后，我们将看到如下图所示的报告界面：

![](https://image.3001.net/images/20201105/1604564648_5fa3b6a87f4b8702e4b67.png!small)

现在，我们来安装一些存在安全问题的依赖组件：

    
    
    pip install insecure-package

接下来，再次运行漏洞检测命令：

    
    
    safety check

这一次的扫描结果如下：

![](https://image.3001.net/images/20201105/1604564662_5fa3b6b61b0e840fde6d3.png!small)

## 工具使用样例

### 读取工具所需文件

跟pip一样，Safety能够读取本地requirement文件：

    
    
    safety check -r requirements.txt

### 从Stdin读取

Safety还能够使用--stdin参数来从Stdin读取输入数据。如需检测一个本地依赖文件，可运行下列命令：

    
    
    cat requirements.txt | safety check --stdin

或者，从pip freeze的输出读取输入：

    
    
    pip freeze | safety check --stdin

或者，检测一个单一依赖包：

    
    
    echo "insecure-package==0.1" | safety check --stdin

## 在Docker中使用Safety

Safety还能够以Docker容器的形式运行：

    
    
    echo "insecure-package==0.1" | docker run -i --rm pyupio/safety safety check --stdin
    
    cat requirements.txt | docker run -i --rm pyupio/safety safety check --stdin

## 使用Safety源码

Safety的源代码还提供了某些额外的[ _安全功能_](https://pyup.io/posts/patched-vulnerability/)，安装完成之后，我们就能够使用常规命令行版本的Safety了。点击【[
_这里_](https://github.com/pyupio/safety/releases)】即可获取Safety源代码。

## 通过CI服务使用Safety

Safety还能够配合CI管道一起使用，如果扫描到了一个漏洞的话，它会返回一个非零退出状态。

### Travis：

    
    
    install:
    
      - pip install safety
    
     
    
    script:
    
      - safety check

### Gitlab CI：

    
    
    safety:
    
      script:
    
        - pip install safety
    
    - safety check

### Tox：

    
    
    [tox]
    
    envlist = py37
    
     
    
    [testenv]
    
    deps =
    
        safety
    
        pytest
    
    commands =
    
        safety check
    
    Pytest

## 深度GitHub整合

如果你想要将Safety跟你自己的GitHub库进行深度整合的话，可以直接使用[
_pyup.io_](https://pyup.io/)中的Safety服务，即[ _Safety
CI_](https://pyup.io/safety/ci/)。Safety CI能够检测GitHub库中依赖组件的commit和pull
request，并寻找已知的安全漏洞，并将检测结果和状态显示在GitHub中。

![](https://image.3001.net/images/20201105/1604564722_5fa3b6f2e4cf488c463bc.png!small)

## 在产品中使用Safety

Safety是免费且开源的，它的底层开放数据库每个月还会更新一次。为了访问到所有最新添加进去的安全漏洞，我们需要使用一个Safety
API密钥以及一个付费的pyup.io账号（约99美元）。

## 工具选项

### \--key

即pyup.io的漏洞数据库API密钥，需要在SAFETY_API_KEY环境变量中设置：

    
    
    safety check --key=12345-ABCDEFGH

### \--db

指向本地数据库的目录路径，其中包括insecure.json和insecure_full.json：

    
    
    safety check --db=/home/safety-db/data

### \--proxy-host

代理主机的IP或DNS

    
    
    --proxy-port

代理端口号

    
    
    --proxy-protocol

代理协议(https或http)

### \--json

JSON格式的漏洞报告输出：

    
    
    safety check --json
    
    [
    
        [
    
            "django",
    
            "<1.2.2",
    
            "1.2",
    
            "Cross-site scripting (XSS) vulnerability in Django 1.2.x before 1.2.2 allows remote attackers to inject arbitrary web script or HTML via a csrfmiddlewaretoken (aka csrf_token) cookie.",
    
            "25701"
    
        ]
    
    ]

### \--full-report

获取完整的漏洞扫描报告，还包括安全建议：

    
    
    safety check --full-report
    
    +==============================================================================+
    
    |                                                                              |
    
    |                               /$$$$$$            /$$                         |
    
    |                              /$$__  $$          | $$                         |
    
    |           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$           |
    
    |          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$           |
    
    |         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$           |
    
    |          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$           |
    
    |          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$           |
    
    |         |_______/  \_______/|__/     \_______/   \___/   \____  $$           |
    
    |                                                          /$$  | $$           |
    
    |                                                         |  $$$$$$/           |
    
    |  by pyup.io                                              \______/            |
    
    |                                                                              |
    
    +==============================================================================+
    
    | REPORT                                                                       |
    
    +============================+===========+==========================+==========+
    
    | package                    | installed | affected                 | ID       |
    
    +============================+===========+==========================+==========+
    
    | django                     | 1.2       | <1.2.2                   | 25701    |
    
    +==============================================================================+
    
    | Cross-site scripting (XSS) vulnerability in Django 1.2.x before 1.2.2 allows |
    
    |  remote attackers to inject arbitrary web script or HTML via a csrfmiddlewar |
    
    | etoken (aka csrf_token) cookie.                                              |
    
    +==============================================================================+

### \--bare

仅输出包含漏洞的依赖包，可结合其他工具一起使用：

    
    
    safety check --bare
    
    cryptography django

### \--cache

漏洞数据库本地缓存，有效时长为两小时：

    
    
    safety check --cache

### \--stdin

从stdin读取输入数据：

    
    
    cat requirements.txt | safety check --stdin
    
    pip freeze | safety check --stdin
    
    echo "insecure-package==0.1" | safety check --stdin

### \--output, -o

将扫描结果输出至文件：

    
    
    safety check -o insecure_report.txt
    
    safety check --output --json insecure_report.json

## 开源许可证协议

本项目的开发与发布遵循MIT开源许可证协议。

## 项目地址

Safety：【[ _GitHub传送门_](https://github.com/pyupio/safety)】

