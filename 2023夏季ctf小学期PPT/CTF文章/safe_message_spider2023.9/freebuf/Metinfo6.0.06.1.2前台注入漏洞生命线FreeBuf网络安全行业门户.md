***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：Mochazz，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

大家好，我是 **红日安全-七月火** ，这篇文章是以往挖掘的 **Metinfo** 漏洞，鉴于官方已修复，遂将分析文章放出。

## 前言

 **这个前台注入漏洞存在已久，从MetInfo发布的6.0版本就存在，且后来官方的修复代码，也可以直接绕过。笔者于7月份提交了当时最新 MetInfo
6.1.0版本SQL注入漏洞，该漏洞直到6.1.3版本才被修复。如下漏洞分析，权当思路分享。**

![1](https://image.3001.net/images/20181108/1541661264_5be3e250390c7.png!small)

## 漏洞分析

2018-1-29， **MetInfo** 官方重写后台及前台代码，并发布了 **MetInfo6.0。**
然而这一新版代码，却存在一个严重的前台SQL注入漏洞，我们来看一下具体详情。

首先漏洞存在于 **app\system\message\web\message.class.php** 文件中，变量
**{$_M[form][id]}** 直接拼接在 **SQL** 语句中，且验证码检测函数是在 **SQL**
语句查询之后，这也就造成了我们可以无视验证码检测函数，进行 **SQL** 注入。具体问题函数代码如下：

![2](https://image.3001.net/images/20181108/1541661279_5be3e25f3061f.png!small)

那么实际上，开发者是有考虑到 **SQL** 注入问题，并写了 **sqlinsert** 来检测 **SQL** 注入攻击的，甚至还对
**{$_M[form][id]}** 进行了 **is_numeric** 判断处理，但是为什么最终还是存在 **SQL** 注入呢？下面我们具体来看看
**{$_M[form][id]}** 变量的获取过程。

想要触发这个 **SQL** 注入漏洞，我们可以通过前台的 **在线留言** 和 **在线反馈** 两个功能来触发。我们这里先分析 **在线留言**
处的程序逻辑。我们填写留言处的表单，并在最下方添加上 **id** 字段，其值对应我们的攻击 **payload**
，具体如下：（为了避免图片太长，我把一些参数的值给略去）

![3](https://image.3001.net/images/20181108/1541661288_5be3e268526da.png!small)

然后我们在 **message\index.php** 文件中打下断点，会发现在
**app\system\include\class\common.class.php** 的构造方法中，加载了表单，具体的调用链即代码如下：

![4](https://image.3001.net/images/20181108/1541661296_5be3e270bbae2.png!small)

此时 **this** 对象指的是 **web** 类，我们继续跟进 **web** 类的 **load_form** 方法。

![5](https://image.3001.net/images/20181108/1541661305_5be3e2793897c.png!small)

我们会发现 **common** 基类的 **load_form** 方法将 **GET** 、 **POST** 、 **COOKIE**
获取的所有数据存放在 **$_M['form']** 中，数据仅用 **daddslashes** 函数处理。而 **web** 类的
**load_form** 方法重写了 **common** 类的 **load_form** 方法，对 **$_M['form']** 中的所有数据进行了
**sqlinsert** 处理，并且在后面判断 **$_M['form']['id']**
是否为数字，如果不是数字就直接设置为空字符串。这些过滤函数具体代码如下：

![6](https://image.3001.net/images/20181108/1541661316_5be3e284c5258.png!small)

![7](https://image.3001.net/images/20181108/1541661321_5be3e289a2399.png!small)

可以看到 **sqlinsert** 函数对 **sleep** 关键字进行了处理，但是我们还是可以使用 **MYSQL** 中的
**benchmark**
函数轻松绕过（这两个函数都能利用在时间盲注中，具体可以参考：<https://xz.aliyun.com/t/2288>)。但是我们的
**payload** 却绕不过 **is_numeric** 函数，所以此时的 **$_M['form']['id']**
会被设置成空字符串。那为什么还存在 **SQL** 攻击呢？我们接着看程序逻辑。

在跟进程序的过程中，我们会发现在执行完 **load::sys_class('upfile', 'new')** 代码后，
**$_M['form']['id']** 的值又变成了我们传入的 **payload** ，这说明这里面一定是又重新进行了表单赋值。

![8](https://image.3001.net/images/20181108/1541661332_5be3e29482fc6.png!small)

果不其然，程序中加载的 **upfile** 类又重新载入了 **$_M['form']** 的值，而且并没有进行除了基类中 **daddslashes**
方法以外的消毒处理，这也是造成 **SQL** 注入的原因。

![9](https://image.3001.net/images/20181108/1541661342_5be3e29ebc3d7.png!small)

我们可以根据上面的漏洞原理，轻松的写出攻击脚本：

![10](https://image.3001.net/images/20181108/1541661355_5be3e2abdd0d0.png!small)

接着，我们再来对比一下5月份的修复代码，此时 **MetInfo** 官方并没有更新版本号，而是偷偷修复了代码，修复代码如下右图：

![11](https://image.3001.net/images/20181108/1541661360_5be3e2b09ec92.png!small)

可以清晰的看见 **daddslashes** 方法开始对每个参数进行 **sqlinsert**
处理。而上面我们说过，这个消毒函数是可以绕过的，所以我们依然可以进行 **SQL** 注入。

虽然可以进行盲注，但是还是太耗费时间了，我们是否有办法将其转换成布尔盲注呢？答案是可以的，接下来我们就来看看，如何将这一处时间盲注变成布尔盲注。

在 **app\system\message\web\message.class.php** 文件中，我们会发现如果SQL语句查询结果中的
**value** 字段非空，则会进行验证码的检测，否则会直接返回 **反馈已经被关闭** 。

![12](https://image.3001.net/images/20181108/1541661370_5be3e2ba51dc5.png!small)

![13](https://image.3001.net/images/20181108/1541661377_5be3e2c10fc0b.png!small)

这样子，我们就可以根据不同的返回结果，进行布尔盲注。现在我们来看一下如何找到满足查询结果中的 **value** 字段非空的 **columnid**
，直接在 **MYSQL** 中做如下查询：

![14](https://image.3001.net/images/20181108/1541661383_5be3e2c769de6.png!small)

![15](https://image.3001.net/images/20181108/1541661390_5be3e2ce6718b.png!small)

这样子我们就找到了两个可用的 **columnid** 最终我们同样可以写出攻击脚本，如下：

![16](https://image.3001.net/images/20181108/1541661407_5be3e2df14c28.png!small)

我们再来看另一处注入点，前面我们分析的是 **在线留言** 处的 **SQL** 注入问题，这次我们要分析 **在线反馈** 处的 **SQL**
注入，漏洞的成因都是类似的。不过在利用这个漏洞时，我们需要经过 **feedback** 类 **check_field** 方法的检测。

![17](https://image.3001.net/images/20181108/1541661409_5be3e2e104fae.png!small)

这里实际上可用的 **id** 有两个，如下：

![18](https://image.3001.net/images/20181108/1541661415_5be3e2e7eb67d.png!small)

例如这里我想利用 **id=71** ，那么需要构造如下数据包，才会进入漏洞触发处。

![19](https://image.3001.net/images/20181108/1541661423_5be3e2efa2c2e.png!small)

现在绕过了 **check_field** 方法的检测，我们就顺利来到了触发 **SQL** 注入漏洞的 **feedback** 累的 **add**
方法，其位置在 **app\system\feedback\web\feedback.class.php** ，具体代码如下：

![20](https://image.3001.net/images/20181108/1541661436_5be3e2fc3b7e1.png!small)

我们会发现这次的验证码校验，位置在注入点前面，所以利用起来比较麻烦。这里我们可以使用爆破验证码结合时间盲注的方式进行攻击，用以下程序生成全排列验证码字典：

    
    
    from itertools import product
    rand_chrs="A2B3C4D5E6F7G8H9iJKLMNPQRSTUVWXYZ"
    with open("codes.txt",'w') as f:
        for code in product(rand_chrs,rand_chrs,rand_chrs,rand_chrs):
            code = ''.join(list(code))
            print(code)
            f.write(code+'\n')
    

![21](https://image.3001.net/images/20181108/1541661441_5be3e3014caaa.png!small)

但是这样的攻击成本还是太高了，如果大家会机器学习，可以加入相关算法来自动识别验证码。

最后我们来看一下 **MetInfo** **6.1.3** 最新版的修复情况如何，具体情况如下 **DIFF** 图：

![22](https://image.3001.net/images/20181108/1541661447_5be3e307b6d5d.png!small)

## 结语

文章中提到的这个漏洞点，实际上也可以从其他入口点进行触发，之前也已经有师傅放出分析文章，漏洞的成因都是一样的，具体可以参阅文末的相关文章，这里不再赘述。本文分析到此结束，如有不当还望各位斧正。另外，我们团队正在招收代码审计成员，如果您在这方面有丰富的经验，欢迎加入我们。（可以发邮件至：379032449@qq.com）。对代码审计感兴趣的朋友，也可以关注我们的代码审计项目：[
**PHP-Audit-Labs**](https://github.com/hongriSec/PHP-Audit-Labs)

## 相关文章

[Metinfo 6.1.2 SQL注入](https://bbs.ichunqiu.com/thread-46687-1-1.html)

[[代码审计]METINFO 6.1.2 SQL注入](http://www.lsafe.org/?p=437)

 ***本文作者：Mochazz，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

