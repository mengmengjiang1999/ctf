## 概述

![61d7bdc32ab3f51d91d334da.jpg](https://image.3001.net/images/20220121/1642734238_61ea229e4e3567dc7cb4e.jpg!small)

在Windows系统中，Google Chrome的配置文件存放在`%LocalAppData%`目录下。只有一个账号的数据存储目录：

    
    
    C:\Users\xxxxx\AppData\Local\Google\Chrome\User Data\Default

该路径下的主要文件：

    
    
    Bookmarks  
    Cookies  
    History  
    Login Data  
    QuotaManager  
    Shortcuts  
    Top Sites  
    Web Data

用winhex打开，其中，Bookmarks（书签） 是JSON文件，而且是明文存储。

![61d7d73f2ab3f51d91e631ef.jpg](https://image.3001.net/images/20220121/1642734239_61ea229f9023df1d2b77d.jpg!small)

    
    
    {  
    "checksum": "483389db8b8adcb356227e06ee6d533a",  
    "roots": {  
    "bookmark_bar": {  
    "children": [ {  
    "date_added": "13286008493612852",  
    "guid": "50589c41-c552-4e29-a407-8e8a401ec4ff",  
    "id": "5",  
    "name": "Site administration | Django site admin",  
    "type": "url",  
    "url": "http://127.0.0.1:8000/admin/"  
    } ],  
    "date_added": "13285924453837021",  
    "date_modified": "13286008493612852",  
    "guid": "00000000-0000-4000-A000-000000000002",  
    "id": "1",  
    "name": "书签栏",  
    "type": "folder"  
    },  
    "other": {  
    "children": [ ],  
    "date_added": "13285924453837056",  
    "date_modified": "0",  
    "guid": "00000000-0000-4000-A000-000000000003",  
    "id": "2",  
    "name": "其他书签",  
    "type": "folder"  
    },  
    "synced": {  
    "children": [ ],  
    "date_added": "13285924453837072",  
    "date_modified": "0",  
    "guid": "00000000-0000-4000-A000-000000000004",  
    "id": "3",  
    "name": "移动设备书签",  
    "type": "folder"  
    }  
    },  
    "version": 1  
    }

除了 Bookmark 是JSON文件外，其他都是SQLite3文件。

## 历史记录分析

History 是SQLite3 文件，可以用Python脚本读取，也可以直接用 Navicat 直接打开，Python脚本：

    
    
    import sqlite3  
    ​  
    db_file_path = './History'  
    sql = 'select name from sqlite_master where type="table" order by name'   # 查询所有表格  
    sql = 'pragma table_info(downloads)'     # 查询表格字段  
    ​  
    conn = sqlite3.connect(db_file_path)  
    cursor = conn.cursor()  
    cursor.execute(sql)  
    ​  
    # 接收全部返回结果  
    for data in cursor.fetchall():  
    print(data)

  * 表格
    
        ('downloads',)  
    ('downloads_slices',)  
    ('downloads_url_chains',)  
    ('keyword_search_terms',)  
    ('meta',)  
    ('segment_usage',)  
    ('segments',)  
    ('sqlite_sequence',)  
    ('typed_url_sync_metadata',)  
    ('urls',)  
    ('visit_source',)  
    ('visits',)

  * downloads 表

> 文件下载记录

主要字段：

![61dba0af2ab3f51d916a8fc1.jpg](https://image.3001.net/images/20220121/1642734240_61ea22a0eed8b4ce129dd.jpg!small)

其中 start_time 和end_time 都是 **微秒** 级别的时间戳，转化是需要先除以10^6

    
        >>> import time  
    >>> start_time = 13286256367986952  
    >>> time.strftime("%Y-%m-%d %X",time.localtime((start_time / 1000000) - 11644473600))  
    '2022-01-10 10:46:07'

  * urls表

> 记录所有访问过的链接的地址、页面标题、访问次数以及最后访问时间

![61dba8ff2ab3f51d91711287.jpg](https://image.3001.net/images/20220121/1642734242_61ea22a25710ad34d02bc.jpg!small)

> 通过 History 文件分析，可以获取到用户的浏览记录、下载记录，甚至可以进一步分析出用户的喜好。

## 登录信息分析

> 主流浏览器都有记住密码到本地的功能，该功能方便用户管理不同网站的密码，无需记忆，可以保存到本地，甚至通过账号可以实现多设备同步。

![61d6b0d12ab3f51d91268230.jpg](https://image.3001.net/images/20220121/1642734243_61ea22a37f4eb40e6985b.jpg!small)

存储登录信息的文件为`Login Data`，是 SQLite3 文件，用Python脚本读取

    
    
    import sqlite3  
    ​  
    db_file_path = './Login Data'  
    ​  
    conn = sqlite3.connect(db_file_path)  
    cursor = conn.cursor()  
    cursor.execute(  
    'select username_value, password_value, signon_realm from logins')  
    ​  
    # 接收全部返回结果  
    for data in cursor.fetchall():  
    print(data)
    
    
    ('Hillstone', b'\x01\x00\x00\x00\xd0\x8c\x9d\xdf\x01\x15\xd1\x11\x8cz\x00\xc0O\xc2\x97\xeb\x01\x00\x00\x00\xdc\x8cEq;\x07!H\xba+8\xaaF0\xe3\xe2\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x10f\x00\x00\x00\x01\x00\x00 \x00\x00\x00P\xa86x\x97\x82!U\xbbS\xe6\x85\xc3\xc8\x87\xff@\x1e\xdd\x93\xf8\x9c\x16\x91\xdc\x9b&\xac\xc0\x0b\xfb&\x00\x00\x00\x00\x0e\x80\x00\x00\x00\x02\x00\x00 \x00\x00\x00\xbaf\x18\xbe\xc0_S\xe7\xa8\xd9@\xbf\xb9\x89\xd6nV\xdc\x1c,\xd3\xdf\xbb\xfc\x00\x8c\x80\xb6\x94\x15\x0f\xf1\x10\x00\x00\x00"P\xd5\xb9\xaeA\x994f\xad\xf5aJ\x07f\x0c@\x00\x00\x00\x13\xf9\xf2\xe5s\x07\xf1nla\xd9#W\xdbE\x8b{g\xb4\xe7\xd6e\x1f\x1em\x1d\x81\x7f3c\xf5\x14\xbc\x8b\xbfH\xad\x9a\xbe\\\xa4\xe8\x80\x04\x8f~F\xdb\xbe.\xbf%\xdb\xc0\xa3\xc1\xcb,\x17\x03\x99\x98D^', 'http://127.0.0.1:8000/')

其中 password_value 字段被加密，使用的是 Microsoft的数据保护API（DPAPI）

> #### 引用的知识点
>
> 从Windows 2000开始，Microsoft随操作系统一起提供了一种特殊的数据保护接口，称为Data Protection Application
> Programming Interface（DPAPI）。其分别提供了加密函数CryptProtectData 与解密函数
> CryptUnprotectData 以用作敏感信息的加密解密。
>
> 其用作范围包括且不限于：
>
>   * IE、Chrome的登录表单自动完成
>
>   * Powershell加密函数
>
>   * Outlook, Windows Mail等邮箱客户端的用户密码。
>
>   * FTP管理账户密码
>
>   * 共享资源文件夹的访问密码
>
>   * 无线网络帐户密钥和密码
>
>   * 远程桌面身份凭证
>
>   * EFS
>
>   * EAP/TLS 和 802.1x的身份凭证
>
>   * Credential Manager中的数据
>
>   * 以及各种调用了CryptProtectData函数加密数据的第三方应用，如Skype, Windows Rights Management
> Services, Windows Media, MSN messenger, Google Talk等。
>
>

>
> DPAPI 采用的加密类型为 **对称加密** ，所以只要找到了密钥，就能解开物理存储的加密信息了。
>
> [more](https://www.4hou.com/posts/AQzP)

chrome version 80（80.0.3987.163） 版本前可以直接通过 DPAPI 中的解密函数
CryptUnprotectData来进行解密的。

> 实验版本：79.0.3945.117，需要关掉 Chrome 的自动更新服务，否则回自动更新的最新版
    
    
    python -m pip install pypiwin32
    
    
    import sqlite3  
    from win32 import win32crypt  
    ​  
    db_file_path = './Login Data'  
    ​  
    ​  
    conn = sqlite3.connect(db_file_path)  
    cursor = conn.cursor()  
    cursor.execute(  
    'select username_value, password_value, signon_realm from logins')  
    ​  
    # 接收全部返回结果  
    for data in cursor.fetchall():  
    passwd = win32crypt.CryptUnprotectData(data[1], None, None, None, 0)  
    # print(passwd)  
    if passwd:  
    print('-------------------------')  
    print('[+]用户名: ' + data[0])  
    print('[+]密码: ' + str(passwd[1]))  
    print('[+]网站URL: ' + str(data[2]))  
    # print(data)  
    ​
    
    
    -------------------------  
    [+]用户名: Hillstone  
    [+]密码: b'admin'  
    [+]网站URL: http://127.0.0.1:8000/

chrome version 80 （80.0.3987.163）版本后，password_value使用AES-GCM加密算法加密，加密使用的主密钥用
DPAPI 的加密函数 CryptProtectData 加密存放在Local State文件中。

Local State 实际上是一个 JSON文件，被加密的密钥存储在 os_crypt 下的 encrypted_key ，文件位置

    
    
    C:\Users\xxxxx\AppData\Local\Google\Chrome\User Data\Local State

> ### 解密步骤
>
>   1. 打开 Local State 的 encrypted_key ，解 Base64，再调用 CryptUnprotectData 解密得到
> 主密钥的明文，其中前五个字符为DPAPI
>
>   2. 打开 Login Data 数据库文件，查询 password_value 字段
>
>   3. 使用 aes-gcm 解密 password_value 字段
>
>

    
    
    python -m pip install -i https://pypi.douban.com/simple/ pycryptodome
    
    
    import json  
    from win32 import win32crypt  
    import base64  
    import sqlite3  
    from Crypto.Cipher import AES  
    ​  
    ​  
    # --- 文件路径配置 ---  
    local_state_path = './Local State'  
    login_data_path = './Login Data'  
    # --- end ---  
    ​  
    ​  
    # 获取解密后的主密钥  
    def get_master_key():  
    with open(local_state_path, 'r') as f:  
    local_state = json.load(f)  
    master_key = local_state['os_crypt']['encrypted_key']  
    # print(key)  
    ​  
    master_key = base64.b64decode(master_key)  
    master_key = master_key[5:]  # removing DPAPI  
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]  
    return master_key  
    ​  
    ​  
    # 调用解密方法  
    def decrypt_payload(cipher, payload):  
    return cipher.decrypt(payload)  
    ​  
    ​  
    # 实例化解密器  
    def generate_cipher(aes_key, iv):  
    return AES.new(aes_key, AES.MODE_GCM, iv)   
    ​  
    ​  
    # 解密密码字段，参数是密码的密文和主密钥  
    def decrypt_password(encrypted_password, master_key):  
    # 密文的3-15是iv，剩下的是密文  
    iv = encrypted_password[3:15]  
    payload = encrypted_password[15:]  
    try:  
    cipher = generate_cipher(master_key, iv)         # 实例化解密器  
    decrypted_pass = decrypt_payload(cipher, payload)       # 调用解密方法  
    decrypted_pass = decrypted_pass[:-16].decode()  # 去掉后缀字节   
    # print(decrypted_pass)  
    return decrypted_pass  
    except :  
    return "Chrome version < 80.0.3987.163"  
    ​  
    ​  
    if __name__ == '__main__':  
    # 1.获取主密钥  
    master_key = get_master_key()  
    print(master_key)  
    # 2.打开 Login Data 数据库文件，查询 password_value 字段  
    conn = sqlite3.connect(login_data_path)  
    cursor = conn.cursor()  
    try:  
    cursor.execute('select username_value, password_value, signon_realm from logins')  
    for data in cursor.fetchall():  
    # print(data)  
    encrypted_password = data[1]  
    # 3. 解密密码字段  
    decrypted_password = decrypt_password(encrypted_password, master_key)  
    # print(decrypted_password)  
    print("Username:" + data[0])  
    print("Password:" + decrypted_password)  
    print("Username:" + data[2])  
    print("------------------------------")  
    except:  
    print("Fail: 数据库查询失败！")  
    # 关闭连接  
    cursor.close()  
    conn.close()

## 无痕模式

现代网络浏览器，大多数都增加了隐私浏览模式来浏览网页，其目的在于保护用户隐私。在Chrome浏览器中，称之为无痕模式.

![61dbe13f2ab3f51d919bd1a2.jpg](https://image.3001.net/images/20220121/1642734244_61ea22a494d6df5c32061.jpg!small)

简而言之，无痕模式只是在本地不会保存浏览记录、Cookie、表单中填写的信息。同时，还有阻止第三方 Cookie功能。

> #### 第三方Cookie
>
> 第三方Cookie是由用户当时所访问的域以外的域创建的Cookie，主要用于跟踪和在线广告目的。
>
> [more](https://www.jianshu.com/p/7e7d41cd2bac)

隐私功能的局限性：

  * 关闭窗口时，并不会删除无痕模式下载的文件

  * 添加的书签正常保存

  * 不会阻止服务端获取定位

  * ISP （Internet 服务提供商）和出口（如学校、公司）可以获取上网活动，即无痕模式连IP都无法屏蔽

在无痕模式下，用户不登陆访问网站，服务端还能否区分不同的用户？

> 实验：
>
>   1. 正常模式下访问 [nothing private](https://www.nothingprivate.ml/)，输入表示字段
>
>   2. 使用无痕模式再次访问网站，输出标识字段
>
>

抓包分析：

在提交标识字段的时候，还提交了另一个 finger 参数

![61dcf11f2ab3f51d914afb55.jpg](https://image.3001.net/images/20220121/1642734245_61ea22a5bbf3d629f497b.jpg!small)

使用无痕模式访问时，会带着 finger 参数，也就能识别出用户

![61dcf1c22ab3f51d914b696e.jpg](https://image.3001.net/images/20220121/1642734246_61ea22a6f3bcf95df6625.jpg!small)

> [常见获取设备唯一标识的方法](https://blog.csdn.net/qq_32403473/article/details/81505664)
>
> 像常见的MAC地址等，一般都需要特殊权限才能访问，而Server一般可控的只有前端代码。

finger 参数是根据什么生成的？它是否能作为唯一的用户标识？

> #### 浏览器指纹
>
> 浏览器指纹是指仅通过浏览器的各种信息，如 CPU
> 核心数、显卡信息、系统字体、屏幕分辨率、浏览器插件等组合成的一个字符串，就能近乎绝对定位一个用户，就算使用浏览器的隐私窗口模式，也无法避免。
>
> 这是一个被动的识别方式。也就是说，理论上你访问了某一个网站，那么这个网站就能识别到你，虽然不知道你是谁，但你有一个唯一的指纹，将来无论是
> **广告投放、精准推送、安全防范** ，还是其他一些关于隐私的事情，都非常方便。

查看 [nothing private 源码](https://github.com/gautamkrishnar/nothing-private/blob/794bf714af5bbe5b1c69abfbb3566afd90a8474a/main.js)

![61dcf8b22ab3f51d91506a47.jpg](https://image.3001.net/images/20220121/1642734248_61ea22a81b533bee2bfd5.jpg!small)

[跟进 getFingerprint
函数](https://github.com/jackspirou/clientjs/blob/92d4df728f5a7085da582565e3e616d8c8ac9529/src/client.base.js)

![61dcf95e2ab3f51d9150e18a.jpg](https://image.3001.net/images/20220121/1642734249_61ea22a934229228d4939.jpg!small)

Nothing Private 使用 [ClientJS](https://github.com/jackspirou/clientjs)（用纯
JavaScript 编写的设备信息和数字指纹）的浏览器指纹识别功能来获取 Web 浏览器的指纹，通过 getFingerprint 方法，获取
UA、cookie、本地存储、canvas 指纹等信息，再经过`Murmur Hash`算法进行加密。

> MurmurHash 是一种 **非加密型哈希** 函数，适用于一般的哈希检索操作。

### 无痕模式检测

在 Chrome76之前，由于 FileSystem API
在无痕模式下被禁用，而正常访问时存在，利用此差异可以用来检测用户是否使用无痕模式浏览网站，有些网站还会阻止这类用户的访问。检测 Javascript：

    
    
    const fs = window.RequestFileSystem || window.webkitRequestFileSystem;  
    if (!fs) {  
    console.log('check failed?');  
    } else {  
    fs(  
    window.TEMPORARY,  
    100,  
    console.log.bind(console, 'not in incognito mode'),  
    console.log.bind(console, 'incognito mode')  
    );  
    }

后来 Google 修复了该漏洞，但是导致了另外两种检测方法：

  1. 基于文件系统大小

> 安全研究人员 Vikas
> Mishra[发现](https://link.segmentfault.com/?enc=gf%2FRUWTO8RzAsRisivtDcg%3D%3D.impYiHXBaBkXNhzsnIPFh5SYGjbIZ2syiIN%2BppCk5LM1m6hkEeHqaEewORjW7A2%2FpryiMzrJtcXlpOVtqsUdrj6eNqfHz%2FOipNevMXv0qty6oLFh134W%2BNm7aRj2v9c5)，Chrome
> 隐身模式和非隐身模式之间存储配额存在区别，如果临时存储配额<= 120MB，那么可以肯定地说它是一个隐身窗口。
>
> 实验版本：79
    
    
    if ('storage' in navigator && 'estimate' in navigator.storage) {  
    const { usage, quota } = await navigator.storage.estimate();  
    console.log(`Using ${usage} out of ${quota} bytes.`);  
    ​  
    if (quota < 120000000) {  
    console.log('Incognito');  
    } else {  
    console.log('Not Incognito');  
    }  
    } else {  
    console.log('Can not detect');  
    }

![61dbf6b52ab3f51d91b08106.jpg](https://image.3001.net/images/20220121/1642734250_61ea22aa29d9c80a0e5a4.jpg!small)

![61e90f2e2ab3f51d913afd9e.jpg](https://image.3001.net/images/20220121/1642734251_61ea22ab662d0be76c455.jpg!small)

  2. 通过访问时间检

在读取和写入数据时，内存文件系统总是比磁盘文件系统快。在无痕模式下，Chrome 会将写入 API
的数据存储在内存中，而不是像在正常模式下那样将数据持久化到磁盘。

>  **在 2018 年 3 月的设计文档中，Chrome 确定了基于时间和文件系统大小检测隐私模式的风险，并进行了替代实现**
> ：只将元数据保存在内存中，并加密磁盘上的文件。这将解决网站使用时间来区分内存和磁盘存储的风险，并消除基于文件系统大小和文件系统类型（临时与持久）的差异。
>
> 虽然它可以抵御隐私模式检测，但它会留下元数据：即使数据本身无法解密，但是也能作为使用无痕模式的判断依据。

## 参考

<https://segmentfault.com/a/1190000040475726>

<https://www.wenwenya.com/anquan/500644.html>

