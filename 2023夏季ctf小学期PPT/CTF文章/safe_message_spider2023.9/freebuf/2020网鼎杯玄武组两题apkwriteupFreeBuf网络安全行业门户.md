上周参加了网鼎杯玄武组比赛，现在把两题apk的解题过程分享出来，水平太菜，大佬路过勿喷。

## 题目名称：java

题目类型：Reverse

下载题目
[java.zip](https://github.com/kafroc/kafroc.github.io/blob/master/assets/misc/java.zip)，
解压发现一个文件java.apk

用[jadx-gui](https://github.com/skylot/jadx/releases)打开java.apk

![2020-05-25_115851.jpg](https://image.3001.net/images/20200525/1590389139_5ecb6993dde16.jpg!small)

![](2020-05-25_115851.jpg)

## 分析MainActivity

    
    
        c p;
    
        /* access modifiers changed from: protected */
        public void onCreate(Bundle bundle) {
            ...
            this.n.setOnClickListener(new View.OnClickListener() {
                public void onClick(View view) {
                    MainActivity mainActivity;
                    String str;
                    MainActivity.this.o = MainActivity.this.m.getText().toString();
                    MainActivity.this.p = new c();
                    if (MainActivity.this.o == null) {
                        mainActivity = MainActivity.this;
                        str = "Need Input";
                    } else if (MainActivity.this.p.a(MainActivity.this.o)) {
                        mainActivity = MainActivity.this;
                        str = "Congratulations";
                    } else {
                        mainActivity = MainActivity.this;
                        str = "Wrong Flag";
                    }
                    Toast.makeText(mainActivity, str, 1).show();
                }
            });
        }
    

关键点在于下面几行代码

    
    
    MainActivity.this.o = MainActivity.this.m.getText().toString();
    
    ...
    
    } else if (MainActivity.this.p.a(MainActivity.this.o)) {
                        mainActivity = MainActivity.this;
                        str = "Congratulations";
    

用户输入的字符串应该就是flag，调用MainActivity.this.p.a校验flag，如果校验成功就输出Congratulations

而p是class c的实例，我们去看看class c

## 分析class c

class c的代码如下

    
    
    public class c {
        public static String a = "aes_check_key!@#";
        public static String b = "VsBDJCvuhD65/+sL+Hlf587nWuIa2MPcqZaq7GMVWI0Vx8l9R42PXWbhCRftoFB3";
        int[] c = {214, 144, 233, 254, 204, 225, 61, 183, 22, 182, 43, a.j.AppCompatTheme_textColorAlertDialogListItem, 20, 194, 40, 251, 44, 5, 43, a.j.AppCompatTheme_textColorAlertDialogListItem, 154, a.j.AppCompatTheme_windowMinWidthMinor, 42, 190, 4, 195, 43, a.j.AppCompatTheme_textColorAlertDialogListItem, 170, 68, 19, 38, 73, 134, 43, a.j.AppCompatTheme_textColorAlertDialogListItem, 153, 156, 66, 80, 244, 145, 80, a.j.AppCompatTheme_textColorAlertDialogListItem, 239, 152, 122, 98, 50, 214};
        d d;
    
        public boolean a(String str) {
            byte[] bArr = new byte[0];
            byte[] a2 = e.a(str.getBytes(), a.getBytes());
            this.d = new d();
            this.d.a(a2, 22, this.c);
            return new String(b.a(a2)).equals(b);
        }
    }
    

这里是破解的关键，我们来梳理一下流程  
第一步 aes加密  
byte[] a2 = e.a(str.getBytes(), a.getBytes());

第二步 异或运算  
this.d.a(a2, 22, this.c);

第三步 base64编码  
new String(b.a(a2))

第四步 比较结果  
new String(b.a(a2)).equals(b);  
比较第三步的结果与b是否一致，而b为"VsBDJCvuhD65/+sL+Hlf587nWuIa2MPcqZaq7GMVWI0Vx8l9R42PXWbhCRftoFB3"

到这里，解题思路就很清晰了，逆向整个算法  
第一步  
把b通过base64解编码，结果赋值给x

第二步  
把x经过异或运算，结果赋值给y

第三步  
把y经过aes解密，结果赋值给z，z则为我们要的flag

实现脚本如下：

    
    
    import base64
    from Crypto.Cipher import AES
    
    b = "VsBDJCvuhD65/+sL+Hlf587nWuIa2MPcqZaq7GMVWI0Vx8l9R42PXWbhCRftoFB3"
    
    c = [214, 144, 233, 254, 204, 225, 61, 183, 22, 182, 43, 103, 20, 194, 40, 251, 44, 5, 43, 103, 154, 118, 42, 190, 4,
         195, 43, 103, 170, 68, 19, 38, 73, 134, 43, 103, 153, 156, 66, 80, 244, 145, 80, 103, 239, 152, 122, 98, 50, 214]
    
    x = base64.b64decode(b)
    
    y = []
    for i in range(len(x)):
        y.append(x[i] ^ 22 ^ c[i])
    y = bytes(y)
    
    aeskey = 'aes_check_key!@#'
    cipher = AES.new(aeskey, AES.MODE_ECB)
    z = cipher.decrypt(y)
    
    print(z)
    

执行上述脚本，发现解密后的数据不对，再回去看看apk代码，发现在App类中，有一行代码

    
    
    c.a = c.a.replace("e", "o");
    

而c.a就是我们看到的aes密钥

    
    
    public class c {
        public static String a = "aes_check_key!@#";
    

那只要把上述python脚本中，把aeskey = 'aes_check_key!@#'替换为aeskey =
'aes_check_key!@#'.replace('e', 'o').encode()即可解题成功

## 题目名称：vulcrack

题目类型：misc

下载
[vulcrack.zip](https://github.com/kafroc/kafroc.github.io/blob/master/assets/misc/vulcrack.zip)，解压发现vulcrack.apk

用jadx-gui打开apk，发现assets中有libjiagu.so，是用360加固了

先脱壳

## 手机端准备工作

把[frida-server](https://github.com/frida/frida/releases)传入手机

通过adb install vulcrack.apk安装apk

启动frida-server并打开vulcrack app

## pc端准备工作

下载脱壳工具，<https://github.com/hluwa/FRIDA-DEXDump>

进入FRIDA-DEXDump执行python main.py

即可在FRIDA-DEXDump目录下看到dump出来的dex文件

用jadx-gui打开dex文件

![2020-05-25_120946.jpg](https://image.3001.net/images/20200525/1590389174_5ecb69b65efc0.jpg!small)

![](2020-05-25_120946.jpg)

flag的逻辑如下

    
    
    public class Flag {
        public static String keyFirst = "Zm1jan85NztBN0c0NjJIOzJGLzc8STk0OTZFSDE=";
        public static String keySecond = "QTpISTlFNEkxRTY8fQ==";
    
        public static String calcFlagFirstStep() {
            return comm(Base64.decodeToString(keyFirst), 8);
        }
    
        public static String calcFlagSecondStep() {
            return comm(Base64.decodeToString(keySecond), 4);
        }
    
        public static String comm(String str, int num) {
            byte[] cmdbyte = str.getBytes();
            for (byte i = 0; i < cmdbyte.length; i = (byte) (i + 1)) {
                cmdbyte[i] = (byte) (cmdbyte[i] - (i % num));
            }
            try {
                return new String(cmdbyte, "UTF-8");
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
                return "";
            }
        }
    }

上面这个Flag类提供两个方法calcFlagFirstStep, calcFlagSecondStep, 调用者调用者两个方法即可获取Flag内容

其实这题的主要难点在于怎么脱壳，脱完壳，flag的逻辑非常简单，只要复现上面的过程，并调用即可

编写python解密代码vulcrack.py如下

    
    
    import base64
    
    keyFirst = "Zm1jan85NztBN0c0NjJIOzJGLzc8STk0OTZFSDE="
    keySecond = "QTpISTlFNEkxRTY8fQ=="
    
    def comm(key, num):
        ns = []
        for i in range(len(key)):
            ns.append(key[i] - (i % num))
        print(bytes(ns))
    
    comm(base64.b64decode(keyFirst), 8)
    comm(base64.b64decode(keySecond), 4)
    

执行python vulcrack.py即可获取flag

