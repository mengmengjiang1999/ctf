> 作者简介：c1o2a3，Goby社区推荐安全专家。毕业于计算机网络专业，现供职于某安全公司，从事等保渗透测试
> 懂点PHP、python，擅长挖掘JS源码泄露漏洞。

 **前言：** 其实之前看到goby自带的海贼王主题就想着：Goby能不能做一款自己的主题呢？最近更新194版本告诉我可以↓↓↓

##  **01** **插件效果**

![](https://image.3001.net/images/20200901/1598950910.png!small)

##  **02** **开发流程**

###  **2.1 相关准备**

1）首先下载科比主题，然后到科比主题的源码文件，复制新建一个文件夹：![640?wx_fmt=png](https://image.3001.net/images/20200901/1598951032.png!small)2）
根据官方的文档说明修改

`package.js`

    
    
    {  
    "name": "Super Saiyan",   
    "publisher": "c1o2a3",  
    "description": "超级赛亚人",  
    "version": "0.1.00",  
    "engines": "1.7.192",  
    "icon": "src/logo.png",  
    "initEvents": "init",  
    "main": "./src/extension.js",  
    "contributes": {  
    },  
    "scripts": {},  
    "devDependencies": {},  
    "dependencies": {}  
    }

 **2.2 处理图片**

1）打开SRC文件夹，文件列表如下，列表中有4张图片：

kobe.png是下载主题的预览图

left-nav-bg-kobe.png是左侧的菜单的背景图

right-bg-kobe.png是右侧的背景图

logo.png是下载的时候的logo图标

![640?wx_fmt=png](https://image.3001.net/images/20200901/1598951126.png!small)

2）发挥优秀的PS技术使用Photoshop之类的软件打开这些图片，比如kobe.png

由图片可以看出，做了半透明处理，并且把背景都扣了：

![640?wx_fmt=png](https://image.3001.net/images/20200901/1598951172.png!small)

找张心仪的图片也扣掉背景啥的再修改一下合适的图片大小，复制图层到原图（left-nav-bg-kobe.png）里面然后根据自己的喜好修改透明度：

![640?wx_fmt=png](https://image.3001.net/images/20200901/1598951190.png!small)

其他图片与此类似，最后删掉原科比主题的图片。

![640?wx_fmt=png](https://image.3001.net/images/20200901/1598951206.png!small)

###  **2.3 修改配色**

修改`extension.js`

    
    
    function activate(content) {var fs = require('fs');var path = require('path');//左侧菜单背景图let leftNavBgImg = path.join(__dirname, "left-nav-bg-test.png").replace(new RegExp(/(\\)/g), '/');//右侧背景图，根据自己的修改let rightBgImg = path.join(__dirname, "right-bg-goku.png").replace(new RegExp(/(\\)/g), '/');goby.registerCommand('init', function (content) {// 主题名字let name = "test";// 主题配置let config = {//主配色（包括图标，logo颜色）"main": "#c81c1c",//以下是配置字体的颜色"primaryFont": "rgba(0, 0, 0, 0.87)","secondaryFont": "rgba(0, 0, 0, 0.6)","level3Font": "rgba(0, 0, 0, 0.34)","primaryBorder": "rgba(0, 0, 0, 0.16)","secondaryBorder": "rgba(0, 0, 0, 0.09)",//右侧背景的配色"primaryBackground": "#f3eac3",//扩展程序、插件管理那些背景的配色"secondaryBackground": "#f8eaaf","lv3Background": "#f3eac3","lv4Background": "rgba(0, 0, 0, 0.12)","navBackground": "#f3eac3","navFont": "rgba(0, 0, 0, 0.6)","navHoverFont": "#000","scanResTopMainFont": "#000","scanResTopSubFont": "rgba(0, 0, 0, 0.3)","scanResTopIcon": "rgba(0, 0, 0, 0.06)","navOtherFont": "rgba(0, 0, 0, 0.7)","primaryIcon": "rgba(0, 0, 0, 0.2)","chartColors": ["rgba(0, 0, 0, 1)","rgba(0, 0, 0, 0.6)","rgba(0, 0, 0, 0.4)","rgba(0, 0, 0, 0.2)","rgba(0, 0, 0, 0.1)"],"leftNavBgImg": "url("+leftNavBgImg+")","rightBgImg": "url("+rightBgImg+")",//菜单背景色"navSelectBackground": "#c81c1c","entranceImg": __dirname+"/goku.png"}let userConfigJson = require(rootPathData + '/config/config.json');if (!userConfigJson.theme) {userConfigJson.theme = {};}userConfigJson.theme[name] = config;userConfigJson.curTheme = name;setTheme(config);let mergeConfigJson = JSON.stringify(userConfigJson, null, 6);fs.writeFileSync(rootPathData + '/config/config.json', mergeConfigJson);});}​exports.activate = activate;

里面的颜色配置可以自己更改，都修改完后保存。（我新加的颜色注释记得删除，不然可能会出错）

###  **2.4 安装调试**

修改完保存之后打开Goby发现还是没有该主题，原因应该是自己弄的主题没有将数据写进Goby的/config/config.json文件（大概率是某些函数没有执行，但是我又看不懂）。打开config.json文件找到theme字段，可以发现，安装后的主题都往这里面写了一些数据进去。

1）找到科比主题的数据：![640?wx_fmt=png](https://image.3001.net/images/20200901/1598951367.png!small)仔细一看，很眼熟啊，不就是extension.js的配置吗，复制一下字段，改一下使其变成自己主题（图片文件用的是绝对路径，也改成自己主题的），嘿嘿这不就是传说中的手动安装吗？![640?wx_fmt=png](https://image.3001.net/images/20200901/1598951378.png!small)然后打开Goby>设置>主题设置就能看到自己的主题了：![640?wx_fmt=png](https://image.3001.net/images/20200901/1598951388.png!small)后续就是修改颜色，图片，调试（修改/config/config.json的主题数据即可，如果需要上传插件的话再同步修改extension.js文件即可）。

##  **03** **小结**

本人是老龙珠迷了，小时候买了好几本的漫画。所以动动手尝试弄了一下主题。最喜欢打架从来没有赢过的逼王——贝吉塔。

整个开发流程下来，发现其实主题只需要复制粘贴，扣扣图片，再改改颜色的参数就可以了。Goby用着属实舒服，我还有尝试过夏目主题，下次再分享出来吧~

![640?wx_fmt=jpeg](https://image.3001.net/images/20200901/1598951605.jpg!small)

>  **插件任务领取：**
>
> <https://github.com/gobysec/GobyExtension/projects>
>
>  **插件开发交流：**
>
> 关注微信公众号gobysec，回复“插件”

