![](https://image.3001.net/images/20210602/1622635542_60b77416b87dc9a1ce4d6.png!small)

## 关于DomainRelationShips

DomainRelationShips这个脚本可以利用一个URL地址并通过Google Analytics
IDs来查询相关联的域名和子域名。首先，我们需要在Web页面中搜索相关的Google
Analytics的ID，然后使用这个ID来请求builtwith和hackertarget。

注意：该工具目前还无法适用于所有的网站，它主要通过下列表达式来实现搜索功能：

    
    
    ->  "www\.googletagmanager\.com/ns\.html\?id=[A-Z0-9\-]+"
    
    -> GTM-[A-Z0-9]+
    
    ->  "UA-\d+-\d+"

## 工具可用版本

Python版本：【[
_点我获取_](https://github.com/Josue87/AnalyticsRelationships/blob/main/Python)】

Go版本：【[
_点我获取_](https://github.com/Josue87/AnalyticsRelationships/blob/main/GO)】

## 工具安装

DomainRelationShips的安装需要选择对应的语言。

### Python版本

    
    
    > git clone https://github.com/Josue87/AnalyticsRelationships.git
    
    > cd AnalyticsRelationships/Python
    
    > sudo pip3 install -r requirements.txt

### Go版本

    
    
    > git clone https://github.com/Josue87/AnalyticsRelationships.git
    
    > cd AnalyticsRelationships/GO
    
    > go build -ldflags "-s -w"

### Docker版本

    
    
    > git clone https://github.com/Josue87/AnalyticsRelationships.git
    
    > cd AnalyticsRelationships
    
    > docker build -t analyticsrelationships:latest .

## 工具使用

对于DomainRelationShips的使用，不同语言版本的使用方式也不同。

### Python版本

    
    
    > python3 analyticsrelationships.py -u https://www.example.com

或者，直接将输出存储至一个文件中：

    
    
    python3 analyticsrelationships.py -u https://www.example.com > /tmp/example.txt

### Go版本

    
    
    >  ./analyticsrelationships --url https://www.example.com

或者，直接将输出存储至一个文件中：

    
    
    >  ./analyticsrelationships --url https://www.example.com > /tmp/example.txt

### Docker版本

    
    
    >  docker run -it  analyticsrelationships:latest https://www.example.com

或者，直接将输出存储至一个文件中：

    
    
    >  docker run -it  analyticsrelationships:latest https://www.example.com > /tmp/example.txt

## 工具使用样例

### Python版本

输出重定向至文件：/tmp/example.txt

![](https://image.3001.net/images/20210602/1622635614_60b7745ee652651fc2855.png!small)

输出不带重定向：

![](https://image.3001.net/images/20210602/1622635620_60b7746493b73e5844be5.png!small)

### Go版本

输出不带重定向：

![](https://image.3001.net/images/20210602/1622635632_60b77470096a5dd9ad7a3.png!small)

输出带重定向信息的方法跟Python版本的使用方法相同。

## 项目地址

 **DomainRelationShips：** 【[
_GitHub传送门_](https://github.com/Josue87/AnalyticsRelationships)】

## 参考资料

> [
> _https://github.com/Josue87/AnalyticsRelationships/blob/main/Python_](https://github.com/Josue87/AnalyticsRelationships/blob/main/Python)
>
> [
> _https://github.com/Josue87/AnalyticsRelationships/blob/main/GO﻿_](https://github.com/Josue87/AnalyticsRelationships/blob/main/GO)

