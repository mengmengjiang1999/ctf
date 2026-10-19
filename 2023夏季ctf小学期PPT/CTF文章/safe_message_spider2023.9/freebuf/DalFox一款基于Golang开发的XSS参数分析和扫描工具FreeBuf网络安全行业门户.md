![](https://image.3001.net/images/20200518/1589812969_5ec29ee97d511.png!small)**DalFox是一款功能强大的XSS参数分析和扫描工具，该工具基于Golang开发，可以帮助广大研究人员通过分析参数，来寻找XSS漏洞，并基于DOM解析器来对找到的XSS漏洞进行验证。**

## 核心功能

1、参数分析（寻找反射参数，寻找存在问题的字符，识别注入点）；

2、静态分析（检测存在问题的Header，例如CSP、X-Frame-optiopns等）；

3、优化Payload查询，通过Payload生成检查注入点，消除不必要的Payload；

4、XSS扫描，支持反射型和存储型；

5、所有的测试Payload已通过编码器测试，支持双重URL编码和HTML十六进制编码；

6、友好的管道支持（单一URL、文件和IO）；

##  **工具安装**

目前，DalFox提供了三种安装方式，但我个人建议使用go安装。

## 开发者版本（go-get或go-install）

### go-install

使用下列命令将该项目源码克隆至本地：

    
    
    $ git clone https://github.com/hahwul/dalfox  
    

在本地DalFox项目目录下使用下列命令完成安装：

    
    
    $ go install  
    

使用dalfox：

    
    
    $ ~/go/bin/dalfox  
    

### go-get

使用下列命令下载和安装DalFox：

    
    
    $ go get -u github.com/hahwul/dalfox  
    

使用dalfox：

    
    
    $ ~/go/bin/dalfox  
    

## 发布版本

首先，访问该项目GitHub库的Release页面下载最新版本的DalFox：【[传送门](https://github.com/hahwul/dalfox/releases/latest)】。

针对你自己的操作系统版本，下载并提取对应版本的DalFox。

你也可以直接将其放入可执行目录中，比如说：

    
    
    $ cp dalfox /usr/bin/  
    

## 工具使用

![](https://image.3001.net/images/20200518/1589813018_5ec29f1a8f757.png!small)

    
    
    $ dalfox [mode] [flags]  
    

单一目标模式：

    
    
    $ dalfox url http://testphp.vulnweb.com/listproducts.php\?cat\=123\&artist\=123\&asdf\=ff -b https://hahwul.xss.ht  
    

多目标模式，从文件读取扫描目标：

    
    
    $ dalfox file urls_file --custom-payload ./mypayloads.txt  
    

管道模式：

    
    
    $ cat urls_file | dalfox pipe -H "AuthToken: bbadsfkasdfadsf87"  
    

工具运行截图

![](https://image.3001.net/images/20200518/1589813038_5ec29f2e8e3b3.png!small)

##
![](https://image.3001.net/images/20200518/1589813046_5ec29f364a74c.png!small)
项目地址

DalFox：【[GitHub传送门](https://github.com/hahwul/dalfox)】

***参考来源：[hahwul](https://github.com/hahwul/dalfox)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

