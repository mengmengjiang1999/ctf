## 0x00前言  

一直对模板注入漏洞懵懵懂懂，直到最近在某gayhub上瞎逛碰到一个cms，再一番操作之后找到了一个前台getshell的漏洞。由于相关要求，这里隐去这个cms的全称，就分享漏洞发掘的思路。

## 0x01 代码审计  

我们全局搜索eval(可以发现有一个地方使用了eval，可以大胆猜测这个模板引擎是使用eval去实现。我们跟进ii_eval()函数。

![v2-3cdc1eda03f387e6b6d8c810570338c2_hd.j](https://pic4.zhimg.com/80/v2-3cdc1eda03f387e6b6d8c810570338c2_hd.jpg)

可以见到函数的$strers可控，我们继续跟进ii_eval()看谁对他进行了调用。

![v2-d1ed564f3466d54f44cc40c2d99fc1d4_hd.j](https://pic4.zhimg.com/80/v2-d1ed564f3466d54f44cc40c2d99fc1d4_hd.jpg)

全局搜索发现就只有一个地方对他进行了调用那就是ii_creplace()函数

![v2-118e458b0b3c5e5c5d3aa45bc7155549_hd.j](https://pic2.zhimg.com/80/v2-118e458b0b3c5e5c5d3aa45bc7155549_hd.jpg)

我们跟进ii_creplace()可以看到，$strers可控但是他必须传入一个与({\$=(.[^\\}]*)})这个正则匹配的字符串才能传入到iieval(),这里我们就可以得知要想执行代码必须符合类似下面的格式：

  1. {$=phpinfo()}   

![v2-71e83c312f84e3bd675c2bc02b8c76df_hd.j](https://pic2.zhimg.com/80/v2-71e83c312f84e3bd675c2bc02b8c76df_hd.jpg)

那么我们继续跟进ii_creplace()函数看谁对他进行了调用，找了很多但是都对函数中的$进行了转义，但是在passport\address\common\incfiles\manage_config.inc.php中的xxx_cms_admin_manage_list()并未做任何过滤。我们继续跟进。

![v2-8180a386b28dcccc59b5ec97e2203bb6_hd.j](https://pic4.zhimg.com/80/v2-8180a386b28dcccc59b5ec97e2203bb6_hd.jpg)

我们发现\passport\address\manage.php对passport\address\common\incfiles\manage_config.inc.php进行了包含并调用了xx_cms_admin_manage_action(),而它调用了xx_cms_admin_manage_list(),那么很明显我们只需将符合{\$=(.[^\\}]*)}正则的payload传入即可导致getshell.

![v2-e01435d9d15eeafaa842eed576a61052_hd.j](https://pic4.zhimg.com/80/v2-e01435d9d15eeafaa842eed576a61052_hd.jpg)

那么从哪传入呢，我们直接把xxx_cms_admin_manage_list()中的sql语句打印出来即可知道。

![v2-dd66c36527409d39a8919991cbc6383c_hd.j](https://pic1.zhimg.com/80/v2-dd66c36527409d39a8919991cbc6383c_hd.jpg)

![v2-758fed491cba7c30e959943883d42718_hd.j](https://pic3.zhimg.com/80/v2-758fed491cba7c30e959943883d42718_hd.jpg)

很明显是从用户地址处传入。那么我们先注册个用户添加用户地址传入我们payload

  1. {$=phpinfo()}   

![v2-4810d14f76fcbb3c22bbea98ff1cf2eb_hd.j](https://pic2.zhimg.com/80/v2-4810d14f76fcbb3c22bbea98ff1cf2eb_hd.jpg)

再次刷新页面已经显示phpinfo，说明getshell成功。

![v2-1d9629b77352dbb67d0c5e71d42b67bc_hd.j](https://pic4.zhimg.com/80/v2-1d9629b77352dbb67d0c5e71d42b67bc_hd.jpg)

## 0x02总结  

其实纵观代码，这个cms的开发人员是有考虑过代码注入的问题，但是其对传入的内容并没有做全局过滤，而是每个点做过滤。这样难免会造成遗漏过滤的情况，当然这个cms的sql注入防护也是采取每个变量前套上一个转义函数，但是在后续的版本开发中难免也会有开发人员遗漏，这里不做深究了。

看完文章有没有想要自己尝试一下呢！登录合天网安实验室，get同款实验。或者点击阅读原文，了解相关说明。通过实验了解服务端模板注入漏洞的危害与利用。

Flask服务端模板注入漏洞：http://www.hetianlab.com/expc.do?ec=ECID87ed-2223-40e5-8083-f5c55d69af28

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

