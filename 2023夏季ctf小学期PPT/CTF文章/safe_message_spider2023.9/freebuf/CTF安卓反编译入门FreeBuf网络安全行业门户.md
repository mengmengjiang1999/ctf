# ****spyNote_client_easy 安卓逆向分析****

spyNote_client_easy1.apk

链接：https://pan.baidu.com/s/1TC7LxXMQzcOAcRJgKh-b8A?pwd=qdqn

在某员工手机中发现一个疑似远控木马样本，请分析该样本，请找到远控终端的host与port，为后续的攻击溯源提供帮助，flag提交格式为：flag{host:port}

工具:

Android Killer 或者 jadx-gui-1.4.7

Android Killer

链接：https://pan.baidu.com/s/1fsu-etrR4l5uWq_8eSHzXw?pwd=fog6

![1692694034_64e4761285997e0c4158d.png!small](https://image.3001.net/images/20230822/1692694034_64e4761285997e0c4158d.png!small)

jadx-gui-1.4.7

链接：https://pan.baidu.com/s/1QVhdXgANWL_RKbSAPdCPIg?pwd=rszh

![1692694042_64e4761ab5fe83437376f.png!small](https://image.3001.net/images/20230822/1692694042_64e4761ab5fe83437376f.png!small)

SpyNote是用来创建Android恶意程序的工具。它的功能引人注目，读取联系人、录音、命令执行、应用管理、键盘记录、GPS定位等等

android.support 安卓支持包

AndroidX 本质上其实就是对Android Support Library进行的一次升级

com 待分析的代码

|—google.android.material 界面UI

|—test.easysignure 功能代码

|—connect() 我们需要分析的位置

![1692694055_64e4762709b2799654387.png!small](https://image.3001.net/images/20230822/1692694055_64e4762709b2799654387.png!small)

Ctrl+鼠标左键 跟踪变量

R.string.host

![1692694060_64e4762c9708f19c51a30.png!small](https://image.3001.net/images/20230822/1692694060_64e4762c9708f19c51a30.png!small)

R.string.port

![1692694067_64e47633b9c9aa594b34b.png!small](https://image.3001.net/images/20230822/1692694067_64e47633b9c9aa594b34b.png!small)

public static final int host = 0x7f0e0029;

public static final int port = 0x7f0e0063;

这两个变量都通过getResources().getString() 的作用是从应用程序的资源文件中获取与 host/port ID
关联的字符串，并将其作为字符串返回

直接到资源目录文件夹下寻找

![1692694154_64e4768ae53a7d2032634.png!small](https://image.3001.net/images/20230822/1692694154_64e4768ae53a7d2032634.png!small)

![1692694136_64e47678383bfd27c9dfb.png!small](https://image.3001.net/images/20230822/1692694136_64e47678383bfd27c9dfb.png!small)

答案： 221.153.25.103:666

资源定位知识点，可以参考

<https://blog.csdn.net/beyond702/article/details/51744082>

