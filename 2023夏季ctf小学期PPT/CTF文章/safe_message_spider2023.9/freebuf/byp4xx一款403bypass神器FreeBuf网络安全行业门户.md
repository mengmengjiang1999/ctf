## 一、介绍

当渗透一个站点，首先要做的工作就是扫路径，但是扫出来看到满屏的403就很烦，没错，dirsearch说的就是你。但是当200的路径没有任何突破时我们就应该考虑一下403bypass的问题了。

众所周知，HTTP请求方式有OPTIONS, TRACE, GET, HEAD,
POST，PUT,CONNECT等多种，最常用的是GET和POST。但是当GET和POST碰见站点403时我们能不能尝试其他的请求方式呢？答案是肯定的。这里就给出403bypass测试神器：byp4xx。作者为：lobuhi

GitHub地址：

    
    
    https://github.com/lobuhi/byp4xx

它支持的绕过方法包括以下几种

    
    
    HTTP Methods...        //请求方式
    GET request: 
    POST request: 
    HEAD request: 
    OPTIONS request: 
    PUT request: 
    TRACE request: 
    TRACK request: 
    CONNECT request: 
    PATCH request: 
    
    #Bugbountytips 403 bypass methods...
    %2e payload: 
    /. payload: 
    ? payload: 
    ?? payload: 
    // payload: 
    /./ payload: 
    / payload: 
    /.randomstring payload: 
    ..;/ payload: 
    
    HEADERS...
    Referer payload:                     //referer
    X-Custom-IP-Authorization payload: 
    X-Custom-IP-Authorization+..;/ payload: 
    X-Original-URL payload: 
    X-Rewrite-URL payload: 
    X-Originating-IP payload: 
    X-Forwarded-For payload: 
    X-Remote-IP payload: 
    X-Client-IP payload: 
    X-Host payload: 
    X-Forwarded-Host payload: 

## 二、安装和使用

安装

    
    
    git clone https://github.com/lobuhi/byp4xx.git
    
    cd byp4xx
    
    chmod u+x byp4xx.sh

使用介绍

    
    
    ./byp4xx.sh [OPTIONS] http(s)://url/path

使用示例

    
    
    ./byp4xx.sh https://www.google.es/test

特色

多个HTTP动词/方法  
#bugbountytips中提到的多种方法  
多个标头：引荐来源，X-Custom-IP-Authorization ...  
允许重定向  
如果响应为200，则返回整个curl命令

此工具搭配burpsuite食用更佳。

