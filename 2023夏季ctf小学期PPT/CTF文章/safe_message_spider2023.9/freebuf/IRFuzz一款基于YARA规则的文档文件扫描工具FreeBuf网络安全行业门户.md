![](https://image.3001.net/images/20201002/1601620592_5f76ca708156eb603cc7b.png!small)

## 工具介绍

IRFuzz是一款基于YARA规则的扫描工具，可以帮助广大研究人员扫描文档以及文件。

目前，该工具适用于Linux和macOS操作统平台。

## 依赖组件

1、[
_Yara_](https://github.com/VirusTotal/yara/)：仅使用了该项目最新发布的源代码，我们需要编译并安装它，或者直接通过pip命令来安装yara-python。

2、Y[ _ara规则_](https://github.com/Yara-Rules/rules)：广大研究人员可以点击【[
_这里_](https://github.com/Yara-Rules/rules)】下载Yara规则，或导入自己自定义的规则集。

3、Python依赖。

该项目使用了pipenv来管理依赖组件，如需安装依赖组件并激活虚拟环境，请运行下列命令：

    
    
    $ pipenv install
    
    $ pipenv shell

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/oxiqa/IRFuzz.git

## 工具运行

    
    
    $ python -m watchd.watch ~/tools/IR/ -y rules/maldocs --csv csvfile.csv

![](https://image.3001.net/images/20201002/1601620620_5f76ca8c99f372ed32d54.png!small)

## 支持的功能

  * 使用inotify扫描新的文件；
  * 如果不支持inotify，则使用轮询方式扫描文件；
  * 支持自定义扩展；
  * 删除模式将删除匹配的文件；
  * 递归目录扫描；
  * 使用yara字符串和ctime枚举匹配的Yara函数；
  * 以CSV格式存储扫描结果；

### 自定义扩展

    
    
    $ python -m watchd.watch ~/tools/IR/ -y rules/maldocs --csv csvfile.csv --extensions .zip,.rar

### 匹配YARA规则

首先，点击【这里】生成令牌。然后运行下列命令，并在网站中配置匹配警告提醒，这里支持Telegram或电子邮件：

    
    
    $ python -m watchd.watch ~/tools/IR/ -y rules/maldocs --csv csvfile.csv --extensions .php --token tokenhere

### 删除匹配的文件

    
    
    $ python -m watchd.watch ~/tools/IR/ -y rules/maldocs --csv csvfile.csv --delete

### 轮询（如果不支持inotify）

    
    
    $ python -m watchd.watch ~/tools/IR/ -y rules/maldocs --csv csvfile.csv --polling

添加--poll选项可以强制使用轮询机制来检测数据目录中的修改，这种方式与操作系统底层机制相比，速度要慢很多，但针对SMB文件系统的话，则只能使用这种方式。

### 默认支持的扩展

Microsoft Office Word支持的文件格式：

    
    
    .doc .docm .docx .docx .dot .dotm .dotx .odt

Microsoft Office Excel支持的文件格式：

    
    
    .ods .xla .xlam .xls .xls .xlsb .xlsm .xlsx .xlsx .xlt .xltm .xltx .xlw

Microsoft Office PowerPoint支持的文件格式：

    
    
    .pot .potm .potx .ppa .ppam .pps .ppsm .ppsx .ppt .pptm .pptx .pptx .pptx

### zipdump.py

IRFuzz使用了[
_zipdump.py_](https://github.com/DidierStevens/DidierStevensSuite/blob/master/zipdump.py)来对ZIP压缩文件进行分析。

## 项目地址

IRFuzz：【[ _GitHub传送门_](https://github.com/oxiqa/IRFuzz)】

