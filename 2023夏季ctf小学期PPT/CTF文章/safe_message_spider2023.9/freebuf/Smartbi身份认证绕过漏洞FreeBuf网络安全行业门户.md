# 内置账号密码登录

因为自己搭建的环境存在一些问题，可能是版本过高的原因，(奇奇怪怪的问题，用户没有权限)，所以目前仅仅做概念性验证，对漏洞的原理进行分析。

在未登录的情况下访问接口 `/smartbi/vision/RMIServlet`​

![image](https://image.3001.net/images/20230725/1690273850_64bf883a61d10a2058b60.png!small)

![image](https://image.3001.net/images/20230725/1690273851_64bf883bde256ecbac0c8.png!small)

我们可以比较明显的看到对应的处理类 `CheckIsLoggedFilter`​

`smartbi.freequery.filter.CheckIsLoggedFilter#doFilter`​

![image](https://image.3001.net/images/20230725/1690273853_64bf883d6f06ebca9af51.png!small)

从这里开始可能就是要进行比较详细的分析，首先是判断请求的路径是不是`/vision/RMIServlet`​ 是的话进入这个分支，然后判断请求体中是不是有以
`windowUnloading`​ 开头的字符串，这个跟另一种绕过方式有关，这里先不做分析

![image](https://image.3001.net/images/20230725/1690273855_64bf883f406217a44f995.png!small)

接下来依次判断是否有通过 POST 或者 GET 方法来获取参数 `className`​ `methodName`​ 如果没有的话，就对参数 encode
进行解码，对相关参数进行赋值

![image](https://image.3001.net/images/20230725/1690273857_64bf88410e6a861cc67cb.png!small)​这里有一个判断，对类和方法进行鉴权操作，如果是
true 就会继续判断是否登录，只需要满足 `FilterUtil.needToCheck`​ 返回 false 就可以

`smartbi.util.FilterUtil#needToCheck`​

![image](https://image.3001.net/images/20230725/1690273859_64bf88432edfd7e8da79c.png!small)

我们就注意到从数据库登录的操作也是不需要鉴权就可以进行访问的

`smartbi.usermanager.UserManagerModule`​

![image](https://image.3001.net/images/20230725/1690273860_64bf88448589602be14fa.png!small)​

`smartbi.usermanager.UserManagerModule#loginFromDB`​

![image](https://image.3001.net/images/20230725/1690273861_64bf88457ffce74781297.png!small)​

`smartbi.usermanager.SecurityServiceImpl#loginFromDB`​

![image](https://image.3001.net/images/20230725/1690273862_64bf8846d734a7eb07882.png!small)

这里直接比较的是从数据库中查询出的密码，所以我们就可以直接利用内置的账号和 MD5密码登录

![image](https://image.3001.net/images/20230725/1690273864_64bf8848762526475963b.png!small)

![image](https://image.3001.net/images/20230725/1690273865_64bf8849920c5982f5e33.png!small)

admin 也是可以登录成功的

![image](https://image.3001.net/images/20230725/1690273867_64bf884b378d8c1c1d0c6.png!small)​

为什么不用原本的登录模式登录，首先原本的登录模式登录是不知道对应的账号和密码的其次我们再对原本的登录逻辑进行简单的分析

`smartbi.usermanager.UserManagerModule#clickLogin`​

![image](https://image.3001.net/images/20230725/1690273868_64bf884c8af36cca05c97.png!small)

`smartbi.usermanager.UserManagerModule#login`​

![image](https://image.3001.net/images/20230725/1690273869_64bf884db17a687984156.png!small)​

`smartbi.usermanager.SecurityServiceImpl#login`​

![image](https://image.3001.net/images/20230725/1690273871_64bf884f36188d7096594.png!small)​主要的处理登录逻辑在这一部分

`smartbi.usermanager.SecurityServiceImpl#loginDB`​

![image](https://image.3001.net/images/20230725/1690273872_64bf8850b906086867a77.png!small)

`smartbi.usermanager.UserBO#isPasswordValidate`​

![image](https://image.3001.net/images/20230725/1690273874_64bf885230cbeab67b990.png!small)

这里在进行比较的时候

首先 `String passwordInLib = this.user.getPassword();`​
是从数据库中查找用户的密码，根据用户的密码开头的第一位字符，来进行处理比较

![image](https://image.3001.net/images/20230725/1690273875_64bf88537fedbf5e08d30.png!small)

我们已经知道数据库中对应的值是 `0a`​ 但是并没有任何一个值对应的 MD5 的值是`a`​ 所以正常无法登录内置用户

漏洞修复

`<http://192.168.222.133:18080/smartbi/vision/sysmonitor.jsp>`​

![image](https://image.3001.net/images/20230725/1690273876_64bf8854a9a2d56362071.png!small)![image](https://image.3001.net/images/20230725/1690273877_64bf8855f033741838fd0.png!small)​同样的
POC 已经无法利用成功了，我们关注一下修复的代码内容

![image](https://image.3001.net/images/20230725/1690273879_64bf8857afa0de9baab1f.png!small)

