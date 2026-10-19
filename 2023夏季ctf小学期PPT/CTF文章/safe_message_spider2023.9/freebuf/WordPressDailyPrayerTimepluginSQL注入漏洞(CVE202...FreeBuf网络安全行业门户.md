## 1.项目介绍

    
    
    WordPress和WordPress plugin都是WordPress基金会的产品。WordPress是一套使用PHP语言开发的博客平台。该平台支持在PHP和MySQL的服务器上架设个人博客网站。WordPress plugin是一个应用插件。
    
    WordPress最近爆出的漏洞都是大多数都是由于WordPress Plugin中应用插件出现的问题，在Daily Prayer Time< 2022.03.01版本中存在未授权SQL注入漏洞，在2022.03.01版本中开发者将该漏洞修复。

![](https://image.3001.net/images/20220707/1657180894_62c692de0a13851809886.png!small)

![](https://image.3001.net/images/20220707/1657180968_62c6932891cb08ae82501.png!small)

## 2.代码对比

通过代码对比工具发现在新版本中调用了Wordpress中的`sanitize_text_field()`过滤函数对传入的内容进行过滤。

![](https://image.3001.net/images/20220707/1657180994_62c693425a282d6df4b59.png!small)![](https://image.3001.net/images/20220707/1657181021_62c6935d45ebec062f4d5.png!small)

## 3.代码分析

首先我们将存在漏洞的插件进行安装

![](https://image.3001.net/images/20220707/1657181100_62c693ac7cabd34ff229d.png!small)

安装成功后该插件会在下方显示

![](https://image.3001.net/images/20220707/1657181190_62c694063973cf239ebcd.png!small)我们随便抓一个安装插件包就可以发现，通过WordPress安装插件功能发现在安装插件时会注册以插件名为后缀的ajax请求接口，以便后续插件功能的调用。  

![](https://image.3001.net/images/20220707/1657181271_62c694579627fbdde4b60.png!small)这里在数组中定义了很多请求参数，
上述的 `install-plugin`就在其中。

![](https://image.3001.net/images/20220707/1657181326_62c6948e1058e19b7d7eb.png!small)![](https://image.3001.net/images/20220707/1657181335_62c6949726aa6c947420f.png!small)如果传入的action值在数组中，就对下面的Ajax请求接口进行注册。  

![](https://image.3001.net/images/20220707/1657181375_62c694bf9c208a8aced2a.png!small)如上通过代码对比我们发现`get_monthly_timetable()`函数存在可控参数`month`、`display`，我们全局搜索`get_monthly_timetable`函数，发现该函数被成功注册为ajax请求，也就意味着我们可以直接通过action调用该函数，而且在未授权的还是在未授权的状态下。  

![](https://image.3001.net/images/20220707/1657181419_62c694eb36049ecc8441f.png!small)在`dpt.js`中也可以明显看到请求的具体参数  

![](https://image.3001.net/images/20220707/1657181475_62c695231d2f7aae134dd.png!small)继续分析其调用链，在`get_monthly_timetable()`函数中将参数`month`传入实例化对象`NEW
MonthlyTimeTable()`中并触发构造方法从而进行内存空间分配，跟进`MonthlyTimeTable`。  

![](https://image.3001.net/images/20220707/1657181557_62c69575381387a40f8ee.png!small)将`month`传入`getMonthlyCalendar`()`函数中，继续跟进。

![](https://image.3001.net/images/20220707/1657181686_62c695f66e24fac8258cf.png!small)在`getMonthlyCalendar()`函数最上面将`DatabaseConnection`类实例化，调用类中的`getPrayerTimeForMonth()`函数，其实到这步已经要将传入的SQL语句去执行了。继续跟进  

![](https://image.3001.net/images/20220707/1657181721_62c6961931e59cd4d55d7.png!small)`getPrayerTimeForMonth()`中将传入的`$monthNumber`也就是`month`拼接到SQL语句中，最后传入`get_results()`函数中进行简单SQL语句检测，但并不影响后续的执行。继续跟进  

![](https://image.3001.net/images/20220707/1657181760_62c6964022bac0a84a8eb.png!small)在`get_results()`函数中调用`check_safe_collation()`函数进行SQL语句检测，但只是针对功能性以及编码进行检测，并不影响传入SQL语句的执行。  

![](https://image.3001.net/images/20220707/1657181799_62c69667f2b61bc59ce84.png!small)![](https://image.3001.net/images/20220707/1657181816_62c69678cd93dc146f3a4.png!small)完整的调用链如下：  

![](https://image.3001.net/images/20220707/1657181832_62c69688d23571e360f6f.png!small)

## 4.复现

拼接的参数直接带到数据库中执行

![](https://image.3001.net/images/20220707/1657181893_62c696c5227d38af54394.png!small)![](https://image.3001.net/images/20220707/1657181919_62c696df235f4d7e5bf1c.png!small)

## 5.总结  

    
    
    本次针对代码层面对漏洞进行分析，在WordPress中很多组件其实都存在类似的问题，发现问题的方法也是相同的,在文章中就不过多赘述，本文章环境以及组件有需要可添加文后gzh。如果有对代码审计感兴趣的小伙伴也可以关注作者公众号（不懂代码的匹夫），该gzh只发布PHP、Java代码审计的相关内容，期待志同道合的小伙伴一起学习进步！  
    

