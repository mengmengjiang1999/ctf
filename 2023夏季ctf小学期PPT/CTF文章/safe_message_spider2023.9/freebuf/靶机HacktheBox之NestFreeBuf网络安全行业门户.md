# 信息收集

发现目标主机只开放了两个端口，其中445端口可能存在匿名登录。

![image.png](https://image.3001.net/images/20220510/1652173159_627a296719d940bfc387f.png!small)

使用smbmap工具匿名登录成功，发现Data和Users目录是可读权限

![image.png](https://image.3001.net/images/20220510/1652173290_627a29ea222c44bc98901.png!small)

使用smbclient进行登录，并将相关文件下载分析

![image.png](https://image.3001.net/images/20220510/1652173507_627a2ac3c115d0f00338b.png!small)

下载的文件中，发现了TempUser账户的用户名和密码

![image.png](https://image.3001.net/images/20220510/1652173606_627a2b26bc3608bf8d9c0.png!small)

# 漏洞利用

使用这个账户名和密码进行smb登录，发现拥有Secure$目录的权限

![image.png](https://image.3001.net/images/20220510/1652173689_627a2b794335865341ad0.png!small)

使用这个账户登录到data目录后，发现又能访问和下载更多的文件

![image](https://image.3001.net/images/20220530/1653890138_62945c5a08074fcbee361.png!small)

在其中的RU_config.xml文件中，发现了存在一段加密的字符串。经过base64解密，发现不能解密成功

![image](https://image.3001.net/images/20220530/1653890186_62945c8a42d67b50abd59.png!small)

![image](https://image.3001.net/images/20220530/1653890218_62945caabc0aabbda7544.png!small)

在NotepadPlusPlus目录中发现了一个config文件，这个文件中发现了一个新的目录\HTB-NEST\Secure$\IT\Carl\

![image](https://image.3001.net/images/20220530/1653890274_62945ce2e398e548d2464.png!small)

在RU目录上发现了一个C#的项目

![image](https://image.3001.net/images/20220530/1653890327_62945d171697259658c7d.png!small)

在Module1.vb这个文件上发现存在RU_Config.xml这个文件，这个文件包含了用户名和密码信息

![image](https://image.3001.net/images/20220531/1653959309_62956a8d0ec5045f54193.png!small)

根据代码的提示，程序要运行需要RU_Config.xml文件，设置断点，可以看到解密成功的密码

![image](https://image.3001.net/images/20220531/1653959648_62956be05b08d39e0338c.png!small)

因为目标主机没有开放22端口，所以只能通过SMB服务的Users文件夹中进行flag值提取

![image](https://image.3001.net/images/20220531/1653959683_62956c0320a6d962a84a2.png!small)

# 用户提权

使用C.Smith账号登录到SMB应用后，发现了一个备份文件的xml，下载分析后发现了一个新的SMB路径

![image](https://image.3001.net/images/20220531/1653959728_62956c30bd4441d918c13.png!small)

从应用程序的端口上看，这个应用是运行在4386端口的，也就是之前的telnet端口，开启Debug模式并进入C:\Program
Files\HQK这个目录下

![image](https://image.3001.net/images/20220531/1653959757_62956c4d3f851a0fa8c8e.png!small)

进入到LDAP目录中，查看LDAP.conf文件，发现了Administrator用户的加密值

![image](https://image.3001.net/images/20220531/1653959790_62956c6e702fc54c2d220.png!small)

为了更好地分析密码是通过怎样进行加密的，因此需要对HqkLdap.exe这个程序进行代码分析，将其导入到dnSpy程序中进行分析

![image](https://image.3001.net/images/20220531/1653959816_62956c8830b432d1d5066.png!small)

可以深层次看到代码逻辑是，通过命令行去传递文件中读取配置。因为DS函数涉及到密码的加密方式，因此可以去跟踪一下这个函数的具体实现方法

![image](https://image.3001.net/images/20220531/1653959850_62956caa224c1a8fcab2f.png!small)

然后跟踪到RD这个方法上，RD这个方法是将密文还原成明文的形式。对比Utils.vb这个文件，里面的代码实现逻辑是和RD这个方法一致的

![image](https://image.3001.net/images/20220531/1653959876_62956cc4ac76beabcd361.png!small)

因此可以根据这些代码，保留大部分的代码，并别写解密脚本

    
    
    using System;
    using System.IO;
    using System.Text;
    using System.Security.Cryptography;
    namespace Dec {
    class Decryptor {
    public static void Main() {
        
    	var EncryptedString = "yyEq0Uvvhq2uQOcWG8peLoeRQehqip/fKdeG/kjEVb4=";
    	var pt = Decrypt(EncryptedString, "667912", "1313Rf99", 3,"1L1SA61493DRV53Z", 256);
    	Console.WriteLine("Plaintext: " + pt);
    }
        
    public static String Decrypt(String cipherText, String passPhrase, String saltValue, int passwordIterations, String initVector,int keySize) {
        
    	var initVectorBytes = Encoding.ASCII.GetBytes(initVector);
    	var saltValueBytes = Encoding.ASCII.GetBytes(saltValue);
    	var cipherTextBytes = Convert.FromBase64String(cipherText);
    	var password = new Rfc2898DeriveBytes(passPhrase, saltValueBytes,passwordIterations);
    	var keyBytes = password.GetBytes(keySize / 8);
    	var symmetricKey = new AesCryptoServiceProvider();
    	symmetricKey.Mode = CipherMode.CBC;
    	var decryptor = symmetricKey.CreateDecryptor(keyBytes, initVectorBytes);
    	var memoryStream = new MemoryStream(cipherTextBytes);
    	var cryptoStream = new CryptoStream(memoryStream, decryptor,CryptoStreamMode.Read);
    	var plainTextBytes = new byte[cipherTextBytes.Length];
    	var decryptedByteCount = cryptoStream.Read(plainTextBytes, 0,plainTextBytes.Length);
    	memoryStream.Close();
    	cryptoStream.Close();
    	var plainText = Encoding.ASCII.GetString(plainTextBytes, 0,decryptedByteCount);
    	return plainText;
    		}
    	}
    }
    

使用mcs命令生成一个exe文件，命令为mcs decrypt.cs，并运行他获得Administrator的明文值

![image](https://image.3001.net/images/20220531/1653959980_62956d2cc1c07dc934a4d.png!small)

![image](https://image.3001.net/images/20220531/1653959997_62956d3d7dfcade2a3e76.png!small)

最后使用psexec.py脚本获得SYSTEM32的权限

![image](https://image.3001.net/images/20220531/1653960025_62956d59e60a4adb35483.png!small)

