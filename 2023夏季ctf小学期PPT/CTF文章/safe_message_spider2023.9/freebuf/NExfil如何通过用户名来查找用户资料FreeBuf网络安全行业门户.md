![](https://image.3001.net/images/20210722/1626920737_60f8d72107d20ef6c91c2.jpg!small)

## 关于NExfil

NExfil是一款功能强大的OSINT公开资源情报工具，该工具采用Python开发，可以帮助广大研究人员通过用户名来查找目标用户的个人资料。研究人员在将目标用户名提供给NExfil之后，NExfil会在几秒钟之内快速查询超过350个网站。该工具的主要目标就是在保持低误报率的同时快速得到扫描结果。

## 功能介绍

快速扫描查询，20秒内即可完成查询；

支持对超过350个网站进行扫描；

Batch批处理：可通过命令行提供目标用户名，也可通过文件提供目标用户名列表；

扫描结果自动存储至txt文件中；

即将支持JSON和CSV文件格式；

即将添加代理支持；

即将支持Tor；

## 工具安装

广大研究人员可以使用下列命令将该项目源码克隆至本地，并完成依赖组件和工具的下载和安装：

    
    
    git clone https://github.com/thewhiteh4t/nexfil.git
    
    cd nexfil
    
    pip3 install -r requirements.txt

## 工具使用

### 查看帮助信息

    
    
    python3 nexfil.py -h
    
    usage: nexfil.py [-h] [-u U] [-d D [D ...]] [-f F] [-l L] [-t T] [-v]
    
     
    
    nexfil - Find social media profiles on the web | v1.0.0
    
     
    
    optional arguments:
    
      -h, --help      显示帮助信息和退出
    
      -u U          指定目标用户名
    
      -d D [D ...]   指定DNS服务器【默认为 1.1.1.1】
    
      -f F         指定一个包含用户名列表的文件 
    
      -l L         指定多个目标用户名，使用逗号分隔
    
      -t T         指定超时时长【默认为20秒】
    
      -v           输出当前工具版本信息

### 查询单个目标用户名

    
    
    python3 nexfil.py -u username

### 查询多个目标用户名（使用逗号分隔）

    
    
    python3 nexfil.py -l "user1, user2"

### 查询文件中的目标用户名列表

    
    
    python3 nexfil.py -f users.txt

## 工具使用演示

![](https://image.3001.net/images/20210722/1626920785_60f8d751d29c68533f5e7.gif)

## 项目地址

 **NExfil：** 【[ _GitHub传送门_](https://github.com/thewhiteh4t/nexfil)】

