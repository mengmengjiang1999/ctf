**作者：墨云科技VLab Team  
原文链接：<https://mp.weixin.qq.com/s/2DqN3EsHqG24AjMy8scecA>**

![](https://images.seebug.org/content/images/2022/11/fdf39512-d28b-489a-bbb5-e4b23df2460f.jpeg-w331s)

# **漏洞简述**

WooCommerce Currency Switcher
(WOOCS)是WooCommerce的多货币插件，它允许你的网站访问者根据设定的货币汇率实时切换产品价格的货币，并以选定的货币支付。允许为WooCommerce商店添加任何货币,
是WooCommerce商城系统不可或缺的货币切换器及多货币付款WordPress插件。WOOCS在WordPress官方统计有6W+的用户量。

![](https://images.seebug.org/content/images/2022/11/c44788f4-d158-4d52-9209-a784150748f3.png-w331s)

# **漏洞分析**

先查看WordPress官方仓库，对比下有哪些文件进行了改动。

![](https://images.seebug.org/content/images/2022/11/799d99a3-adca-42fe-9d4c-5367724d5df1.png-w331s)

可以看到修改的文件较多，对官方文档进行阅读后发现，该插件可以支持使用短标签shortcode方式调用显示，并且支持对短标签进行传入值，在classes/woocs.php中找到了注册shortcode的部分。

![](https://images.seebug.org/content/images/2022/11/da7987d4-c88e-4732-904c-0f646248d6dc.png-w331s)

逐一看一下其具体实现的代码

![](https://images.seebug.org/content/images/2022/11/cf0662c2-fe5d-41eb-9ce9-ba3969985e12.png-w331s)

首先会通过args接收短标签传入的值等配置信息,然后进过内部的赋值等操作到最后一步会调用render_html会传入两个值，一个是写死的woocs.php的路径，另一个为短标签接收到的参数,跟进该方法看一下具体逻辑

![](https://images.seebug.org/content/images/2022/11/f7f35276-76e7-4ad5-b92d-8a6b831b3865.png-w331s)

    
    
       public function render_html($pagepath, $data = array()) {
            @extract($data);
            ob_start();
            include($pagepath);
            return ob_get_clean();
        }

可以看到该代码非常简单，在第一步就调用了

    
    
    extract

而该函数可以从数组中将变量导入到当前的符号表，即将数组中的键值对注册成函数，使用数组键名作为变量名，使用数组键值作为变量值。

这样就会导致变量覆盖的问题，接着看到下面直接调用了

    
    
    include($pagepath)

看到这大家应该就明白了，只需要给传入的pagepath,从而导致达到任意文件包含的问题。然后我们制作一个图片马，就可以轻松将LFI漏洞升级为RCE漏洞。

# **漏洞验证**

LFI:

![](https://images.seebug.org/content/images/2022/11/aade7d03-8045-4c46-9398-ab487791a364.png-w331s)

RCE:

![](https://images.seebug.org/content/images/2022/11/56dd3a14-c490-4c9c-9852-0cd2ad4d3213.png-w331s)

# **时间线**

  * 2021年7月19日WOOCS插件发布更新
  * 2021年7月26日VLab实验室监测到漏洞通告
  * 2021年7月26日VLab实验室完成该漏洞复现

# **影响版本**

WooCommerce Currency Switcher(<= 1.3.6.2)

# **修复建议**

登录WordPress后台，将相关插件更新至最新版。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2021/>

