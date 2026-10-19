# 一例简单的frida反调试绕过

阅读量 **161280**

发布时间 : 2022-08-29 10:31:02

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

## 前言

最近在分析一款app时遇见了frida反调试，花了时间简单学习了一下，有不少收获，记录下学习的过程。

## 抛出问题

frida是一个很强大的hook框架，用的人多了，自然而然就出现了很多检测方案，这次碰到的app就检测了frida，可以正常打开，但是当你用frida
-f启动或者attach进程，不久后就会闪退。

## 常见frida检测

1.检测frida-server文件名  
2.检测27042默认端口  
3.检测D-Bus  
4.检测/proc/pid/maps映射文件  
5.检测/proc/pid/tast/tid/stat或/proc/pid/tast/tid/status  
6.双进程保护

前两种可以通过修改frida-server文件名，改默认端口绕过。双进程可以通过-f spawn模式启动绕过。其他的需要去hook修改。

## 定位

先针对简单的几个可能检测的方式，我修改了文件名，改了端口，也尝试了spawn启动，均会在启动后不久闪退。  
这时考虑到其他几种检测。  
首先用frida去看看载入了哪些so，看看是哪里检测了，看了个寂寞。

    
    
        function fridaProcess(){
          Java.perform(function () {
            var enumMoudle = Process.enumerateModules();
            for (var i = 0; i < enumMoudle.length; i++){
              console.log("", enumMoudle[i].name)
            }
          });
        }
    
      setImmediate(fridaProcess,0)
    

![](https://p0.ssl.qhimg.com/t01e78de64f78b1414b.png)

因为so载入的时候，底层最后open去打开的。  
所以再用frida去hook应用中的open函数，看看读取了哪些so或者文件，可以看到最后断在了/proc/self/maps。

    
    
    var pth = Module.findExportByName(null,"open");
        Interceptor.attach(ptr(pth),{
            onEnter:function(args){
                this.filename = args[0];
                console.log("",this.filename.readCString())
                if (this.filename.readCString().indexOf(".so") != -1){
                    args[0] = ptr(0)
    
                }
    
            },onLeave:function(retval){
                return retval;
            }
        })
    

![](https://p2.ssl.qhimg.com/t01ae5fc2b8b6d65f9a.png)

## 稍稍深入

这里当挂上frida后对应的maps文件中会出现re.frida.server之类的特征，这是在使用frida
server的时候自动创建的，其中存放着frida的功能模块，可以在载入so的hook脚本输出中能看到最后也是断在frida-agent.so。

![](https://p4.ssl.qhimg.com/t01cd0e5e257d27726d.png)

这里要绕过这个检测，我是通过备份一个正常启动时的maps文件（这里前面也讲到app不使用frida是能正常启动不闪退的）。

    
    
    function main() {
      const openPtr = Module.getExportByName('libc.so', 'open');
      const open = new NativeFunction(openPtr, 'int', ['pointer', 'int']);
      var readPtr = Module.findExportByName("libc.so", "read");
      var read = new NativeFunction(readPtr, 'int', ['int', 'pointer', "int"]);
      var fakePath = "/data/data/com.app/maps";
      var file = new File(fakePath, "w");
      var buffer = Memory.alloc(512);
      Interceptor.replace(openPtr, new NativeCallback(function (pathnameptr, flag) {
          var pathname = Memory.readUtf8String(pathnameptr);
          var realFd = open(pathnameptr, flag);
          if (pathname.indexOf("maps") >= 0) {
              while (parseInt(read(realFd, buffer, 512)) !== 0) {
                  var oneLine = Memory.readCString(buffer);
                  if (oneLine.indexOf("tmp") === -1) {
                      file.write(oneLine);
                  }
              }
              var filename = Memory.allocUtf8String(fakePath);
              return open(filename, flag);
          }
          var fd = open(pathnameptr, flag);
          return fd;
      }, 'int', ['pointer', 'int']));
    }
    setImmediate(main)
    

![](https://p3.ssl.qhimg.com/t014a72f20b6974647a.png)

然后就可以继续调试了。

## 总结

这只是一个简单的例子，但是确实在这个bypass的过程中学到了东西，只要花时间是去分析，总能找到对应的突破口。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **雷石安全实验室** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/278827](/post/id/278827)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [frida](/tag/frida)

 **+1** __3赞

 __收藏

![](https://p2.ssl.qhimg.com/t01ebe472d127128939.png) 雷石安全实验室

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

