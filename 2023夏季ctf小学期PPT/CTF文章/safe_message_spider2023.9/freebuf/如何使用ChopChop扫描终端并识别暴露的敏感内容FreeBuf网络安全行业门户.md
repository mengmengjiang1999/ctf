![](https://image.3001.net/images/20220101/1641000691_61cfaef3e90c83f3d8e6f.png!small)

## 关于ChopChop

ChopChop是一款功能强大的命令行工具，可以帮助广大研究人员针对Web应用程序进行动态应用程序测试。该工具的主要目的是扫描终端节点，并识别暴露的敏感服务、文件和目录。开发人员还可以在配置文件中声明检测项和签名，所有内容均支持配置，配置文件为chopchop.yml。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/michelin/ChopChop

## 项目构建

我们可以通过下列命令轻松构建项目代码：

    
    
    $ go mod download
    
    $ go build .

运行上述命令后，项目目录内将出现构建生成的gochopchop代码。

### Docker使用

多亏了Github Container Registry，我们可以直接给大家提供最新版本的Docker镜像：

    
    
    docker run ghcr.io/michelin/gochopchop scan https://foobar.com -v debug

如果你愿意的话，你也可以在本地进行镜像构建：

    
    
    docker build -t gochopchop .

## 工具使用

我们希望ChopChop的使用是尽可能简单的，所以我们可以直接使用下列命令将该ChopChop当作一款实用工具来直接对目标主机进行扫描：

    
    
    $ ./gochopchop scan https://foobar.com

### 使用Docker

    
    
    docker run gochopchop scan https://foobar.com

### 自定义配置文件

    
    
    docker run -v ./:/app chopchop scan -c /app/chopchop.yml https://foobar.com

## 可选参数

当前版本的ChopChop支持使用下列参数选项来配合scan命令执行扫描：

 ** **选项****

|

 ** **完整选项****

|

 ** **描述****  
  
---|---|---  
  
-h

|

\--help

|

查看帮助信息  
  
-v

|

\--verbosity

|

Verbose日志等级  
  
-c

|

\--signature

|

自定义签名文件的路径  
  
-k

|

\--insecure

|

禁用SSL认证  
  
-u

|

\--url-file

|

待测试URL文件路径  
  
-b

|

\--max-severity

|

屏蔽严重性匹配标签的CI管道  
  
-e

|

\--export

|

导出数据的格式类型（CSV/JSON）  
  
  

|

\--export-filename

|

指定导出文件的文件名  
  
-t

|

\--timeout

|

HTTP请求超时  
  
  

|

\--severity-filter

|

过滤器插件（按严重程度分）  
  
  

|

\--plugin-filter

|

过滤器插件（按插件名称分）  
  
  

|

\--threads

|

并发线程数  
  
## 高级使用

### 扫描和禁用SSL验证

    
    
    $ ./gochopchop scan https://foobar.com --insecure

### 使用自定义配置文件扫描

    
    
    $ ./gochopchop scan https://foobar.com --insecure --signature test_config.yml

### 按严重程度枚举所有插件

    
    
    $ ./gochopchop plugins --severity High

### 执行扫描指定并发线程数量

    
    
    $ ./gochopchop plugins --threads 4

### 指定需要检测的签名

    
    
    ./gochopchop scan https://foobar.com --timeout 1 --verbosity --export=csv,json --export-filename boo --plugin-filters=Git,Zimbra,Jenkins

### 枚举所有插件

    
    
    $ ./gochopchop plugins

### 枚举高严重性插件

    
    
    $ ./gochopchop plugins --severity High

### 在文件中设置URL列表

    
    
    $ ./gochopchop scan --url-file url_file.txt

### 将ChopChop扫描结果导出为CSV和JSON格式

    
    
    $ ./gochopchop scan https://foobar.com  --export=csv,json --export-filename results

## 外部代码库

 ** **库名称****

|

 ** **链接****

|

 ** **许可证****  
  
---|---|---  
  
Viper

|

<https://github.com/spf13/viper>

|

MIT  
  
Go-pretty

|

<https://github.com/jedib0t/go-pretty>

|

MIT  
  
Cobra

|

<https://github.com/spf13/cobra>

|

Apache 2.0  
  
strfmt

|

<https://github.com/go-openapi/strfmt>

|

Apache 2.0  
  
Go-homedir

|

<https://github.com/mitchellh/go-homedir>

|

MIT  
  
pkg-errors

|

<https://github.com/pkg/errors>

|

BSD 2  
  
Go-runewidth

|

<https://github.com/mattn/go-runewidth>

|

MIT  
  
## 工具使用演示

![](https://image.3001.net/images/20220101/1641000822_61cfaf76e7b5dd9b5aa3b.gif!small)

## 项目地址

本项目的开发与发布遵循Apache v2.0开源许可证协议。

## 项目地址

 **ChopChop：** 【[ _GitHub传送门_](https://github.com/michelin/ChopChop)】

## 参考资料

> [
> _https://docs.google.com/presentation/d/1uVXGUpt7tC7zQ1HWegoBbEg2LHamABIqfDfiD9MWsD8/edit_](https://docs.google.com/presentation/d/1uVXGUpt7tC7zQ1HWegoBbEg2LHamABIqfDfiD9MWsD8/edit)
>
> [ _https://drive.google.com/file/d/15P8eSarIohwCVW-> tR3FN78KJPGbpAtR1/view﻿_](https://drive.google.com/file/d/15P8eSarIohwCVW-> tR3FN78KJPGbpAtR1/view)

