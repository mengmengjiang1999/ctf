【CTF MISC】压缩包题型

[ Du1in9](https://www.jianshu.com/u/32aab16373de)关注赞赏支持

# 【CTF MISC】压缩包题型

 **一.常规操作**

  * winhex打开，搜索字符pass 、 key 等，查看是否有含有密码
  * 工具爆破（ ARCHPR，Accent RAR）
  * 根据题意或者社工猜密码

**二.CRC32碰撞**

> 压缩文档中会提供一个CRC32的值，这个值是文档在压缩之前的CRC32值，每个不同的文件都有唯一的一个CRC32值，小范围内基本不可能重复

  * 第一步

先在7-zip里看CRC32值和文档字节大小

也可以用脚本获取CRC32值

    
    
    # 我这里flag.zip里有5个文档
    import zipfile
    import binascii
    
    f = zipfile.ZipFile('flag.zip', 'r')
    for I in range(1,6):
        GetCrc = f.getinfo(str(I)+'.txt')
        crc = GetCrc.CRC
        print hex(crc)
    

  * 第二步

用工具碰撞，命令：python crc32.py reverse CRC32值  
[https://github.com/theonlypwner/crc32](https://links.jianshu.com/go?to=https%3A%2F%2Fgithub.com%2Ftheonlypwner%2Fcrc32)

所以这里猜测“can_U_”就是flag的一部分了  
同样也可以用脚本碰撞，只不过字节数大了就要爆破很久...

    
    
    # 我这里字节数为6
    import binascii
    
    dic = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+- ={}[]"
    crc = 0x1bf18e63    
    for i in dic : 
        for j in dic:
            for p in dic:
                for q in dic:
                    for a in dic:
                        for b in dic:
                            s=i+j+p+q+a+b
                            if crc == (binascii.crc32(s) & 0xffffffff):
                                print(s)
    

**三.伪加密**

  * 直接用7z解压或linux下打开
  * ZipCenOp修改或手改加密标记位

**四.明文攻击**

>
> 如果有一个加密压缩包里的相同的未加密文件，把该文件用zip压缩即可利用它来破解加密压缩包，由于用不同的压缩工具压缩的压缩包进行破解时会提示不符，可以挨个儿试一下，反正常用的压缩软件也不多，winrar，好压，7z，Bandizip

  * 一般加密压缩包作为破解文件，但也有例外。例题：我们的密码，secret.bin提出一个压缩包和readme.txt，可以直接使用secre.bin作为要破解的文件 ，然后把readme.txt压缩为zip
  * 破解时要注意看，哪怕破解成功了，它也会继续运行下去，这时暂停即可看到密码

**五.掩码爆破**

  * 例如已知压缩包密码为：ISCC****（未知），掩码爆破：ISCC????即可

**六.字典爆破**

  * 常用字典
  * 自己构造字典  
例如已知压缩包密码为：ISCC****（字母和数字）

    
    
    # Python3
    pw = 'ISCC'
    dic = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    f = open('dic.txt','w')
    for i in dic:
        for j in dic:
            for a in dic:
                for b in dic:
                    f.write(pw+i+j+a+b+'\n')
    f.close
    

**七.在图片中隐藏压缩包**

  * 使用foremost分离或直接改后缀名

**八.通过进制转换隐藏信息**

  * 例如一串16进制信息：504B0304.....或52617221....，分别是zip和rar的文件头，我们就可以在winHex中创建压缩包

