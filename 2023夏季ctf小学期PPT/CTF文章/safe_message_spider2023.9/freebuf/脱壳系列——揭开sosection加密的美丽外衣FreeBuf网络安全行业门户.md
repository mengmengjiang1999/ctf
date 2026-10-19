[i春秋作家：HAI_](https://bbs.ichunqiu.com/thread-37949-1-1.html?from=beef)

# 0x00 前言  

对so的加密，[](https://bbs.pediy.com/thread-191649.htm%E5%A4%A7%E7%A5%9E%E7%9A%84%E5%B8%96%E5%AD%90%E9%87%8C%E5%B7%B2%E7%BB%8F%E5%BE%88%E8%AF%A6%E7%BB%86%E7%9A%84%E8%AF%B4%E6%98%8E%E4%BA%86%E3%80%82%E5%BD%93%E7%84%B6%E5%8A%A0%E5%AF%86%E4%B8%8D%E6%98%AF%E6%88%91%E4%BB%AC%E7%A0%94%E7%A9%B6%E7%9A%84%E9%87%8D%E7%82%B9%EF%BC%8C%E5%A6%82%E4%BD%95%E6%90%9E%E6%8E%89%E8%BF%99%E4%B8%AAso%E7%9A%84%E5%8A%A0%E5%AF%86%E6%89%8D%E6%98%AF%E6%88%91%E4%BB%AC%E7%9A%84%E8%A6%81%E4%BA%8B)[https://bbs.pediy.com/thread-191649.htm大神的帖子里已经很详细的说明了。当然加密不是我们研究的重点，如何搞掉这个so的加密才是我们的要事。](https://bbs.ichunqiu.com/thread-37949-1-1.html?from=beef)

或许你想看看这里  

[HAI_使用手册](https://bbs.ichunqiu.com/thread-37949-1-1.html?from=beef)

[java开发之旅](https://bbs.ichunqiu.com/thread-37949-1-1.html?from=beef)

[Android开发之旅](https://bbs.ichunqiu.com/thread-37949-1-1.html?from=beef)

# 0x01 so静态分析

## 1.未加密之前的so

![image.png](https://image.3001.net/images/20180409/15232604937944.png!small)  

## 2.加密之后的so

我们使用ida打开的时候，ida进行了报错提示。

![image.png](https://image.3001.net/images/20180409/15232605021779.png!small)  

可能在平时很多时候都会发现so是被加密了的，ida就会报这个错误，我们忽略这个，然后进入。

![image.png](https://image.3001.net/images/20180409/15232605182222.png!small)  

这个就是我们加密过后的内容。

## 3.结论

so文件进行加密之后效果很明显，无法在加密之后的so得出有用信息。也相当于是对so进行了加壳，再详细一点就是加密壳。

而我们最主要做的就是脱掉这个加密壳。

  
![image.png](https://image.3001.net/images/20180409/15232605323634.png!small)  

# 0x02 动态脱壳

又到了我们最好玩的脱壳环节了。

利用一个最原理就是，不管你加密成什么样子，在内存中，你总是要还原的，不还原系统怎么运行。

所以我们需要进行一个动态脱壳。

## 连接手机，开启服务，attach

    
    
    su
    
    cd data/local/tmp
    
    ./zhu -p23333
    
    adb forward tcp:23333 tcp:23333
    
    //可能会用到
    adb shell am start -D -n com.example.shelldemo/.MainActivity
    
    adb forward tcp:8700 jdwp:7728
    
    jdb -connect com.sun.jdi.SocketAttach:hostname=127.0.0.1,part=8700

成功附加。

![image.png](https://image.3001.net/images/20180409/15232605544187.png!small)  

这个时候程序已经在运行了。

所以我们需要找到demo里的so文件。

![image.png](https://image.3001.net/images/20180409/15232605636136.png!small)  

文件偏移是：75A00000  
大小是：5000

我们来dump一下。

程序的话还是用之前的程序把。

    
    
    static main(void){
        auto fp, begin, end, dexbyte;
        //打开或创建一个文件
        fp = fopen("d:\\dump.dex", "wb");
        //dex基址
        begin =  0xF34C6320;    
    //dex基址 + dex文件大小
    end = begin + 0x00013570;
        for ( dexbyte = begin; dexbyte < end;     dexbyte ++ ){
    //按字节将其dump到本地文件中
    fputc(Byte(dexbyte), fp);
            }
    }

稍稍的更改一下就可以使用了。

好了我们成功dump。

  
![image.png](https://image.3001.net/images/20180409/15232605799630.png!small)  

## 测试

使用ida打开。

发现ida还是报错。

  
![image.png](https://image.3001.net/images/20180409/15232605874583.png!small)  

![image.png](https://image.3001.net/images/20180409/15232606167130.png!small)  

先忽略，进去。

![image.png](https://image.3001.net/images/20180409/15232606228026.png!small)  

这个时候发现关键函数已经出来了。

但是我们还是想要追求一下完美。

# 0x03 修复

我们这里修复使用工具进行。

![image.png](https://image.3001.net/images/20180409/15232606358083.png!small)  

然后使用ida进行测试。

![image.png](https://image.3001.net/images/20180409/15232606424842.png!small)  

修复成功。

  

