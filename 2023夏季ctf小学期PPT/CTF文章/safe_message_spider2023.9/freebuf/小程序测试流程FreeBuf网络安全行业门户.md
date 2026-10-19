流程分为两个方面，解包可以挖掘信息泄露问题、隐藏的接口，抓包可以测试一些逻辑漏洞、API安全问题。两者结合起来就可以边调试边进行测试，更方便于安全测试。

## 搜索目标小程序

目标搜索不能仅仅局限于主体单位，支撑单位、供应商、全资子公司等都可能是入口点，所以小程序当然也不能放过它们。

## 小程序主体信息确认

查看小程序账号主体信息，否则打偏了花费了时间不说，还可能有法律风险。

点击小程序，

![image-20220114152229428](https://image.3001.net/images/20220210/1644475350_6204b3d6c235e573e99de.png!small)

点更多资料就能看到小程序相关信息。

![image-20220114152155720](https://image.3001.net/images/20220210/1644475351_6204b3d7c846752a580cb.png!small)

## 小程序包获取

### PC端

首先在微信中搜索到小程序，并打开简单浏览。

然后在自己微信文件保存路径下找到applet下找到该小程序包，可以通过时间或者小程序的appid快速定位到目标包。

![image-20220114140944208](https://image.3001.net/images/20220210/1644475352_6204b3d8ad3e0f85f09ba.png!small)

微信电脑端小程序包存在加密，需要使用工具进行解密。

下载地址：微信后台 回复口令领取。

### windows端获取小程序包流程

打开解密工具，在工具目录建立wxpack文件夹（解密后的小程序包会放在这个地方），运行工具解密需要操作的小程序包即可。

![image-20220114141036225](https://image.3001.net/images/20220210/1644475353_6204b3d950772796ba5ec.png!small)

![微信图片_20220114112546](https://image.3001.net/images/20220210/1644475354_6204b3da0ed362c697f9f.png!small)

### 移动端

找到对应目录，把包拉出来即可。

安卓保存路径：/data/data/com.tencent.mm/MicroMsg/{⽤户ID}/appbrand/pkg/

iOS保存路径：/var/mobile/Containers/Data/Application/{程序
UUID}/Library/WechatPrivate/{⽤户ID}/WeApp/LocalCache/release/{⼩程序ID}/ ）

由于安卓data目录需要root权限访问，所以需要手机或模拟器root。

#### android模拟器获取小程序包流程，

这里我用到的是夜神模拟器，登录微信，找到小程序。

![image-20220114141407869](https://image.3001.net/images/20220210/1644475354_6204b3dabca0074263d35.png!small)

方法是将复制的内容放到mnt->shared->orther下，就会自动同步到PC端，这是模拟器的共享目录。

![image-20220114141438940](https://image.3001.net/images/20220210/1644475355_6204b3db8e7bda5f6de94.png!small)

## 解包

工具地址：<https://github.com/xuedingmiaojun/wxappUnpacker>

环境安装

    
    
    npm install uglify-es --save  
    npm install esprima --save  
    npm install css-tree --save  
    npm install cssbeautify --save  
    npm install vm2 --save  
    npm install js-beautify --save  
    npm install escodegen --save  
    npm install cheerio --save

执行node wuWxapkg.js xxxxxx.wxapkg

![image-20220114142107734](https://image.3001.net/images/20220210/1644475356_6204b3dc53367cddaa6fe.png!small)

不出意外应该没啥问题，但意外往往很多。node版本问题，依赖问题等等都有可能导致解包失败，这个时候就希望懂nodejs的同学深入了解小程序的打包压缩逻辑，然后动手二开项目。不懂的又没打算往这方面深入研究的怎么办呢，那换一个目标呗。

## 调试

打开微信开发者工具，选择导入项目。

![微信截图_20220114100328](https://image.3001.net/images/20220210/1644475357_6204b3dd151b26a227e90.png!small)

导入项目后可能会出现一些代码错误，需要自己手动修改，没有错误后可以编译，之后愉快的进行调试了。

![微信截图_20220114103018](https://image.3001.net/images/20220210/1644475357_6204b3ddea2f600da7f0a.png!small)

记得在“本地设置”模块，勾选上“不校验合法域名”功能。

有些小程序包含第三方插件，而⼩程序插件直接在微信客户端内是⽆法搜索得到的，但我们可以通过登录⾃⼰的⼩程序微信开放平台账 户在“设置” --> “第三⽅设置”
--> “添加插件”中搜寻⼩程序插件。

## 抓包

简单来讲就是配置全局代理，让微信走全局代理。首先打开抓包工具，配置好代理，然后修改windows代理配置。

![微信截图_20220114111919](https://image.3001.net/images/20220210/1644475359_6204b3df03ce9d586be7a.png!small)

就可以抓包分析了。

![微信截图_20220114111211](https://image.3001.net/images/20220210/1644475359_6204b3dfeabc9bdc9c69c.png!small)

