## 前言

> 2018年8月22日，Apache Strust2发布最新安全公告，Apache
> Struts2存在远程代码执行的高危漏洞（S2-057/CVE-2018-11776），该漏洞由Semmle Security Research
> team的安全研究员Man YueMo发现。

该漏洞是由于在Struts2开发框架中使用namespace功能定义XML配置时，namespace值未被设置且在上层动作配置（Action
Configuration）中未设置或用通配符namespace，可能导致远程代码执行。同理，url标签未设置value和action值且上层动作未设置或用通配符namespace时也可能导致远程代码执行，经过笔者自建环境成功复现漏洞且可以执行命令回显，文末有你们想要的
!

## 漏洞利用

笔者搭的环境分别是Strust2 2.3.20版本和 Strust2 2.3.34版本，漏洞利用大致分为三种方式：数值计算、弹出计算器、 命令回显。

### 2.1 数值计算

数值计算相对最简单，在URL上指定 %{100+200} 就可以发生跳转，得到计算的结果

  
![image.png](https://image.3001.net/images/20180830/1535612156_5b8794fc21a10.png!small)

### 2.2 弹出计算器

2.3.20版本的POC如下：

![image.png](https://image.3001.net/images/20180830/1535612172_5b87950c3a9df.png!small)![image.png](https://image.3001.net/images/20180830/1535612180_5b8795142ef5a.png!small)

### 2.3.3 4版本参考的POC如下：  

  
![image.png](https://image.3001.net/images/20180830/1535612191_5b87951fe1cbe.png!small)![image.png](https://image.3001.net/images/20180830/1535612198_5b8795261f74c.png!small)

### 2.3 命令回显

两个版本都是利用com.opensymphony.xwork2.dispatcher.HttpServletResponse对象去打印命令执行后的回显数据

2.3.20版本的POC如下：

![image.png](https://image.3001.net/images/20180830/1535612219_5b87953b0ff70.png!small)2.3.34版本的POC如下：  

![image.png](https://image.3001.net/images/20180830/1535612229_5b87954570ade.png!small)攻击后效果如下图  

![image.png](https://image.3001.net/images/20180830/1535612240_5b8795505cc3f.png!small)

## 漏洞分析

在分析漏洞之前，需要配置struts.xml文件，这个文件就是struts2的核心配置文件，大多数的时候增减配置都需要操控这里；

![image.png](https://image.3001.net/images/20180830/1535612370_5b8795d212275.png!small)

总共两处需要注意，第一处一定要配置struts.mapper.alwaysSelectFullNamespace = true
，否则不能触发漏洞，这个配置的目的是设定是否一直在最后一个斜线之前的任何位置选定NameSpace；第二处result标签返回的类型选择 “
redirectAction 或 chain“ , 只有这两个配置选项的值是可以将action转发或者重定向；关于type具体可以参考下图  

![image.png](https://image.3001.net/images/20180830/1535612393_5b8795e9b9769.png!small)  

说完了配置，开始动态分析。漏洞位于

struts2-core.jar!/org/apache/struts2/dispatcher/ServletActionRedirectResult.class

![image.png](https://image.3001.net/images/20180830/1535612406_5b8795f69a5f6.png!small)this.namespace这个成员的值来自于getNamespace()方法，再通过getUriFromActionMapping()返回URI字符串；  

![image.png](https://image.3001.net/images/20180830/1535612417_5b879601da537.png!small)通过getUriFromActionMapping获取的值赋给了tmpLocation变量，接着表达式进入setLocation方法  

![image.png](https://image.3001.net/images/20180830/1535612430_5b87960e5ac9e.png!small)

再通过super.execute方法调用了ServletActionResult
，而在execute方法体内跟进了conditionalParse方法，在这个方法内调用了ONGL执行的关键方法translateVariables。  

![image.png](https://image.3001.net/images/20180830/1535612442_5b87961ae1383.png!small)获得的param值传入到translateVariables()方法内，最终在OnglTextPaser里导致了OGNL表达式执行。  

![image.png](https://image.3001.net/images/20180830/1535612453_5b879625b3c2d.png!small)  

![image.png](https://image.3001.net/images/20180830/1535612459_5b87962bf1622.png!small)再弹出计算器后获得lastFinalLocation的值为当前执行后的句柄，这个值作为响应跳转的action地址，也就是在浏览器中弹出计算器后在地址栏中出现的URI  

![image.png](https://image.3001.net/images/20180830/1535612473_5b879639b02f7.png!small)到这里弹出计算器的分析到此为止，接下来看下基于命令执行回显结果的分析，基本上流程和上述一样，唯一不同之处lastFinalLocation返回的值是NULL，这也就引发出提交后没有做302的跳转，依旧是当前的action，并且返回的值是200  

![image.png](https://image.3001.net/images/20180830/1535612488_5b879648d266b.png!small)![image.png](https://image.3001.net/images/20180830/1535612494_5b87964e4d879.png!small)知道了原理后小同事用python实现了exp检测脚本，此脚本用途仅供学习研究；  

![image.png](https://image.3001.net/images/20180830/1535612505_5b879659675af.png!small)

## 防御措施

> 1\. 将框架版本升级到官方最新版本；
>
> 2\. 对于Web应用来说，尽量保证代码的安全性；
>
> 3\.
> 对于IDS规则层面来说，数值计算和弹计算器返回的状态码都是302，并且Location跳转字段含有特征句柄字符串；如果是命令回显返回的200状态码，且有命令结果输出；

## 小结

文章中提及的python EXP下载地址： <https://github.com/Ivan1ee> ；

## 参考链接

<https://cwiki.apache.org/confluence/display/WW/S2-057>

<https://lgtm.com/blog/apache_struts_CVE-2018-11776>

<https://blog.csdn.net/madison__/article/details/55671426>

