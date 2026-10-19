## 0x00 前言

这是安卓 CTF 实战系列的第四个案例，本系列以实战方式，分享安卓渗透与逆向分析相关的技术。朋友们可以下载 CTF 的 apk 文件，进行分析学习。

这个案例还是比较有意思的，本文将会分享 **四种获取 flag 值的解题思路** ，一起动手实战一下吧！

本文涉及技术：

  * 熟悉 Jadx-gui 和 Android killer 工具

  * hook 技术（Frida，Objection）

  * 静态分析 IDA pro

  * 动态调试技术

  * Java 代码编写

> 本案例所需要的 apk 文件，已经上传到知识星球，需要的朋友可以到文末关注后下载。

## 0x01 准备分析

首先下载需要的的 apk 文件（apk文件已经上传到知识星球，需要的朋友可以到文末关注后下载），安装看看。

![1660659572_62fba774b09ff154f9047.png!small?1660659572851](https://image.3001.net/images/20220816/1660659572_62fba774b09ff154f9047.png!small?1660659572851)

只能看到一些提示信息，使用反编译工具查看，

![1660659586_62fba7824d81e4791515b.png!small?1660659586699](https://image.3001.net/images/20220816/1660659586_62fba7824d81e4791515b.png!small?1660659586699)

在这里发现，除了 MainActivity 之外，还有三个 Activity，但是在界面中无法直接触发。

分析反编译之后的代码：

![1660659600_62fba7909abae94e4d3c5.png!small?1660659600892](https://image.3001.net/images/20220816/1660659600_62fba7909abae94e4d3c5.png!small?1660659600892)

发现在 IsThisTheRealOne、DefinitelyNotThisOne、ThisIsTheRealOne 活动中，点击按钮，会触发广播，flag
值应该就在广播信息中，接下来就是要获取广播的信息内容。

## 0x02 解法一：修改代码

第一个种解法，可以修改smali代码，打印消息日志，获取 flag 值。这里可以使用 Android killer 这个工具对 apk 解码出来的
smali 代码以及 配置文件进行更改后，再重新打包发布

###  **1、修改AndroidManifest.xml**

在以下这个三个 Activity 中添加`android:exported="true"`，作用是允许其它应用调用它，修改完这个属性之后，可以使用`adb
shell am start -n 应用包名/活动名称`来启动相应的活动：

![1660659636_62fba7b4df864c31a6374.png!small?1660659637412](https://image.3001.net/images/20220816/1660659636_62fba7b4df864c31a6374.png!small?1660659637412)

###  **2、 修改smali代码**

IsThisTheRealOne$1.smali 中加入以下日志相关代码：

![1660659650_62fba7c28adb96d332cdf.png!small?1660659650784](https://image.3001.net/images/20220816/1660659650_62fba7c28adb96d332cdf.png!small?1660659650784)

DefinitelyNotThisOne$1.smali 中加入以下日志相关代码：

![1660659663_62fba7cf3e36ca0c6c35b.png!small?1660659663457](https://image.3001.net/images/20220816/1660659663_62fba7cf3e36ca0c6c35b.png!small?1660659663457)

ThisIsTheRealOne$1.smali 中加入以下日志相关代码：

![1660659674_62fba7dac9bd2000ad1c4.png!small?1660659675020](https://image.3001.net/images/20220816/1660659674_62fba7dac9bd2000ad1c4.png!small?1660659675020)

保存之后，重新编译打包，安装到手机。

###  **3、查看日志**

使用 adb 命令启动相应的 Activity。

 **1、启动 DefinitelyNotThisOne**

    
    
    adb shell am start -n com.example.hellojni/com.example.application.DefinitelyNotThisOne

点击按钮，查看日志，

![1660659684_62fba7e44a80ab2d84bff.png!small?1660659684513](https://image.3001.net/images/20220816/1660659684_62fba7e44a80ab2d84bff.png!small?1660659684513)

 **2、启动 ThisIsTheRealOne**

    
    
    adb shell am start -n com.example.hellojni/com.example.application.ThisIsTheRealOne

查看日志：

![1660659711_62fba7ff0666ad648a177.png!small?1660659711139](https://image.3001.net/images/20220816/1660659711_62fba7ff0666ad648a177.png!small?1660659711139)

 **3、启动 IsThisTheRealOne**

    
    
    adb shell am start -n  com.example.hellojni/com.example.application.IsThisTheRealOne

查看日志：

![1660659721_62fba809803bfeb6f7cbc.png!small?1660659721737](https://image.3001.net/images/20220816/1660659721_62fba809803bfeb6f7cbc.png!small?1660659721737)

这里已经拿到 flag 值了。

## 0x03 解法二：hook

第二种解法，可以使用 Frida 或者 Objection 工具进行 hook，这样不需要修改 smali 代码，也可以拿到 flag 值。

分析发现三个 Activity 代码，都使用了`android.content.Intent.putExtra`方法，所以可以 hook 这个方法：

![1660659739_62fba81b4eedaacb67ab2.png!small?1660659739758](https://image.3001.net/images/20220816/1660659739_62fba81b4eedaacb67ab2.png!small?1660659739758)

### 3.1 使用 objection 进行hook

 **1、启动 objection**

    
    
    objection -g com.example.hellojni explore

watch 这个`android.content.Intent.putExtra`方法：

    
    
    android hooking watch class_method android.content.Intent.putExtra --dump-args -  
    -dump-backtrace --dump-return   

![1660659754_62fba82a3bc8601dcfb06.png!small?1660659754544](https://image.3001.net/images/20220816/1660659754_62fba82a3bc8601dcfb06.png!small?1660659754544)

**2、使用 adb 分别启动三个活动**

    
    
    adb shell am start -n  com.example.hellojni/com.example.application.IsThisTheRealOne

查看 objection 显示信息，

![1660659795_62fba8532a617c6c34c6b.png!small?1660659795728](https://image.3001.net/images/20220816/1660659795_62fba8532a617c6c34c6b.png!small?1660659795728)

拿到 flag 值。

### 3.2 使用 frida 进行hook

objection 是基于 frida 开发的，当然我们可以自己编写脚本进行 hook：

![1660659809_62fba8613c5e3a57a1445.png!small?1660659809468](https://image.3001.net/images/20220816/1660659809_62fba8613c5e3a57a1445.png!small?1660659809468)

启动 活动

    
    
    adb shell am start -n  com.example.hellojni/com.example.application.IsThisTheRealOne

启动 frida

    
    
    frida -U com.example.hellojni -l hook1.js

加载 test() 函数，点击屏幕按钮，可以看到 hook 的结果：

![1660659827_62fba873f251efca637d4.png!small?1660659828679](https://image.3001.net/images/20220816/1660659827_62fba873f251efca637d4.png!small?1660659828679)

拿到 flag 值。

## 0x04 解法三：静态分析

第三种解法，不需要修改代码，使用静态分析获取 flag ，过程会比较麻烦一些，纯碎是多一种思路

###  **1、我们可以分析以下这四个 native 方法**

    
    
    public native String computeFlag(String str, String str2);  
    public native String definitelyNotThis(String str, String str2, String str3);  
    public native String orThat(String str, String str2, String str3);  
    public native String perhapsThis(String str, String str2, String str3);

这里就拿 IsThisTheRealOne 活动中的 onClick 来分析：

![1660659846_62fba8860461ba6ed85c1.png!small?1660659846944](https://image.3001.net/images/20220816/1660659846_62fba8860461ba6ed85c1.png!small?1660659846944)

###  **2、分析代码，可以发现， a , b, c 这三个值我们可以获取**

    
    
    String a = "TRytfrgooq|F{i-JovFBungFk" + "\\VlphgQbwvj~HuDgaeTzuSt.@Lex^~";  
    String b = doBoth("SendAnIntentApplication");  
    String className = "com.example.application.IsThisTheRealOne$1";  
    String c = doBoth(className.substring(0,className.length()-2));

接下来就是 将 a ，b，c 传入 perhapsThis 方法，要分析这个方法，就要分析 so 文件，使用 IDA pro
进行静态分析，找到`Java_com_example_application_IsThisTheRealOne_perhapsThis`，使用 F5 转为
c/c++ 的伪代码，进行分析：

![1660659857_62fba891df105ba981e8f.png!small?1660659858316](https://image.3001.net/images/20220816/1660659857_62fba891df105ba981e8f.png!small?1660659858316)

###  **3、分析代码，可以使用 java 代码等价实现关键代码**

![1660659872_62fba8a0e26f6559dd417.png!small?1660659873248](https://image.3001.net/images/20220816/1660659872_62fba8a0e26f6559dd417.png!small?1660659873248)

###  **4、最后，写一个完整的 Java 脚本**

    
    
    import java.security.MessageDigest;  
    import java.security.NoSuchAlgorithmException;  
    import java.util.Base64;  
    import java.util.HashMap;  
    import java.util.Map;  
    ​  
    public class CTF4test {  
    public static void main(String args[]){  
    String a = "TRytfrgooq|F{i-JovFBungFk" + "\\VlphgQbwvj~HuDgaeTzuSt.@Lex^~";  
    System.out.println(a);  
    String b = doBoth("SendAnIntentApplication");  
    System.out.println(b);  
    String className = "com.example.application.IsThisTheRealOne$1";  
    String c = doBoth(className.substring(0,className.length()-2));  
    System.out.println(c);  
    ​  
    String flag = perhapsThis(a,b,c);  
    System.out.println("---------------------------------------------");  
    System.out.println(flag);  
    }  
    public static String perhapsThis(String a,String b,String c){  
    byte[] bs = {0x77,0x6E,0x77,0x47,0x72,0x61,0x62,0x7B,0x4F,0x75,0x74,0x62,0x68,0x7F,0x72,0x43,0x74,0x66,0x71,0x6D,0x7D};  
    a = a + new String(bs);  
    System.out.println(a);  
    String result = "";  
    int tmp;  
    for(int i=0;i<76;i++){  
    char x = a.substring(i,i+1).toCharArray()[0];  
    char y = b.substring(i,i+1).toCharArray()[0];  
    char z = c.substring(i,i+1).toCharArray()[0];  
    tmp = z ^ y ^ x;  
    result += (char)tmp;  
    }  
    return result;  
    }  
    ​  
    public static String doBoth(String input) {  
    return translate(customEncodeValue(input));  
    }  
    ​  
    public static String translate(String input) {  
    char[] inputchars = input.replace('=', '?').toCharArray();  
    Map<Integer, Character> table = new HashMap<>();  
    int[] numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 0};  
    char[] characters = {'W', 'h', 'a', 't', 'i', 's', 'd', 'o', 'n', 'e'};  
    for (int i = 0; i < 10; i++) {  
    table.put(Integer.valueOf(numbers[i]), Character.valueOf(characters[i]));  
    }  
    for (int i2 = 0; i2 < inputchars.length; i2++) {  
    char c = inputchars[i2];  
    if (c > '/' && c < ':') {  
    int charcode = c - '0';  
    inputchars[i2] = table.get(Integer.valueOf(charcode)).charValue();  
    }  
    }  
    return new String(inputchars);  
    }  
    ​  
    public static String customEncodeValue(String input) {  
    String output = "";  
    byte[] input_bytes = input.getBytes();  
    MessageDigest md = null;  
    try {  
    md = MessageDigest.getInstance("SHA-224");  
    } catch (NoSuchAlgorithmException e) {  
    }  
    md.update(input_bytes, 0, input_bytes.length);  
    byte[] hash_bytes = md.digest();  
    for (int i = 0; i < hash_bytes.length; i++) {  
    output = output + String.format("%02x", Byte.valueOf(hash_bytes[i]));  
    }  
    return Base64.getEncoder().encodeToString(output.getBytes());  
    }  
    }

###  **5、运行脚本得到 flag**

![1660659890_62fba8b2b56b323ff8eed.png!small?1660659891416](https://image.3001.net/images/20220816/1660659890_62fba8b2b56b323ff8eed.png!small?1660659891416)

## 0x05 解法四：动态调试

使用 android studio 或者 Jeb 工具动态调试 apk 文件，也可以得到 flag。

也可以通过 IDA Pro 动态调试 so 文件，得到 flag 值。

这两种调试的具体过程和方法，将会在接下来的两篇文章进行分享。

