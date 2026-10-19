***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 *** 本文作者：BlackWater，本文属FreeBuf原创奖励计划，未经许可禁止转载。**  

## 一、背景介绍

**HongCMS是一个轻量级的中英文企业网站系统，访问速度极快，使用简单，程序代码简洁严谨，功能强大，完全免费开源，可用于建设各种类型的中英文网站，同时它是一个小型开发框架。**

## 二、漏洞描述

程序在后台进行清空数据库操作时对传入的数据库名过滤不严格，可插入和执行恶意sql语句。

## 三、影响版本

Hongcms < 3.0.0

## 四、漏洞细节

首先，我们登录到网站后台管理定位到系统--->数据库维护。

![f1.png](https://image.3001.net/images/20180721/15321570245786.png)系统默认情况下只允许我们对sessions和vvc数据表进行清空操作，我们随机选择一个，此处我使用vvc表来进行分析，随后我们点击清空按钮并结合phpstorm对执行流程进行动态调试。为了方便大家能清楚地看清执行过程，笔者已经在关键的函数位置设置了断点。

首先程序在APP.php第170行使用call_user_func函数对接受的参数进行动态函数回调：

![f2.png](https://image.3001.net/images/20180721/15321570727341.png)跟进operate：

![f3.png](https://image.3001.net/images/20180721/15321571013096.png)将数据表名称传递给ForceStringFrom函数，继续跟进ForceStringFrom：

    
    
    ForceStringFrom通过$_GET[$VariableName]获取我们传递的tablename参数值并传递给了ForceString,跟进ForceString

![f5.png](https://image.3001.net/images/20180721/15321571641210.png)

ForceString判断Invalue是否为字符串之后随即将值传递给给EscapeSql，函数进行安全过滤，继续跟进。

![f6.png](https://image.3001.net/images/20180721/15321572459884.png)

首先函数判断了gpc是否开启，如果开启则使用 _stripslashes_
进行过滤，否则将使用htmlspecialchars并对\0和空格字符进行了替换，随后判断mysql_real_escape_string或mysql_escape_string函数是否存在，并调用相应的函数进行编码，否则使用addslashes。随后程序进入switch语句进行动作匹配，根据不同的action参数值进行相应的操作。

![f7.png](https://image.3001.net/images/20180721/15321573065497.png)

我们定位到emptytable，程序将tablename值传入了EmptyTable函数。

![f8.png](https://image.3001.net/images/20180721/15321573282388.png)

跟进EmptyTable。

![f9.png](https://image.3001.net/images/20180721/15321573539055.png)

在这里我们看到定义了要执行的sql语句，并将其传入了exe函数，跟进exe。

![f10.png](https://image.3001.net/images/20180721/15321574041593.png!small)

Exe接收了传递的sql语句后随即进行了执行，并返回执行结果。

![f11.png](https://image.3001.net/images/20180721/15321574286501.png)

最后调用PrintResults将结果打印到后台显示，我们可以看到在整个执行过程中程序仅仅使用了内置的函数和简单的替换函数对传入的参数值进行了安全处理，而这些函数是可以被绕过的。

## 五、漏洞复现

经过上一节的分析，下面我们就要着手构造我们的sql语句，同样我们定位到数据表操作的页面点击要清空的数据表，随后我们用burp截断来修改我们的数据表名称来注入我们构造的sql语句。

![f12.png](https://image.3001.net/images/20180721/15321574736793.png)此处我们将数据表名称改为`
where vvcid=1 orupdatexml(2,concat(0x7e,(version())),0) or `

同样我们来跟踪我们传入的参数值：

![f13.png](https://image.3001.net/images/20180721/15321575098040.png!small)可以看到我们成功的绕过了程序的安全防护并正确的进行了返回，我们继续往下走看看最终的要执行的sql语句，是否是我们想要的结果。

![f14.png](https://image.3001.net/images/20180721/15321575363906.png!small)看到执行的sql语句和我们预想的一样，我们返回后台页面看看执行的结果：

![f15.png](https://image.3001.net/images/20180721/15321575612702.png)可以看到当前使用的数据库版本已经被查询了出来。

## 六、修补措施

系统已停止维护，可以考虑自行安装WAF进行防护。

 *** 本文作者： BlackWater，本文属FreeBuf原创奖励计划，未经许可禁止转载。**  

