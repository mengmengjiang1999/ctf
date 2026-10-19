> 本文由东塔网络安全学院学员---张同学 投稿。

## 1 漏洞描述

通达OA是一套使用比较广泛的办公系统。该漏洞因为使用uid作为身份标识，攻击者通过构造恶意请求，可以直接绕过登录验证逻辑，伪装为系统管理员身份登录OA系统。通达OA官方于2020年4月17日发布安全更新。

## 2 影响版本

通达OA < 11.5.200417版本

通达OA 2017版本

## 3 漏洞原理

本次复现为2017版本，则重点分析该版本，但原理都是基本相同的，只不过文件路径不同而已。根据POC的代码分析如下，该漏洞涉及的文件包含以下四个：

/ispirit/login_code.php

/general/login_code_scan.php

/ispirit/login_code_check.php

/general/index.php

首先说明，通达OA源码使用zend5加密，这里推荐一款解密工具:SeayDzend，工具使用也很简单，创建两个目录，一个存放加密文件，另一个用来输出解密结果。

![](https://image.3001.net/images/20201202/1606909829_5fc77f851fe044b6899e4.png!small)

  

  

###  **/ispirit/login_code.php：**

![](https://image.3001.net/images/20201202/1606909838_5fc77f8e05ea6e65a18d0.png!small)

该文件用来获取codeuid参数，如果不存在，则会自动生成一个codeuid，并且将其写入CODE_LOGIN_PC缓存中（通达OA使用了缓存系统Redis，同时也提供了对缓存的使用方法），但是在18行位置将这个参数显示出来，导致用户可以获取这个参数的值，从而可以绕过后面的验证。

###  **/general/login_code_scan.php：**

![](https://image.3001.net/images/20201202/1606909849_5fc77f9976dcb6247e938.png!small)

在这一文件中，用户可以控制输入的关键参数uid，在存在漏洞的通达OA版本中，后台数据库里uid对应的用户是admin管理员账户。并且将该数据存储在CODE_INFO_PC缓存中，因为我们在第一个文件中获取的codeuid存储在CODE_LOGIN_PC中，所以这里在复现时需要指明source变量为pc，这里的username则为admin，而type变量需要指明为confirm，原因在后面会进行解释。

  

###  **/ispirit/login_code_check.php：**

![](https://image.3001.net/images/20201202/1606909863_5fc77fa71cd7f2440c3c4.png!small)

这里使用之前存储的两个缓存中的内容，一个用来获取codeuid，一个用来获取通过post传入的uid等关键信息，这里红框就是为什么前一步需要将type设置为confirm。

![](https://image.3001.net/images/20201202/1606909878_5fc77fb6d8677a955f34f.png!small)

这里是最为关键的位置，代码获取用户可控的参数uid，并依次作为依据直接带入数据库进行查询

![](https://image.3001.net/images/20201202/1606909890_5fc77fc27c79a5aaaef99.png!small)

![](https://image.3001.net/images/20201202/1606909899_5fc77fcb808e0066d9df3.png!small)

随后将查询的信息直接写入session中，通过这一步，session中包含的就是管理员的身份信息。

以上就是该漏洞的原理，V11版本原理类似，可用对照POC中的步骤进行分析复现。

## 4 漏洞复现

### 环境搭建：

下载源码直接安装即可，注意在安装完毕检测端口是否占用；

![](https://image.3001.net/images/20201202/1606909912_5fc77fd8e99b97f6ae826.png!small)

这里使用80端口，成功访问，环境搭建完成：

![](https://image.3001.net/images/20201202/1606909924_5fc77fe4307ad4c3013d7.png!small)

###  **手工抓包复现：**

按照poc中的步骤，首先抓首页的包进行更改，访问/ispirit/login_code.php

通过返回包获取codeuid

![](https://image.3001.net/images/20201202/1606909935_5fc77fef39581d35f4efb.png!small)

而后使用POST方式访问/general/login_code_scan.php

提交相关参数，其中codeuid需要改为上一步中返回的值。

payload：uid=1&codeuid={2448FFAD-A63E-F010-653B-8814A083440A}&type=confirm&source=pc&username=admin

![](https://image.3001.net/images/20201202/1606909944_5fc77ff81b37e364a8820.png!small)

第三步使用GET方式访问/ispirit/login_code_check.php，传入关键参数codeuid，让后台进行代入查询，并返回携带管理员身份信息的凭证。

![](https://image.3001.net/images/20201202/1606909957_5fc780050b472f80ec777.png!small)

经过这步后客户端已经拥有了管理员的身份信息，直接访问OA主页，放行该数据包，成功以管理员身份登录OA系统。

![](https://image.3001.net/images/20201202/1606909968_5fc780101b11bb0738476.png!small)

![](https://image.3001.net/images/20201202/1606909977_5fc7801956ebd88085913.png!small)

###  **POC自动获取复现：**

直接在python环境下运行POC，-u指定url，-v指定版本，返回cookie

![](https://image.3001.net/images/20201202/1606909986_5fc780224a041087fd149.png!small)

![](https://image.3001.net/images/20201202/1606909995_5fc7802b1943e69f600c7.png!small)

替换浏览器存储的cookie，成功以管理员身份登录OA系统。

![](https://image.3001.net/images/20201202/1606910011_5fc7803bbcf9fcfc595e4.png!small)

Poc：https://github.com/NS-Sp4ce/TongDaOA-Fake-User

  

