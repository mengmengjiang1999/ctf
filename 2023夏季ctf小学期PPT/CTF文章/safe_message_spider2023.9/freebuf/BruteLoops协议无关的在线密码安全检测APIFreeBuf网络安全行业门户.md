![](https://image.3001.net/images/20211122/1637579847_619b7c479f96c5b9782ae.png!small)

## 关于BruteLoops

BruteLoops是一款功能强大且协议无关的在线密码安全检测API，广大研究人员可以使用BruteLoops来实现在线密码猜解，以检查用户所使用的密码是否安全，或识别密码中的安全问题。

BruteLoops针对身份验证接口提供了密码爆破猜解功能，代码库中提供了一个模块化的使用示例，并演示了如何使用BruteLoops来实现密码安全解析。它的功能非常齐全，并且提供了多个爆破模块，下面给出的是其功能示例：

  * http.accellion_ftp FTP HTTP接口登录加速模块
  * http.basic_digest 通用HTTP基本摘要验证
  * http.basic_ntlm 通用HTTP基本NTLM身份验证
  * http.global_protectWeb接口全局保护
  * http.mattermost Mattermost登录Web接口
  * http.netwrix Netwrix登录Web接口
  * http.okta Okta JSON API
  * http.owa2010 OWA 2010Web接口
  * http.owa2016 OWA 2016 Web接口
  * smb.smb 针对单个SMB服务器执行任务
  * testing.fake 用于培训/测试的模拟身份验证模块

## 关键功能

  * 协议无关
  * SQLite支持
  * 密码喷射和密码填充
  * 密码猜解计划任务
  * 细粒度可配置性以避免锁定事件
  * 任务暂停和继续
  * 多进程支持
  * 日志记录

## 工具依赖

BruteLoops工具要求Python 3.7或更高版本的Python环境，以及[ _SQLAlchemy
1.3.0_](https://www.sqlalchemy.org/)，后者可以通过pip工具以及该项目提供的requirements.txt来安装：

    
    
    python3.7 -m pip install -r requirements.txt

## 工具安装

广大研究人员可以通过下列命令将该项目源码克隆至本地，并安装该工具所需的依赖组件：

    
    
    git clone https://github.com/arch4ngel/bruteloops
    
    cd bruteloops
    
    python3 -m pip install -r requirements.txt

## 工具使用

在使用该工具时，我们可以按照以下步骤来对密码安全测试进行拆分：

  * 寻找一个需要测试的目标服务；
  * 如果py【[ _1_](https://github.com/arch4ngel/BruteLoops/wiki/Using-example.py-to-Execute-Brute-Force-Attacks)】中没有存在该目标，则需要构建一个回调；
  * 搜索某些用户名、密码和凭证信息；
  * 通过向py【[ _2_](https://github.com/arch4ngel/BruteLoops/wiki/Using-dbmanager.py-To-Manage-Databases)】输入认证数据来构建一个数据库；
  * 如果相关，则枚举或请求活动目录锁定策略来智能地配置安全测试过程；
  * 根据目标锁定策略执行密码安全测试【[ _1_](https://github.com/arch4ngel/BruteLoops/wiki/Using-example.py-to-Execute-Brute-Force-Attacks)】【[ _3_](https://github.com/arch4ngel/BruteLoops/wiki/Explanation-of-Configuration-Parameters)】【[ _4_](https://github.com/arch4ngel/BruteLoops/wiki/Jitter-Time-Format-Specification)】；

## 工具使用样例

### 通过example.py执行爆破猜解模块

 **命令：**

    
    
    archangel@deskjet:bruteloops_dev~> ./example.py test.sqlite3 testing.fake --help

 **输出：**

    
    
    usage: example.py dbfile testing.fake [-h] --username USERNAME --password PASSWORD
    
     
    
    Fake authentication module for training/testing
    
     
    
    optional arguments:
    
      -h, --help           show this help message and exit
    
      --username USERNAME  required - str - Username to check against
    
      --password PASSWORD  required - str - Password to check against

### 通过dbmanager.py创建输入数据库

 **命令：**

    
    
    archangel@deskjet:bruteloops_dev~> ./dbmanager.py --help

 **输出：**

    
    
    usage: dbmanager.py [-h] dbfile {dump-valid,dump-credentials,import-values,import-credentials,delete-values,delete-credentials} ...
    
     
    
    Manage BruteLoops input databases
    
     
    
    positional arguments:
    
      dbfile                Database file to manipulate
    
      {dump-valid,dump-credentials,import-values,import-credentials,delete-values,delete-credentials}
    
                            SUBCOMMANDS:
    
        dump-valid          Dump valid credentials from the database
    
        dump-credentials    Dump all credential values from the database
    
        import-values       Import values into the target database
    
        import-credentials  Import credential pairs into the target database
    
        delete-values       Delete values from the target database
    
        delete-credentials  Delete credential pairs from the target database
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit

### 通过example.py执行模拟爆破猜解模块

 **命令：**

    
    
    ./example.py test.sqlite3 \
    
      --parallel-guess-count 4  --auth-threshold 2 \
    
      --auth-jitter-min 1s --auth-jitter-max 5s \
    
      --threshold-jitter-min 10s --threshold-jitter-max 20s \
    
      -lf test.log \
    
      testing.fake --username administrator --password P@ssw0rd

 **输出：**

    
    
    archangel@deskjet:bruteloops_dev~> ./example.py test.sqlite3 -pgc 4 -at 2 -ajmin 1s -ajmax 5s -tjmin 10s -tjmax 20s -lf test.log testing.fake --username administrator --password P@ssw0rd
    
    2020-12-08 15:22:50,077 - example.py - GENERAL - Initializing attack
    
    2020-12-08 15:22:50,078 - BruteForcer - GENERAL - Initializing 4 process
    
    2020-12-08 15:22:50,078 - BruteForcer - GENERAL - Logging attack configuration parameters
    
    2020-12-08 15:22:50,078 - BruteForcer - GENERAL - Config Parameter -- authentication_jitter: <Jitter(min="1s", max="5s")>
    
    2020-12-08 15:22:50,078 - BruteForcer - GENERAL - Config Parameter -- max_auth_jitter: <Jitter(min="10s", max="20s")>
    
    2020-12-08 15:22:50,078 - BruteForcer - GENERAL - Config Parameter -- max_auth_tries: 2
    
    2020-12-08 15:22:50,078 - BruteForcer - GENERAL - Config Parameter -- stop_on_valid: False
    
    2020-12-08 15:22:50,078 - BruteForcer - GENERAL - Config Parameter -- db_file: test.sqlite3
    
    2020-12-08 15:22:50,083 - BruteForcer - GENERAL - Beginning attack: 15:22:50 EST (20/12/08)
    
    2020-12-08 15:22:51,572 - BruteForcer - INVALID - user1:pass1
    
    2020-12-08 15:22:53,544 - BruteForcer - INVALID - admin:password
    
    2020-12-08 15:22:54,597 - BruteForcer - INVALID - user1:password
    
    2020-12-08 15:22:55,025 - BruteForcer - INVALID - admin:pass1
    
    2020-12-08 15:22:55,247 - BruteForcer - INVALID - user2:pass1
    
    2020-12-08 15:22:56,307 - BruteForcer - INVALID - user2:password
    
    2020-12-08 15:22:59,025 - BruteForcer - INVALID - administrator:pass1
    
    2020-12-08 15:22:59,680 - BruteForcer - INVALID - administrator:password
    
    2020-12-08 15:23:07,384 - BruteForcer - INVALID - user1:welcome1
    
    2020-12-08 15:23:07,955 - BruteForcer - INVALID - user1:P@ssw0rd
    
    2020-12-08 15:23:08,775 - BruteForcer - INVALID - administrator:welcome1
    
    2020-12-08 15:23:09,631 - BruteForcer - VALID - administrator:P@ssw0rd
    
    2020-12-08 15:23:12,057 - BruteForcer - INVALID - user2:welcome1
    
    2020-12-08 15:23:12,299 - BruteForcer - INVALID - admin:welcome1
    
    2020-12-08 15:23:12,309 - BruteForcer - INVALID - user2:P@ssw0rd
    
    2020-12-08 15:23:12,534 - BruteForcer - INVALID - admin:P@ssw0rd
    
    2020-12-08 15:23:12,748 - BruteForcer - GENERAL - Attack finished
    
    2020-12-08 15:23:12,748 - BruteForcer - GENERAL - Shutting attack down
    
    2020-12-08 15:23:12,755 - BruteForcer - GENERAL - Closing/joining Processes
    
    2020-12-08 15:23:12,758 - example.py - GENERAL - Attack complete

## 项目地址

 **BruteLoops：** 【[ _GitHub传送门_](https://github.com/arch4ngel/BruteLoops)】

