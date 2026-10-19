## 靶标介绍：

多语言药房管理系统 (MPMS) 是用 PHP 和 MySQL 开发的,
该软件的主要目的是在药房和客户之间提供一套接口，客户是该软件的主要用户。该软件有助于为药房业务创建一个综合数据库，并根据到期、产品等各种参数提供各种报告。
该CMS中php_action/editProductImage.php存在任意文件上传漏洞，进而导致任意代码执行。

## 漏洞复现过程

1.打开靶场，并进行访问

![1688966613_64ab95d5e6adbf65fb2b5.png!small](https://image.3001.net/images/20230710/1688966613_64ab95d5e6adbf65fb2b5.png!small)

2.使用默认账号密码：[
_mayuri.infospace@gmail.com_](mailto:mayuri.infospace@gmail.com)/mayurik登录

![1688966628_64ab95e43551eb8214d2b.png!small](https://image.3001.net/images/20230710/1688966628_64ab95e43551eb8214d2b.png!small)

3.找到上传点，编辑上传PHP一句话木马

![1688966698_64ab962a355c0b40bd6b7.png!small](https://image.3001.net/images/20230710/1688966698_64ab962a355c0b40bd6b7.png!small)

![1688966733_64ab964df238128903ec6.png!small](https://image.3001.net/images/20230710/1688966733_64ab964df238128903ec6.png!small)

![1688966784_64ab9680aec35a67b5cd5.png!small](https://image.3001.net/images/20230710/1688966784_64ab9680aec35a67b5cd5.png!small)

4.使用burp抓包工具进行抓包修改png后缀为php后缀![1688966821_64ab96a59e2d8fcf9c4ba.png!small](https://image.3001.net/images/20230710/1688966821_64ab96a59e2d8fcf9c4ba.png!small)![1688966834_64ab96b2135514a051f5b.png!small](https://image.3001.net/images/20230710/1688966834_64ab96b2135514a051f5b.png!small)

5.右击图片，右键在标签中打开图片，查看木马路径。![1688966843_64ab96bbc6a5246ce5668.png!small](https://image.3001.net/images/20230710/1688966843_64ab96bbc6a5246ce5668.png!small)

![1688966854_64ab96c696ba07f36b16b.png!small](https://image.3001.net/images/20230710/1688966854_64ab96c696ba07f36b16b.png!small)

6.复制路径http://eci-2zeidvpxyny5m513h4w4.cloudeci1.ichunqiu.com/assets/myimages/3.php使用中国蚁剑工具连接

![1688966862_64ab96ce32e7692e81342.png!small](https://image.3001.net/images/20230710/1688966862_64ab96ce32e7692e81342.png!small)![1688966878_64ab96de613210bd89524.png!small](https://image.3001.net/images/20230710/1688966878_64ab96de613210bd89524.png!small)

![1688966891_64ab96ebc43fb642cd71e.png!small](https://image.3001.net/images/20230710/1688966891_64ab96ebc43fb642cd71e.png!small)

成功找到flag

![1688966898_64ab96f2357aefd257285.png!small](https://image.3001.net/images/20230710/1688966898_64ab96f2357aefd257285.png!small)

