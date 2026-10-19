## 记某次js前端逆向

某次渗透测试过程中发现这样一个页面

![](./img/7682362962821617852.png)

登录抓包时发现密码被加密了

![](./img/736002712792217012.png)

遇到密码加密怎么办？直接谷歌打断点逆向啊

F12 全文搜索password字段

![](./img/6517858505363380010.png)

![](./img/2607997098168286659.png)

找到加密点 继续下去

搜索encryptedPassword

![](./img/5678579315409135816.png)

开启打断点

对194行和203打断点接下来进行调式

![](./img/7519661777540799341.png)

继续

![](./img/8195044756838396400.png)

成功得到加密后的密文 接下来就是如何批量生成

这里我们利用execjs模块

    
    
    pip install pyexecjs
    
    
    pyexecjs可以执行js文件 当然nodejs也行
    主要这里是用来批量加密

案列：

这里定义一个s.js文件

    
    
    function f(x,y) {
        return x+y
    }

python调用s.js

    
    
    import execjs
    
    with open('s.js', 'r', encoding='utf-8') as f:  #代码意思为打开s.js文件
        jstext = f.read()
    ctx = execjs.compile(jstext)  #加载js
    x=1
    y=2
    result = ctx.call('f',x,y) #调用js里面的函数
    print(result)

![](./img/7005250735022324878.png)

接下来就是利用python加密

![](./img/7749132119361390477.png)

这里的key在之前返回包中有我们直接导进去

    
    
    function encryptedPassword(password){
        //老的加密算法有问题，使用新的实现方法
         var key = '10001&94dd2a8675fb779e6b9f7103698634cd400f27a154afa67af6166a43fc26417222a79506d34cacc7641946abda1785b7acf9910ad6a0978c91ec84d40b71d2891379af19ffb333e7517e390bd26ac312fe940c340466b4a5d4af1d65c3b5944078f96a1a51a5a53e4bc302818b7c9f63c4a1b07bd7d874cef1c3d4b2f5eb7871'
        var split = key.split("&");
        var publicKeyExponent = split[0];
        var publicKeyModulus =split[1];
         RSAUtils.setMaxDigits(200);
         var key = new RSAUtils.getKeyPair(publicKeyExponent, "", publicKeyModulus); 
         var passwordEncry = RSAUtils.encryptedString(key,password.split("").reverse().join(""));//这里要对字符串进行反转，否则解密的密码是反的
         return passwordEncry;
    }

nodejs调式下

![](./img/6342189974615783836.png)

我们看到 RSAUtils未定义

继续上F12搜索RSAUtils

![](./img/5410794720793286073.png)

直接将代码抄下来

这里需要注意一个点 我们需要把encryptedPassword函数放在里面

![](./img/4541640547808547875.png)

去除$w和})(window);后继续debug下

![](./img/3077922808069715129.png)

这里oK

对比下之前浏览器后的密文

![](./img/399436609915626964.png)

OJBK 没有任何问题

最后写入文件

![](./img/8292300388795781096.png)

![](./img/136564037700349313.png)  
没毛病

  

