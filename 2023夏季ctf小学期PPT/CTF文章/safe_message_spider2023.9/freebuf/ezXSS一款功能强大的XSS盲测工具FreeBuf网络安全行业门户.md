**今天给大家介绍的是一款名叫ezXSS的漏洞测试工具，该工具可以轻松地帮助渗透测试人员完成Blind XSS漏洞的扫描任务。**  

![1.png](https://image.3001.net/images/20180314/15210167116533.png!small)  

## 功能介绍

ezXSS当前所支持的全部功能如下：

> 1\. 提供了易于使用的仪表盘（Dashboard），用户可查看、分享和搜索漏洞报告；
>
> 2\. Payload生成器；
>
> 3\. 实时电子邮件警报；
>
> 4\. 自定义JavaScript以进行额外测试；
>
> 5\. 跟其他ezXSS用户分享漏洞报告；
>
> 6\. 可直接在系统中管理和查看报告；
>
> 7\. 利用额外的保护机制（2FA）保护系统账号的安全；

ezXSS可从存在安全漏洞的页面中收集下列信息：

> 1\. 页面中的URL；
>
> 2\. IP地址；
>
> 3\. 任意页面referer；
>
> 4\. User-Agent；
>
> 5\. 所有Non-HTTP-Only Cookie；
>
> 6\. 页面的完整HTML DOM结构；
>
> 7\. 页面源；
>
> 8\. 执行时间

### 工具要求

> 1\. PHP5.5以及更高版本；
>
> 2\. 一个可用域名（越短越好）；
>
> 3\. 如果你需要测试HTTPS网站，请准备SSL证书（可从Cloudflare或Let’s Encrypt获取免费的SSL证书）；

### 工具下载

ezXSS下载地址：【[GitHub传送门](https://github.com/ssl/ezXSS)】

## 工具安装  

ezXSS的安装也非常简单，大致步骤如下：

> 1\. 从本项目的GitHub库中下载“files”，然后把里面所有的文件放到root目录中；
>
> 2\. 创建一个空的数据库，然后在'/manage/src/Database.php'中填写你的数据库信息；
>
> 3\. 在浏览器中进入/manage/install，设置一个密码和电子邮箱地址；
>
> 4\. 安装完成！是不是很简单？

## 工具运行截图

登录界面：

![2.png](https://image.3001.net/images/20180314/15210167647017.png!small)  

工具仪表盘：

![3.png](https://image.3001.net/images/20180314/15210167755735.png!small)  

设置界面：

![4.png](https://image.3001.net/images/20180314/15210167848234.png!small)  

Payload生成界面：

![5.png](https://image.3001.net/images/20180314/15210167956760.png!small)  

报告查看界面：

![6.png](https://image.3001.net/images/20180314/15210168078159.png!small)  

***
参考来源：[ezXSS](https://github.com/ssl/ezXSS)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

