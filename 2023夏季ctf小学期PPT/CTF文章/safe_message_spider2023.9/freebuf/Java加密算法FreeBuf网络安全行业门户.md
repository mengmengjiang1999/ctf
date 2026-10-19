# 1.基础知识

密码学：主要是研究 **编制密码** 和 **破译密码** 的学科

密码学的主要目的：简单的直接说就是，研究如何隐藏信息并且把信息传递出去的一个学科。

## 1.1密码学的历史

### 1.1.1古典密码学

古代就开始使用密码，目的：就是希望保护信息。

核心原理：替换法，移位法

①替换法：

就是使用固定的信息，将原文替换成密文。

例如：bee，将b替换成w，e替换成p，单词就变成了wpp。

替换法的加密方式： **单表替换** 、 **多表替换**

  * 单表替换：原文和密文使用的是同一张表  
例如：abcde ------> swtrp

  * 多表替换：表示有多张表，原文和密文进行对比  
表单1：abcde-swtrp、表单2：abcde-chfhk、表单3：abcde-jftou  
原文：bee  
密钥：312  
密文：fpk

②移位法：

移位法是按照字母，在字母表上面的位置，进行移动

凯撒加密

### 1.1.2近代密码学

### 1.1.3现代密码学

  * 散列函数

MD5，SHA-1，SHA-256，SHA-512

  * 对称加密

    * 加密方式和解密方式，使用的是同一把密钥

DES加密和解密，AES加密和解密

对称加密的核心原理：流加密，块加密

toString()和new String()核心原理和区别

加密模式：ECB CBC

填充模式：NoPadding和PKCS5padding

  * 非对称加密

    * 有两把密钥，使用公钥加密，必须使用私钥解密，或者，私钥加密，必须使用公钥解密

非对称加密的特点

RSA算法和ECC算法

数字摘要

base64核心加密原则，和base64原理

数字签名和数字证书

keytool工具的使用

## 1.2 ASCII编码

JAVA代码例子

### maven依赖

首先导入一下`commons-io`的maven依赖

    
    
    <dependency>
                <groupId>commons-io</groupId>
                <artifactId>commons-io</artifactId>
                <version>2.11.0</version>
    </dependency>
    

### JavaDemo

#### charDemo

    
    
    package com.red.javacodeaudit.encode;
    
    public class AsciiDemo {
        public static void main(String[] args) {
            char a = 'A';
            int b = a;
            //打印出来A字母的ascii编码的大小
            System.out.println(b);
        }
    }
    

可以看到就是A->65，这里直接对`char`和`int`类型进行转换。  
![image](https://image.3001.net/images/20210927/1632732699_6151861b6358d311039e1.png!small)

#### StringDemo

    
    
    public class AsciiDemo {
        public static void main(String[] args) {
            String str = "rebeyond";
            char[] chars = str.toCharArray();
            for (char aChar : chars) {
                int i = aChar;
                System.out.println(i);
            }
        }
    }
    

其实平时我们基本不会总是用到`char`来定义字符，更多的都是用到`String`来定义字符串，这里利用了`toCharArray`方法来返回一个`char[]`数组，然后转化成`ascii`形式  
![image](https://image.3001.net/images/20210927/1632732725_61518635133f81323da35.png!small)

### 凯撒加密

#### CaesarDemo

    
    
    public static void main(String[] args) {
            String input = "Hello World";
            int key = 3;
            char[] chars = input.toCharArray();
            StringBuilder sb = new StringBuilder();
            for (char aChar : chars) {
                int b = aChar;
                b = b + key;
                char newchar = (char) b;
                sb.append(newchar);
            }
            System.out.println(sb.toString());
    }
    

我们知道凯撒加密就是简单的移位法，然后这里`key`设置成3，强调一个知识点就是`StringBuilder`这个类，我们将`char`数组想要转换成`String`类型的字符串的时候是需要这个类的`append`方法来实现的。这里就是加密之后的数据`Khoor#Zruog`  
![image](https://image.3001.net/images/20210927/1632732746_6151864a6a99d741daa3d.png!small)

### 凯撒解密

知道这里需要传入一个密文，和一个解密的key，参数就是这两个，然后返回的是一个`String`类型的明文

    
    
    private static String decryptCaesar(String newStr, int key) {
            char[] chars = newStr.toCharArray();
            StringBuilder sb = new StringBuilder();
            for (char aChar : chars) {
                int i = aChar;
                i -= key;
                char newChar = (char) i;
                sb.append(newChar);
            }
            return sb.toString();
    }
    

## 完整Demo代码

    
    
    package com.red.javacodeaudit.encode;
    
    public class CaesarDemo {
        public static void main(String[] args) {
            String input = "Hello World";
            int key = 3;
            String newStr = encryptCaesar(input, key);
            System.out.println("密文===>"+newStr);
            String str = decryptCaesar(newStr,key);
            System.out.println("明文===>"+str);
        }
    
        private static String decryptCaesar(String newStr, int key) {
            char[] chars = newStr.toCharArray();
            StringBuilder sb = new StringBuilder();
            for (char aChar : chars) {
                int i = aChar;
                i -= key;
                char newChar = (char) i;
                sb.append(newChar);
            }
            return sb.toString();
        }
    
        private static String encryptCaesar(String input, int key) {
            char[] chars = input.toCharArray();
            StringBuilder sb = new StringBuilder();
            for (char aChar : chars) {
                int b = aChar;
                b = b + key;
                char newchar = (char) b;
    //            System.out.print(newchar);
                sb.append(newchar);
            }
            return sb.toString();
        }
    }
    

![image](https://image.3001.net/images/20210927/1632732790_6151867634abd59ef96c6.png!small)

## 1.3 频率分析法

目的：在不知道密钥的情况下，也想破解秘文

我认为这里我应该自己写出来这个工具类，来完善一下自己的java开发水平

 **原理** ：字母e，出现的频率是最高的，第二高的是t，然后就是a

这里代码我就放到github上了这里就不具体演示了，知道怎么做就好.

[Github链接](https://github.com/Tuantuan6560/JavaCodeAudit)，第一次写这种项目，写的非常的乱

## 1.4 byte和bit的关系

byte：就是所谓的 **字节** ，数据存储的基本单位，比如移动硬盘1T，单位事byte

bit： **比特** ，又叫做 **位**
，一位要么是0要么是1。数据传输的单位，比如家里的宽带是100MB，下载速度并没有达到100MB，一般都是12-13MB，那是因为需要100/8的速度来看。

 **1byte = 8bit**

### 代码示例

    
    
    public static void main(String[] args) {
            String str = "a";
            byte[] bytes = str.getBytes();
            for (byte aByte : bytes) {
                int c = aByte;
                System.out.println(c);
            }
    }
    

这里输出的结果就是`97`，对应`a`的`ascii`编码。

之后我看查看一下97的bit形式,`Integer`类下有一个`toBinaryString()`方法，可以将字节转化成比特，然后返回一个字符串

`String s = Integer.toBinaryString(c);`得到结果`1100001`.  
![image](https://image.3001.net/images/20210927/1632732828_6151869c37cf9349ec6f1.png!small)

## 1.5 中文英文对应的字节

这里代码先写出来，然后显示一下`红`的字节编码

    
    
    package com.red.javacodeaudit.encode.ByteBit;
    
    public class bytebit {
        public static void main(String[] args) {
            String str1 = "a";
            String str2 = "红";
    
            ByteToBit(str2);
        }
    
        public static void ByteToBit(String str){
            byte[] bytes = str.getBytes();
            for (byte aByte : bytes) {
                System.out.println(aByte);
                String s = Integer.toBinaryString(aByte);
                System.out.println(s);
            }
        }
    }
    

可以看到这里是一个中文汉字是3个字节，因为这里是UTF-8编码，如果是UTF-8一个中文对应的是三个字节  
![image](https://image.3001.net/images/20210927/1632732848_615186b060954d093db9b.png!small)  
这里修改一下代码`byte[] bytes =
str.getBytes("GBK");`设置成GBK编码之后，就会变成两个字节，如果是GBK一个中文对应的是两个字节  
![image](https://image.3001.net/images/20210927/1632732864_615186c02f40cb2307925.png!small)  
如果是英文，就没有编码的概念了，全部对应的是一个字节

# 2.对称加密

  * 采用单密钥系统的加密方法，同一个密钥可以同时加密和解密，也成单密钥加密。

  * 常见加密算法

    * DES

    * AES

  * 特点

    * 加密速度快，可以加密大文件

    * 密文可逆，一旦密钥文件泄露，就会导致数据暴露

    * 加密后编码表找不到对应字符，出现乱码

    * 一般结合Base64使用

## 2.1 DES

### 2.1.1 Cipher加密对象

根据java官方API的描述：该类提供加密和解密的加密密码的功能。 它构成了Java加密扩展（JCE）框架的核心。

为了创建一个Cipher对象，应用程序调用Cipher的`getInstance`方法，并将所请求的转换的名称传递给它。 可选地，可以指定提供者的名称。

转换是描述要在给定输入上执行的操作（或操作集）的字符串，以产生一些输出。 转换总是包括加密算法的名称（例如， DES），并且可以跟随有反馈模式和填充方案。

转换形式如下：

  * “ 算法/模式/填充”或

  * “ 算法”

（在后一种情况下，使用模式和填充方案的提供者特定的默认值）。 例如，以下是有效的转换：

    
    
    Cipher c = Cipher.getInstance("DES/CBC/PKCS5Padding");
    

我们新建一个`Cipher`的时候需要调用`getInstance`函数，里边的参数是“算法/模式/填充”或者仅仅是“算法”。

### 2.1.2 DES代码示例

加密一段数据，首先需要原文和密钥

    
    
    public class DesDemo {
        public static void main(String[] args) throws NoSuchPaddingException, NoSuchAlgorithmException {
            String data = "小红爱JAVA";
            String key = "12345678";
            String transformation = "DES";//这里是加密算法
          	String algoritm = "DES";//这里是加密规则，跟加密算法是有区别的，但是这里先理解成是一个东西
            Cipher cipher = Cipher.getInstance(transformation);
        }
    }
    

这里就得到了一个完整的`cipher`对象，之后需要对对象进行`init`，其中有两个参数

  * 行为模式--->`ENCRYPT_MODE`就是加密，因为cipher对象可以加密也可以解密，所以需要声明这个对象是用来加密的还是解密的  
![image](https://image.3001.net/images/20210927/1632732930_61518702d38449f144787.png!small)

  * 加密规则--->`SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(), algoritm)`这里就是`new`一个加密规则。

    
    
    String data = "小红爱JAVA";
    String key = "12345678";
    String transformation = "DES";
    String algoritm = "DES";
    Cipher cipher = Cipher.getInstance(transformation);
    SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(), algoritm);//new一个加密规则
    cipher.init(Cipher.ENCRYPT_MODE,secretKeySpec);
    

这里的`init`用到的就是这个构造方法  
![image](https://image.3001.net/images/20210927/1632732972_6151872caacbd44ec2601.png!small)  
我们可以看到`SecretKeySpec`是实现了`SecretKey`接口，`SecretKey`接口继承的`Key`类，所以本质上还是一个`Key`.  
![image](https://image.3001.net/images/20210927/1632732989_6151873da43d02b29c748.png!small)  
现在有了一个加密的`cipher`对象之后，就要执行加密方法了就是`doFinal()`，需要传入原文的`byte[]`数组，也会返回一个`byte[]`数组。  
![image](https://image.3001.net/images/20210927/1632733003_6151874b186e6c62065fc.png!small)加密后的代码是这个样子

    
    
    public class DesDemo {
        public static void main(String[] args) throws Exception {
            String data = "小红爱JAVA";
            String key = "12345678";
            String transformation = "DES";
            String algoritm = "DES";
            Cipher cipher = Cipher.getInstance(transformation);
            SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(), algoritm);
            cipher.init(Cipher.ENCRYPT_MODE,secretKeySpec);
            byte[] bytes = cipher.doFinal(data.getBytes());
            System.out.println(new String(bytes));
        }
    }
    

执行结果是乱码，因为ascii中找不到对应的字节编码  
![image](https://image.3001.net/images/20210927/1632733044_6151877475a7ba48ff850.png!small)  
之后使用base64继续编码一下

    
    
    public static void main(String[] args) throws Exception {
            String data = "小红爱JAVA";
            String key = "12345678";
            String transformation = "DES";
            String algoritm = "DES";
            Cipher cipher = Cipher.getInstance(transformation);
            SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(), algoritm);
            cipher.init(Cipher.ENCRYPT_MODE,secretKeySpec);
            byte[] bytes = cipher.doFinal(data.getBytes());
            byte[] encode = Base64.encodeBase64(bytes);
            System.out.println(new String(encode));
    }
    

![image](https://image.3001.net/images/20210927/1632733072_6151879052ddd6f63223c.png!small)

**注意这里有一个坑是，使用DES加密的时候密钥key必须是8位数，其他位数会报错**

#### 加密解密完整代码

    
    
    package com.red.javacodeaudit.encode.DesAes;
    
    import com.sun.org.apache.xml.internal.security.utils.Base64;
    
    import javax.crypto.Cipher;
    import javax.crypto.spec.SecretKeySpec;
    import java.security.NoSuchAlgorithmException;
    
    public class DesDemo {
        public static void main(String[] args) throws Exception {
            String data = "小红爱JAVA";
            String key = "12345678";
            String transformation = "DES";
            String algoritm = "DES";
          	String encryptData = encryptDes(data,key,transformation,algoritm);
            System.out.println("加密后的数据："+encryptData);
            String finaldata = decryptDes(encryptData,key,transformation,algoritm);
            System.out.println("解密后的数据："+finaldata);
        }
    
        /**
         *
         * @param encryptData 密文
         * @param key
         * @param transformation
         * @param algoritm
         */
    
        private static String decryptDes(String encryptData, String key, String transformation, String algoritm) throws Exception{
            Cipher cipher = Cipher.getInstance(transformation);
            SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(), algoritm);
            cipher.init(Cipher.DECRYPT_MODE,secretKeySpec);
            byte[] bytes = cipher.doFinal(Base64.decode(encryptData));
            return new String(bytes);
        }
    
        /**
         * 用DES算法加密文本
         * @param data
         * @param key
         * @param transformation
         * @param algoritm
         * @return
         * @throws Exception
         * @throws NoSuchAlgorithmException
         */
        private static String encryptDes(String data, String key, String transformation, String algoritm) throws Exception, NoSuchAlgorithmException {
            Cipher cipher = Cipher.getInstance(transformation);
            SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(), algoritm);
            cipher.init(Cipher.ENCRYPT_MODE,secretKeySpec);
            byte[] bytes = cipher.doFinal(data.getBytes());
            String encode = Base64.encode(bytes);
            return encode;
        }
    }
    

![image](https://image.3001.net/images/20210927/1632733121_615187c1672b8ddccec5f.png!small)

## 2.2 Base64

base64不是加密算法，是可读性算法。目的不是保护我们的数据，目的是为了 **可读性**

Base64 由64个字符组成，大写A-Z，小写a-z，数字0-9，两个符号 + 和 / 。其实还有=是填充字符

Base64
编码原理：Base64是3个字节为一组，一个字节是8位，一共就是24位，base64把三个字节，转换为4组，每组6位，一个字节，应该是8位，缺少2位，在高位进行补0，这样做的好处就是，base64取后面6位，前面的两位都是0，不进行计算，可以把base64控制在0-63之间。  
![image](https://image.3001.net/images/20210927/1632733139_615187d333e8f6c9e5d23.png!small)  
在base64中，需要设置一共是3个字节，为一组，如果在输出的时候，不够三个字节，就需要使用=进行补齐

    
    
    public class Base64Demo {
        public static void main(String[] args) {
            //这里就一个字符,就需要填充两个等号
            System.out.println(Base64.encode("1".getBytes()));
            System.out.println(Base64.encode("12".getBytes()));
            System.out.println(Base64.encode("123".getBytes()));
            System.out.println(Base64.encode("嘿嘿".getBytes()));
        }
    }
    

![image](https://image.3001.net/images/20210927/1632733161_615187e95668c9efcf04b.png!small)

## 2.3 toString()和new String()

首先看一下代码示例

    
    
    public class Base64Demo {
        public static void main(String[] args) throws Exception{
            String str = "SmF2YUNvZGVBdWRpdA==";
            System.out.println("new String===>"+new String(Base64.decode(str.getBytes())));
            System.out.println("toString=====>"+Base64.decode(str.getBytes()).toString());
        }
    }
    

结果如下，可以看到`new String`得到的结果是正确的，那么为什么会是`new String`得到正确的结果呢  
![image](https://image.3001.net/images/20210927/1632733191_61518807db1715da7422f.png!small)  
其实在调用`toString`的时候会调用的是`Object`的`toString`方法，调用的是`hashcode()`方法，得到的是一个哈希值  
![image](https://image.3001.net/images/20210927/1632733207_6151881720552ea6604c9.png!small)  
`new
String`方法：是根据参数，参数是一个字节数组，使用JVM虚拟机默认编码格式，会把这个字节数组进行decode，找到对应的字符，如果虚拟机的编码格式，如果是ISO-8859-1，会去找ascii里面的编码进行参照，找到对应的字符。

`new String()`:一般在进行转码的时候，需要使用

`toString()`:做对象打印的时候，或者想得到地址的时候，就使用`toString()`.

## 2.4 AES

这里跟DES没有区别，就是将代码里的变量改成AES就可以，但是key注意要改成16位的，否则会报错。

## 2.5 加密模式

### 2.5.1 ECB（电子密码本）

ECB：把一段文本进行分拆加密，使用同一个key，分别进行加密，然后组合到一起

  * 优点：可以并行处理数据

  * 缺点：同样的原文生成同样的密文，不能很好的保护数据

  * 同时加密，原文是一样的，加密出来的密文也是一样的

### 2.5.2 CBC（密码块链接）

每个明文块先与前一个密文块进行异或后，再进行加密。在这种方法中，每个密文块都依赖于它前面的所有明文块。这里存在一个IV向量来加密原文

  * 优点：安全系数很高，同样的原文产生的密文是不同的

  * 缺点：串行处理数据，加密速度很慢  
![image](https://image.3001.net/images/20210927/1632733240_615188387c3fbd23f43d6.jpeg!small)

## 2.6 填充模式

当需要按照块处理的数据，数据长度不符合块处理需求时，按照一定的方法填充满块长的规则

### 2.6.1 NoPadding

  * 不填充

  * 在DES算法中，要求原文长度必须是8byte的整数倍

  * 在AES算法中，要求原文长度必须是16byte的整数倍

### 2.6.2 PKCS5Padding

数据块的大小为8位，不够就补齐

 **TIPS：**

  * 如果没有设置加密模式和填充模式就默认使用`ECB/PKCS5Padding`模式

## 代码示例

这里看到单纯的使用`DES`加密的结果是`OaaGdLrz6BRTP49DWl2Q6w==`  
![image](https://image.3001.net/images/20210927/1632733266_6151885247706408eae68.png!small)  
更换到`DES/ECB/PKCS5Padding`加密模式和填充模式的时候，密文还是没有变化，说明默认就是这个加密模式和填充模式  
![image](https://image.3001.net/images/20210927/1632733287_61518867ec82220b1f223.png!small)现在来看CBC加密模式，仅仅更换加密模式的话会产生错误，因为我们知道CBC加密是需要一个IV向量的。  
![image](https://image.3001.net/images/20210927/1632733312_615188806e6e18402a11d.png!small)`new
IvParameterSpec(key.getBytes());`得到一个iv，参数就是`key`的字节数组，然后在`cipher.init`的时候加入`iv`，同样解密的方法里也需要一个`iv`

    
    
    IvParameterSpec iv = new IvParameterSpec(key.getBytes());
    cipher.init(Cipher.ENCRYPT_MODE,secretKeySpec,iv);
    
    
    
    private static String encryptDes(String data, String key, String transformation, String algoritm) throws Exception, NoSuchAlgorithmException {
            Cipher cipher = Cipher.getInstance(transformation);
            SecretKeySpec secretKeySpec = new SecretKeySpec(key.getBytes(), algoritm);
            IvParameterSpec iv = new IvParameterSpec(key.getBytes());
            cipher.init(Cipher.ENCRYPT_MODE,secretKeySpec,iv);
            byte[] bytes = cipher.doFinal(data.getBytes());
            String encode = Base64.encode(bytes);
            return encode;
    }
    

可以看到就不会报错了  
![image](https://image.3001.net/images/20210927/1632733351_615188a7637cb4103ada2.png!small)

# 3.消息摘要

  * 消息摘要又称数字摘要

  * 它是一个唯一对应一个消息或文本的固定长度的值，由一个单向的Hash加密函数对消息进行作用而产生

  * 使用数字摘要生成的值是不可篡改的， **为了保证文件或者值的安全性**

消息摘要算法是不可逆的，常见的算法有

    
    
    - MD5
    - SHA1
    - SHA256
    - SHA512
    

使用的是`MessageDigest`，使用`getInstace()`方法传入参数`algorithm`表示加密类型

    
    
    MessageDigest digest = MessageDigest.getInstance("SHA");
    

![image](https://image.3001.net/images/20210927/1632733416_615188e892d7fc2fcff64.png!small)  
得到一个`digest`对象之后就能调用其`digest`方法，该方法的参数就是原文的字节数组

    
    
    public class digestDemo {
        public static void main(String[] args) throws NoSuchAlgorithmException {
            String input = "java";
            String algorithm = "MD5";
            MessageDigest digest = MessageDigest.getInstance(algorithm);
            byte[] bytes = digest.digest(input.getBytes());
            System.out.println(Base64.encode(bytes));
        }
    }
    

![image](https://image.3001.net/images/20210927/1632733494_6151893660bd4a0e27bab.png!small)写一个直接生成MD5值的demo

    
    
    public class digestDemo {
       public static void main(String[] args) throws NoSuchAlgorithmException {
           String input = "aa";
           String algorithm = "MD5";
           MessageDigest digest = MessageDigest.getInstance(algorithm);
           byte[] mdcryptData = digest.digest(input.getBytes());
           StringBuilder sb = new StringBuilder();
           for (byte b : mdcryptData) {
               String s = Integer.toHexString(b & 0xff);//将加密的byte数组转换成16进制的代码，返回String字符串
               if(s.length()==1){
                   s = "0"+s;//对单个的字符高位进行补0，否则会出现问题
               }
               sb.append(s);
           }
           System.out.println(sb.toString()); 
       }
    }
    

## 完整案例

    
    
    package com.red.javacodeaudit.encrypt.digest;
    
    
    import com.sun.org.apache.xerces.internal.impl.dv.util.HexBin;
    
    import java.security.MessageDigest;
    import java.security.NoSuchAlgorithmException;
    
    public class digestDemo {
        public static void main(String[] args) throws NoSuchAlgorithmException {
            String input = "java";
            String algorithm = "MD5";
            String digest = getDigest(input, algorithm);
            System.out.println(digest);
            String sha1 = getDigest(input, "SHA-1");
            System.out.println(sha1);
            String sha256 = getDigest(input, "SHA-256");
            System.out.println(sha256);
            String sha512 = getDigest(input, "SHA-512");
            System.out.println(sha512);
    
        }
        private static String getDigest(String input,String algorithm) throws NoSuchAlgorithmException {
            MessageDigest digest = MessageDigest.getInstance(algorithm);
            byte[] cryptData = digest.digest(input.getBytes());
            String encode = HexBin.encode(cryptData);
            return encode;
        }
    }
    

这里分别是各种加密算法加密出来的数据。  
![image](https://image.3001.net/images/20210927/1632733553_6151897168ae40d3be1cd.png!small)

# 4.非对称加密

简介：

1.非对称加密，又叫现在加密算法

2.必须要有两个密钥，一个公钥，一个私钥

3.公钥和私钥是一对，我们叫做密钥对

4.如果使用公钥加密，必须使用私钥解密

5.如果使用私钥加密，必须使用公钥解密

常见的非对劲加密算法

  * RSA

  * ECC

## 4.1 RSA

### 4.1.1 获取公钥私钥

我们知道非对劲加密有一个密钥对，需要生成一对密钥，就先要拿到密钥对生成器，也就是`KeyPairGenerator`.

对于`KeyPairGenerator`，API中是这么说的：KeyPairGenerator类用于生成公钥和私钥对。
密钥对生成器使用`getInstance`工厂方法（返回给定类的实例的静态方法）构造。

通过`getInstace(algorithm)`方法生成一个密钥对生成器，这里`algorithm`是我们自己定义的`RSA`算法

`KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(algorithm);`

得到了`keyPairGenerator`对象是生成器，来生成密钥对，调用`keyPairGenerator.generateKeyPair();`方法来获取到密钥对`keyPair`  
![image](https://image.3001.net/images/20210927/1632733575_615189870821558122551.png!small)然后得到密钥对之后，我们就可以调用`getPrivate`和`getPublic`方法来获取到
**私钥** 和 **公钥** 了，获取到的公钥和私钥有`getEncoded()`方法可以将其转换成`byte[]`数组之后进行Base64编码显示。

    
    
    public static void main(String[] args) throws Exception{
            String algorithm = "RSA";
            //获取到密钥对
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(algorithm);
            KeyPair keyPair = keyPairGenerator.generateKeyPair();
            PrivateKey privateKey = keyPair.getPrivate();
            PublicKey publicKey = keyPair.getPublic();
            System.out.println(Base64.encode(privateKey.getEncoded()));
            System.out.println(Base64.encode(publicKey.getEncoded()));
    }
    

![image](https://image.3001.net/images/20210927/1632733600_615189a0bf514e06a261d.png!small)

### 4.1.2 使用私钥加密数据

Java中只要是想加密，就需要创建加密对象也就是`Cipher`对象，现在就需要先`getInstance`一个`cipher`.之后的步骤跟前面类似

    
    
    Cipher cipher = Cipher.getInstance(algorithm);
    cipher.init(Cipher.ENCRYPT_MODE,privateKey);
    byte[] bytes = cipher.doFinal(input.getBytes());
    System.out.println(Base64.encode(bytes));
    

这里就是最后得到的密文数据![image](https://image.3001.net/images/20210927/1632733644_615189ccac7b8d8ebf1bb.png!small)

### 4.1.3 使用公钥解密数据

非对称算法，私钥加密数据，必须使用公钥解密，否则会报错，有兴趣的朋友就自己动手试试了.

跟其他的解密一样，key设置为`publicKey`即可

    
    
    cipher.init(Cipher.DECRYPT_MODE,publicKey);
    byte[] bytes1 = cipher.doFinal(bytes);
    System.out.println(new String(bytes1));
    

![image](https://image.3001.net/images/20210927/1632733663_615189df5c7ea658e1452.png!small)

### 4.1.4 保存公钥和私钥

我们一直生成公钥和私钥就很不方便，所以一般是将公钥和私钥给保存下来

    
    
    package com.red.javacodeaudit.encrypt.RSA;
    
    
    import com.sun.org.apache.xml.internal.security.utils.Base64;
    import org.apache.commons.io.FileUtils;
    
    import java.io.File;
    import java.io.IOException;
    import java.nio.charset.Charset;
    import java.security.*;
    
    public class RSADemo {
        public static void main(String[] args) throws Exception{
            String input = "Red256's Java";
            String algorithm = "RSA";
            String publicKeyFile = "a.pub";
            String privateKeyFile = "a.pri";
            generatorKeyFile(algorithm,publicKeyFile,privateKeyFile);
    
    }
        private static void generatorKeyFile(String algorithm,String pubFile,String priFile) throws NoSuchAlgorithmException, IOException {
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(algorithm);
            KeyPair keyPair = keyPairGenerator.generateKeyPair();
            PrivateKey privateKey = keyPair.getPrivate();
            PublicKey publicKey = keyPair.getPublic();
            String privatekeyString = Base64.encode(privateKey.getEncoded());
            String publickeyString = Base64.encode(publicKey.getEncoded());
          //这里commins-IO的包中的方法
            FileUtils.writeStringToFile(new File(pubFile),publickeyString, Charset.forName("UTF-8"));
            FileUtils.writeStringToFile(new File(priFile),privatekeyString,Charset.forName("UTF-8"));
        }
    }
    

成功的生成了公钥和私钥文件  
![image](https://image.3001.net/images/20210927/1632733680_615189f08b28204c1c07f.png!small)

### 4.1.5 抽取出加密解密方法

这里就是把都在main方法中的代码，封装成独立的方法了，没有什么值得说的。

    
    
    package com.red.javacodeaudit.encrypt.RSA;
    
    
    import com.sun.org.apache.xml.internal.security.utils.Base64;
    import org.apache.commons.io.FileUtils;
    
    import javax.crypto.BadPaddingException;
    import javax.crypto.Cipher;
    import javax.crypto.IllegalBlockSizeException;
    import javax.crypto.NoSuchPaddingException;
    import java.io.File;
    import java.io.IOException;
    import java.nio.charset.Charset;
    import java.security.*;
    
    public class RSADemo {
        public static void main(String[] args) throws Exception{
            String input = "Red256's Java";
            String algorithm = "RSA";
            String publicKeyFile = "a.pub";
            String privateKeyFile = "a.pri";
    //        generatorKeyFile(algorithm,publicKeyFile,privateKeyFile);
    
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(algorithm);
            KeyPair keyPair = keyPairGenerator.generateKeyPair();
            PrivateKey privateKey = keyPair.getPrivate();
            PublicKey publicKey = keyPair.getPublic();
            String s = encryptRSA(algorithm, privateKey, input);
            System.out.println(s);
            String s1 = decryptRSA(algorithm, publicKey, s);
            System.out.println(s1);
    
        }
    
        /**
         *
         * @param algorithm     加密规则
         * @param publicKey     公钥
         * @param encrypted     密文
         * @return
         */
        private static String decryptRSA(String algorithm,Key publicKey,String encrypted) throws Exception{
            Cipher cipher = Cipher.getInstance(algorithm);
            cipher.init(2,publicKey);
            byte[] decode = Base64.decode(encrypted);
            byte[] bytes = cipher.doFinal(decode);
            return new String(bytes);
        }
        /**
         *
         * @param algorithm     加密规则
         * @param privateKey    私钥
         * @param input         原文
         * @return
         */
        private static String encryptRSA(String algorithm,Key privateKey,String input) throws NoSuchPaddingException, NoSuchAlgorithmException, InvalidKeyException, IllegalBlockSizeException, BadPaddingException {
            Cipher cipher = Cipher.getInstance(algorithm);
            cipher.init(Cipher.ENCRYPT_MODE,privateKey);
            byte[] bytes = cipher.doFinal(input.getBytes());
            String encode = Base64.encode(bytes);
            return encode;
        }
        private static void generatorKeyFile(String algorithm,String pubFile,String priFile) throws NoSuchAlgorithmException, IOException {
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(algorithm);
            KeyPair keyPair = keyPairGenerator.generateKeyPair();
            PrivateKey privateKey = keyPair.getPrivate();
            PublicKey publicKey = keyPair.getPublic();
            String privateKeyString = Base64.encode(privateKey.getEncoded());
            String publicKeyString = Base64.encode(publicKey.getEncoded());
            FileUtils.writeStringToFile(new File(pubFile),privateKeyString, Charset.forName("UTF-8"));
            FileUtils.writeStringToFile(new File(priFile),publicKeyString,Charset.forName("UTF-8"));
        }
    }
    

### 4.1.6 读取公钥私钥

写一个方法，读取出来文件中的内容，给私钥编码的规则是`PKCS8EncodedKeySpec`，官方API的介绍。  
![image](https://image.3001.net/images/20210928/1632798326_615286765454cdab54f2c.png!small)  
给公钥进行编码的规则是`X509EncodedKeySpec`，这里记住就好，下面是官方API的介绍  
![image](https://image.3001.net/images/20210928/1632798305_615286611311f11614392.png!small)

    
    
    psvm(){
      String input = "Red256's Java";
            String algorithm = "RSA";
            String publicKeyFile = "a.pub";
            String privateKeyFile = "a.pri";
            PrivateKey privateKey = getPrivateKey(privateKeyFile,algorithm);
      			PublicKey publicKey = getPublicKey(publicKeyFile,algorithm);
    }
    /**
         * 文件中读取私钥
         * @param privateKeyFile 私钥文件
         * @return
         * @throws IOException
         */
    private static PrivateKey getPrivateKey(String privateKeyFile,String algorithm) throws IOException, NoSuchAlgorithmException, Base64DecodingException, InvalidKeySpecException {
            String privateKey = FileUtils.readFileToString(new File(privateKeyFile), Charset.defaultCharset());
      			//新建一个key工厂来生成key
            KeyFactory keyFactory = KeyFactory.getInstance(algorithm);
      			//生成key的时候需要传入一个KeySpec规则，RSA私钥对应的就是PKCS8EncodedKeySpec这个规则
            PKCS8EncodedKeySpec keySpec = new PKCS8EncodedKeySpec(Base64.decode(privateKey));
            return keyFactory.generatePrivate(keySpec);
    }
    
     private static PublicKey getPublicKey(String publicKeyFile, String algorithm) throws Exception {
            String publicKeyString = FileUtils.readFileToString(new File(publicKeyFile), Charset.defaultCharset());
            KeyFactory keyFactory = KeyFactory.getInstance(algorithm);
            X509EncodedKeySpec keySpec = new X509EncodedKeySpec(Base64.decode(publicKeyString));
            PublicKey publicKey = keyFactory.generatePublic(keySpec);
            return publicKey;
    }
    

## 4.2 数字签名

数字签名：公钥数字签名，只有信息的发送者，才能产生别人无法伪造的一段数字串，类似于写在纸上的普通物理签名

[阮一峰老师图解数字签名](https://www.ruanyifeng.com/blog/2011/08/what_is_a_digital_signature.html)，讲解的毁更加的详细。

### 4.2.1 代码生成数字签名

使用Java生成数字签名的时候，会用到`Signature`这个类，Java的API是这么对它解释的。而且签名算法跟加密算法还是有区别的常见的签名算法是`sha256withrsa`  
![image](https://image.3001.net/images/20210928/1632798272_6152864049b3f28053e74.png!small)根据API中的描述，给得到一个私钥的数字签名分为三步

  * 初始化 --->`getInstance`这里的参数就是算法，常见的就是`sha256withrsa`\--->`initSign`初始化的时候需要传入一个私钥

  * 更新---->`update(input.getBytes)`，更新原文数据转换成字节数组更新到其中

  * 签名--->`sign`方法，进行签名，返回字节数组。

    
    
    public class SignatureDemo {
        public static void main(String[] args) throws Exception {
            String a = "123";
            String priPath = "a.pri";
            String algorithm = "RSA";
            PrivateKey privateKey = RSADemo.getPrivateKey(priPath, algorithm);
    
            getSignature(a,"sha256withrsa",privateKey);
        }
    
        private static String getSignature(String input, String algorithm, PrivateKey privateKey) throws Exception {
            Signature signature = Signature.getInstance(algorithm);
            signature.initSign(privateKey);
            signature.update(input.getBytes());
            byte[] sign = signature.sign();
            return Base64.encode(sign);
        }
    }
    

运行结果如下，把得到的签名文件打印出来了。  
![image](https://image.3001.net/images/20210928/1632798407_615286c70cd164e3da737.png!small)

### 4.2.2 校验数字签名

    
    
    psvm(){
     boolean b = verifySignature(a, "sha256withrsa", publicKey, signpriKey);
     System.out.println(b);
    }
    private static boolean verifySignature(String input, String algorithm, PublicKey publicKey, String signpriKey) throws NoSuchAlgorithmException, InvalidKeyException, SignatureException, Base64DecodingException {
           Signature signature = Signature.getInstance(algorithm);
           signature.initVerify(publicKey);//这里是初始化校验
           signature.update(input.getBytes());
           return signature.verify(Base64.decode(signpriKey));
    }
    

用私钥加密的数字签名，就要公钥来解密，于是校验的算法里传入的是公钥，跟私钥加密不同的地方在于`initVerify`是初始化校验，而不是签名的时候的`initSign()`方法，这里参数传入的是`publicKey`也就是公钥。并且校验方法比签名方法多了参数就是，密文参数，需要得到原文和密文才可以进行校验。

运行结果如下，判断是一致的签名。[Github链接](https://github.com/Tuantuan6560/JavaCodeAudit)  
![image](https://image.3001.net/images/20210928/1632798448_615286f05c6be28ae29c4.png!small)

