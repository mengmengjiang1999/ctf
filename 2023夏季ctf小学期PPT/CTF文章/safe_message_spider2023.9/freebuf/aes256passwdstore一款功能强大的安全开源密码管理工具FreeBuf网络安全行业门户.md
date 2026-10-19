![](https://image.3001.net/images/20210930/1632952455_6154e087e40be0ab4f876.png!small)

## 关于aes256_passwd_store

aes256_passwd_store是一款功能强大的安全开源密码管理工具，该脚本可以安全地加密或解密自定义数据库文件中磁盘上的密码。除此之外，该工具还可以从以前生成的数据库文件中检索密码信息。

## 技术分析

该脚本可以从stdin/或内存中获取Master密码，然年后使用指定的哈希算法参数（scrypt、sha256）对密码进行哈希计算，最后使用AES-256并以算法的哈希作为AES-256密钥对文件数据进行加密/解密。

当为算法参数提供'scrypt'参数时，脚本将为每个数据库文件的编辑或创建生成自定义scrypt
salt。唯一生成的salt是base64编码的，并在每个数据库文件的加密字节前加上前缀，这些字节由回车行分隔，以作为元数据使用。

使用密码修改参数“-cp‘时，脚本将会解密数据库文件信息，并向数据库文件中写入随机字节“*WIPE_PASSES”，然后截断文件，并最终将新的AES-256解密数据以及新的Master密码哈希写入至数据库文件。这样一来，将增加数据恢复和安全取证的难度。

## 工具下载

由于该工具基于Python3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。

接下来，就可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/c0dy-c0des/aes256_passwd_store.git

## 工具使用-以scrypt作为哈希算法

创建一个数据库文件：

    
    
    python3 aespasswd_store.py -a scrypt -c <filename>

修改数据库文件的Master密码：

    
    
    python3 aespasswd_store.py -a scrypt -cp <filename>

编辑数据库文件：

    
    
    python3 aespasswd_store.py -a scrypt -e <filename>

从数据库文件中查询密码数据：

    
    
    python3 aespasswd_store.py -a scrypt -q <filename>

## 工具使用样例

    
    
    # 向数据库中添加实体/修改现有数据:
    pass_id1=password
    pass_id2=password
    pass_id3=password
    # 删除现有数据:
    pass_id1=delete
    pass_id2=delete
    # -q参数：查询数据（输入为空的情况下将导出所有数据）：
    pass_id1
    pass_id3
    # 按下Ctrl + D键（Linux）或Ctrl + Z键（Windows）来存储标准输入数据。

## 项目地址

 **aes256_passwd_store：** 【[
_GitHub传送门_](https://github.com/c0dy-c0des/aes256_passwd_store)】

