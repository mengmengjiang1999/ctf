***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**2018年9月1日，阿里云态势感知发布预警，近日利用ECShop全系列版本的远程代码执行漏洞进行批量化攻击量呈上升趋势。该漏洞利用简单且危害较大，黑客可通过WEB攻击直接获得服务器权限。**

##  漏洞原理  

该漏洞产生的根本原因在于ECShop系统的user.php文件中，display函数的模板变量可控，导致注入，配合注入可达到远程代码执行的效果。使得攻击者无需登录等操作，直接可以获得服务器的权限。

首先从user.php文件入手，代码中可以看到，系统读取HTTP_REFERER传递过来的

内容赋值给$back_act变量。

![1.jpeg](https://image.3001.net/images/20180902/1535852828_5b8b411cd2038.jpeg!small)(/user.php)

接着以$back_act的值为参数，调用assign方法。

![2.png](https://image.3001.net/images/20180902/1535852892_5b8b415c4b705.png!small)
(/user.php)  

assign方法的作用是把可控变量传递给模版函数，紧接着再通过display方法展示

到页面上。接下来跟进display内部的insert_mod方法。

![3.png](https://image.3001.net/images/20180902/1535852966_5b8b41a6ab299.png!small)(/includes/cls_template/php)  

insert_mod方法返回了一个动态函数调用，该函数名和参数均可控，根据攻击者

的利用方法，我们可以得知调用的函数名为insert_ads，接下来跟进这一方法。

![4.png](https://image.3001.net/images/20180902/1535853007_5b8b41cf37f85.png!small)(/includes/lib_insert.php)  

不难发现，$arr['id']和$arr['num']这两个变量，都是外部可控的输入点，在构造攻

击向量的过程中执行的SQL语句如下。

![5.png](https://image.3001.net/images/20180902/1535854804_5b8b48d4398e7.png!small)
(打印$sql变量)  

![6.png](https://image.3001.net/images/20180902/1535854838_5b8b48f6f080d.png!small)(sql语句执行结果)

接着，程序调用了fetch方法，参数由$row['position_style']变量赋值，这一变量同样为外部可控输入点。  

![7.png](https://image.3001.net/images/20180902/1535854906_5b8b493abfc53.png!small)（/includes/lib_insert.php）  

这里fetch函数调用了危险函数，这就是最终触发漏洞的点。但是参数在传递之前

要经过fetch_str方法的处理。

![8.png](https://image.3001.net/images/20180902/1535854999_5b8b499798375.png!small)(/includes/cls_template.php)  

最终输入点依次经过fetch_str、select、get_val，最终传入make_var方法。  

![9.png](https://image.3001.net/images/20180902/1535855061_5b8b49d58802b.png!small)
(/includes/cls_template.php）  

最终传递到eval的字符串为:  

![10.png](https://image.3001.net/images/20180902/1535855118_5b8b4a0e42808.png!small)到此，漏洞原理分析完成，攻击者的恶意代码执行成功。  

## 漏洞攻击利用实例  

阿里云态势感知于2018年8月1日监控到云上首例此漏洞利用。黑客通过HTTP 请求头的Referer字段植入恶意代码如下：  

![11替换.png](https://image.3001.net/images/20180902/1535855228_5b8b4a7cc61b3.png!small)当黑客恶意代码成功被执行后，会尝试访问链接：'<http://uee.me/MrJc>'，具体的payload代码如下所示：  

![12.jpg](https://image.3001.net/images/20180902/1535855281_5b8b4ab1c9952.jpg!small)其中[http-//uee.me/MrJc](http://http-//http//uee.me/MrJc)是一个短连接，其完整的url为：[http-//www.thaihaogo.com/images/201608/4.jpg](http://http-//www.thaihaogo.com/images/201608/4.jpg)。  

此文件下载到成功后会重命名为1.php，实际上4.jpg文件就是一个混淆后的php木马。  

![13.png](https://image.3001.net/images/20180902/1535855343_5b8b4aefd9355.png!small)去除混淆部分，将木马执行逻辑还原如下：  

![14.png](https://image.3001.net/images/20180902/1535855362_5b8b4b0226c69.png!small)该木马中的PHP代码会去下载一个功能齐全的WEB木马，地址为：[http-//i.niupic.com/images/2017/05/26/Lfkavl.gif](http://http-//i.niupic.com/images/2017/05/26/Lfkavl.gif)，该WEB木马的功能详情如下：  

![15.png](https://image.3001.net/images/20180902/1535855377_5b8b4b11ca1ac.png!small)

## 漏洞影响  

阿里云应急中心测试发现，ECShop全系列版本（包括2.x、3.0.x、3.6.x）均存在该远程代码执行漏洞。阿里云态势感知数据研究中心监控的数据显示，该漏洞利用难度低，影响面广，并已经发现有批量入侵迹象，需要存在相关业务的用户及时关注并进行修补。

## 专家建议  

在官方补丁没放出之前，我们建议站长可以修改include/lib_insert.php文件中相关漏洞的代码，将$arr[id]和$arr[num]强制将数据转换成整型，该方法可作为临时修复方案将入侵风险降到最低。需要修改的部分代码如下：  

![16png.png](https://image.3001.net/images/20180902/1535855753_5b8b4c894a8e0.png!small)

(includes/lib_insert.php )

