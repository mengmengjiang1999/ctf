**今天给大家介绍的是一款名叫Penta的自动化渗透测试工具，Penta，即渗透测试Pentest与自动化实现Automation。Penta是一个开源项目，并且整合了多种功能，来帮助研究人员自动化实现渗透测试任务。**

![1.png](https://image.3001.net/images/20191008/1570547337_5d9ca689ed464.png!small)

Penta采用Python 3开发，并且提供了大量高级功能，例如Metasploit以及Nexpose，可帮助研究人员从指定服务器中提取出详细的漏洞信息。

![](https://image.3001.net/images/20191009/1570619714_5d9dc142b587d.gif)

## 工具安装

### 安装依赖组件

Penta的正常运行需要用户安装下列代码包：

> -Python 3.7
>
> -pipenv

解析Python包依赖：

    
    
    $ pipenv install
    

如果你不喜欢使用pipenv的话，你也可以使用pip命令完成依赖组件的配置：

    
    
    $ pip install -r requirements.txt
    

## 工具下载

广大用户可以使用git命令直接将项目代码从GitHub库克隆至本地：

    
    
    git clone https://github.com/takuzoo3868/penta.git
    

## 工具使用

    
    
    $ pipenv run start <options>
    

如果你不想使用pipenv的话，你也可以使用下列命令运行Penta：

    
    
    $ python penta/penta.py
    

使用-h参数可查看工具的可用选项列表：

    
    
    $ pipenv run start -h
    usage: penta.py [-h] [-target TARGET] [-ports PORTS] [-proxy PROXY]
    
    Penta is Pentest automation tool
    
    optional arguments:
      -h, --help      show this help message and exit
      -target TARGET  Specify target IP / domain
      -ports PORTS    Please, specify the target port(s) separated by comma.
                      Default: 21,22,25,80,110,443,8080
      -proxy PROXY    Proxy[IP:PORT]
    

### 工具主菜单：

    
    
    [ ] === MENU LIST ===========================================
    [0] EXIT
    [1] Port scanning Default: 21,22,25,80,110,443,8080
    [2] Nmap & vuln scanning
    [3] Check HTTP option methods
    [4] Grab DNS server info
    [5] Shodan host search
    [6] FTP connect with anonymous
    [7] SSH connect with Brute Force
    [99] Change target host
    

> 1、端口扫描：对目标设备进行常规端口扫描，并输出详细扫描日志。
>
> 2、Nmap：使用Nmap作为辅助来扫描端口。
>
> 3、检测HTTP选项方法：例如Get和POST等。
>
> 4、获取DNS服务器的详细信息。
>
> 5、利用Shodan主机扫描功能来收集主机服务信息，此功能需要用户配置Shodan API秘钥。
>
>
> 6、利用FTP匿名登录来判断目标主机是否开启端口21。FTP用户可以使用明文登录协议来完成身份认证，但服务器允许的话，他们同样可以使用匿名登录来访问服务器。
>
> 7、暴力破解SSH链接，字典数据位于data/dict路径下。

 ***参考来源：[
_takuzoo3868_](https://github.com/takuzoo3868/penta)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

