> 目前，小程序的应用可以说相当普遍，在渗透测试和外部打点时，如果对目标系统没有有效的思路时，不妨试着从小程序下手。

## 解密与解包

获取小程序源码的方式有很多种，可以通过夜神这类安卓模拟器、iOS、安卓手机等获取到小程序包，而PC端的小程序包则进行了相应的加密。这里就以比较复杂PC端为例展开讲解。

### 找到目标小程序包

1、一般小程序包位置位于微信文件管理目录的`\WeChat Files\Applet\`目录下

![](https://image.3001.net/images/20220320/1647780114_623721125a0fc8d829ceb.jpg!small)

2、打开相应目录后，再打开需要测试的微信小程序，这时就会生成相应的包，再根据时间进行排序，这样就能很快定位到目标小程序

![](https://image.3001.net/images/20220320/1647780115_623721134b31413a7a833.jpg!small)

3、逐一开打目录，可以找到`.wxapkg`结尾的包，这里选择主包`__APP__.wxapg`

![](https://image.3001.net/images/20220320/1647780116_623721144bf2c465784ee.jpg!small)

### 解密

> 新版的PC小程序需要先解密才能进行反编译。

双击打开解密工具，选择对应小程序包的位置，需要注意的是，不能将包拷贝到其他目录，否则会无法获取到小程序的ID，导致解密失败；同时不能删除工具下的
wxpack 目录，这是解密结果的目录

![](https://image.3001.net/images/20220320/1647780117_6237211513d578cacd971.jpg!small)

![](https://image.3001.net/images/20220320/1647780117_62372115be841b038b55c.jpg!small)

### 解包

在 wxpack 目录下找到对应同名的小程序包

  1. 先 [下载 nodejs](https://nodejs.org/zh-cn/download/)，一直下一步安装即可

  2. 下载解包工具

    
    
    git clone https://github.com/wanliofficial/wxappUnpacker.git
    

  3. 安装依赖

    
    
    npm install
    

  4. 解包

    
    
    node wuWxapkg.js <wx_mini_progranm_file_path>
    

解包成功后，会得到如下文件  
![](https://image.3001.net/images/20220320/1647780118_623721166503ee7852742.jpg!small)

> 这里仅演示解密主包，如果小程序有其他分包，可以用同样的方法进行解密和解包，但是在反编译分包时，需要带上`-s`参数，如下
    
    
    node wuWxapkg.js -s=../ xxxx.wxapkg
    

> `../`表示结果输出目录
>
> `xxxx.wxapkg`表示分包位置

## 抓包环境搭建

小程序的抓包环境也有非常多的搭建方式，同样可以采用模拟器或者移动端，可以参考APP抓包的方式，这里同样是以PC端为例，搭建一个 Wechat ->
Proxifier -> Burp 的抓包环境

### 将Burp的证书安装到系统中

> 注意是系统，不是浏览器，否则将抓不到 HTTPS流量

1、访问Burp代理端口，下载证书  
![](https://image.3001.net/images/20220320/1647780119_62372117541d41da2c323.jpg!small)

（1）安装证书  
双击打开证书，点击确定  
![](https://image.3001.net/images/20220320/1647780120_623721180c322c6eb3fb6.jpg!small)![](https://image.3001.net/images/20220320/1647780120_62372118a4327cad2935f.jpg!small)  
![](https://image.3001.net/images/20220320/1647780121_623721195a5826ee3370d.jpg!small)  
根据图示依次点击，注意要选择为 **受信任的根证书颁发机构**  
![](https://image.3001.net/images/20220320/1647780122_6237211a1001894f45a22.jpg!small)  
然后一路下一步即可

### Proxifier配置

1、配置代理服务器  
![](https://image.3001.net/images/20220320/1647780122_6237211aaa7b2d8c6a8e7.jpg!small)  
![](https://image.3001.net/images/20220320/1647780123_6237211b8d4bc9d2d810f.jpg!small)  
填入Burp代理的IP和端口，选择协议为 HTTPS  
![](https://image.3001.net/images/20220320/1647780124_6237211c36b471abf7e0a.jpg!small)

（1）添加规则

> 由于系统的流量会比较多，如果不设置指定的规则，会有许多干扰流量，不方便后续的渗透测试

![](https://image.3001.net/images/20220320/1647780124_6237211ccdc01be4d9cef.jpg!small)  
点击Browser，选择小程序的主程序，在Windows下文件名为`wechatapp.exe`，在 MacOS下名为`Mini
Program.app`，这里我用 search Everything 搜索文件名，定位到相应位置再打开  
选择好应用后，操作点击刚刚配置好的Burp代理服务器  
![](https://image.3001.net/images/20220320/1647780125_6237211d95a6c9b884f5e.jpg!small)  
最后再将默认的流量设置为直接连接即可  
![](https://image.3001.net/images/20220320/1647780126_6237211e657b351ad398a.jpg!small)  
再把设置的规则 mini-program前面的选框勾上，就能进行抓包了  
![](https://image.3001.net/images/20220320/1647780127_6237211f17847408b4956.jpg!small)

## 声明

本文初衷为分享网络安全知识，请勿利用技术做出任何危害网络安全的行为，由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由 **使用者**
本人负责，与SpaceSec安全团队及作者无关！

文章中部分学习内容来自于网络，回馈予网络，如涉及版权问题，请联系删除。

