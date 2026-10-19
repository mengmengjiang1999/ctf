上期的`Android逆向之动态分析so篇`主要讲述了Android逆向动态分析的环境配置以及利用`IDA`配合模拟器动态分析so文件。这期斗哥将带来`Android逆向之动态分析Frida篇`主要讲述Frida环境搭建与Frida在Android环境下的运行与使用。

## 0X01 Frida框架安装详解

#### 1、简述：

Frida是以Python为载体，注入Javascript作为Android中执行代码的一款Hook框架，可用Android、ios、linux、win等平台。

#### 2、安装客户端：

在已有python和pip环境的系统下安装frida，如windows则使用`pip install frida-tools`命令安装frida包![11](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824154144479.png)使用frida命令查看版本（成功查看到frida版本表示安装成功）![12](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824154344383.png)

#### 2、安装服务端：

首先到github上下载frida-server，网址为：<https://github.com/frida/frida/releases>下载与客户端相同版相同的[frida-server](https://github.com/frida/frida/releases)（注意位数）在客户端（windows）上使用`adb
push`命令将frida-servser传到虚拟机目录中![13](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824135030831.png)修改frida-servser权限，让frida-servse拥有可执行权限![14](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824161423147.png)运行frida服务器![15](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-2018082416223351.png)在客户端开启端口转发adb forward tcp:27042 tcp:27042adb
forward tcp:27043 tcp:27043![16](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824164847460.png)使用`frida-ps -U`或者`frida-ps
-R`命令查看手机端进程（成功查看到进程表示Frida环境搭建成功）

## 0X02 Frida框架的初步使用

将frida服务器运行起来后，客户端就可以利用frida API对Android设备中的进程以及APP应用进行操作

#### 例一：

使用Frida获取android手机当前最前端Activity所在的进程

    
    
    import frida
    rdev = frida.get_usb_device()
    front_app = rdev.get_frontmost_application()
    print(front_app)
    

![17](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181017232435358.png)

#### 例二：

查看手机所有已安装的android APP应用

    
    
    import frida
    rdev = frida.get_usb_device()
    apps = rdev.enumerate_applications()
    for app in apps:
        print(app)
    

![18](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20181017233619380.png)

#### 例三：

frida自带的Messages机制与进程交互模板

    
    
    import frida, sys
    
    
    def on_message(message, data):
        if message['type'] == 'send':
            print("[*] {0}".format(message['payload']))
        else:
            print(message)
    
    
    jscode = """
    //分析hook点，编写javascript代码
    //javascript代码，重点
    """
    
    process = frida.get_usb_device().attach('ds.tetris.android')
    script = process.create_script(jscode)
    script.on('message', on_message)
    script.load()
    sys.stdin.read()
    

## 0X03 Frida框架解题技巧

Frida可以用来解决CTF中移动安全题，如Frida官网的一个APP例子，就是一道CTF题。以下就已一道CTF题为例，通过解题过程深入了解Frida的使用。

#### 1、题目描述：

寻一名可以拿到20000分的高手，在线等很急！

#### 2、寻找hook点：

MainActivity部分代码如下：静态分析得到`getScore()`方法是记录分数的关键

    
    
    public final void invoke(@NotNull Score arg6) {
        Intrinsics.checkParameterIsNotNull(arg6, "$receiver");
        if(arg6.getScore() > 20000) {
            Game.access$getView$p(Game.this).setScore(0xFFFFFFFF);
        }
        else {
            Game.access$getView$p(Game.this).setScore(arg6.getScore());
        }
    
        if(Game.access$getView$p(Game.this).getLevel() < arg6.getLevel() && Game.access$getView$p(Game.this).getLevel() != 0 && (Game.this.getSoundEnabled())) {
            DefaultImpls.play$default(Game.access$getSoundtrack$p(Game.this), Sound.LEVEL_UP, 0, 2, null);
        }
    
        Game.access$getView$p(Game.this).setLevel(arg6.getLevel());
    }
    

Hook点:setScore方法值置为-1,程序将就会自动为我们解密flag

    
    
    public void setScore(int arg4) {
        if(arg4 == -1) {
            UtilsKt.errorhandler(this);
        }
    
        this.score = arg4;
        View v0 = this._$_findCachedViewById(id.scoreLabel);
        Intrinsics.checkExpressionValueIsNotNull(v0, "scoreLabel");
        ((TextView)v0).setText("Score: " + arg4);
    }
    

#### 3、解题过程：

（请先阅读Android逆向之静态分析文章）静态分析完应用逻辑后可知只要将 MainActivity 中的
setScore方法参数值设为-1,程序就会自动为我们解密flag,所以可以通过Frida框架重写setScore方法将值直接设为-1![15](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824170826907.png)用`frida-ps
-R`发现应用进程![16](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824170507120.png)Javascript脚本如下:

    
    
    Java.perform(function() {
        var clz = Java.use("ds.tetris.android.MainActivity");
        clz.setScore.overload('int').implementation = function(args){
        args = -1
        clz.setScore.overload('int').call(this,args)
        }
        });
    

运行服务器frida-server，客户端使用`Frida`运行以下命令:![17](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824170422859.png)

点击游戏开始，程序会解密并弹窗。![18](http://pcplqdlf7.bkt.clouddn.com/markdown-img-paste-20180824170105858.png)完整的python代码如下：

    
    
    import frida, sys
    
    
    def on_message(message, data):
        if message['type'] == 'send':
            print("[*] {0}".format(message['payload']))
        else:
            print(message)
    
    jscode = """
    Java.perform(function() {
        var clz = Java.use("ds.tetris.android.MainActivity");
        clz.setScore.overload('int').implementation = function(args){
        args = -1
        clz.setScore.overload('int').call(this,args)
        }
        });
    """
    process = frida.get_usb_device().attach('ds.tetris.android')
    script = process.create_script(jscode)
    script.on('message', on_message)
    script.load()
    sys.stdin.read()
    

## 0X04 小小总结：

本期斗哥带来的`Android逆向之动态分析Frida篇`主要讲述Frida环境搭建与Frida在Android环境下的运行与使用，并且利用Frida框架解决CTF移动安全题。下期将带来`Android逆向之动态分析smail篇`主要简述Android
Studio的开发基础与动态调试smail源码。

![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20181022/1540196074_5bcd86eae65c4.jpg!small)

