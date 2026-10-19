## 系列文章

>
> [App安全检测实践基础：客户端程序安全（一）](https://www.freebuf.com/articles/terminal/255712.html)

##  **目录**

> Activity简述
>
> Activity拒绝服务
>
> Activity组件越权
>
> Activity劫持

![](https://image.3001.net/images/20201130/1606717030_5fc48e6645b8f9a103880.png!small)

##  **Activity** **简述**

Activity是一个应用程序组件，提供一个屏幕，用户可以用来交互为了完成某项任务。Activity中所有操作都与用户密切相关，是一个负责与
**用户交互** 的组件，可以通过setContentView(View)来 **显示指定控件** 。

在一个android应用中，一个Activity通常就是一个单独的屏幕，它上面可以显示一些控件也可以监听并处理用户的事件做出响应。Activity之间通过Intent进行通信。

Activity是Android组件中最基本也是最常用的一种组件，每一个Activity都被实现为一个独立的类，并且继承于Activity这个基类。

activity类处于android.app包中，继承体系如下：

> 1.java.lang.Object
>
> 2.android.content.Context
>
> 3.android.app.ApplicationContext
>
> 4.android.app.Activity

##  **Activity** **拒绝服务**

 **1** **、描述**

开发者为方便调用，会把Activity组件设置为导出状态。Android组件之间采用Intent来传递数据，如果Intent接收方没有对Intent的畸形数据进行异常捕获，可以通过构造附有畸形数据的Intent，导致APP崩溃，触发拒绝服务漏洞。

 **2**
**、过程**![](https://image.3001.net/images/20201130/1606717196_5fc48f0c261bac309bc2c.png!small)

 **查看AndroidManifest.xml是（否）存在Activity导出**

​![](https://image.3001.net/images/20201130/1606717280_5fc48f60bce49e72516f3.png!small)

 **查看一下 Intent相关的代码，进行分析运行情况**

    
    
    <intent-filter>
    
    <action android:name="android.intent.action.MAIN"/>
    
    </intent-filter>
    
    </activity>
    
    <activity-alias android:enabled="true" android:icon="@drawable/ic_logo_toast" android:label="@string/app_name" android:name="semem.toast.logo1" android:targetActivity="semem.toast.MainActivity">
    
    <intent-filter>
    
    <action android:name="android.intent.action.MAIN"/>
    
    <category android:name="android.intent.category.LAUNCHER"/>
    
    </intent-filter>

 **利用adb命令启动被导出的Activity**

adb shell am start -S -n
包名/Activity名![1606717430_5fc48ff606c110e0da3b2.png!small?1606717431502](https://image.3001.net/images/20201130/1606717430_5fc48ff606c110e0da3b2.png!small?1606717431502)

如何找到的这个包和Activity名，请查看[相关内容](https://blog.csdn.net/weixin_43650289/article/details/109306735)

 **3** **、建议**

> 将不必要导出的组件调整为不导出
>
> 对intent的数据处理进行保护

##  **Activity** **组件越权**

 **1** **、描述**

开发者为方便外部调用，会把Activity组件设置为导出状态。如果由于开发者的疏忽，把一些包含用户敏感信息或可进行敏感操作的组件设置为导出状态，可能会造成越权查看敏感信息泄露以及越权操作等安全风险。

 **2** **、过程**

> 查看AndroidManifest.xml是否存在Activity导出
>
> 利用adb命令启动被导出的Activity

adb shell am start -S -n 包名/Activity组件名

    
    
    Package: semem.toast
    
    semem.toast.MainActivity
    
    Permission: null
    
    semem.toast.logo1
    
    Permission: null
    
    Target Activity: semem.toast.MainActivity
    
    semem.toast.TranslateActivity
    
    Permission: null
    
    semem.toast.shortwww_activity
    
    Permission: null
    
    semem.toast.NewQRCodeActivity
    
    Permission: null
    
    semem.toast.GetWebCodeActivity
    
    Permission: null
    
    semem.toast.SearchActivity
    
    Permission: null

 **确认Activity是（否）存在敏感信息泄露和越权操作等安全风险**

菜单如下所示：![1606717503_5fc4903fbd2f4d1f7cac5.png](https://image.3001.net/images/20201130/1606717503_5fc4903fbd2f4d1f7cac5.png!small?1606717505110)

