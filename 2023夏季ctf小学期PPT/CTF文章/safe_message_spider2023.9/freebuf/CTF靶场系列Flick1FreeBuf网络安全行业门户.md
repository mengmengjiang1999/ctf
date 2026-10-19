# 下载地址

    
    
    https://download.vulnhub.com/flick/flick.tar.gz
    

# 实战演练

查找靶机的IP

![image.png](https://image.3001.net/images/20191004/1570167817_5d96dc095050b.png!small)  

查看靶机开放的端口

![image.png](https://image.3001.net/images/20191004/1570168080_5d96dd1066ba0.png!small)

只有两个端口是开放的。在端口22上使用SSH，在端口8881上使用其他服务。我使用netcat首先查看在端口8881上运行的程序。  

![image.png](https://image.3001.net/images/20191004/1570191626_5d97390a986e9.png!small)  

我尝试了一些常用密码，以长字符串发送，以查看服务是否会崩溃，试图查找格式字符串错误，甚至用SPIKE对其进行了模糊处理，但并没有引起奇怪，所以我不得不找到要求输入的密码对于。

端口22是唯一的其他开放端口，因此我使用SSH连接到它，并收到一串漂亮的文字

    
    
    root@kali:/tmp# ssh 192.168.0.109
    The authenticity of host '192.168.0.109 (192.168.0.109)' can't be established.
    ECDSA key fingerprint is SHA256:OgFkTDTD/D7ndkanMRwJI92zYuzltDSkOS7E3sPlpPk.
    Are you sure you want to continue connecting (yes/no)? yes
    Warning: Permanently added '192.168.0.109' (ECDSA) to the list of known hosts.
    
    \x56\x6d\x30\x77\x64\x32\x51\x79\x55\x58\x6c\x56\x57\x47\x78\x57\x56\x30\x64\x34
    \x56\x31\x59\x77\x5a\x44\x52\x57\x4d\x56\x6c\x33\x57\x6b\x52\x53\x57\x46\x4a\x74
    \x65\x46\x5a\x56\x4d\x6a\x41\x31\x56\x6a\x41\x78\x56\x32\x4a\x45\x54\x6c\x68\x68
    \x4d\x6b\x30\x78\x56\x6d\x70\x4b\x53\x31\x49\x79\x53\x6b\x56\x55\x62\x47\x68\x6f
    \x54\x56\x68\x43\x55\x56\x5a\x74\x65\x46\x5a\x6c\x52\x6c\x6c\x35\x56\x47\x74\x73
    \x61\x6c\x4a\x74\x61\x47\x39\x55\x56\x6d\x68\x44\x56\x56\x5a\x61\x63\x56\x46\x74
    \x52\x6c\x70\x57\x4d\x44\x45\x31\x56\x54\x4a\x30\x56\x31\x5a\x58\x53\x6b\x68\x68
    \x52\x7a\x6c\x56\x56\x6d\x78\x61\x4d\x31\x5a\x73\x57\x6d\x46\x6b\x52\x30\x35\x47
    \x57\x6b\x5a\x53\x54\x6d\x46\x36\x52\x54\x46\x57\x56\x45\x6f\x77\x56\x6a\x46\x61
    \x57\x46\x4e\x72\x61\x47\x68\x53\x65\x6d\x78\x57\x56\x6d\x70\x4f\x54\x30\x30\x78
    \x63\x46\x5a\x58\x62\x55\x5a\x72\x55\x6a\x41\x31\x52\x31\x64\x72\x57\x6e\x64\x57
    \x4d\x44\x46\x46\x55\x6c\x52\x47\x56\x31\x5a\x46\x62\x33\x64\x57\x61\x6b\x5a\x68
    \x56\x30\x5a\x4f\x63\x6d\x46\x48\x61\x46\x4e\x6c\x62\x58\x68\x58\x56\x6d\x30\x78
    \x4e\x46\x6c\x56\x4d\x48\x68\x58\x62\x6b\x35\x59\x59\x6c\x56\x61\x63\x6c\x56\x71
    \x51\x54\x46\x53\x4d\x57\x52\x79\x56\x32\x78\x4f\x56\x57\x4a\x56\x63\x45\x64\x5a
    \x4d\x46\x5a\x33\x56\x6a\x4a\x4b\x56\x56\x4a\x59\x5a\x46\x70\x6c\x61\x33\x42\x49
    \x56\x6d\x70\x47\x54\x32\x52\x57\x56\x6e\x52\x68\x52\x6b\x35\x73\x59\x6c\x68\x6f
    \x57\x46\x5a\x74\x4d\x58\x64\x55\x4d\x56\x46\x33\x54\x55\x68\x6f\x61\x6c\x4a\x73
    \x63\x46\x6c\x5a\x62\x46\x5a\x68\x59\x32\x78\x57\x63\x56\x46\x55\x52\x6c\x4e\x4e
    \x56\x6c\x59\x31\x56\x46\x5a\x53\x55\x31\x5a\x72\x4d\x58\x4a\x6a\x52\x6d\x68\x57
    \x54\x57\x35\x53\x4d\x31\x5a\x71\x53\x6b\x74\x57\x56\x6b\x70\x5a\x57\x6b\x5a\x77
    \x62\x47\x45\x7a\x51\x6b\x6c\x57\x62\x58\x42\x48\x56\x44\x4a\x53\x56\x31\x5a\x75
    \x55\x6d\x68\x53\x61\x7a\x56\x7a\x57\x57\x78\x6f\x62\x31\x64\x47\x57\x6e\x52\x4e
    \x53\x47\x68\x50\x55\x6d\x31\x34\x56\x31\x52\x56\x61\x47\x39\x58\x52\x30\x70\x79
    \x54\x6c\x5a\x73\x57\x6d\x4a\x47\x57\x6d\x68\x5a\x4d\x6e\x68\x58\x59\x7a\x46\x57
    \x63\x6c\x70\x47\x61\x47\x6c\x53\x4d\x31\x46\x36\x56\x6a\x4a\x30\x55\x31\x55\x78
    \x57\x6e\x4a\x4e\x57\x45\x70\x71\x55\x6d\x31\x6f\x56\x31\x52\x58\x4e\x56\x4e\x4e
    \x4d\x56\x70\x78\x55\x32\x74\x30\x56\x31\x5a\x72\x63\x46\x70\x58\x61\x31\x70\x33
    \x56\x6a\x46\x4b\x56\x32\x4e\x49\x62\x46\x64\x57\x52\x55\x70\x6f\x56\x6b\x52\x4b
    \x54\x32\x52\x47\x53\x6e\x4a\x61\x52\x6d\x68\x70\x56\x6a\x4e\x6f\x56\x56\x64\x57
    \x55\x6b\x39\x52\x4d\x57\x52\x48\x56\x32\x35\x53\x54\x6c\x5a\x46\x53\x6c\x68\x55
    \x56\x33\x68\x48\x54\x6c\x5a\x61\x57\x45\x35\x56\x4f\x56\x68\x53\x4d\x48\x42\x4a
    \x56\x6c\x64\x34\x63\x31\x64\x74\x53\x6b\x68\x68\x52\x6c\x4a\x58\x54\x55\x5a\x77
    \x56\x46\x5a\x71\x52\x6e\x64\x53\x4d\x56\x4a\x30\x5a\x55\x64\x73\x55\x32\x4a\x59
    \x59\x33\x68\x57\x61\x31\x70\x68\x56\x54\x46\x56\x65\x46\x64\x75\x53\x6b\x35\x58
    \x52\x58\x42\x78\x56\x57\x78\x6b\x4e\x47\x46\x47\x56\x58\x64\x68\x52\x55\x35\x55
    \x55\x6d\x78\x77\x65\x46\x55\x79\x64\x47\x46\x69\x52\x6c\x70\x7a\x56\x32\x78\x77
    \x57\x47\x45\x78\x63\x44\x4e\x5a\x61\x32\x52\x47\x5a\x57\x78\x47\x63\x6d\x4a\x47
    \x5a\x46\x64\x4e\x4d\x45\x70\x4a\x56\x6d\x74\x53\x53\x31\x55\x78\x57\x58\x68\x57
    \x62\x6c\x5a\x57\x59\x6c\x68\x43\x56\x46\x6c\x72\x56\x6e\x64\x57\x56\x6c\x70\x30
    \x5a\x55\x63\x35\x55\x6b\x31\x58\x55\x6e\x70\x57\x4d\x6a\x56\x4c\x56\x30\x64\x4b
    \x53\x46\x56\x74\x4f\x56\x56\x57\x62\x48\x42\x59\x56\x47\x78\x61\x59\x56\x64\x48
    \x56\x6b\x68\x6b\x52\x32\x68\x70\x55\x6c\x68\x42\x64\x31\x64\x57\x56\x6d\x39\x55
    \x4d\x56\x70\x30\x55\x6d\x35\x4b\x54\x31\x5a\x73\x53\x6c\x68\x55\x56\x6c\x70\x33
    \x56\x30\x5a\x72\x65\x46\x64\x72\x64\x47\x70\x69\x56\x6b\x70\x49\x56\x6c\x64\x34
    \x61\x32\x46\x57\x53\x6e\x52\x50\x56\x45\x35\x58\x54\x57\x35\x6f\x57\x46\x6c\x71
    \x53\x6b\x5a\x6c\x52\x6d\x52\x5a\x57\x6b\x55\x31\x56\x31\x5a\x73\x63\x46\x56\x58
    \x56\x33\x52\x72\x56\x54\x46\x73\x56\x31\x56\x73\x57\x6c\x68\x69\x56\x56\x70\x7a
    \x57\x57\x74\x61\x64\x32\x56\x47\x56\x58\x6c\x6b\x52\x45\x4a\x58\x54\x56\x5a\x77
    \x65\x56\x59\x79\x65\x48\x64\x58\x62\x46\x70\x58\x59\x30\x68\x4b\x56\x31\x5a\x46
    \x57\x6b\x78\x57\x4d\x56\x70\x48\x59\x32\x31\x4b\x52\x31\x70\x47\x5a\x45\x35\x4e
    \x52\x58\x42\x4b\x56\x6d\x31\x30\x55\x31\x4d\x78\x56\x58\x68\x58\x57\x47\x68\x68
    \x55\x30\x5a\x61\x56\x6c\x6c\x72\x57\x6b\x74\x6a\x52\x6c\x70\x78\x56\x47\x30\x35
    \x56\x31\x5a\x73\x63\x45\x68\x58\x56\x45\x35\x76\x59\x56\x55\x78\x57\x46\x56\x75
    \x63\x46\x64\x4e\x56\x32\x68\x32\x56\x31\x5a\x61\x53\x31\x49\x78\x54\x6e\x56\x52
    \x62\x46\x5a\x58\x54\x54\x46\x4b\x4e\x6c\x5a\x48\x64\x47\x46\x68\x4d\x6b\x35\x7a
    \x56\x32\x35\x53\x61\x31\x4a\x74\x55\x6e\x42\x57\x62\x47\x68\x44\x54\x6c\x5a\x6b
    \x56\x56\x46\x74\x52\x6d\x70\x4e\x56\x31\x49\x77\x56\x54\x4a\x30\x61\x31\x64\x48
    \x53\x6c\x68\x68\x52\x30\x5a\x56\x56\x6d\x78\x77\x4d\x31\x70\x58\x65\x48\x4a\x6c
    \x56\x31\x5a\x49\x5a\x45\x64\x30\x55\x32\x45\x7a\x51\x58\x64\x58\x62\x46\x5a\x68
    \x59\x54\x4a\x47\x56\x31\x64\x75\x53\x6d\x6c\x6c\x61\x31\x70\x59\x57\x57\x78\x6f
    \x51\x31\x52\x47\x55\x6e\x4a\x58\x62\x45\x70\x73\x55\x6d\x31\x53\x65\x6c\x6c\x56
    \x57\x6c\x4e\x68\x56\x6b\x70\x31\x55\x57\x78\x77\x56\x32\x4a\x59\x55\x6c\x68\x61
    \x52\x45\x5a\x72\x55\x6a\x4a\x4b\x53\x56\x52\x74\x61\x46\x4e\x57\x56\x46\x5a\x61
    \x56\x6c\x63\x78\x4e\x47\x51\x79\x56\x6b\x64\x57\x62\x6c\x4a\x72\x55\x6b\x56\x4b
    \x62\x31\x6c\x59\x63\x45\x64\x6c\x56\x6c\x4a\x7a\x56\x6d\x35\x4f\x57\x47\x4a\x47
    \x63\x46\x68\x5a\x4d\x47\x68\x4c\x56\x32\x78\x61\x57\x46\x56\x72\x5a\x47\x46\x57
    \x56\x31\x4a\x51\x56\x54\x42\x6b\x52\x31\x49\x79\x52\x6b\x68\x69\x52\x6b\x35\x70
    \x59\x54\x42\x77\x4d\x6c\x5a\x74\x4d\x54\x42\x56\x4d\x55\x31\x34\x56\x56\x68\x73
    \x56\x56\x64\x48\x65\x46\x5a\x5a\x56\x45\x5a\x33\x59\x55\x5a\x57\x63\x56\x4e\x74
    \x4f\x56\x64\x53\x62\x45\x70\x5a\x56\x47\x78\x6a\x4e\x57\x45\x79\x53\x6b\x64\x6a
    \x52\x57\x68\x58\x59\x6c\x52\x42\x4d\x56\x5a\x58\x63\x33\x68\x58\x52\x6c\x5a\x7a
    \x59\x55\x5a\x6b\x54\x6c\x59\x79\x61\x44\x4a\x57\x61\x6b\x4a\x72\x55\x7a\x46\x6b
    \x56\x31\x5a\x75\x53\x6c\x42\x57\x62\x48\x42\x76\x57\x56\x52\x47\x64\x31\x4e\x57
    \x57\x6b\x68\x6c\x52\x30\x5a\x61\x56\x6d\x31\x53\x52\x31\x52\x73\x57\x6d\x46\x56
    \x52\x6c\x6c\x35\x59\x55\x5a\x6f\x57\x6c\x64\x49\x51\x6c\x68\x56\x4d\x46\x70\x68
    \x59\x31\x5a\x4f\x63\x56\x56\x73\x57\x6b\x35\x57\x4d\x55\x6c\x33\x56\x6c\x52\x4b
    \x4d\x47\x49\x79\x52\x6b\x64\x54\x62\x6b\x35\x55\x59\x6b\x64\x6f\x56\x6c\x5a\x73
    \x57\x6e\x64\x4e\x4d\x56\x70\x79\x56\x32\x31\x47\x61\x6c\x5a\x72\x63\x44\x42\x61
    \x52\x57\x51\x77\x56\x6a\x4a\x4b\x63\x6c\x4e\x72\x61\x46\x64\x53\x4d\x32\x68\x6f
    \x56\x6b\x52\x4b\x52\x31\x59\x78\x54\x6e\x56\x56\x62\x45\x4a\x58\x55\x6c\x52\x57
    \x57\x56\x64\x57\x55\x6b\x64\x6b\x4d\x6b\x5a\x48\x56\x32\x78\x57\x55\x32\x45\x78
    \x63\x48\x4e\x56\x62\x54\x46\x54\x5a\x57\x78\x73\x56\x6c\x64\x73\x54\x6d\x68\x53
    \x56\x45\x5a\x61\x56\x56\x63\x31\x62\x31\x59\x78\x57\x58\x70\x68\x53\x45\x70\x61
    \x59\x57\x74\x61\x63\x6c\x56\x71\x52\x6c\x64\x6a\x4d\x6b\x5a\x47\x54\x31\x5a\x6b
    \x56\x31\x5a\x47\x57\x6d\x46\x57\x62\x47\x4e\x34\x54\x6b\x64\x52\x65\x56\x5a\x72
    \x5a\x46\x64\x69\x62\x45\x70\x79\x56\x57\x74\x57\x53\x32\x49\x78\x62\x46\x6c\x6a
    \x52\x57\x52\x73\x56\x6d\x78\x4b\x65\x6c\x5a\x74\x4d\x44\x56\x58\x52\x30\x70\x48
    \x59\x30\x5a\x6f\x57\x6b\x31\x48\x61\x45\x78\x57\x4d\x6e\x68\x68\x56\x30\x5a\x57
    \x63\x6c\x70\x48\x52\x6c\x64\x4e\x4d\x6d\x68\x4a\x56\x31\x52\x4a\x65\x46\x4d\x78
    \x53\x58\x68\x6a\x52\x57\x52\x68\x55\x6d\x73\x31\x57\x46\x59\x77\x56\x6b\x74\x4e
    \x62\x46\x70\x30\x59\x30\x56\x6b\x57\x6c\x59\x77\x56\x6a\x52\x57\x62\x47\x68\x76
    \x56\x30\x5a\x6b\x53\x47\x46\x47\x57\x6c\x70\x69\x57\x47\x68\x6f\x56\x6d\x31\x34
    \x63\x32\x4e\x73\x5a\x48\x4a\x6b\x52\x33\x42\x54\x59\x6b\x5a\x77\x4e\x46\x5a\x58
    \x4d\x54\x42\x4e\x52\x6c\x6c\x34\x56\x32\x35\x4f\x61\x6c\x4a\x58\x61\x46\x68\x57
    \x61\x6b\x35\x54\x56\x45\x5a\x73\x56\x56\x46\x59\x61\x46\x4e\x57\x61\x33\x42\x36
    \x56\x6b\x64\x34\x59\x56\x55\x79\x53\x6b\x5a\x58\x57\x48\x42\x58\x56\x6c\x5a\x77
    \x52\x31\x51\x78\x57\x6b\x4e\x56\x62\x45\x4a\x56\x54\x55\x51\x77\x50\x51\x3d\x3d
    
     .o88o. oooo   o8o            oooo        
     888 `" `888   `"'            `888        
    o888oo   888  oooo   .ooooo.   888  oooo  
     888     888  `888  d88' `"Y8  888 .8P'   
     888     888   888  888        888888.    
     888     888   888  888   .o8  888 `88b.  
    o888o   o888o o888o `Y8bod8P' o888o o888o 
                                              
    
    root@192.168.0.109's password: 
      
    

将这段代码进行解密

    
    
    >>> import sys
    >>> sys.stdout.write(buf)
    
    Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSWFJteFZVMjA1VjAxV2JETlhhMk0xVmpKS1IySkVUbGhoTVhCUVZteFZlRll5VGtsalJtaG9UVmhDVVZacVFtRlpWMDE1VTJ0V1ZXSkhhRzlVVmxaM1ZsWmFkR05GWkZSTmF6RTFWVEowVjFaWFNraGhSemxWVmpOT00xcFZXbUZrUjA1R1drWndWMDFFUlRGV1ZFb3dWakZhV0ZOcmFHaFNlbXhXVm0xNFlVMHhXbk5YYlVaclVqQTFSMWRyV2xOVWJVcEdZMFZ3VjJKVVJYZFpla3BIVmpGT2RWVnRhRk5sYlhoWFZtMXdUMVF3TUhoalJscFlZbFZhY2xWcVFURlNNVlY1VFZSU1ZrMXJjRmhWTW5SM1ZqSktWVkpZWkZwbGEzQklWbXBHVDJSV1ZuUmhSazVzWWxob1dGWnRNSGhPUm14V1RVaG9XR0pyTlZsWmJGWmhZMnhXYzFWclpGaGlSM1F6VjJ0U1UxWnJNWEpqUm1oV1RXNVNNMVpxU2t0V1ZrcFpXa1p3VjFKV2NIbFdWRUpoVkRKT2RGSnJaRmhpVjNoVVdWUk9RMWRHV25STlZFSlhUV3hHTlZaWE5VOVhSMHBJVld4c1dtSkhhRlJXTUZwVFZqRndSMVJ0ZUdsU2JYY3hWa1phVTFVeFduSk5XRXBxVWxkNGFGVXdhRU5UUmxweFUydGFiRlpzV2xwWGExcDNZa2RGZWxGcmJGZFdNMEpJVmtSS1UxWXhWblZWYlhCVFlrVndWVlp0ZUc5Uk1XUnpWMjVLV0dKSFVtOVVWbHBYVGxaYVdHVkhkR2hpUlhBd1dWV
      
    

测试发现，这段代码是base64加密，而且加密了很多次，写个脚本进行自动解密

    
    
    from base64 import b64decode
    
    data = 'Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSWFJteFZVMjA1VjAxV2JETlhhMk0xVmpKS1IySkVUbGhoTVhCUVZteFZlRll5VGtsalJtaG9UVmhDVVZacVFtRlpWMDE1VTJ0V1ZXSkhhRzlVVmxaM1ZsWmFkR05GWkZSTmF6RTFWVEowVjFaWFNraGhSemxWVmpOT00xcFZXbUZrUjA1R1drWndWMDFFUlRGV1ZFb3dWakZhV0ZOcmFHaFNlbXhXVm0xNFlVMHhXbk5YYlVaclVqQTFSMWRyV2xOVWJVcEdZMFZ3VjJKVVJYZFpla3BIVmpGT2RWVnRhRk5sYlhoWFZtMXdUMVF3TUhoalJscFlZbFZhY2xWcVFURlNNVlY1VFZSU1ZrMXJjRmhWTW5SM1ZqSktWVkpZWkZwbGEzQklWbXBHVDJSV1ZuUmhSazVzWWxob1dGWnRNSGhPUm14V1RVaG9XR0pyTlZsWmJGWmhZMnhXYzFWclpGaGlSM1F6VjJ0U1UxWnJNWEpqUm1oV1RXNVNNMVpxU2t0V1ZrcFpXa1p3VjFKV2NIbFdWRUpoVkRKT2RGSnJaRmhpVjNoVVdWUk9RMWRHV25STlZFSlhUV3hHTlZaWE5VOVhSMHBJVld4c1dtSkhhRlJXTUZwVFZqRndSMVJ0ZUdsU2JYY3hWa1phVTFVeFduSk5XRXBxVWxkNGFGVXdhRU5UUmxweFUydGFiRlpzV2xwWGExcDNZa2RGZWxGcmJGZFdNMEpJVmtSS1UxWXhWblZWYlhCVFlrVndWVlp0ZUc5Uk1XUnpWMjVLV0dKSFVtOVVWbHBYVGxaYVdHVkhkR2hpUlhBd1dWV**UMVp0Um5KT1ZsSlhUVlp3V0ZreFdrdGpiVkpIVld4a2FWSnRPVE5XTW5oWFlqSkZlRmRZWkU1V1ZscFVXV3RrVTFsV1VsWlhiVVpzWWtad2VGVXlkREJXTVZweVYyeHdXbFpXY0hKV1ZFWkxWMVpHY21KR1pGZE5NRXBKVm10U1MxVXhXWGhhU0ZaVllrWktjRlpxVG05V1ZscEhXVE5vYVUxWFVucFdNV2h2V1ZaS1IxTnVRbFZXTTFKNlZHdGFhMk5zV25Sa1JtUnBWbGhDTlZkVVFtRmpNV1IwVTJ0a1dHSlhhR0ZVVmxwM1pXeHJlV1ZIZEd0U2EzQXdXbFZhYTJGV1duSmlla1pYWWxoQ1RGUnJXbEpsUm1SellVWlNhVkp1UWxwV2JYUlhaREZrUjJKSVRtaFNWVFZaVlcxNGQyVkdWblJrUkVKb1lYcEdlVlJzVm5OWGJGcFhZMGhLV2xaWFVrZGFWV1JQVTBkR1IyRkhiRk5pYTBwMlZtMTBVMU14VVhsVVdHeFZZVEZ3YUZWcVNtOVdSbEpZVGxjNWEySkdjRWhXYlRBMVZXc3hXRlZzYUZkTlYyaDJWakJrUzFkV1ZuSlBWbHBvWVRGd1NWWkhlR0ZaVm1SR1RsWmFVRll5YUZoWldIQlhVMFphY1ZOcVVsWk5WMUl3VlRKMGIyRkdTbk5UYkdoVlZsWndNMVpyV21GalZrcDBaRWQwVjJKclNraFdSM2hoVkRKR1YxTnVVbEJXUlRWWVdWUkdkMkZHV2xWU2ExcHNVbTFTZWxsVldsTmhSVEZaVVc1b1YxWXphSEpaYWtaclVqRldjMkZGT1ZkV1ZGWmFWbGN4TkdReVZrZFdibEpyVWtWS2IxbFljRWRsVmxKelZtMDVXR0pHY0ZoWk1HaExWMnhhV0ZWclpHRldNMmhJV1RJeFMxSXhjRWRhUms1WFYwVktNbFp0Y0VkWlYwVjRWbGhvV0ZkSGFGWlpiWGhoVm14c2NsZHJkR3BTYkZwNFZXMTBNRll4V25OalJXaFhWak5TVEZsVVFYaFNWa3B6Vkd4YVUySkZXWHBXVlZwR1QxWkNVbEJVTUQwPQ=='decoded = Truewhile decoded:
            try:
                    print(data)
                    data = b64decode(data)
            except:
                    decoded = False

结果显示如下，最后字符串是tabupJievas8Knoj

    
    
    Vm0wd2QyUXlVWGxWV0d4V1YwZDRWMVl3WkRSWFJteFZVMjA1VjAxV2JETlhhMk0xVmpKS1IySkVUbGhoTVhCUVZteFZlRll5VGtsalJtaG9UVmhDVVZacVFtRlpWMDE1VTJ0V1ZXSkhhRzlVVmxaM1ZsWmFkR05GWkZSTmF6RTFWVEowVjFaWFNraGhSemxWVmpOT00xcFZXbUZrUjA1R1drWndWMDFFUlRGV1ZFb3dWakZhV0ZOcmFHaFNlbXhXVm0xNFlVMHhXbk5YYlVaclVqQTFSMWRyV2xOVWJVcEdZMFZ3VjJKVVJYZFpla3BIVmpGT2RWVnRhRk5sYlhoWFZtMXdUMVF3TUhoalJscFlZbFZhY2xWcVFURlNNVlY1VFZSU1ZrMXJjRmhWTW5SM1ZqSktWVkpZWkZwbGEzQklWbXBHVDJSV1ZuUmhSazVzWWxob1dGWnRNSGhPUm14V1RVaG9XR0pyTlZsWmJGWmhZMnhXYzFWclpGaGlSM1F6VjJ0U1UxWnJNWEpqUm1oV1RXNVNNMVpxU2t0V1ZrcFpXa1p3VjFKV2NIbFdWRUpoVkRKT2RGSnJaRmhpVjNoVVdWUk9RMWRHV25STlZFSlhUV3hHTlZaWE5VOVhSMHBJVld4c1dtSkhhRlJXTUZwVFZqRndSMVJ0ZUdsU2JYY3hWa1phVTFVeFduSk5XRXBxVWxkNGFGVXdhRU5UUmxweFUydGFiRlpzV2xwWGExcDNZa2RGZWxGcmJGZFdNMEpJVmtSS1UxWXhWblZWYlhCVFlrVndWVlp0ZUc5Uk1XUnpWMjVLV0dKSFVtOVVWbHBYVGxaYVdHVkhkR2hpUlhBd1dWV**UMVp0Um5KT1ZsSlhUVlp3V0ZreFdrdGpiVkpIVld4a2FWSnRPVE5XTW5oWFlqSkZlRmRZWkU1V1ZscFVXV3RrVTFsV1VsWlhiVVpzWWtad2VGVXlkREJXTVZweVYyeHdXbFpXY0hKV1ZFWkxWMVpHY21KR1pGZE5NRXBKVm10U1MxVXhXWGhhU0ZaVllrWktjRlpxVG05V1ZscEhXVE5vYVUxWFVucFdNV2h2V1ZaS1IxTnVRbFZXTTFKNlZHdGFhMk5zV25Sa1JtUnBWbGhDTlZkVVFtRmpNV1IwVTJ0a1dHSlhhR0ZVVmxwM1pXeHJlV1ZIZEd0U2EzQXdXbFZhYTJGV1duSmlla1pYWWxoQ1RGUnJXbEpsUm1SellVWlNhVkp1UWxwV2JYUlhaREZrUjJKSVRtaFNWVFZaVlcxNGQyVkdWblJrUkVKb1lYcEdlVlJzVm5OWGJGcFhZMGhLV2xaWFVrZGFWV1JQVTBkR1IyRkhiRk5pYTBwMlZtMTBVMU14VVhsVVdHeFZZVEZ3YUZWcVNtOVdSbEpZVGxjNWEySkdjRWhXYlRBMVZXc3hXRlZzYUZkTlYyaDJWakJrUzFkV1ZuSlBWbHBvWVRGd1NWWkhlR0ZaVm1SR1RsWmFVRll5YUZoWldIQlhVMFphY1ZOcVVsWk5WMUl3VlRKMGIyRkdTbk5UYkdoVlZsWndNMVpyV21GalZrcDBaRWQwVjJKclNraFdSM2hoVkRKR1YxTnVVbEJXUlRWWVdWUkdkMkZHV2xWU2ExcHNVbTFTZWxsVldsTmhSVEZaVVc1b1YxWXphSEpaYWtaclVqRldjMkZGT1ZkV1ZGWmFWbGN4TkdReVZrZFdibEpyVWtWS2IxbFljRWRsVmxKelZtMDVXR0pHY0ZoWk1HaExWMnhhV0ZWclpHRldNMmhJV1RJeFMxSXhjRWRhUms1WFYwVktNbFp0Y0VkWlYwVjRWbGhvV0ZkSGFGWlpiWGhoVm14c2NsZHJkR3BTYkZwNFZXMTBNRll4V25OalJXaFhWak5TVEZsVVFYaFNWa3B6Vkd4YVUySkZXWHBXVlZwR1QxWkNVbEJVTUQwPQ==
    b'Vm0wd2QyUXlVWGxWV0d4V1YwZDRXRmxVU205V01WbDNXa2M1VjJKR2JETlhhMXBQVmxVeFYyTkljRmhoTVhCUVZqQmFZV015U2tWVWJHaG9UVlZ3VlZadGNFZFRNazE1VTJ0V1ZXSkhhRzlVVjNOM1pVWmFkR05GWkZwV01ERTFWVEowVjFaWFNraGhSemxWVm14YU0xWnNXbUZrUjA1R1drWlNUbUpGY0VwV2JURXdZekpHVjFOdVVtaFNlbXhXVm1wT1QwMHhjRlpYYlVaclVqQTFSMVV5TVRSVk1rcFhVMnR3VjJKVVJYZFpla3BIVmpGT2RWVnRhRk5sYlhoWFZtMHhORmxWTUhoWGJrNVlZbFZhY2xWc1VrZFhiR3QzV2tSU1ZrMXJjRmhWTW5SM1ZqSktWVkpZWkZwV1JWcHlWVEJhVDJOdFJrZFhiV3hUWVROQ1dGWnRNVEJXTWxGNVZXNU9XR0pIVWxsWmJHaFRWMFpTVjFwR1RteGlSbXcxVkZaU1UxWnJNWEpqUld4aFUwaENTRlpxU2tabFZsWlpXa1p3YkdFelFrbFdWM0JIVkRKU1YxVnVVbXBTYkVwVVZteG9RMWRzV25KWGJHU**UVlpXTlZaWGVHdGhiRXAwWVVoT1ZtRnJOVlJXTVZwWFkxWktjbVJHVWxkaVJtOTNWMnhXYjJFeFdYZE5WVlpUWWtkU1lWUlZXbUZsYkZweFUydDBWMVpyV2xwWlZWcHJWVEZLV1ZGcmJGZFdNMEpJVmtSS1UxWXhaSFZVYkZKcFZqT**WVlpHWTNoaU1XUnpWMWhvWVZKR1NuQlVWM1J6VGtaa2NsWnRkRmRpVlhCNVdUQmFjMWR0U2tkWGJXaGFUVlp3ZWxreWVHdGtSa3AwWlVaa2FWWnJiekZXYlhCTFRrWlJlRmRzYUZSaVJuQlpWbXRXZDFkR2JITmhSVTVZVW14d2VGVnRkREJoYXpGeVRsVnNXbFpXY0hKWlZXUkdaVWRPU0dGR2FHbFNia0p2Vm10U1MxUXlUWGxVYTFwaFVqS**WRlJYTlc5a2JGcEhWbTA1VWsxWFVsaFdNV2h2VjBkS1dWVnJPVlpoYTFwSVZHeGFZVmRGTlZaUFYyaFhZWHBXU0ZacVNqUlZNV1IwVTJ0b2FGSnNTbGhVVlZwM1ZrWmFjVkp0ZEd0V2JrSkhWR3hhVDJGV1NuUlBWRTVYWVRGd2FGWlVSa1psUm1SellVWlNhRTFZUW5oV1YzaHJZakZrUjFWc2FFOVdWVFZaVlcxNGQyVkdWblJrUkVKb1lYcEdlVlJzVm05WGJGcFhZMGhLV2xaWFVrZGFWM2hIWTIxS1IxcEdaRk5XV0VKMlZtcEdZV0V4VlhoWFdHaFZZbXhhVmxscldrdGpSbFp4VW10MFYxWnNjRWhXVjNSTFlUQXhSVkpzVGxaU2JFWXpWVVpGT1ZCUlBUMD0='
    b'Vm0wd2QyUXlVWGxWV0d4WFlUS**WMVl3Wkc5V2JGbDNXa1pPVlUxV2NIcFhhMXBQVjBaYWMySkVUbGhoTVVwVVZtcEdTMk15U2tWVWJHaG9UV3N3ZUZadGNFZFpWMDE1VTJ0V1ZXSkhhRzlVVmxaM1ZsWmFkR05GWkZSTmJFcEpWbTEwYzJGV1NuUmhSemxWVmpOT00xcFZXbUZrUjA1R1UyMTRVMkpXU2twV2JURXdZekpHVjFOdVVtaFNlbXhXVm0xNFlVMHhXbk5YYlVaclVsUkdXbGt3WkRSVk1rcFhVMnR3VjJKVVJYZFpWRVpyVTBaT2NtRkdXbWxTYTNCWFZtMTBWMlF5VW5OWGJHUllZbGhTV0ZSV1pGTmxiRmw1VFZSU1ZrMXJjRWxhU0hCSFZqSkZlVlZZWkZwbGEzQklWV3BHVDJSV1VuUmpSbEpUVmxoQ1dsWnJXbGRoTVZWNVZXeGthbEp0YUhOVmFrNVRWMVpXY1ZKcmRGUldiR**3V2xWb2ExWXdNVVZTYkdSYVRVWmFlbFpxU2t0V1ZrWlpZVVprVTFKWVFrbFdWM0JIVkRKU1YxZHVUbFJpVjNoVVZGY3hiMWRzV1hoYVJGSnBUV3RzTkZkclZtdFdiVXB5WTBac1dtSkdXbWhaTVZwelkyeGtkRkp0ZUZkaVZrbzFWbXBLTkZReFdsaFRiRnBZVmtWd1dGbHNhRU5YUmxweFVtdDBhazFyTlVsWlZWcHJZVWRGZUdOSGFGaGlSbkJvVmtSS1QyTXlUa1phUjJoVFRXNW9kbFpHVm05Uk1XUlhWMWhvV0dKWVVrOVZha1pIVGxaYVdFNVZPV2hXYXpWSFZqSjRVMWR0U2toaFJsSlhUVVp3VkZacVJtdGtWbkJHVGxaT2FWSnRPVE5XYTFwaFZURkZlRmRzYUZSaE1YQnhWV3hrYjFkR1VsaE9WVTVZVW14d2VGVnRkREJoYXpGeVRsV**XbFpXY0hKWlZXUkdaV3hHY21KR1pGZFNWWEJ2VmpGYWExVXhXWGhVYmxaVllrWktjRlZxUmt0V1ZscEhWV3RLYTAxRVJsTlZSbEYzVUZFOVBRPT0='
    b'Vm0wd2QyUXlVWGxXYTJoV1YwZG9WbFl3WkZOVU1WcHpXa1pPV0Zac2JETlhhMUpUVmpGS2MySkVUbGhoTWsweFZtcEdZV015U2tWVWJHaG9UVlZ3VlZadGNFZFRNbEpJVm10c2FWSnRhRzlVVjNOM1pVWmFkR05GU214U2JWSkpWbTEwYzJGV1NuUmhSemxWVm14YU0xWnNXbUZrUlRGWlkwZDRVMkpXU2twV2JURXdZVEZrU0ZOcmFGWmlSa3BXVm10V2QyUnNXbGRYYlhSWFRWZFNlbFl5TVRSVk1rcElaSHBHVjJFeVVYZFpla3BIVWpGT2RWUnRjRlJTVlhCWlZrWldhMVV5VWxkalJtaHNVak5TV1ZWcVJrdFRWbFowWlVoa1YwMUVSbGRaTUZaelZqSktWVkZZYUZkU1JYQklWV3BHVDJSV1duTlRiV3hUVFcxb1dsWXhaRFJpTWtsNFdrVmtWbUpyY0ZsWmJGWmhZMVpzY2xkdFJteFdiVko1VmpKNFQxWlhTbFpYVkVwWFlsaENXRlpxUmt0ak1rNUlZVVprYUdFeGNHaFhiRnBoVkRKT2MyTkZaR2hTTW5odlZGV**RMWRXV1hoWGJYUk9VakZHTlZaWE5VOWhWazVHVjJ4U1dtSkhhRlJXTUZwVFZqRmtkVnBGTlZOaVJtOTNWa1phVTFFeFdsaFRhMXBxVWxkb1dGUlhOVU5YUmxweFVtdDBhazFyTlVoWlZWcHJZVWRGZWxGcmJGZFdSVXBvVjFaa1UxWXhUblZVYkZKcFVqRktWVlpHVWtKa01ERlNVRlF3UFE9PQ=='
    b'Vm0wd2QyUXlWa2hWV0doVlYwZFNUMVpzWkZOWFZsbDNXa1JTVjFKc2JETlhhMk0xVmpGYWMySkVUbGhoTVVwVVZtcEdTMlJIVmtsaVJtaG9UV3N3ZUZadGNFSmxSbVJJVm10c2FWSnRhRzlVVmxaM1ZsWmFkRTFZY0d4U2JWSkpWbTEwYTFkSFNraFZiRkpWVmtWd2RsWldXbXRXTVdSelYyMTRVMkpIZHpGV2EyUXdZekpHUjFOdVRtcFRSVXBZVkZWa1UyUldjRmhsUjNSWVVqRktTVlZ0ZUhkV01ERldZMFZzVjJKVVFYaFdSRXBIVWpGT2RWWnNTbWxTTW1oWlYxZDRiMkl4WkVkVmJrcFlZbFZhY1ZscldtRmxWbVJ5VjJ4T1ZXSlZXVEpXYlhCWFZqRktjMk5IYUZkaGExcGhXbFphVDJOc2NFZGhSMnhvVFVoQ1dWWXhXbXROUjFGNVZXNU9hVk5GV2xSWmJHaFRWMFpTVjFkdVpFNVNiR**3VkZaU1ExWlhTa1pqUldoWFRXNUNXRlpxUmt0ak1rNUhZVVprYUdFelFrbFdWRUpoV1ZkU1YxTnVUbFJpUjFKVVZGUkJkMDFSUFQwPQ=='
    b'Vm0wd2QyVkhVWGhVV0dST1ZsZFNXVll3WkRSV1JsbDNXa2M1VjFac2JETlhhMUpUVmpGS2RHVkliRmhoTWsweFZtcEJlRmRIVmtsaVJtaG9UVlZ3VlZadE1YcGxSbVJJVm10a1dHSkhVbFJVVkVwdlZWWmtWMWRzV214U2JHdzFWa2QwYzJGR1NuTmpTRUpYVFVkU2RWcFhlR3RYUjFKSVVteHdWMDFWY0VsV2JUQXhWREpHUjFOdVZsSmlSMmhZV1d4b2IxZEdVbkpYYlVacVlrWmFlVmRyV2xOVWJVWTJWbXBXVjFKc2NHaFdha1phWlZaT2NscEdhR2xoTUhCWVYxWmtNR1F5VW5OaVNFWlRZbGhTV0ZSV1duZE5SbFowVFZSQ1ZXSkZjRWhXTW5CWFZqRktjMk5HYUZkaGEzQklWVEJhWVdSV1NuTlRiR1JUVFRBd01RPT0='
    b'Vm0wd2VHUXhUWGROVldSWVYwZDRWRll3Wkc5V1ZsbDNXa1JTVjFKdGVIbFhhMk0xVmpBeFdHVkliRmhoTVVwVVZtMXplRmRIVmtkWGJHUlRUVEpvVVZkV1dsWmxSbGw1Vkd0c2FGSnNjSEJXTUdSdVpXeGtXR1JIUmxwV01VcElWbTAxVDJGR1NuVlJiR2hYWWxob1dGUnJXbUZqYkZaeVdrWlNUbUY2VmpWV1JscGhWakZaZVZOclpGaGlhMHBYV1ZkMGQyUnNiSEZTYlhSWFRWWndNRlZ0TVRCVWJFcEhWMnBXVjFKc2NGaFdha3BIVTBaYWRWSnNTbGRTTTAwMQ=='
    b'Vm0weGQxTXdNVWRYV0d4VFYwZG9WVll3WkRSV1JteHlXa2M1VjAxWGVIbFhhMUpUVm1zeFdHVkdXbGRTTTJoUVdWWlZlRll5VGtsaFJscHBWMGRuZWxkWGRHRlpWMUpIVm01T2FGSnVRbGhXYlhoWFRrWmFjbFZyWkZSTmF6VjVWRlphVjFZeVNrZFhia0pXWVd0d2RsbHFSbXRXTVZwMFVtMTBUbEpHV2pWV1JscFhWakpHU0ZadVJsSldSM001'
    b'Vm0xd1MwMUdXWGxTV0doVVYwZDRWRmxyWkc5V01XeHlXa1JTVmsxWGVGWldSM2hQWVZVeFYyTklhRlppV0dneldXdGFZV1JHVm5OaFJuQlhWbXhXTkZaclVrZFRNazV5VFZaV1YySkdXbkJWYW****lqRmtWMVp0Um10TlJGWjVWRlpXVjJGSFZuRlJWR3M5'
    b'Vm1wS01GWXlSWGhUV0d4VFlrZG9WMWxyWkRSVk1XeFZWR3hPYVUxV2NIaFZiWGgzWWtaYWRGVnNhRnBXVmxWNFZrUkdTMk5yTVZWV2JGWnBVakpvYjFkV1ZtRmtNRFZ5VFZWV2FHVnFRVGs9'
    b'VmpKMFYyRXhTWGxTYkdoV1lrZDRVMWxVVGxOaU1WcHhVbXh3YkZadFVsaFpWVlV4VkRGS2NrMVVWbFZpUjJob1dWVmFkMDVyTVVWaGVqQTk='
    b'VjJ0V2ExSXlSbGhWYkd4U1lUTlNiMVpxUmxwbFZtUlhZVVUxVDFKck1UVlViR2hoWVVad05rMUVhejA9'
    b'V2tWa1IyRlhVbGxSYTNSb1ZqRlplVmRXYUU1T1JrMTVUbGhhYUZwNk1Eaz0='
    b'WkVkR2FXUllRa3RoVjFZeVdWaE5ORk15TlhaaFp6MDk='
    b'ZEdGaWRYQkthV1YyWVhNNFMyNXZhZz09'
    b'dGFidXBKaWV2YXM4S25vag=='
    b'tabupJievas8Knoj'
    b'\xb5\xa6\xee\xa4\x98\x9e\xbd\xab<*z#'

重新连接8881端口，输入字符串之后，会提示后门已经打开

![image.png](https://image.3001.net/images/20191004/1570192932_5d973e244536f.png!small)重新扫描端口，我们看到80端口已经打开了

![image.png](https://image.3001.net/images/20191004/1570193293_5d973f8d7a52b.png!small)浏览器打开80端口

![image.png](https://image.3001.net/images/20191004/1570193351_5d973fc7aa2a8.png!small)![image.png](https://image.3001.net/images/20191004/1570193534_5d97407e835bf.png!small)根据社会工程学，生成了demo+数字的字典，使用BP进行爆破

![image.png](https://image.3001.net/images/20191004/1570194577_5d97449197873.png!small)  

![image.png](https://image.3001.net/images/20191004/1570194556_5d97447c6507b.png!small)登录进去，发现多了一个上传功能

![image.png](https://image.3001.net/images/20191004/1570194612_5d9744b42f0af.png!small)  

测试发现，上传功能虽然可以上传webshell，但是无法执行。

然后发现http://192.168.0.109/image/download?filename=images/mPTRlZ8Bf3Wt可能存在遍历漏洞，提示无效文件不能下载

![image.png](https://image.3001.net/images/20191004/1570194820_5d974584744a5.png!small)换个遍历方式，发现可以查看

![image.png](https://image.3001.net/images/20191004/1570194916_5d9745e435d5f.png!small)查看web目录是什么

![image.png](https://image.3001.net/images/20191004/1570195286_5d97475660ab4.png!small)  

这显示了网站的DocumentRoot，位于/var/www/flick_photos。我记得该Web应用程序使用的是Laravel，我并不熟悉。经过一段时间的Google搜索，我在[GitHub上](https://github.com/andrewelkins/Laravel-4-Bootstrap-Starter-Site/)找到了Laravel ，这使我得以了解Laravel的结构。环顾四周后，我发现了几个有趣的目录。

我能够从目标中拉出app/database/production.sqlite。我什至不必使用sqlite3加载它，因为转储实际上显示了表和字段：

![image.png](https://image.3001.net/images/20191004/1570195466_5d97480a8df52.png!small)现在，我有了robin和dean的密码。

    
    
    robin: JoofimOwEakpalv4Jijyiat5GloonTojatticEirracksIg4yijovyirtAwUjad1
    dean : FumKivcenfodErk0Chezauggyokyait5fojEpCayclEcyaj2heTwef0OlNiphAnA

我尝试使用这些新发现的凭据通过SSH进入服务器。robin的密码无效，但dean的密码有效  

主目录中有两个有趣的文件。message.txt和read_docker。message.txt包含以下内容：  

![image.png](https://image.3001.net/images/20191004/1570195738_5d97491a8b927.png!small)按照message的提示，找到了一个dockerfile

![image.png](https://image.3001.net/images/20191004/1570195864_5d9749985c562.png!small)

使用符号链接，我们可以读取robin用户拥有的任意文件。

![image.png](https://image.3001.net/images/20191004/1570196295_5d974b4741b1d.png!small)

找到了robin用户的密钥

![image.png](https://image.3001.net/images/20191004/1570196415_5d974bbf65a1a.png!small)使用密钥进行登录

    
    
    dean@flick:~$ ssh -i id_rsa  robin@127.0.0.1 
    The authenticity of host '127.0.0.1 (127.0.0.1)' can't be established.
    ECDSA key fingerprint is 2d:32:93:ce:0e:54:3f:84:ee:01:c7:c0:bb:68:e2:02.
    Are you sure you want to continue connecting (yes/no)? yes
    Warning: Permanently added '127.0.0.1' (ECDSA) to the list of known hosts.
    
    Welcome to Ubuntu 12.04.4 LTS (GNU/Linux 3.11.0-15-generic x86_64)
    
     * Documentation:  https://help.ubuntu.com/
    
      System information as of Fri Oct  4 15:41:43 SAST 2019
    
      System load:  0.02              Processes:              121
      Usage of /:   35.8% of 6.99GB   Users logged in:        1
      Memory usage: 55%               IP address for eth0:    192.168.0.109
      Swap usage:   0%                IP address for docker0: 172.17.42.1
    
      Graph this data and manage this system at:
        https://landscape.canonical.com/
    
    Last login: Sat Aug  2 12:43:16 2014 from 192.168.56.1
    robin@flick:~$ 
    
    

事实证明，robin能够使用sudo运行至少一个命令：  

![image.png](https://image.3001.net/images/20191004/1570196712_5d974ce81504a.png!small)  

不幸的是，我对该文件没有读取权限，所以我不知道它在做什么。我注意到robin的PATH环境变量包含/home/robin/bin，该变量不存在。我假设/opt/start_apache/restart.sh可能会调用某些未指定绝对路径的命令，因此它将在/home/robin/bin中运行。因此，我在/bin中制作了每个命令的副本，其中包含一个简单的命令，如果执行则回显“
w00t”。

不幸的是，事实并非如此。因此，我将注意力转向了docker

![image.png](https://image.3001.net/images/20191004/1570196784_5d974d30080b6.png!small)我发现可以将主机操作系统的/root目录挂载到映像的/root目录中。这使我可以访问主机操作系统的/root的内容  

被调戏了

![image.png](https://image.3001.net/images/20191004/1570196881_5d974d915daa9.png!small)查看另外一个目录，找到了真正的flag

![image.png](https://image.3001.net/images/20191004/1570196926_5d974dbe5c10e.png!small)  

