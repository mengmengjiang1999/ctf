## 前言

**BabySploit是一款由Python编写的渗透测试框架。该框架旨在帮助初学者轻松的学习并掌握其它更为复杂强大的渗透测试框架，如Metasploit。由于针对的是初学者，BabySploit框架还为我们提供了一个非常易于使用的UI，以及功能丰富的工具套件。因此，可以说任何层级水平的人都能在BabySploit上找到它的用武之地。**

 **
**![68747470733a2f2f737465616d63646e2d612e616b616d616968642e6e65742f737465616d636f6d6d756e6974792f7075626c69632f696d616765732f636c616e732f32373039303534312f38646435633930376632613065656362373364633661343737366663396132.png](https://image.3001.net/images/20181205/1543969025_5c071901c46a9.png!small)**  
**

注：BabySploit当前只支持在Kali Linux上使用，不支持其它任何的发行版本。

视频演示：<https://asciinema.org/a/FKAPSoELbeclWr8TxKClOxWd9>

## 安装说明

### 使用Pip

    
    
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install exploitdb netcat nmap perl php7.0 
    pip3 install babysploit
    babysploit

要使用search命令，你必须[按照此处的步骤](https://www.exploit-db.com/searchsploit/#install)安装searchsploit二进制文件！

### 克隆存储库

    
    
    sudo apt-get update
    sudo apt-get upgrade
    sudo apt-get install exploitdb netcat nmap perl php7.0
    git clone https://github.com/M4cs/BabySploit.git
    cd BabySploit/
    python3 setup.py install
    babysploit

### Docker Run命令

    
    
    docker run --rm -idt --name babysploit xshuden/babysploit    # container is deleted when you're done
    或
    docker run -idt --name babysploit xshuden/babysploit

## 使用

### 设置配置值：

BabySploit使用ConfigParser来编写和读取配置。你的配置文件是自动生成的，位于./babysploit/config/config.cfg。你可以打开该文件并使用文本编辑器进行编辑，来手动更改配置。或者你也可以使用set命令为key设置新值。命令如下：

    
    
    set rhost
    >> Enter Value For rhost: 10
    >> Config Key Saved!

如果在运行该命令之前，rhost key的值为80，则运行该命令后rhost key的值将被更改为10。你还可以通过使用带有new
key的set命令，将配置变量添加到配置中，命令如下：

    
    
    set newkey
    >> Enter Value For newkey: hello
    >> Config Key Saved!

在运行该命令之前，并没有名为“newkey”的键。运行该命令后，你将在配置中看到一个名为“newkey”的键，直到你使用reset命令重置已保存的配置。

### 运行工具

运行工具，你只需在BabySploit中输入相应工具的名称即可，例如ftpbruteforce -runs。你可以使用tools命令查看当前包含的所有工具及其描述，如下所示：

![68747470733a2f2f696d6167652e70726e747363722e636f6d2f696d6167652f644d6c554f6a466e516b5f4b537972753167545132412e706e67.png](https://image.3001.net/images/20181205/1543969062_5c071926ea62f.png!small)

## 特性（当前，进行中，计划）

在[project页面](https://github.com/M4cs/BabySploit/projects/1)列出了我们当前最新添加的功能，以及正在进行中和计划实现的功能。

> 信息收集
>
> 利用
>
> 后利用
>
> 暴破
>
> 网络钓鱼
>
> 加密/隐写

### 信息收集：

> Nmap
>
> IP Info
>
> Tcpdump（进行中）
>
> Datasploit（进行中）
>
> Censys Lookup
>
> DNS Lookup
>
> Raccoon
>
> Cloudflare Bypasser

### 利用：

> Searchsploit
>
> ReverseShell Wizard
>
> FTP Buffer Overflow Scan
>
> WPSeku WordPress Vuln Scanner

### 后利用：

> 进行中

### 暴力破解：

> FTP Bruteforcer
>
> WPSeku WordPress Login Bruteforce

### 网络钓鱼：

> BlackEye Python

### 加密/隐写：

> MetaKiller
>
>  **PDFMeta**

 **
*参考来源：[GitHub](https://github.com/M4cs/BabySploit)，FB小编secist编译，转载请注明来自FreeBuf.COM**

