frida简单实用脚本的使用

[ 萌木盖](https://www.jianshu.com/u/0e56159ab5a7)关注赞赏支持

# frida简单实用脚本的使用

在公众号[跟小雅一起学逆向]看到的 具体怎么用还不知道，先保存上以后再看  
下面是python脚本，然后根据需求该js代码就可

    
    
    import frida, sys
    
    def on_message(message, data):
        if message['type'] == 'send':
            print("[*] {0}".format(message['payload']))
        else:
            print(message)
    
    jscode = """
        Java.perform(function () {
        // Function to hook is defined here
        var http = Java.use('com.cmstop.ctmediacloud.util.SignUtil');
        http.getSignStr.implementation = function (a1,a2,a3) {
                send("start");
                send("参数1:"+a1);
                send("参数2:"+a2);
                send("参数3:"+a3);
                var result = this.getSignStr(a1,a2,a3)
                send("结果:"+result);
                send("end");
                return result;
            };
        });
    """
    
    process = frida.get_usb_device().attach('com.baotounews.api.m')
    script = process.create_script(jscode)
    script.on('message', on_message)
    print('[*] Running CTF')
    script.load()
    sys.stdin.read()
    

## js代码

  * Android中使用StringBuffer，  
StringBuilder这两个类操作字符串，Hook其toString方法并打印堆栈，在很多情况下可以定位到加密字段的生成堆栈。

    
    
    console.log("加载脚本成功！");
    Java.perform(function x() {
        //定位StringBuilder,StringBuffer类
        const stringbuilder = Java.use("java.lang.StringBuilder");
        const stringbuffer = Java.use("java.lang.StringBuffer");
    
        //定位方法
        const toString = "toString";
    
    
        // 使用log类和Exception类产生堆栈
        var jAndroidLog = Java.use("android.util.Log");
        var jException = Java.use("java.lang.Exception");
    
        stringbuilder[toString].implementation = function(){
            //执行原逻辑
            const result = this[toString]();
            // 打印返回的字符串内容
            console.log(result);
    
            // 只有长度大于30时，才打印堆栈
            if (result.length > 30) {
                // 抛出异常。打印堆栈
                console.log(jAndroidLog.getStackTraceString(jException.$new()));
            }
    
            //return出去
            return result;
        };
    
        stringbuffer[toString].implementation = function() {
            //执行原逻辑
            const result = this[toString]();
            // 打印返回的字符串内容
            console.log(result);
            // 只有长度大于30时，才打印堆栈
            if (result.length > 30) {
                // 抛出异常。打印堆栈
                console.log(jAndroidLog.getStackTraceString(jException.$new()));
            }
            //return出去
            return result;
        }
    
    });
    

  * Hook 用于字符串比较的方法，同样可以得到大量信息，需要注意的是，代码没有做优化，应该加上堆栈调用+输出筛选，否则遇到较大的应用会崩溃。

    
    
    console.log("加载脚本成功！");
    Java.perform(function x() {
        //定位类
        const str = Java.use('java.lang.String');
        const objectClass = 'java.lang.Object';
        console.log("已经定位到目标类");//定位类成功！
        // 在这里更改类的方法的实现（implementation）
        str.equals.overload(objectClass).implementation = function(obj) {
            //打印传入的参数
            var response = str.equals.overload(objectClass).call(this, obj);
            console.log(str.toString.call(this) + ' == ' + obj.toString() + ' ? ' + response);
    
    
            //return出去
            return response;
        }
    
    });
    

  * 加密算法中，明文调用getBytes方法转换为字节数组，Hook并打印堆栈可以快速定位

    
    
    console.log("加载脚本成功！");
    Java.perform(function x() {
        //定位类
        const str = Java.use('java.lang.String');
    
        console.log("已经定位到目标类");//定位类成功！
        // 在这里更改类的方法的实现（implementation）
        str.getBytes.overload().implementation = function() {
    
            var response = this["getBytes"]();
            console.log(this.toString());
            //return出去
            return response;
        }
    
    });
    

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [老爸的“贵”](https://www.jianshu.com/p/8a5fe7926d11)

那天，我兴高采烈地拿着展销会上购买的花生糖，塞到父亲手边，原以为他会说，哈，你还真懂我的心意。没想到，脱口而出说了...

[幽幽草](https://www.jianshu.com/u/7cab99bf8b16)阅读 139评论 0赞 0

  * [深入理解JVM虚拟机 - 内存分配与回收策略](https://www.jianshu.com/p/fab8865f9b79)

Java技术体系中所提倡的自动内存管理最终可归结为自动化的解决了两个问题：给对象分配内存以及回收分配给对象的内存。...

[FX_SKY](https://www.jianshu.com/u/215e5a237558)阅读 286评论 0赞 0

  * [手里的沙](https://www.jianshu.com/p/66a8e14be8d8)

感情就是手机的沙 越紧握越走的快 可是 握紧是因为在乎 原来适度 是这么难得一个事 我让他紧张到想退了 我认真的觉...

[茶小样](https://www.jianshu.com/u/87aabea74fed)阅读 209评论 0赞 0

  * [站桩打卡Day69](https://www.jianshu.com/p/3bc969a3e672)

[90b80e36b8cf](https://www.jianshu.com/u/90b80e36b8cf)阅读 215评论 0赞 0

  * [springmvc.xml注解](https://www.jianshu.com/p/276a9520ad58)

1、<mvc:annotation-driven/> 开启MVC所需要的注解 <mvc:annotation-...

[尼尔君](https://www.jianshu.com/u/182581d780d2)阅读 432评论 0赞 0

 