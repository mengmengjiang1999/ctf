**今天给大家介绍一款名叫OWTF（Offensive Web Testing Framework-攻击型Web测试框架），该框架整合了多种优秀的工具，可以有效提升渗透测试的效率。**

![OWTF：一款功能强大的攻击型Web测试框架](https://image.3001.net/images/20180820/1534699512_5b79a7f8db7bd.png!small)

## OWTF

OWASPOWTF项目的主要目标就是提升渗透测试的效率，测试过程和标准符合类似OWASP测试指南（v3或v4）、OWASP TOP
10、PTES和NIST这样的安全标准，这样就可以让广大渗透测试人员拥有更多的时间去完成以下事情：

> 1\. 从整体大局出发去思考，不受思维限制。
>
> 2\. 更有效率地去寻找、识别和利用漏洞。
>
> 3\. 有更多的时间去研究复杂的漏洞，例如逻辑漏洞、架构漏洞或虚拟主机会话。
>
> 4\. 对更有可能出现漏洞的组件进行更多有针对性的模糊测试。
>
> 5\. 更好地去演示漏洞对目标系统的影响。

研究人员可根据自己的需要来进行工具配置，就算你没有编程经验，你也可以直接在配置文件中添加简单的插件或测试项目。

## 功能介绍

> 快速恢复能力：如果某个工具/测试目标让OWTF崩溃了，你可以直接切换到其他工具/测试莫表，并保存部分输出数据。
>
> 灵活性：可随时暂定或恢复工作。
>
> 测试分离：OWTF可以将流量分成三种类型。
>
> Web接口：可轻松管理各种大规模渗透测试。
>
> 交互性：工具高度可配置，提供了大量REST API。
>
> 代码编辑：提供了相关的插件编辑器。

## 工具要求

OWTF可在Kali Linux和macOS平台上运行，但该工具主要针对的平台是Kali Linux或其他Debian衍生版本。

OWTF支持Python 2和Python 3。

## 工具安装

强烈建议大家使用virtualenv。

### 手动搭建数据库

替换settings.py文件中db_name、$db_user和$db_pass变量的值，确保值的正确性。接下来，开启postgreSQL服务器：

macOS：

    
    
    brew install postgresql
    pg_ctl-D /usr/local/var/postgres start

Kali：

    
    
    sudo systemctl enable postgresql
    sudo systemctl start postgresql
    sudo service postgresql start

### 创建owtf_db_user用户：

macOS：

    
    
    psqlpostgres -c "CREATE USER $db_user WITH PASSWORD '$db_pass';"

Kali：

    
    
    sudo su postgres -c "psql -c \"CREATE USER $db_user WITH PASSWORD'$db_pass'\""

### 创建数据库：

macOS：

    
    
    psqlpostgres -c "CREATE DATABASE $db_name WITH OWNER $db_user ENCODING 'utf-8'TEMPLATE template0;"

Kali：

    
    
    sudo su postgres -c "psql -c \"CREATE DATABASE $db_name WITH OWNER$db_user ENCODING 'utf-8' TEMPLATE template0;\""

### 克隆项目：

    
    
    pip install git+https://github.com/owtf/owtf#egg=owtf
    python setup.py develop

注：如果你想在Windows或macOS平台上运行OWTF的话，你需要使用到Docker Compose，运行命令“make
compose”之后，你可以直接访问localhost:8009进入到OWTF Web接口。

### 在OSX上安装

依赖：安装[Homebrew](https://brew.sh/)并按照下列步骤操作：

    
    
    $virtualenv <venv name>
    $source <venv name>/bin/activate
    $brew install coreutils gnu-sed openssl
    # Weneed to install 'cryptography' first to avoid issues
    $ pipinstall cryptography --global-option=build_ext --global-option="-L/usr/local/opt/openssl/lib"--global-option="-I/usr/local/opt/openssl/include"
    $ gitclone <this repo>
    $ cdowtf
    $python setup.py install
    # RunOWTF!
    $owtf

 ***
参考来源：[owtf](https://github.com/owtf/owtf)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

