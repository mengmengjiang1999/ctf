## 关于LEAF

LEAF是一款功能强大的Linux安全取证框架，在该工具的帮助下，广大研究人员可以轻松对Linux主机执行信息安全取证任务。

LEAF全称为Linux Evidence Acquisition Framework，该框架可以从Linux
EXT4系统中获取文件和程序等信息安全取证信息，而且可以接收用户输入参数并进行自定义功能扩展。向LEAF提供了模块参数后，该工具将能够通过智能分析技术来提取Linux组件，并将分析数据输出到一个ISO镜像文件中。

## 工具要求

该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python环境。

推荐使用Python 3.8或更高版本。安装命令如下：

    
    
    apt install python3
    
    apt install pip3

接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/alex-cart/LEAF.git

切换到项目目录中，使用下列命令并通过requirements.txt文件安装该工具所需的依赖组件：

    
    
    pip3 install -r requirements.txt

如果遇到报错的话，可以使用下列命令尝试修复：

    
    
    sudo -H pip3 install -r requirements.txt

## 工具使用

    
    
    LEAF_master.py [-h] [-i INPUT [INPUT ...]] [-o OUTPUT] [-u USERS [USERS ...]] [-c CATEGORIES [CATEGORIES ...]] [-v]
    
                          [-s] [-g [GET_FILE_BY_OWNER [GET_FILE_BY_OWNER ...]]] [-y [YARA [YARA ...]]]
    
                          [-yr [YARA_RECURSIVE [YARA_RECURSIVE ...]]] [-yd [YARA_DESTINATIONS [YARA_DESTINATIONS...]]]
    
     
    
    LEAF (Linux Evidence Acquisition Framework) - Cartware
    
         ____        _________    ___________   __________
    
        /   /       /   _____/   /  ____    /  /   ______/
    
       /   /       /   /____    /  /___/   /  /   /____  
    
      /   /       /   _____/  /   ____    /  /   _____/
    
     /   /_____  /   /_____  /   /   /   /  /   /      
    
    /_________/ /_________/ /___/   /___/  /___/          v2.0

## 工具运行

此时，我们就可以使用下列命令并配合选项参数来运行LEAF了：

    
    
    sudo python3 LEAF_master.py

## 工具参数

    
    
    optional arguments:
    
     
    
      -h, --help            显示帮助信息和退出工具
    
     
    
      -i INPUT [INPUT ...], --input INPUT [INPUT ...]
    
                            额外输入文件路径，多个文件以空格划分
    
                            默认: /home/user1/Desktop/LEAF-3/target_locations
    
     
    
      -o OUTPUT, --output OUTPUT
    
      
    
                            输出目录地址
    
                            默认: ./LEAF_output
    
     
    
      -u USERS [USERS ...], --users USERS [USERS ...]
    
      
    
                            要包含在输出文件中的用户信息，以空格划分
    
    例如-u alice bob root).
    
                            /etc/passwd中不存在的用户将会被移除
    
      -c CATEGORIES [CATEGORIES ...], --categories CATEGORIES [CATEGORIES ...]
    
                            取证期间需要包含的工具组件和目录
    
                            目录以空格划分，例如-c network users apache
    
                            默认包含的目录为：APPLICATIONS, EXECUTIONS, LOGS, MISC, NETWORK, SHELL, STARTUP, SERVICES, SYSTEM, TRASH, USERS
    
      -v, --verbose          Verbose模式输出，默认：False
    
      -s, --save             存储原始取证信息目录，默认：False
    
      -g [GET_OWNERSHIP [GET_OWNERSHIP ...]], --get_ownership [GET_OWNERSHIP [GET_OWNERSHIP ...]]
    
                            获取引入用户的所拥有的全部文件和目录
    
                            默认: Disabled
    
      -y [YARA [YARA ...]], --yara [YARA [YARA ...]]
    
                            配置Yara IOC扫描
    
                            默认: None
    
      -yr [YARA_RECURSIVE [YARA_RECURSIVE ...]], --yara_recursive [YARA_RECURSIVE [YARA_RECURSIVE ...]]
    
                            配置递归Yara IOC扫描
    
                            默认: None
    
      -yd [YARA_DESTINATIONS [YARA_DESTINATIONS...]], --yara_destinations [YARA_DESTINATIONS [YARA_DESTINATIONS...]]
    
                            需要运行Yara文件的目的路径
    
                            多个路径以空格划分，例如/home/alice/ /bin/star/
    
                            默认: 所用的用户目录

## 工具使用样例

使用默认参数运行LEAF，默认输入文件为./target_locations，用户为所有用户，目录为所有目录，输出文件路径为./LEAF_output/。克隆的数据不会存储在本地目录，默认关闭Verbose模式，禁用YARA扫描：

    
    
    LEAF_main.py

输出所有参数：

    
    
    LEAF_main.py -i /home/alice/Desktop/customfile1.txt -o /home/alice/Desktop/ExampleOutput/ -c logs startup services apache -u alice bob charlie -s -v -y /path/to/yara_rule1.yar -yr /path2/to/yara_rules/ -yd /home/frank -g /etc/

指定用户名、目录和YARA文件：

    
    
    LEAF_main.py -u alice bob charlie -c applications executions users -y /home/alice/Desktop/yara1.yar /home/alice/Desktop/yara2.yar

引入自定义输入文件和目录：

    
    
    LEAF_main.py -i /home/alice/Desktop/customfile1.txt /home/alice/Desktop/customfile2.txt -c apache xampp

## 项目地址

 **LEAF：** 【[ _GitHub传送门_](https://github.com/alex-cart/LEAF)】

