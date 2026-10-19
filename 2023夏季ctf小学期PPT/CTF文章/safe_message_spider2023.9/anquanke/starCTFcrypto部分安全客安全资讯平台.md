# starCTF-crypto部分

阅读量 **202219**

|评论 **1**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-05-07 10:45:03

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t019b3c176eff1daf8e.jpg)

## 前言

临近五一事情比较多，基本用的是零碎的时间玩的*ctf，有些题目还是很有趣的

## babyprng

首先看一下主要代码：

    
    
    def run(self, code):
        stack = []
        out = []
        cnt = 0
        random.seed(os.urandom(8))
        self.TH = 0.7 + random.random()*0.25
        for _ in xrange(self.SIZE):
            stack.append(self.randbit())
        try:
            pos = 0
            for _ in xrange(self.SIZE*10):
                c = code[pos]
                pos += 1
                if c=='x00':
                    out.append(stack[-1])
                elif c=='x01':
                    if stack[-1]==1:
                        pos += 1
                elif c=='x02':
                    del stack[-1]
                elif c=='x03':
                    stack[-1] = stack[-1]&stack[-2]
                elif c=='x04':
                    stack[-1] = stack[-1]|stack[-2]
                elif c=='x05':
                    stack[-1] = stack[-1]^stack[-2]
                #elif c=='x06':
                #    stack[-1] = 1-stack[-1]
                #elif c=='x06':
                #    stack.append(stack[-1])
                elif ord(c)>=0x10 and ord(c)<=0x30:
                    pos += ord(c)-0x10
                elif ord(c)>=0x30 and ord(c)<=0x50:
                    pos -= ord(c)-0x30
    

首先TH随机生成的值大概会在0.8左右，后面就以TH=0.8来讨论，那么按照算法，stack中大概有80%为0，20%为1

我们要做的是使得最终的out有大约一半的0和一半的1，而且元素的个数不能太少，我做这种题目喜欢在本地搭建，因为proof_of_work等待的时间实在有点长

我们关注第三个，第四个，第五个操作，列举出stack最后两个元素的可能情况和经过这些操作后的值：

出现的概率 | 最后两个元素可能的值 | 与操作 | 或操作 | 异或操作  
---|---|---|---|---  
64% | 00 | 00 | 00 | 00  
16% | 01 | 00(改变) | 01 | 01  
16% | 10 | 10 | 11（改变） | 11（改变）  
4% | 11 | 11 | 11 | 10（改变）  
  
###  自己的解法

观察到对于10来说^操作可以将其变为11而11又可以变成10，这样最后一位就可以在我们的控制下做周期性的交替了，而且最后两步操作是可以重新将pos指针重新指向code的任意位置的，如此一来就能实现周期性的循环操作，所以解法是在一个周期的前半周期里重复执行0的操作，然后中间执行一次异或操作，改变最后一元素的值，后半周期再重复执行0操作，这样就能再一个周期里取一半的0再取一半的1了

上面能成功的前提条件是stack最后两位的初始值为10或者11，可能的概率为16%+4%=20%，所以如果没有成功的话多尝试几次就可以了，exp：

    
    
    from socket import *
    from libnum import *
    import string
    from re import *
    from hashlib import sha256
    
    def connect(host, port):
        s = socket()
        s.connect((host, port))
        return s
    
    def cal(proof, ans, set):
        for i in set:
            for j in set:
                for k in set:
                    for m in set:
                        if sha256(i+j+k+m+proof).hexdigest() == ans:
                            print i+j+k+m
                            return i+j+k+m
    
    def proof_of_work(s):
        msg = s.recv(1024)
        print msg
        set = string.ascii_letters+string.digits
    
        reg = 'sha256(XXXX+(.+)) == (.+)n'
        regexp = compile(reg)
        res = regexp.findall(msg)
    
        proof = res[0][0]
        ans = res[0][1]
    
        print s.recv(1024)
        s.send(cal(proof, ans, set))
        print s.recv(1024)
    
    
    def main():
        host = '34.92.185.118'
        port = 10002
        s = connect(host, port)
        proof_of_work(s)
    
        msg = chr(0)*15+chr(5)+chr(0)*15+chr(0x50)
        print msg.encode('hex')
        s.send(msg.encode('hex')+'n')
        print s.recv(1024)
    
    
    if __name__ == '__main__':
        main()
    

###  官方的解法

先来看exp（稍微有改动，因为我觉得有一步貌似没必要= =）：

    
    
    msg = 'x02x02x051x35x02'+'x00'*10+'x40'
    

上个自己画的图：

![](https://p4.ssl.qhimg.com/t0192b3e89e9f4a5287.jpg)

可以看到流程就是利用跳转来实现循环语句，直到异或以后最后一位为1，然后删掉1，取倒数第二位10次，然后再删除这一位，继续异或，重复操作。

通过异或使得最后一位为1只有两种可能10和01，且这两种情况等概率出现（均为16%），所以倒数第二位为0或者1的概率各为50%，也即算法等价于在每个周期等概率的取0或者1，这样的话成功的概率就很大了

## babyprng2

核心代码：

    
    
    def run(self, code):
            stack = []
            sequence = []
            out = []
            cnt = 0
            random.seed(os.urandom(8))
            self.TH = 0.7 + random.random()*0.25
            for _ in xrange(self.SIZE):
                stack.append(self.randbit())
            try:
                pos = 0
                for _ in xrange(self.SIZE*0x10):
                    c = code[pos]
                    pos += 1
                    if c=='x00':
                        out.append(stack[-1])
                        del stack[-1]
                    elif c=='x01':
                        if stack[-1]==1:
                            pos += 1
                    elif c=='x02':
                        stack[-1] = stack[-1]&stack[-2]
                    elif c=='x03':
                        stack[-1] = stack[-1]|stack[-2]
                    elif c=='x04':
                        stack[-1] = stack[-1]^stack[-2]
                    elif c=='x05':
                        sequence.append(stack[-1])
                        del stack[-1]
                    elif c=='x06':
                        sequence.insert(0,stack[-1])
                        del stack[-1]
                    elif c=='x07':
                        if len(stack)>=2:
                            pos += 1
                    elif c=='x08':
                        stack+=sequence[::-1]
                        sequence=[]
                    elif ord(c)>=0x10 and ord(c)<=0x1a:
                        pos += ord(c)-0x10
                    elif ord(c)>=0x30 and ord(c)<=0x3a:
                        pos -= ord(c)-0x30
    

这道题和上面题目的区别：

delta更小、out append的时候每次还会把栈删除、多了对seq的操作，循环的次数更多，而要求out的元素更少

###  自己的解法

由于可以做判断是否为一，那么我可以在一个周期里第一步取0，如果不是0就丢弃然后重复判断（送入seq），如果是0就判断下一个是否为1，如果是1就进入下一个周期，如果不是的话就丢弃然后再重复判断，这样相当于每个周期都在重复的取01

画成图就是这个样子：

![](https://p4.ssl.qhimg.com/t01b70ec868a200a3e9.jpg)

或者这个样子

![](https://p5.ssl.qhimg.com/t01a2c97f8e0e0f0372.jpg)

但是这样并不能实现，因为误删除元素（送入seq）的有很多，循环还没结束就会因为stack的元素全部没有了而报错，导致out的元素个数就不够了，本地测试最多也就在2万左右，达不到3万，但是我们有一个判断stack元素还剩多少的方法，当stack要空了的时候只要用第8个方法把seq的元素重新放回stack重复利用就行了，虽然构造有点麻烦，但总归是可以实现的：

![](https://p0.ssl.qhimg.com/t017b8205db22934279.jpg)

对应poc：01140708053607080001140708003a0708053a

## notcurves

题目有一个非常严重的Bug，导致了非常严重的非预期

    
    
    self.dosend("please give me a point(pi,qi): n")
    R = self.recvpoint(30)
    (u,v) = R
    print R
    if (u*v)%p == 0:
        self.dosend("%sn" % FLAG)
    else:
        self.dosend(">.<n")
    self.request.close()
    

没有检查参数R，所以R可以是(0, 0)，直接就能过，应该大部分人都是这样做出来的吧。。。

比赛结束以后我还是很兴奋的重新看了一下，毕竟ECC椭圆曲线的题目很少，但是由于这道题没有官方wp，所以我也只能猜测一下出题人的预期解

首先在循环里能做的操作其实只有3个，第一个是ADD方法，实现的功能是求椭圆曲线上两点相加的结果，第二个是MUL方法，实现的功能是在椭圆曲线上求一个点的倍数，而我觉得预期解法应该是最后一个DIV方法

    
    
    def DIV(self):
        self.dosend('input point A: n')
        A = self.recvpoint(30)
        self.dosend('input number t: n')
        t = self.recvnum(10)
        C = div(t,A)
        self.dosend("the result is :"+str(C)+'n')
    
    
    def div(t,A,B=0):
        (u,v) = A
        if (u*v) %p != 1:
            #print u*v*sub((p,t))%p
            return u*v*sub((p,t))%p
        else:
            return B
    
    
    def sub(A):
        (u,v) = A
        v = v%p
        if v > 2**11:
            print u//v
            return u//v
        else:
            return 0
    

仔细观察代码会发现这个方法并没有调用其他两个方法里的check_point方法，也就是不检查输入的点是否在椭圆曲线上，这就可以任意构造了，题目的要求是求出p的大小，而这个方法完全可以做到：

由于检查u、v不能直接为(1, 1)，所以可以令uv为(1, 2)最后返回的结果除以2就能得到sub(p,
t)的结果，而我们是大致知道p的范围的，因为p=getprime(15)*getprime(15)所以p的范围在pow(2, 29)到pow(2,
30)之间，如果令t也在pow(2, 29)到pow(2,
30)之间且p>=t的话，那么p//t结果一定是返回1，否则的话返回其他结果，那么我们就可以通过二分法查找来缩小范围，从而确定p的值（所以这道题和ecc有啥关系？。。。）

exp：

    
    
    from socket import *
    from libnum import *
    import string
    from re import *
    from hashlib import sha256
    
    
    
    def connect(host, port):
        s = socket()
        s.connect((host, port))
        return s
    
    def cal(proof, ans, set):
        for i in set:
            for j in set:
                for k in set:
                    for m in set:
                        if sha256(i+j+k+m+proof).hexdigest() == ans:
                            print i+j+k+m
                            return i+j+k+m
    
    def proof_of_work(s):
        msg = s.recv(1024)
        print msg
        set = string.ascii_letters+string.digits
    
        reg = 'sha256(XXXX+(.+)) == (.+)n'
        regexp = compile(reg)
        res = regexp.findall(msg)
    
        proof = res[0][0]
        ans = res[0][1]
    
        print s.recv(1024)
        s.send(cal(proof, ans, set))
        print s.recv(1024)
    
    def send4(s, msg):
    
        print '4'
        s.send('4n')
        print s.recv(1024)
        print '(1,2)'
        s.send('(1,2)n')
        print s.recv(1024)
        print str(msg)
        s.send(str(msg) + 'n')
        res = s.recv(1024)
        print res
        print s.recv(1024)
    
        reg = 'the result is :(.+)'
        regexp = compile(reg)
        r = regexp.findall(res)
        num = r[0]
        return int(num)
    
    
    
    def main():
        host ='127.0.0.1'
        port = 20005
        s = connect(host, port)
        proof_of_work(s)
    
    
        print s.recv(1024)
    
        low = 2**29
        high = 2**31
        mid = (low + high) / 2
        count = 0
        while high>low:
            if send4(s, mid)==2:
                low = mid
            else:
                high = mid
            tmp = mid
            mid = (low + high) / 2
            if mid == tmp:
                count += 1
            else:
                count = 0
            if count >5:
                break
    
        mid += 1
    
        print 5
        s.send('5n')
        print s.recv(1024)
        print (1, mid)
        s.send('(1,%d)n'%mid)
        print s.recv(1024)
        print s.recv(1024)
    
    
    if __name__ == '__main__':
        main()
    

## 总结

不管是出题人有心还是无意，这次题目都有很多非预期的解法，也给题目增加了许多乐趣

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **r1ngs** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/177582](/post/id/177582)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __2赞

 __收藏

![](https://p4.ssl.qhimg.com/t012bbf7d938a8def87.png) r1ngs

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

