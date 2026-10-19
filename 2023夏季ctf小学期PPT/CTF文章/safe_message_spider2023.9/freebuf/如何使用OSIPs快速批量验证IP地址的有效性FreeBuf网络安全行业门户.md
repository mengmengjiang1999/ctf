## 关于OSIPs

OSIPs是一款功能强大的Python脚本，该工具可以从一个目录中读取全部的文本文件，并从这些文本文件中收集IP地址信息，然后通过查询Whois数据库、TOR中继和地理位置服务来对目标IP地址的有效性进行批量验证。

该脚本能够递归扫描给定目录中的所有文件，并提取出所有的IPv4和IPv6地址，然后过滤出公共IP。分析完成后，工具将会输出四个文件：包含了所有IP地址详细信息的JSON文件和CSV文件，一个包含了所有IP地址索引目录的CSV文件，以及一个包含了所有IP地理位置信息的KML文件。

## 功能介绍

> 1、在一次运行中解析任意数量的文件；
>
> 2、可以针对单个输入文件执行；
>
> 3、提取所有唯一有效的IPv4和IPv6地址（正确比较两个地址，即使它们的编写方式不同）；
>
> 4、收集所有公共IP地址的公共可用WhoIs信息；
>
> 5、根据TOR中继查询所有公共IP地址；
>
> 6、收集所有公共IP地址的地理位置信息；
>
> 7、可以在非交互式模式下使用命令行参数运行，以便轻松集成到其他脚本中；
>
> 8、可以在没有参数的情况下运行，并且可以交互提供输入值；
>
> 9、允许用户选择要执行或排除的步骤；
>
> 10、在控制台执行的每一步都详细地将信息输出到控制台；
>
> 11、导出CSV文件和JSON文件中的所有IP地址详细信息；
>
> 12、导出一个可以轻松加载到地图中的KML文件；
>
> 13、将找到的所有IP地址的索引保存在单独的CSV文件中，以便于追溯；

## 工具依赖

> Python 3.9.x

## 工具安装&配置

广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/ciprianster/OSIPs.git

接下来，切换到项目目录中，使用pip命令并通过requirements.txt文件安装该工具所需的依赖组件：

    
    
    pip install -r requirements.txt

然后，使用下列命令将该项目代码编译为可执行程序：

    
    
    pip install pyinstaller
    
    pyinstaller --onefile osips.py

## 工具使用

    
    
    python osips.py [-h] [-F INPUTFOLDER] [-f INPUTFILE] [-p INPUTFILESPATTERN] [-o OUTPUTFILESNAME] [-t {y,n,Y,N}] [-w {y,n,Y,N}] [-l {y,n,Y,N}] [-locationEndpoint LOCATIONENDPOINT]

### 交互式使用

    
    
    python osips.py

### 非交互式使用

    
    
    python osips.py --checkTor Y --checkWhoIs Y --checkLocations Y --inputFolder testFolder/ --inputFilesPattern * --outputFilesName test

### 查看工具帮助信息

    
    
    python osips.py -h

## 工具选项参数

    
    
    -h, --help：显示工具帮助信息和退出
    
    -F INPUTFOLDER, --inputFolder INPUTFOLDER：扫描包含IP地址文件的目录
    
    -f INPUTFILE, --inputFile INPUTFILE：扫描IP地址文件，支持日志、邮件和文本文件
    
    -p INPUTFILESPATTERN, --inputFilesPattern INPUTFILESPATTERN：设置输入目录的文件匹配模式，例如：*代表所有文件，*.txt代表所有文本文件
    
    -o OUTPUTFILESNAME, --outputFilesName OUTPUTFILESNAME：输出文件名称，不需要设置后缀
    
    -t {y,n,Y,N}, --checkTor {y,n,Y,N}：指定是否使用TOR中继来检查每一个公共IP地址
    
    -w {y,n,Y,N}, --checkWhoIs {y,n,Y,N}：指定是否使用WhoIs来检查每一个公共IP地址
    
    -l {y,n,Y,N}, --checkLocations {y,n,Y,N}：指定是否获取每个公共IP地址的地理位置信息
    
    -locationEndpoint LOCATIONENDPOINT：默认的地理位置REST节点-"https://reallyfreegeoip.org/json/"，数据结果包含下列字段：country_name、region_code、region_name、city, zip_code、time_zone、latitude、longitude、metro_code

## 许可证协议

本项目的开发与发布遵循[ _GP_
_L-3.0_](https://github.com/ciprianster/OSIPs/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **OSIPs：** 【[ _GitHub传送门_](https://github.com/ciprianster/OSIPs)】

## 参考资料

> [ _https://reallyfreegeoip.org/_](https://reallyfreegeoip.org/)
>
> [ _https://reallyfreegeoip.org/json/_](https://reallyfreegeoip.org/json/)
>
> [
> _https://metrics.torproject.org/exonerator.html_](https://metrics.torproject.org/exonerator.html)
>
> [ _https://ipapi.co/_](https://ipapi.co/)
>
> [ _https://api.ipstack.com/_](https://api.ipstack.com/)
>
> [
> _https://freeapi.robtex.com/ipquery/_](https://freeapi.robtex.com/ipquery/)
>
> [
> _https://gist.github.com/dfee/6ed3a4b05cfe7a6faf40a2102408d5d8_](https://gist.github.com/dfee/6ed3a4b05cfe7a6faf40a2102408d5d8)
>
> [ _http://az4n6.blogspot.com/2017/02/onion-peeler-batch-tor-lookup-> program.html_](http://az4n6.blogspot.com/2017/02/onion-peeler-batch-tor-> lookup-program.html)

