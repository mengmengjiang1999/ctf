**当我们使用YARA规则扫描恶意软件源码后，我们还需要使用调试器（或其它手段）来进行处理，以进一步的分析混淆的恶意软件二进制文件。这是一个相对繁杂的过程，并且需要一个广泛的恶意软件分析环境。tknk_scanner是一个基于社区的集成恶意软件识别系统
，其旨在通过集成的基于社区的开源工具和软件来自动化的识别恶意软件家族，让原本繁杂的过程变得简单化。你可以将恶意软件以PE格式提交给扫描器，并使用你定义的YARA规则来扫描恶意软件源码。**

**![tknk_scanner](https://image.3001.net/images/20181228/1545956468_5c256c743de00.png!small)**

## 特性

自动识别和分类恶意软件

  * 使用yara扫描恶意软件的源码。

转储恶意软件的源码

  * 你可以轻松获取源码。

基于社区

  * 集成了多个开源软件和免费工具。

用户友好的Web-UI

  * 用户可以使用Web-UI提交恶意软件并检查扫描结果。

## 环境要求

> Ubuntu 18.04 (Host OS)
>
> Windows10 (Guest OS)
>
> python 3.5 或 以上
>
> yara-python 3.7.0
>
> qemu-kvm
>
> nginx
>
> Redis
>
> MongoDB

## 安装

### Host **准备**

1\. git clone --recursive repository_url

2\. sudo setup/setup.sh

3\. Edit tknk.conf

  * vm_name 
    * Virtual Machine name
  * vm_url 
    * URL of xmlrpc_server.py
    * e.g. <http://192.168.122.2:8000/>
  * virus_total 
    * If VT use, set to 1
  * vt_key 
    * Your VT API KEY

4\. 下载恶意软件标记工具

  * avclass

    
    
    $ git submodule update

  * Detect It Easy 
    * 从此处下载：<https://ntinfo.biz/>
    * 提取zip（Linux Ubuntu 64-bit(x64)）到totknk_scanner/
    * 重命名文件夹名称die

5\. 下载和复制转储工具到tools/目录

  * [hollows_hunter](https://github.com/hasherezade/hollows_hunter)

    
    
    hollows_hunter.exe
    pe-sieve.dll

  * [ProcDump](https://docs.microsoft.com/en-us/sysinternals/downloads/procdump)

    
    
    procdump.exe

  * [Scylla dll](https://github.com/NtQuery/Scylla)

    
    
    Scylla.dll

6\. 设置yara规则

  * 在“rules”文件夹中保存yara规则。你需要将规则添加到index.yar文件。

### Guest 准备

> 1\. 在KVM上安装Windows
>
> 2\. 关闭Windows Defender和Windows SmartScreen
>
> 3\. 安装Python 3.6
>
> 4\. 设置为vm_url中描述的IP地址。
>
> 5\. 复制并运行xmlrpc_server.py（推荐以管理员身份运行脚本）
>
> 6\. 制作快照

 **设置 Web-UI**

    
    
    $ cd frontend/
    $ npm install
    $ npm run generate
    $ mkdir /usr/share/nginx/tknk/
    $ sudo cp -rf dist/* /usr/share/nginx/tknk/
    $ cd ../
    $ sudo cp -f tknk-scanner.nginx.conf /etc/nginx/sites-available/default
    $ sudo systemctl restart nginx
    

**运行**

    
    
    $ cd tknk_scanner/
    $ ./tknk.py

在另一个终端上

    
    
    $ cd tknk_scanner/
    $ rq worker

## 使用

![tknk_scanner](https://image.3001.net/images/20181228/1545956500_5c256c9444f5f.png!small)

  * 文件上传   

    * 上传需要扫描的文件。
  * 时间   

    * 设置开始运行转储工具的时间。默认值为120秒。
  * 模式 
    * hollows_hunter   
使用 hollows_hunter。

    * prodump   
使用 procdump。

    * scylla   
使用 Scylla。

    * diff(procdump)   
使用procdump运行时转储新创建的进程。

##
![tknk_scanner](https://image.3001.net/images/20181228/1545956522_5c256caaa8197.png!small)![tknk_scanner](https://image.3001.net/images/20181228/1545956522_5c256caaace91.png!small)

## Demo

看不到？点[这里](https://v.qq.com/x/page/q0819jwo8cs.html)

 ***参考来源：[GitHub](https://github.com/nao-sec/tknk_scanner)，FB小编secist编译，转载请注明来自FreeBuf.COM**  

