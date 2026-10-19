# Whatweb

WhatWeb是一个开源的网站指纹识别软件。

WhatWeb可识别Web技术，包括内容管理系统（CMS），博客平台，统计/分析包，Javascript库，服务器和嵌入式设备。

## 简单使用

  1. 单个目标
    
        whatweb 网址

  2. 批量扫描
    
        whatweb -input-file=/path  
    或  
    whatweb -i /path

参数说明：

  * -i : 指定要扫描的文件

  * -v : 详细显示扫描的结果

  * -a : 指定运行级别（1-4）

  * \--log-brief=FILE 简要的记录，每个网站只记录一条返回信息

  * \--log-verbose=FILE 详细输出

  * \--log-xml=FILE 返回XML格式的日志

  * \--log-json=FILE 以 json 格式记录日志

  * \--log-json-verbose=FILE 记录详细的json日志

  * \--log-magictree=FILE XML的树形结构

Tips：

  1. JSON 格式需要安装 json 依赖， sudo gem install json

## 高级用法

    
    
    whatweb -v 192.168.64.139/24 -url-suffix=":8080"

  * -url-prefix : 添加前缀

  * -url-suffix : 添加后缀

  * -url-pattern : 在中间加入参数

    
    
    whatwen -v -proxy-user admin:password url

  * 以指定用户名和密码进行探测

    
    
    whatweb -v -c=cookie url

  * -c : 指定 cookie

    
    
    whatweb -l

  * -l : 列出所有的插件列表

    
    
    whatweb -info-plugins="plugigns"

  * -info-plugins : 查看插件的具体信息

