## 1、小程序反编译

### 环境准备

#### 1、 node 环境准备

下载链接：<https://nodejs.org/en/>

![1687580625_64966fd1018936be4bb9b.png!small?1687580625577](https://image.3001.net/images/20230624/1687580625_64966fd1018936be4bb9b.png!small?1687580625577)

#### 2、反编译工具

项目地址来自于：<https://github.com/xuedingmiaojun/wxappUnpacker>

### 具体操作

#### 1、微信PC获取小程序

在通过微信PC打开小程序前，我们最好先找到缓存到本地的小程序包路径，一般都是在 微信PC安装目录\WeChat Files\WeChat
Files\Applet

比如我的就是安装到D盘根目录的，所以路径为：D:\WeChat\WeChat Files\Applet

![1687580642_64966fe2d57dee4f19f51.png!small?1687580642923](https://image.3001.net/images/20230624/1687580642_64966fe2d57dee4f19f51.png!small?1687580642923)

上图中每个wx开头的文件夹代表一个小程序，一般最新打开的小程序都是在第一个，如果不确定可以排序一下修改日期

找到路径了我们就可以用微信PC打开小程序了，打开后就会发现当前目录新增了一个文件夹，里面存放的就是加密后的小程序包

![1687580655_64966fefd4fa47924a386.png!small?1687580656174](https://image.3001.net/images/20230624/1687580655_64966fefd4fa47924a386.png!small?1687580656174)

#### 2、解密包

刚获取到的包我们还不能进行反编译，必须要通过`解密软件`修改一下才能反编译

![1687580670_64966ffee8dca3aeef5e4.png!small?1687580671144](https://image.3001.net/images/20230624/1687580670_64966ffee8dca3aeef5e4.png!small?1687580671144)

本篇就演示一个主包和一个分包反编译的过程就可以了，先通过解密工具修改一下主包

![1687580684_6496700c8cf9e915e18c9.png!small?1687580684729](https://image.3001.net/images/20230624/1687580684_6496700c8cf9e915e18c9.png!small?1687580684729)

解密的主包自动到 wxpack 这个包里面来了，同样的步骤解密一个分包，下图是我解密好的

![1687580702_6496701e8be4e5e79bc89.png!small?1687580702627](https://image.3001.net/images/20230624/1687580702_6496701e8be4e5e79bc89.png!small?1687580702627)

#### 3、反编译

进入 wxpack的同级目录 wxappUnpacker-master，在路径栏输入 cmd 自动打开当前目录的 命令窗口了

![1687580732_6496703c8128fa492bd55.png!small?1687580732647](https://image.3001.net/images/20230624/1687580732_6496703c8128fa492bd55.png!small?1687580732647)

先反编译一下主包，把反编译后的文件夹放到`wxpack`同级目录中

    
    
    node wuWxapkg.js ..\wxpack\wx464f1fef86a25927.wxapkg

  * `-s`表示分包

  * 第一个`..\`表示输出位置

  * `..\wxpack\_pages_app.wxapkg`需要反编译的分包位置

![1687580745_64967049bd0a7c137ccea.png!small?1687580745933](https://image.3001.net/images/20230624/1687580745_64967049bd0a7c137ccea.png!small?1687580745933)

然后把我们得到的文件夹导入开发者工具或者notepad++查看代码，这里导入开发者工具

![1687580922_649670fad266664c4637a.jpg!small?1687580923535](https://image.3001.net/images/20230624/1687580922_649670fad266664c4637a.jpg!small?1687580923535)

## 2、找漏洞相关js

全局搜索解密，通过查看代码最终定位到request.js中的代码块

![1687580962_64967122b6217d230b608.png!small?1687580963277](https://image.3001.net/images/20230624/1687580962_64967122b6217d230b608.png!small?1687580963277)

进入request.js的文件夹

![1687581011_6496715322d9f56e1cb0b.png!small?1687581011248](https://image.3001.net/images/20230624/1687581011_6496715322d9f56e1cb0b.png!small?1687581011248)

## 3、模块化加载

事先安装好browserify

### 3.1、Browserify

Browserify 可以让你使用类似于 node 的 require() 的方式来组织浏览器端的 Javascript 代码，通过预编译让前端
Javascript 可以直接使用 Node NPM 安装的一些库。

### 3.2、安装

管理员打开cmd（普通用户有可能会安装失败）

    
    
    npm install -g browserify

### 3.3、打包js文件

    
    
    browserify request.js > myboundle.js

![1687581063_64967187604f86e709680.png!small?1687581063440](https://image.3001.net/images/20230624/1687581063_64967187604f86e709680.png!small?1687581063440)

### 3.4、修改js代码

    
    
    var data="WVMNBlsFBgQKWVEPBVgABAFXUFEKVlAGBlRWXVdeWlxRAQcBWQRQUA0GUgcGWwcMAFsBVARRDVkMU1kCBgALWFlfAltQCQIDDFheBV9RB1dXUAMPB1gBAwYHXlZdUA0LVgEDCVlcAF4KCFYAX1ALB1oDBQcAUVQNV1AHUwAAXANYAgwHCABTCVELWg8LAVAFUFAPV19TCQoLWFVdVwpRBAMLDVJYUFFQCQRQXQNbWggDBlADX1UIVg1TBlcKX1AIAg0CUQMFWFcKBlwLUVEHDlBaVF0HCFQDDlULUV0ABQUCXQUNVwg="  
    var t = JSON.parse(u.decryptSM4(data, u.createGenkey("202300")));  
    ​  
    console.log(t)

将以上代码放置在我们定位到的代码块中

![1687581076_64967194bb6230fda1517.png!small?1687581077051](https://image.3001.net/images/20230624/1687581076_64967194bb6230fda1517.png!small?1687581077051)

在下方找个合适的位置放进去，注意不要插入到其他函数内，否则在访问页面时不会启动

![1687581085_6496719dcbe411da36fa0.png!small?1687581086133](https://image.3001.net/images/20230624/1687581085_6496719dcbe411da36fa0.png!small?1687581086133)

### 3.5、编写html文件，将js文件导入

![1687581094_649671a661019c018c3a2.png!small?1687581094498](https://image.3001.net/images/20230624/1687581094_649671a661019c018c3a2.png!small?1687581094498)

### 3.6、访问页面，查看控制台

![1687581173_649671f510ca879ddac3b.jpg!small?1687581173389](https://image.3001.net/images/20230624/1687581173_649671f510ca879ddac3b.jpg!small?1687581173389)

# 4、总结

总的来说，当遇到一些数据泄露或者其他的数据需要加解密的时候，并且无法花时间去查看代码反推的时候，可以借鉴这种方式，可以节省很大一部分时间，简直就是偷懒必备技能，这种方式其实就是类似于把他一整个js文档整合成一个文件，这样不怕混淆，即使是混淆后的代码，也可以参考这种方式，因为把所有的代码都整合进去之后，即使他混淆了，也还是在同个文件里面有记录，所以可以成功加解密。

  

