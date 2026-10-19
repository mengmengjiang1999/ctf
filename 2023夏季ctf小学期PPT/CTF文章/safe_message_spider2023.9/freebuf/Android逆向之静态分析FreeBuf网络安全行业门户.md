想必打过CTF的小伙伴多多少少都触过Android逆向，所以斗哥将给大家整一期关于Android逆向的静态分析与动态分析。本期先带来Android逆向的静态分析，包括逆向工具使用、文件说明、例题解析等。

Android逆向就是反编译的过程，因为看不懂Android正向编译后的结果所以CTF中静态分析的前提是将出现文件反编译到我们看得懂一层源码，进行静态分析。

0X01 基础说明

Android应用的逻辑代码是由Java进行开发，所以是第一层就是java代码

Java虚拟机JVM运行的是java文件编译过后的class文件

Android虚拟机Dalvik并不是执行Java虚拟机JVM编译后生成的class文件，而是执行再重新整合打包后生成的dex文件编译之后的smali文件

APK：是编译完成后的Android应用程序安装包

dex文件：是class文件的打包文件

smali文件：是Dalvik字节码文件

class文件：是JVM字节码文件

0X02 工具使用

在CTF中Android题目不一定给你完整编译完成后的APK，可能是编译过程中任意文件类型，下面斗哥分以下文件类型利用工具来得到斗哥看得懂的java源码

类型一：class文件

这种情况比较简单，推荐工具jd-gui

直接将class文件拉进去就可以看到java源码。

  
![image.png](https://image.3001.net/images/20180831/1535686875_5b88b8db82637.png!small)  

类型二：APK程序

Android工程编译完成会得到我们想要的APK安装包，APK文件其实是一个压缩包。

修改后缀名为zip后解压，解压后的文件如下图所示：

  
![image.png](https://image.3001.net/images/20180831/1535686881_5b88b8e1858b6.png!small)  

META-INF文件夹:

存放apk签名信息，用来保证apk包的完整性和系统的安全。

res文件夹:

存放资源文件，包括icon，xml文件。

AndroidManifest.xml文件:

应用程序配置文件，每个应用都必须定义和包含的，它描述了应用的名字、版本、权限、引用的库文件等信息。

classes.dex文件:

可以直接在Dalvik虚拟机上加载运行的文件，由java文件经过IDE编译生成。

resources.arsc文件>

二进制资源文件，包括字符串等。

反编译APK推荐工具ApkIDE、JEB

1\. JEB使用：

JEB直接导入APK，反编译完成看到smali文件。

  
![image.png](https://image.3001.net/images/20180831/1535686889_5b88b8e9b00af.png!small)  

很多Android逆向工具就反编译到smali文件这步。

JEB选中smali文件中按Q，就可以看到java文件。

  
![image.png](https://image.3001.net/images/20180831/1535686895_5b88b8ef455f5.png!small)  

优点：从smali文件反编译成的java文件代码结构清晰。

缺点：无法修改。

2\. ApkIDE使用：

项目->打开Apk

等待反编译完成。

  
![image.png](https://image.3001.net/images/20180831/1535686901_5b88b8f52f0a5.png!small)  

看到smali文件。

![image.png](https://image.3001.net/images/20180831/1535686907_5b88b8fb652e1.png!small)  

选择要java源码的smali文件，点击下图按钮，打开Java源码。

![image.png](https://image.3001.net/images/20180831/1535686912_5b88b900a176d.png!small)  

ApkIDE关联了jd-gui，点击后将跳转到jd-gui。

![image.png](https://image.3001.net/images/20180831/1535686917_5b88b905e052d.png!small)  

ApkIDE是将APK反编译到class再用jd-gui拿到Java源码。

在ApkIDE的ApkIDE_v3.3\ApkIDE\Worksrc的项目目录下可以看到反编译后的class文件。

![image.png](https://image.3001.net/images/20180831/1535686924_5b88b90c0f7db.png!small)  

优点：功能强大，可以修改反编译出来的smali文件，重新编译生成APK。

缺点：编译成后的java代码不够清晰。

3.反编译区别

Smali文件是由Smali语法编写，Smali语法宽松式的语法

所以反编译过程不同，工具不同，java源码肯定不同

下面是同一个APK用上面两个工具逆向的结果：

![image.png](https://image.3001.net/images/20180831/1535686930_5b88b91257e9b.png!small)

![image.png](https://image.3001.net/images/20180831/1535686935_5b88b917c1f5e.png!small)

  

斗哥作为一名Java开发的爱好者喜欢JEB的逆向结果，看着比较舒服。

类型三：dex文件

推荐工具dex2.jar

classes.dex文件，这个是Android源码编译过的字节码包

尝试使用dex2.jar工具拿到java源码命令如下

.\d2j-dex2jar.bat C:\Users\lin\Desktop\classes.dex

  
![image.png](https://image.3001.net/images/20180831/1535686942_5b88b91e71410.png!small)  

jar文件可以理解为classes文件的压缩包，java虚拟机可以直接运行

用Jd-gui打开classes-dex2jar.jar就可以看到java源码

  
![image.png](https://image.3001.net/images/20180831/1535686946_5b88b9228c48f.png!small)  

类型四：smali文件

当只有一个单独的smali文件时就无法用上述的工具直接进行反编译

斗哥想到ApkIDE可以对一个APK进行反编译到smali文件，对smali文件进行增删改查的操作

于是用ApkIDE打开任意一个完整的APK然后添加smali文件（APK可以用自己开发的）

  
![image.png](https://image.3001.net/images/20180831/1535686954_5b88b92ac4471.png!small)  

将smali文件添加ApkIDE项目中。

  
![image.png](https://image.3001.net/images/20180831/1535686959_5b88b92f7e282.png!small)  

重新编译生成APK。

![image.png](https://image.3001.net/images/20180831/1535686965_5b88b93551475.png!small)  

编译成功后将在原APK目录生成一个APK。

  
![image.png](https://image.3001.net/images/20180831/1535686969_5b88b939ef436.png!small)  

再用JEB等工具打开就能看到Ezreal.smali文件。

  
![image.png](https://image.3001.net/images/20180831/1535686974_5b88b93e42a4e.png!small)  

其他工具：

编辑器：notepad++、Sublime等

Android模拟器：夜神模拟器等

0X04 例题分析

将应用安装到模拟器查看界面是否有提示。

在文本框输入字符点击按钮提示错误，猜想是否用来判断正确的flag。

  
![image.png](https://image.3001.net/images/20180831/1535686981_5b88b9455c39b.png!small)  

使用JEB工具编译成java文件，Android文件下是sdk文件，我们要分析是com包下的源码文件。

  
![image.png](https://image.3001.net/images/20180831/1535686986_5b88b94ab59ee.png!small)  

代码量不多就三个类，先从程序入口MainActivity分析，找到关键代码块。

这句if就是判断flag是否正确。

![image.png](https://image.3001.net/images/20180831/1535686999_5b88b957866ff.png!small)  

搜索类查看哪里调用了此方法。

分析得到arg12就是界面要输入的参数，这时我们知道了v5的值就是我们要的flag。

  
![image.png](https://image.3001.net/images/20180831/1535687007_5b88b95f99c03.png!small)  

onCreate函数调用了checkSN方法并传入两个参数为：

MainActivity.this.edit_userName.trim()

MainActivity.this.edit_sn.getText().toString().trim()

  

//OnCreate是Android中的一个特别的函数，用来“表示一个窗口正在生成”。

//其不产生窗口，只是在窗口显示前设置窗口的属性如风格、位置颜色等。

public void onCreate(Bundle arg3) {

super.onCreate(arg3);

this.setContentView(0x7F040019);

this.setTitle(0x7F06001D);

this.edit_userName = "Tenshine";

this.edit_sn = this.findViewById(0x7F0C0051);

this.btn_register = this.findViewById(0x7F0C0052);

this.btn_register.setOnClickListener(new View$OnClickListener() {

public void onClick(View arg5) {

if(!MainActivity.this.checkSN(MainActivity.this.edit_userName.trim(),
MainActivity.this.edit_sn.getText().toString().trim())) {

Toast.makeText(MainActivity.this, 0x7F06001E, 0).show();

}

else {

Toast.makeText(MainActivity.this, 0x7F06001B, 0).show();

MainActivity.this.btn_register.setEnabled(false);

MainActivity.this.setTitle(0x7F060019);

}

}

});

}

  

分析v5的值，v5是由v3和v4生成的，v4是一个int并直接赋值为0用于循环就可以直接使用

而v3则是toHexString方法的返回值，并要传入，v1是v1.update(arg11.getBytes());生成

arg11就是传入的参数"Tenshine"

  

private boolean checkSN(String arg11, String arg12) {

boolean v7 = false;

if(arg11 != null) {

try {

if(arg11.length() == 0) {

return v7;

}

if(arg12 == null) {

return v7;

}

if(arg12.length() != 22) {

return v7;

}

MessageDigest v1 = MessageDigest.getInstance("MD5");

v1.reset();

v1.update(arg11.getBytes());

String v3 = MainActivity.toHexString(v1.digest(), "");

StringBuilder v5 = new StringBuilder();

int v4;

for(v4 = 0; v4 < v3.length(); v4 += 2) {

v5.append(v3.charAt(v4));

}

if(!"flag{" + v5.toString() + "}".equalsIgnoreCase(arg12)) {

return v7;

}

}

catch(NoSuchAlgorithmException v2) {

goto label_40;

}

v7 = true;

}

return v7;

label_40:

v2.printStackTrace();

return v7;

}

  

将上面的分析结果，取出生成v5的关系代码

都是纯java代码，不需要Android的包引入，只需引入java的依赖包。

  
  

import java.security.MessageDigest;

import java.security.NoSuchAlgorithmException;

public class Code {

static String toHexString(byte[] arg8, String arg9) {

StringBuilder v3 = new StringBuilder();

byte[] v0 = arg8;

int v5 = v0.length;

int v4;

for(v4 = 0; v4 < v5; ++v4) {

String v2 = Integer.toHexString(v0[v4] & 255);

if(v2.length() == 1) {

v3.append('0');

}

v3.append(v2).append(arg9);

}

return v3.toString();

}

public static void main(String[] args)throws NoSuchAlgorithmException{

MessageDigest v1 = MessageDigest.getInstance("MD5");

v1.reset();

v1.update("Tenshine".getBytes());

String v3 = Code.toHexString(v1.digest(), "");

StringBuilder v5 = new StringBuilder();

int v4;

for(v4 = 0; v4 < v3.length(); v4 += 2) {

v5.append(v3.charAt(v4));

}

System.out.println("flag{" + v5.toString() + "}");

}

}

  

用IDEA编辑运行，拿到flag。

  
![image.png](https://image.3001.net/images/20180831/1535687056_5b88b9909ab98.png!small)  

0X05 小小总结

下期斗哥将带来Android逆向之动态分析，讲述Android开发入门、smali语法解析、动态调式smali文件。

# 大家有任何问题可以提问，更多文章可到[i春秋论坛](https://bbs.ichunqiu.com/portal.php?from=beef)阅读哟~

