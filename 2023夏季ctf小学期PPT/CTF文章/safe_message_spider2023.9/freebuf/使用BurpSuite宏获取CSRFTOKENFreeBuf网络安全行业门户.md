原创：3sNwGeek合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

###  **0X01 前言**  
  

在WEB渗透中经常可以看到页面存在一次性token校验的情况，即请求包中包含token，而token值需通过其它页面获取，导致burpsuite抓包后无法重放。除了暴力破解，BurpSuite宏也可以用于其他测试，不过最终目的都是一致的，使我们更加快捷，专注于挖掘信息和渗透上，而不是在重复的工作中上浪费时间。

###  **0X02 开始**

下面以一个简单例子来做个说明。目标网站如下，页面存在一个图片验证码，题目要求暴力破解得到账号密码。这题可以有多种方式实现，这里以burpsuite宏进行实验。

###  **0X03 题目源码**

暴力破解测试题目：<https://github.com/3sNwgeek/BruteForc_test>
这些题目出自都是我平时工作渗透中遇到的各种各样的验证码问题而改成题目的。

![v2-4de80d9e54cee318ccb0677c9f74275b_hd.p](https://pic2.zhimg.com/80/v2-4de80d9e54cee318ccb0677c9f74275b_hd.png)

### **0x04 发现**

虽然题目是使用滑动验证码进行登陆的，但是实际上还是校验登陆session的。 1.
目标URL为：http://1.1.1.1/c/hdyzma/welcome.php，抓个包测试一下，发现其会对token参数校验，拒绝重放的数据包。

![v2-10974cbd71c3d892ed18b525b636f054_hd.p](https://pic1.zhimg.com/80/v2-10974cbd71c3d892ed18b525b636f054_hd.png)

![v2-f43f665edbe44339ba407e0d301d6baa_hd.p](https://pic1.zhimg.com/80/v2-f43f665edbe44339ba407e0d301d6baa_hd.png)

2\. 在登陆页面http://1.1.1.1/c/hdyzma/可发现token值：

![v2-d0235af93476f7fdc1255101201c3c46_hd.p](https://pic3.zhimg.com/80/v2-d0235af93476f7fdc1255101201c3c46_hd.png)

3\. 通过上面的发现，可以使用burpsuite的宏功能自动把登陆页的token值抓取出来填入登陆请求

###  **0x05 创建Macros**

1.创建Macros，获取token值

![v2-7913af3cc0fb3aa944bd713f3cc6ba83_hd.p](https://pic2.zhimg.com/80/v2-7913af3cc0fb3aa944bd713f3cc6ba83_hd.png)

2.在Macro Recorder中选择包含要获取的token的页面

![v2-d41b7add9063a277092264c9e7987669_hd.p](https://pic3.zhimg.com/80/v2-d41b7add9063a277092264c9e7987669_hd.png)

3.配置Macros

![v2-78f578b214cee14b955296ad804678d3_hd.p](https://pic4.zhimg.com/80/v2-78f578b214cee14b955296ad804678d3_hd.png)

![v2-1865d5337839135f2b54a4057f813d6e_hd.p](https://pic3.zhimg.com/80/v2-1865d5337839135f2b54a4057f813d6e_hd.png)

用鼠标选中token值，burpsuite会自动填写开始标记以及结束标记，并且写上Parameter
name为token，注意这里的参数名token是与要爆破页面里的token名称一致：

![v2-aea78ef4dbde6c34baae88c7d9d86148_hd.p](https://pic1.zhimg.com/80/v2-aea78ef4dbde6c34baae88c7d9d86148_hd.png)

定义Macro描述，方便区分：

![v2-fc01e99e64be708f4d21b3bfcaaf0047_hd.p](https://pic2.zhimg.com/80/v2-fc01e99e64be708f4d21b3bfcaaf0047_hd.png)

### 0x06 创建Session Handling Rules  

1、然后在Session Handling Rules里面新建一条规则：

![v2-8fde6f324854c61a0418531b46743f5d_hd.p](https://pic2.zhimg.com/80/v2-8fde6f324854c61a0418531b46743f5d_hd.png)

设置一个名字，这里叫update_token：

![v2-4819e9b7df159553c6041139578f8d2e_hd.p](https://pic1.zhimg.com/80/v2-4819e9b7df159553c6041139578f8d2e_hd.png)

选中刚刚录制好的宏，并且设置要更新的参数名，这里是token：

![v2-0cac58b78119035e65c542020aff4790_hd.p](https://pic2.zhimg.com/80/v2-0cac58b78119035e65c542020aff4790_hd.png)

2.然后是设置宏的影响范围，因为我们只需要暴力破解账号密码，所以Tools
Scope这里只选中Repeater、Intruder就行了，其它模块可根据实际需要勾选：

![v2-482c0922ff1e6d80ed04cf6220a58637_hd.p](https://pic3.zhimg.com/80/v2-482c0922ff1e6d80ed04cf6220a58637_hd.png)

### 0x07 暴力破解  

1.回到Repeater，点击Go重新发包，可以看到现在token参数会自动刷新：

![v2-bd7a7520f70d278d61c4b896b520fe01_hd.p](https://pic3.zhimg.com/80/v2-bd7a7520f70d278d61c4b896b520fe01_hd.png)

![v2-9b4ce16b6bd42d80127760458b9f18a5_hd.p](https://pic2.zhimg.com/80/v2-9b4ce16b6bd42d80127760458b9f18a5_hd.png)

2.使用Intruder暴力破解账号密码：

![v2-d47b2ccf3b8ea0ffbec1e7dae5d568ba_hd.p](https://pic3.zhimg.com/80/v2-d47b2ccf3b8ea0ffbec1e7dae5d568ba_hd.png)

因为多线程会同时刷新token，导致部分请求包拿到的token已经被刷新了，所以只能设置单线程跑：

![v2-8068306d7d61f4f7c2fdbb08e8d05724_hd.p](https://pic1.zhimg.com/80/v2-8068306d7d61f4f7c2fdbb08e8d05724_hd.png)

成功暴破得到账号admin/123456a

![v2-deb0d2f4ab434db4d9944cad9c086993_hd.p](https://pic1.zhimg.com/80/v2-deb0d2f4ab434db4d9944cad9c086993_hd.png)

### 0x08 支持合天  

合天实验室关于暴力破解练习:[暴力破解(合天网安实验室)](http://www.hetianlab.com/expc.do?ec=ECIDcee9-2e23-4a12-83b7-b2957dca9783?channelID=zhihu)

### 0X09 结语  

使用BurpSuite宏获取CSRF-TOKEN，可以不断更新sessions值，使得保持有效的会话进行请求，非常方便。

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  

