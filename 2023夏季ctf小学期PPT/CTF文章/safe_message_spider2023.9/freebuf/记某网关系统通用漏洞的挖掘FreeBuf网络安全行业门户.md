## **前言**

本篇文章分享一下通用漏洞挖掘的过程，想要获得通用漏洞证书，首先要求是中危及中危以上的通用型漏洞且所属公司的注册资本大于5000万。挖掘一个漏洞其实不难，个人觉得是目标公司资产的搜集。访问CNVD平台发现某网关系统被师傅提交过任意文件读取漏洞，然后搜索目标再来挖掘一下说不定能捡个漏。

##  **未授权访问查看管理员账号密码**

目标是个网关系统，使用弱口令进入系统后，开始测试功能点，在系统用户处测试抓包：

![](https://image.3001.net/images/20220427/1651042890_6268ea4a6d56d605b41ff.png!small)

删除cookie后发现仍然可以访问管理员相关信息包括密码、手机号码等：![](https://image.3001.net/images/20220427/1651041719_6268e5b79a86beb0c98b1.png!small)浏览器直接访问，然后查看密码即可：  
![](https://image.3001.net/images/20220427/1651041812_6268e614a4804bd365297.png!small)

##  **任意文件下载**

后台存在日志查询功能点， 查看服务器日志时有下载功能：  
![](https://image.3001.net/images/20220427/1651041847_6268e6372406cd077b3b7.png!small)

点击下载并抓包：  
![](https://image.3001.net/images/20220427/1651041932_6268e68c70c381591d094.png!small)  
将参数fileName的值删除重放后报错泄漏了物理路径，其中fopen(../../../log/)猜测是downFile.php文件中的源代码：

![](https://image.3001.net/images/20220427/1651043197_6268eb7d48646887198fe.png!small)

在参数fileName后拼接：../../../VAG/pag/web/html/serverLog/downFile.php，查看downFile.php源码。定义了$file_dir的值为../../../log/，这里用户传入的值$file_name没有进行任何过滤，就直接拼接在变量$file_dir后面然后使用fopen函数打开拼接后的文件。

这里使用../可以直接下载任意文件：  
![](https://image.3001.net/images/20220427/1651042013_6268e6dd4f5d4958fdda6.png!small)

##  **任意文件读取**

在测试服务器日志时，服务器返回的代码中含有参数showFile.php?fileName=:![](https://image.3001.net/images/20220427/1651042049_6268e7018334437434d66.png!small)这里构造数据包/serverLog/showFile.php?fileName=
可以直接查看目标源文件：  
![](https://image.3001.net/images/20220427/1651042068_6268e714a6640babade8d.png!small)

在测试过程中发现存在未授权访问，在浏览器中可以直接读取文件源代码：  
![](https://image.3001.net/images/20220427/1651042091_6268e72b918195204c7fe.png!small)

##  **未授权创建存储型XSS**

发现在资源管理功能点存在未授权，可以创建存储型XSS，插入XSS平台地址：![](https://image.3001.net/images/20220427/1651042136_6268e75857d7b7eb55010.png!small)

当管理员访问资源管理功能点时：

![](https://image.3001.net/images/20220427/1651042185_6268e78990e2925ea1217.png!small)XSS平台成功获取到系统管理员cookie:

![](https://image.3001.net/images/20220427/1651042211_6268e7a3e5d1eac7a9077.png!small)

##  **任意用户密码修改**

在后台管理测试修改密码功能点，这里原始密码随意输入，点击保存并抓包。![](https://image.3001.net/images/20220427/1651042278_6268e7e66c5e7c32f9e0f.png!small)  
发现在/data/checkIsExist.php数据包中会对当前账户的原始密码进行校验，原始密码错误返回1，密码正确返回0。![](https://image.3001.net/images/20220427/1651042296_6268e7f80df2506541de1.png!small)

这里将服务器返回的数据包修改为0，进入下一个数据包，这里是对密码进行修改。

![](https://image.3001.net/images/20220427/1651042322_6268e8129d60579714fa0.png!small)

释放数据包后显示密码修改成功：![](https://image.3001.net/images/20220427/1651042343_6268e827cc1e69c2fab3b.png!small)

使用修改之后的密码去尝试登录，可以成功登录到管理后台。

此时想到这个系统存在很多未授权操作，如果修改密码功能点也存在未授权，那么就可以直接重置系统任意用户的密码。

这里浏览器直接访问修改密码的URL，发现用户名为空：![](https://image.3001.net/images/20220427/1651042367_6268e83fa157d4812bc71.png!small)

这里按照之前的流程先走一遍，点击保存并抓包，发现name参数的值为空，这里修改为admin：

![](https://image.3001.net/images/20220427/1651042399_6268e85f44d44ba4e0aa9.png!small)

在修改服务器返回的数据包为0之后，再将参数name的值修改为admin：![](https://image.3001.net/images/20220427/1651042427_6268e87bdd9322a3dcecd.png!small)释放数据包后，显示修改成功：  
![](https://image.3001.net/images/20220427/1651042458_6268e89aaeaf0676beb80.png!small)

使用修改之后的密码去登录，成功登录到管理后台。

后来测试发现，不需要原始密码的验证也是可以的，直接使用修改密码的数据包来进行修改密码，即可将密码重置：  
![](https://image.3001.net/images/20220427/1651042480_6268e8b0b865e8170b39b.png!small)

##  **总结**

将漏洞提交CNVD平台后，存储型XSS被驳回了，但是因为是未授权创建存储型XSS，再次提交最终审核通过了。最后觉得挖掘漏洞的话还是要细心，并且资产搜集非常重要！

