> 本文作者：i春秋作家——HAI_  
>

# 0x00 前言

 **[HAI_逆向使用手册](https://bbs.ichunqiu.com/thread-35739-1-1.html?from=beef)**
（想尝试一下新的写法）

其他 **[Android逆向进阶](https://bbs.ichunqiu.com/thread-35142-1-1.html?from=beef)**
系列课程 <<<<<<<  

## 人物说明

小白：已经掌握了一些基础的逆向技能的菜鸟。  
小红：小白的女朋友。  
大白：小白的师傅。

## 竹山（大白居）

师傅师傅，我今天下山听见有人说，江湖中出现了一种为Hook的武林秘籍。据说十分厉害，可以拦截System。拦截程序猿开发的出来app。

小白啊，你知道什么是Hook吗。

听说过，但是却不明白什么是hook。

Hook这个秘籍啊，说白了是对 **函数进行重写** 。我们重写这个函数，就可以实现我们想要的目的，拦截呀，还有其他的内容。

师傅，我想学这个Hook秘籍。

好好，我们慢慢来。

先说说我们今天学习的Hook技能吧。

### 技能（内容）

1.一个新的武器（Xposed框架）的使用  
2.练习使用Hook的第一重内功（Android Studio 3.0 +Xposed）  
3.木桩实战练习  
4.木桩f进阶（小白的自我进步）

# 0x01 一个新的武器（Xposed框架）的使用

小白，认真学习哦，我们先来试试我们的新武器。Xposed，以后江湖闯荡也有一个防身的技巧。

小白你等等，我去找找这个武器我放在哪了。所谓工欲善其事必先利其器。

好了，师傅你快去，别啰嗦了。

## 1\. 武器 get

小白，要想使用这个武器，就要先打通经脉。

### 1.1 经脉（环境）

1.Root，手机root，无root不安卓。打通root经脉我们才能进行之后的操作。

2.Xposed框架安装，想要使用Xposed这个武器，就要先能拿的起来才能谈使用。

### 1.2武器

xposedBridgeApi-82.jar.jar。

这个就是我们的武器了，小白，来，我给你演示演示这个武器的基本使用方法。

## 2.武器演示

![图片.png](https://image.3001.net/images/20180315/1521106911457.png!small)  

我们这里使用Xposed武器拦截packageName，然后进行输出。

其实这个武器还是搭配内功才能发挥最大的能力。

搭配内功，师傅，这个怎么搞。

莫急莫急，我们一步一步来。

# 0x02 练习使用Hook的第一重内功（Android Studio 3.0 +Xposed）

小白，我先传授你第一重内功的运行穴位。要好好听哦。

## Android Studio 3.0 基本配置

我们先来给内容运行提供一个环境。

（1）首先构建一个不需要Activity的项目

![图片.png](https://image.3001.net/images/20180315/152110698078.png!small)  

（2）然后导入jar包。并且右键add as Library。  

![图片.png](https://image.3001.net/images/20180315/15211069934594.png!small)  

（3）填写Androidmanifest.xml文件。  

![图片.png](https://image.3001.net/images/20180315/15211070042997.png!small)  

    
    
      <meta-data
                android:name="xposedmodule"
                android:value="true" />
            <meta-data
                android:name="xposeddescription"
                android:value="Hook log test" />
            <meta-data
                android:name="xposedminversion"
                android:value="53" />

（4） 修改依赖方式

Xposed里已有该jar包内容，再次打包进去会冲突。

![图片.png](https://image.3001.net/images/20180315/15211070251376.png!small)  

（5）基本Xposed模型创建

使用alt+enter实现一个方法。

![图片.png](https://image.3001.net/images/20180315/1521107049234.png!small)  

小白，听我啰嗦两句。

handleLoadPackage，这个方法用于在加载应用程序的包的时候执行用户的操作。

LoadPackageParam loadPackageParam:，这个参数包含了加载的应用程序的一些基本信息。

## 内功实现

![图片.png](https://image.3001.net/images/20180315/15211070684180.png!small)  

这里一句话就可以实现。

XposedBridge.log("HAI_app: " + loadPackageParam.packageName);

这里我们要进行思考了，什么是 XposedBridge.log了。

posedBridge.log的打印会输出到xposed框架的启动程序的日志功能中。这样也更方便我们的查看。

我们来做配置的最后一步。设置开始地方。

新建assets目录里，新建一个file。file名称为xposed_init。

写入包名+类。

## 测试成果

Build APK

安装进行测试。

手机安装然后重新启动即可。

![图片.png](https://image.3001.net/images/20180315/15211070822942.png!small)  

## 思考

所谓师傅领进门，修行看个人。所以啊。

我知道了师傅，我们是不是可以通过这个简单的来进行过滤啊。比如写一个简单的分析系统。或者是其他的东西，我们还可以对这个进行过滤。我先自己去试试。

### 小白的自我修行

通过这个运行路径，对报名进行分析和过滤。

进行简单的尝试。

使用昨天学的java字符串的substring来进行对字符串过滤。

![图片.png](https://image.3001.net/images/20180315/15211070961053.png!small)  

然后进行测试。

  

当然也可以针对这个进行更加详细的说明。

# 0x03木桩实战练习

小白，来来，师傅这里给你找了一个木桩，我打给你看看。这个hook是怎么法功的，怎么打的。要学好哦。

知道了师傅。

## 木桩信息收集

### 1.基本信息

小白啊，用我们之前使用过的一个武器，来收集这些基本信息吧。

师傅，我们一般都收集什么信息啊。

恩，我们一般要收集

1.木桩的包名  
2.木桩的简单的逻辑  
....

小白，这个你就自己收集把。

#### 小白的操作

首先是包名。使用武器，apkhelper。

![图片.png](https://image.3001.net/images/20180315/15211071322907.png!small)

获取到包名信息。com.example.login

然后是简单的逻辑手机。

![图片.png](https://image.3001.net/images/20180315/15211071429479.png!small)  

  

### 2.反编译信息收集

小白啊，收集玩了吗？

收集完了师傅。

好，我们接下来收集反编译信息。知己知彼，方能百战不殆。

#### 师傅的操作

首先我们来看看我们要收集的东西。

1.关键的类名。  
2.关键的函数位置。

来用Android Killer武器反编译木桩。

定位。

查看类名，进行记录。

![图片.png](https://image.3001.net/images/20180315/15211071541496.png!small)

  

小白，看清楚，是这个样子进行记录。

原来是这样。com/example/login/MainActivity;  
但是我们要改成这样的。com.example.login.MainActivity

现在就需要定位到关键函数了。

![图片.png](https://image.3001.net/images/20180315/15211071701483.png!small)  

这个login就是我们要Hook住的函数啦。

Ljava/lang/String;Ljava/lang/String;从这里我们可以看到是两个输入内容。并且类型是String。我们现在要做的就是要hook住这个输出，然后对其进行输出。

## 木桩实战练习

### 环境搭建

好了，小白，前期资料收集的差不多了。我现在要发功了，要看清楚我的使用哦。

先把环境调整好。

然后先做一个简单的过滤。

![图片.png](https://image.3001.net/images/20180315/15211071841120.png!small)  

  

这个时候，收集的包名就排上用场了。

因为是hook的是方法，所以我们这里使用一个方法。

![图片.png](https://image.3001.net/images/20180315/152110719551.png!small)

第一个参数，要hook的包名+方法名，这个也是我们收集好的。

第二个参数不动

第三个参数方法名

第四个参数 输入的参数

我们有两个String类型的参数，所以才这样写

最后一个参数，就是做一个监听。可以监听这个方法的使用前和使用后。

### f for木桩

小白，一切准备你就须，看为师给你f这个木桩。

![图片.png](https://image.3001.net/images/20180315/15211072073929.png!small)  

小白，你看这第一招

    
    
    XposedBridge.log("ZHUZHU520:LoginName："+param.args[0]);

这一招搞它的第一个输入。

然后再来看这一招

    
    
    XposedBridge.log("ZHUZHU520:Passward:"+param.args[1]);

这一招搞它的第二个输入。

然后最后一招。

    
    
    XposedBridge.log("ZHUZHU520:end？？？："+param.getResult());

这一招就是拦截返回值。

小白啊，这里有一个需要思考的内容。

这样hook的意义或者作用是什么？

#### 小白的思考

师傅，我觉得首先，这样可以拦截下输入的参数，还有返回的值。如果在hook里做一个转发信息的技能。那不就可以成功的对登录账户的人进行账号和密码的获取。

这不就是和钓鱼一样了嘛。

我觉得这是一个很大的漏洞，如果登录厂商没有做相应的处理，那这里我可以拿这个搞死他。

好了，小白，你说的很对，我们现在来对这个进行下测试吧。

### f 木桩测试

![图片.png](https://image.3001.net/images/20180315/15211072228283.png!small)

小白啊，你看这里我们就成功的拦截内容了。小白给你一个任务，用hook f掉这个木桩，我希望他能登录成功，哪怕我输入的对的。

# 0x04 木桩f进阶（小白的自我进步）

    
    
    XposedBridge.log("ZHUZHU520:end？？？："+param.getResult());

## 思考一

师傅之前使用了一个param.getResult()获取了返回值，那我是不是可以使用相同的set方法，重新对这个进行赋值啊。

根据各种方式，我们知道了这里的返回值就是Z，也就是布尔型。

说干就干，争取f掉木桩。

![图片.png](https://image.3001.net/images/20180315/15211072365339.png!small)  

进行测试。

成功hook。

## 思考二

除了可以hook返回值，还可以hook输入值。

但是这样有点画蛇添足的感觉。

# 0x05 结束语

小白啊，hook就学到这里吧。有时间我们继续学习hook 技能。回去多练练。

