本文原载于公众号：宽字节安全

作者：potatso

**第一天，群里爆出深信服edr控制端poc。poc在这里就不放了。下面我们分析一下

## RCE

    
    
    echo "<p><b>Log Helper</b></p>";     $show_form($_REQUEST);

跟入show_form

    
    
    /**      * 显示表单      * @param array $params 请求参数      * @return      */     $show_form = function($params) use(&$strip_slashes, &$show_input) {         extract($params);         $host  = isset($host)  ? $strip_slashes($host)  : "127.0.0.1";

唉，一看就是经典的php变量覆盖漏洞。下面我们拓展一下，使用grep搜索一下

![1597717016.png!small](https://image.3001.net/images/20200818/1597717016.png!small)

tools目录下全部都是变量覆盖漏洞。。。看样子单纯只防御网上那个poc是没有用的

不信你看

![1597717034.png!small](https://image.3001.net/images/20200818/1597717034.png!small)

一句话后门都不敢这么写。。。。

所以，在这里我建议，最好 **下线深信服edr的控制中心** ，漏洞太多，你是防不住的。。

## 官方后门？？？

自己看图吧，懒得解释

![1597717049.png!small](https://image.3001.net/images/20200818/1597717049.png!small)

## 任意文件下载漏洞

顺手找到的。。。。大佬们别在意，我说下线是有原因的。我一个菜逼两分钟挖洞。这代码写的太愚蠢了

![1597717066.png!small](https://image.3001.net/images/20200818/1597717066.png!small)![1597717074.png!small](https://image.3001.net/images/20200818/1597717074.png!small)

没有过滤。。。。。

## 验证码绕过

额，没啥说的。。。。好兄弟们，深信服的代码写的真的太愚蠢了。

![1597717092.png!small](https://image.3001.net/images/20200818/1597717092.png!small)

## 整改建议

目前来看，只能暂时 **下线** ，没有太好的办法。。。漏洞太多，且个个都是rce。

从源码来看，深信服的开发完全没有经过任何安全开发的培训，导致写出一堆自带严重BUG的代码。。。。

![1597717112.jpg!small](https://image.3001.net/images/20200818/1597717112.jpg!small)

本文来源：<https://www.cnblogs.com/potatsoSec/p/13520546.html>

