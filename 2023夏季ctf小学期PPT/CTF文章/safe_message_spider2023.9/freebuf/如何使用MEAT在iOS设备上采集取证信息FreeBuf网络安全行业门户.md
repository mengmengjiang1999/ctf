![](https://image.3001.net/images/20210917/1631853085_61441a1d62e8530a1d4df.jpg!small)

## 关于MEAT

MEAT，全称为Mobile Evidence Acquisition
Toolkit，即移动设备取证采集工具。该工具旨在帮助安全取证人员在iOS设备上执行不同类型的信息采集任务，将来该工具会添加针对Android设备的支持。

## 工具要求

> Windows或Linux系统
>
> Python 3.7.4或7.2环境
>
> pip包，具体参考txt

## 已测试的平台

该工具的当前版本已在iPhone X iOS 13.3和iPhone XS iOS 12.4上进行过测试。

## 工具下载

广大研究人员可以通过下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/jfarley248/MEAT.git

## 工具帮助信息

    
    
    usage: MEAT.py [-h] [-iOS] [-filesystem] [-filesystemPath FILESYSTEMPATH]
                   [-logical] [-md5] [-sha1] -o OUTPUTDIR [-v]
    MEAT - Mobile Evidence Acquisition Toolkit
    optional arguments:
      -h, --help            显示帮助信息并退出
      -iOS                在iOS设备上执行信息采集
      -filesystem           执行文件系统采集 
      -filesystemPath       文件系统路径，需配合--filesystem参数使用，默认为"/"
      -logical              执行逻辑采集，使用AFC访问内容
      -md5               使用MD5算法获取哈希文件，输出至Hash_Table.csv
      -sha1               使用MD5算法获取哈希文件，输出至Hash_Table.csv
      -o OUTPUTDIR        存储输出文件的目录
      -v                  开启Verbose模式

## 支持的采集类型

### iOS设备-逻辑采集

在MEAT上使用逻辑采集功能，将指示工具通过越狱设备的AFC提取可访问的文件和文件夹。

允许访问的文件夹为“\private\var\mobile\Media”，其中将包含下列文件夹：

> AirFair
>
> Books
>
> DCIM
>
> Downloads
>
> general_storage
>
> iTunes_Control
>
> MediaAnalysis
>
> PhotoData
>
> Photos
>
> PublicStaging
>
> Purchases
>
> Recordings

### iOS设备-文件系统

 **前提要求：** 已越狱的iOS设备、通过Cydia安装AFC2、Apple File Conduit 2

在MEAT上使用文件系统采集功能，可以允许该工具开启AFC2服务，并将目标设备上所有的文件和文件夹拷贝至我们的主机系统中。这个方法需要目标设备已越狱，并安装好Apple
File Conduit 2。该方法还可以使用-filesystemPath参数来进行修改，并让MEAT提取指定的目录。

## 项目地址

 **MEAT：** 【[ _GitHub传送门_](https://github.com/jfarley248/MEAT)】

## 参考资料

> [
> _https://github.com/iOSForensics/pymobiledevice/tree/master/pymobiledevice_](https://github.com/iOSForensics/pymobiledevice/tree/master/pymobiledevice)
>
> [
> _https://www.blackstonediscovery.com/﻿_](https://www.blackstonediscovery.com/)

