
    对于需要向评委展示的东西，虽然说技术硬核程度永远是第一位，但也不可忽略展示方式、效果的重要性，这是导师教给我的宝贵比赛经验之一。因为有些评委可能并不做信安，即使他做，也可能不是我们这个方向的，所以漏洞技术细节的展示并不止步于分析poc构造exp，可能有时候需要浅浅模拟一个攻击场景来告诉大家，噢这样漏洞的危害有多大，是怎么利用的。于此，本文使用cve-2020-6418的exp，构造恶意插件在正常网页加载漏洞文件来模拟攻击场景。
    

## 漏洞EXP代码

漏洞代码细节以及版本号参考自[CVE-2020-6418
分析与利用](https://www.anquanke.com/post/id/253536#h2-4)  
所以在此不过多展示，只需要会使用写好的exp就可以，此处就命名为hack-script.js：  
![image.png](https://image.3001.net/images/20220511/1652275962_627bbafa681dd5dbc351e.png!small)

## 恶意插件构造

其实熟悉chrome插件编写的小伙伴都知道，插件核心逻辑的编写其实就在于content-script.js和manifest.json。  
先在manifest.json中声明想要可以触发的网站，比如此处想要在新浪官网中触发这个恶意插件就饿看以这么写：  
![image.png](https://image.3001.net/images/20220511/1652276479_627bbcff5ae8da2d8b63f.png!small)  
在于权限申请中把刚刚的hack-script.js加入进来：  
![image.png](https://image.3001.net/images/20220511/1652276575_627bbd5f0ade325c05e37.png!small)

最后在content-script.js中创建元素把漏洞文件拉取即可：  
![image.png](https://image.3001.net/images/20220511/1652276687_627bbdcf6c0d3f4c091e9.png!small)

可以看到访问新浪首页的时候就会弹出一个计算器，以证明攻击成功，因为可以弹出计算器也就意味着可以做很多事情啦。![image.png](https://image.3001.net/images/20220511/1652274937_627bb6f937bf21a3c0ac7.png!small)

