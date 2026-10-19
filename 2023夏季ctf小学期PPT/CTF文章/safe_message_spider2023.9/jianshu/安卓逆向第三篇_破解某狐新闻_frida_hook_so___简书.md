安卓逆向第三篇：破解某狐新闻 frida hook so

[ 萌木盖](https://www.jianshu.com/u/0e56159ab5a7)关注赞赏支持

# 安卓逆向第三篇：破解某狐新闻 frida hook so

# app是：

需要base64解码：  
5pCc54uQ5paw6Ze7YXBwNi40LjQ=

# 遇到问题：

软件内的搜索接口：

  

请求头

请求头有ssig，不带不行。

# 解决吧：

## jadx

上来先jadx打开apk，看看源码，搜一下ssig

  

jadx

  

image.png

太多了 过

#### 搜url

image.png

  

image.png

点开之后右击方法名，点`查找用例`  

image.png

  
点进去  

image.png

  
如果按第一种直接搜ssig都搜不到 我都没点忽略大小写  

image.png

  
再继续  

image.png

  
so先不管了，先hook java

    
    
    import frida, sys
    
    
    def on_message(message, data):
        if message['type'] == 'send':
            print("[*] {0}".format(message['payload']))
        else:
            print(message)
    
    
    jscode = """
    
    
    function showStacks() {
        Java.perform(function() {
            send(Java.use("android.util.Log")
                .getStackTraceString(Java.use("java.lang.Exception")
                    .$new()));
        });
    }
    setImmediate(function() {
    
        console.log("[*] Starting script");
    
        Java.perform(function() {
            // Function to hook is defined here
    
            
            var http = Java.use('com.sohu.newsclient.security.b.a');
            var http2 = Java.use('com.sohu.newsclient.securityencrypt.SecurityNativeUtils');
            //var Context = Java.use('android.content.Context');
            http.a.overload("java.lang.String").implementation = function(a1) {
                    showStacks();
                    send("start");
                    send("a参数1:" + a1);
                    var result = this.a(a1);
                    send("a结果：" + result);
                    return result;
                };
            http2.getSignatureNative.implementation = function(a1,a2,a3) {
                    showStacks();
                    send("start");
                    send("getSignatureNative参数1:" + a1);
                    send("getSignatureNative参数2:" + a2);
                    send("getSignatureNative参数3:" + a3);
                    var result = this.getSignatureNative(a1,a2,a3);
                    send("getSignatureNative参数3结果：" + result);
                    return result;
                };
        
        });
    });
    """
    '''
    
    '''
    
    # // send("结果:"+bytesToString(result));
    process = frida.get_usb_device().attach('com.sohu.newsclient')
    script = process.create_script(jscode)
    script.on('message', on_message)
    print('[*] Running CTF')
    script.load()
    sys.stdin.read()
    

结果

  

image.png

  

传的参数都在抓包的时候可以看到，下面来搞so文件

# IDA

#### 先把这个apk后缀改为zip，然后解压，打开文件夹，打开`lib`文件夹，然后打开到最里面,

找到libsecurity_helper.so 放到ida里，

  

image.png

### 这里点开之后应该跟我不一样，因为是静态方法，java传参是3个，这里参数是5个。所以第一个参数是JNIenv* 第二个是jclass
（如果是动态的就是jobject），然后int不变 ，两个string是char*，

### 具体整理代码的方法看安卓逆向第一篇<https://www.jianshu.com/p/dfa16d43a1e5>

### 整理完如下图

image.png

### 很明显有个md5 ，但是传参并不知道是啥，那就用frida hook它，

# frida hook so

这也是我为什么写这篇文章的原因，frida hook so,  

image.png

  
下面只放了js代码 图里的`复制它` 粘贴到哪了知道吧

    
    
    function c(){
            const hooks = Module.load('libsecurity_helper.so');
            var Exports = hooks.enumerateExports();
            for(var i = 0; i < Exports.length; i++) {
    
                var str;
                Java.perform(function () {
                    str = Java.use("java.lang.String");
                });
                // console.log(Exports[i].name)
                if(Exports[i].name=="_Z13md5_calculatePKcS0_"){
                    //函数类型
                    console.log("type:",Exports[i].type);
                    //函数名称
                    console.log("name:",Exports[i].name);
                    //函数地址
                    console.log("address:",(Exports[i].address));
                    Interceptor.attach(Exports[i].address, {
                        onEnter: function (args) {
                            console.log("_______");
                            console.log(Memory.readCString(args[0]));
                            console.log(Memory.readCString(args[1]));
                            // var s3 = Java.cast(args[0], str);
                            // var s5 = Java.cast(args[1], str);
                            // console.log("s3:",s3);
                            // console.log("s5:",s5);
                            // Java.vm.getEnv().GetObjectClass(args[0])
                            // console.log("param1>>>>>>>>>>>>>>>>--------------------------"+Memory.readUtf16String(args[0]));
                        },
                        onLeave: function (retval) {
                            console.log("param1>>>>>>>>>>>>>>>>--------------------------")
                            console.log(Memory.readCString(retval));
                            // var result=Java.vm.getEnv().newStringUtf(retval)
                            // console.log("param result>>>>>>>>>>>>>>>>--------------------------"+Java.cast(retval, str));
                        }
                    });
                }
            }
        }
    c();
    

结果：

  

image.png

  

image.png

# 总结

最后就是把java层的其中一个参数，拼接上固定的字符串，md5一下。 其他参数用不到。

  

image.png

