## 前言

Electron是一个使用JavaScript、HTML和CSS构建跨平台的桌面应用程序。它基于Node.js和Chromium，被Atom编辑器和许多其他应用程序使用。  
Electron兼容Mac、Windows和Linux，可以构建出三个平台的应用程序。  
相对而言，Electron 的维护成本较低，因而十分流行。VS
Code、一些企业的即时通讯工具等，都使用了Electron。但存在性能问题，同时也引入了其他的安全问题。

## 分析Electron应用

一个正常的Electron程序，通常它的 JS 源码会被打包到 .asar文件中，或者直接以JS文件的方式存储在程序目录内，下面是一个例子。  
![image](https://image.3001.net/images/20230704/1688450529_64a3b5e173fb52e817e9b.png!small)  
针对asar文件，可以用官方提供的工具(https://github.com/electron/asar)
进行解包分析，通过extract参数进行解包，当然直接看解包以后的代码并不是很友好，所有这里不做演示。

## chrome调试Electron应用

Electron应用实际上也是个Chromium ，可以通过Chromium的方式开启开发者工具。以某工具为例为例，在运行程序时，添加--remote-debugging-port=xxxx 参数，即可在对应端口为Electron应用的主窗口开启远程调试功能：  
这里端口需要根据inspect(chrome://inspect/)中的配置来选择。  
![image](https://image.3001.net/images/20230704/1688450557_64a3b5fd3a2e919dca2cc.png!small)  
这里使用9222端口，在命令行添加参数启动。  
![image](https://image.3001.net/images/20230704/1688450567_64a3b60706204a858c257.png!small)  
启动后可以在inspect页面看到对应的Target：  
![image](https://image.3001.net/images/20230704/1688450576_64a3b610a30c1a797a0ba.png!small)  
然后就可以点击进入进行调试了，不过此时开启的是Render Process的开发者工具。  
![image](https://image.3001.net/images/20230704/1688450626_64a3b64258a0e79bc9354.png!small)  
我们可以通过添加--inspect=9222参数来调试Main Process。  
![image](https://image.3001.net/images/20230704/1688450637_64a3b64d54fe443751edb.png!small)

## Debugtron调试Electron应用

Debugtron是一个基于Electron开发的客户端桌面GUI程序，可以用于调试生产环境下的 Electron 应用。  
项目地址：https://github.com/pd4d10/debugtron  
直接下载对应的Releases版本，安装后即可使用。  
![image](https://image.3001.net/images/20230704/1688450648_64a3b65817d10c81290cd.png!small)  
直接将要调试的Electron应用拖拽过来即可。  
![image](https://image.3001.net/images/20230704/1688450657_64a3b661e35e1c909f63a.png!small)  
不过debugtron中没有找到堆栈调用的信息，可以根据这里端口（devtools），添加到inspect的配置中，用chrome的inspect进行调试。  
![image](https://image.3001.net/images/20230704/1688450666_64a3b66aeec72ecb237cc.png!small)  
这样就能跑起来，调起来了。  
不过现在大多的应用都会对关键的js进行混淆加密，或者使用修改过的Chromium内核，要分析还是要有耐心。

## 参考

[Electron 的一些调试技巧](https://mp.weixin.qq.com/s/XNcUXz640wKJq0pHIGshgQ)

