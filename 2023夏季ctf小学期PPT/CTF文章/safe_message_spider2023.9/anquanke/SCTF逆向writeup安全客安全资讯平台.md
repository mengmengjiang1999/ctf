# SCTF逆向writeup

阅读量 **182080**

|评论 **4**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2020-07-09 15:30:18

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

上周末做了一下SCTF的逆向题，整体质量还不错，这里简单分析一下我的做题思路，有问题欢迎交流

## signin

一个GUI程序，使用pyinstaller打包，需要输入正确的用户名的密码。  
使用pyinstxtractor解包，发现是py3.8，于是用相应版本的uncompyle反编译main.pyc：

    
    
    import sys
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
    from signin import *
    from mydata import strBase64
    from ctypes import *
    import _ctypes
    from base64 import b64decode
    import os
    
    class AccountChecker:
    
        def __init__(self):
            self.dllname = './tmp.dll'
            self.dll = self._AccountChecker__release_dll()
            self.enc = self.dll.enc
            self.enc.argtypes = (c_char_p, c_char_p, c_char_p, c_int)
            self.enc.restype = c_int
            self.accounts = {'SCTFer': b64decode('PLHCu+fujfZmMOMLGHCyWWOq5H5HDN2R5nHnlV30Q0EA')}
            self.try_times = 0
    
        def __release_dll(self):
            with open(self.dllname, 'wb') as (f):
                f.write(b64decode(strBase64.encode('ascii')))
            return WinDLL(self.dllname)
    
        def clean(self):
            _ctypes.FreeLibrary(self.dll._handle)
            if os.path.exists(self.dllname):
                os.remove(self.dllname)
    
        def _error(self, error_code):
            errormsg = {0:'Unknown Error', 
             1:'Memory Error'}
            QMessageBox.information(None, 'Error', errormsg[error_code], QMessageBox.Abort, QMessageBox.Abort)
            sys.exit(1)
    
        def __safe(self, username: bytes, password: bytes):
            pwd_safe = 'x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00x00'
            status = self.enc(username, password, pwd_safe, len(pwd_safe))
            return (pwd_safe, status)
    
        def check(self, username, password):
            self.try_times += 1
            if username not in self.accounts:
                return False
            encrypted_pwd, status = self._AccountChecker__safe(username, password)
            if status == 1:
                self._AccountChecker__error(1)
            if encrypted_pwd != self.accounts[username]:
                return False
            self.try_times -= 1
            return True
    
    
    class SignInWnd(QMainWindow, Ui_QWidget):
    
        def __init__(self, checker, parent=None):
            super().__init__(parent)
            self.checker = checker
            self.setupUi(self)
            self.PB_signin.clicked.connect(self.on_confirm_button_clicked)
    
        @pyqtSlot()
        def on_confirm_button_clicked(self):
            username = bytes((self.LE_usrname.text()), encoding='ascii')
            password = bytes((self.LE_pwd.text()), encoding='ascii')
            if username == '' or password == '':
                self.check_input_msgbox()
            else:
                self.msgbox(self.checker.check(username, password))
    
        def check_input_msgbox(self):
            QMessageBox.information(None, 'Error', 'Check Your Input!', QMessageBox.Ok, QMessageBox.Ok)
    
        def msgbox(self, status):
            msg_ex = {0:'', 
             1:'', 
             2:"It's no big deal, try again!", 
             3:'Useful information is in the binary, guess what?'}
            msg = 'Succeeded! Flag is your password' if status else 'Failed to sign inn' + msg_ex[(self.checker.try_times % 4)]
            QMessageBox.information(None, 'SCTF2020', msg, QMessageBox.Ok, QMessageBox.Ok)
    
    
    if __name__ == '__main__':
        app = QApplication(sys.argv)
        checker = AccountChecker()
        sign_in_wnd = SignInWnd(checker)
        sign_in_wnd.show()
        app.exec()
        checker.clean()
        sys.exit()
    

可以看到用户名为SCTF，对应的密码经过enc函数加密后，与那串base64解码后的值相同。  
因此接下来的重点在enc函数，虽然我们找不到其定义，但是可以看到从mydata中读取了一个base64并解码写入到tmp.dll，那enc函数基本就在tmp.dll中没跑了。  
我们可以直接运行程序，找到当前目录的tmp.dll，也可以从mydata中提取出来。  
然后整理enc函数的逻辑：首先输入在sub_180011311做了一个lfsr，然后再做一个异或加密，相应恢复即可：

    
    
    from libnum import *
    
    def enc(n):
        x = n
        for i in range(64):
            if x & 0x8000000000000000 != 0:
                x = (2*x) ^ 0xB0004B7679FA26B3
            else:
                x *= 2
            x &= 0xffffffffffffffff
        return x
    
    def dec(n):
        x = n
        for i in range(64):
            if x & 1 != 0:
                x = (x ^ 0x1B0004B7679FA26B3) >> 1
            else:
                x /= 2
        return x
    
    e='PLHCu+fujfZmMOMLGHCyWWOq5H5HDN2R5nHnlV30Q0EA'.decode('base64')
    key='SCTFer'
    dec0=''
    for i in range(len(e)):
        dec0+=chr( ord(e[i]) ^ ord(key[i%6]) )
    flag=''
    for i in range(0, len(dec0), 8):
        x = s2n(dec0[i:i+8][::-1])
        flag += n2s(dec(x))[::-1]
    print flag
    

## flag_detector

GO写的web server，首先用golang_loader_assist恢复符号。  
main_main里可以看到注册了几个API（都是GET）：

1./v1/login：接受一个name参数，会在当前目录写个json，不加name的话默认是guest，发现并没啥用  
2./v2/user：调用一些初始化函数，写一个asdf文件，里面一堆数字（应该是vm相关的东西）  
3./v2/flag：在当前目录写一个hjkl的文件，里面是假的flag  
4./v3/check：调用一个vm检查hjkl文件

因此重点是逆向check中的vm。  
逆向vm可以写反汇编器也可以动态调试，由于这个vm中有几个比较复杂的操作，因此可以尝试在关键位置下断点进行调试。  
断点下在cmp指令，可以看到对flag长度的判断，长度输入正确后会对flag进行加密，最后进行逐字节比较。  
由于是逐字节比较，就可以侧信道爆破了，我们patch一下程序让它直接运行vm，然后根据断点断在cmp的次数判断flag正确的位置，逐位爆破即可：

    
    
    # gdb -n -q -x
    import gdb
    import re
    import os 
    
    flag = "SCTF{"
    pool=''
    for i in range(32, 128):
        pool+=chr(i)
    gdb.execute("set pagination off")
    gdb.execute("break *0x96CAE5")
    while 1:
        for i in range(len(pool)):
            tmp = flag + pool[i]
            cur_len = len(tmp)
            tmp = tmp.ljust(22,'~')
            with open("hjkl", "w") as f:
                f.write(tmp)
    
            gdb.execute("run")
            for j in range(48):
                gdb.execute("c",to_string=True)
            for j in range(cur_len):
                gdb.execute("c",to_string=True)
            try: 
                gdb.execute("c",to_string=True)
                flag += pool[i]
                break
            except: 
                pass
            print flag
    
    print(flag)
    

## get_up

IDA中shift+f12跟踪字符串引用，从you should give me a word找到输入被读取的位置，即位于0x402700的函数。  
创建函数后，可以看到word长度在6以内，且sub_401DF0函数中检测了其md5值，这里cmd5可以查到是sycsyc  
另外通过right和wrong的引用可以定位到sub_401A70函数，里面有明显的RC4特征。  
根据最后的比较`if ( v5[k] != *(&v12 + k)
)`可知函数上面的一串数字为密文，密钥syclover可以通过动态调试看到，解RC4即可得到flag：

    
    
    dest = [0]*30
    dest[0] = 128;
    dest[1] = 85;
    dest[2] = 126;
    dest[3] = 45;
    dest[4] = 209;
    dest[5] = 9;
    dest[6] = 37;
    dest[7] = 171;
    dest[8] = 60;
    dest[9] = 86;
    dest[10] = 149;
    dest[11] = 196;
    dest[12] = 54;
    dest[13] = 19;
    dest[14] = 237;
    dest[15] = 114;
    dest[16] = 36;
    dest[17] = 147;
    dest[18] = 178;
    dest[19] = 200;
    dest[20] = 69;
    dest[21] = 236;
    dest[22] = 22;
    dest[23] = 107;
    dest[24] = 103;
    dest[25] = 29;
    dest[26] = 249;
    dest[27] = 163;
    dest[28] = 150;
    dest[29] = 217;
    
    enc=''.join(map(chr,dest))
    key='syclover'
    def rc4(data, key):
        x = 0
        box = range(256)
        for i in range(256):
            x = (x + box[i] + ord(key[i % len(key)])) % 256
            box[i], box[x] = box[x], box[i]
        x = y = 0
        out = []
        for char in data:
            x = (x + 1) % 256
            y = (y + box[x]) % 256
            box[x], box[y] = box[y], box[x]
            out.append(chr(ord(char) ^ box[(box[x] + box[y]) % 256]))
    
        return ''.join(out)
    
    print rc4(enc, key)
    

## secret

安卓逆向，从MainActivity入手，发现check用到的d.a.c类中的5个函数无法正常反编译，查看smali发现全是nop，猜测应该是运行时动态加载代码。  
由于SCTF类中调用了native函数，于是接下来逆向一下so文件。  
IDA打开后可以看到一些奇怪名字的函数，然后从JNIOnload入手，可以看到一些_Z12dexFindClassPK7DexFilePKc之类的字符串，和一些诸如relocateInstruction、dexReadClassData之类的函数名，基本上可以猜出是对dex动了手脚。  
另外data段有几个可以的base64字符串，通过引用可以发现他们在init_proc函数被解密，可以通过动态调试或者逆向算法（即base64+RC4）得到解密后的值：

    
    
    Ld/a/c;
    syclover
    UYc0pLw6EdGoEIH3mCpj/kkzRMR5+nl+9VGFICIIL6w=
    sctf/secret/SCTF
    

其中Ld/a/c;就是那个无法反编译的类，而sctf/secret/SCTF是调用native函数的类，另外两个字符串暂时用途未知。

另外initproc中还解密了5个不可打印字符串，看起来与正常dex文件中的Dalvik字节码很像，直觉猜测与那5个被nop的函数有关系。

这里我们使用010editor的dex模板打开apk中的dex文件，定位到这5个函数的位置，发现其中代码的长度刚好与这5个字符串刚好一一对应。

于是我们根据长度，将解密后的字节码恢复回去，就可以正常反编译了。  
可以看到加密过程就是xxtea+base64，但是我们用SCTF中的密钥和密文解出来是fake
flag，在联想到之前那两个用途未知的字符串，猜测是替换了密文和密钥，尝试一下果然解出正确的flag：

    
    
    import xxtea
    from Crypto.Cipher import AES
    
    key = 'syclover'+'x00'*8
    s = 'UYc0pLw6EdGoEIH3mCpj/kkzRMR5+nl+9VGFICIIL6w='.decode('base64')
    
    dec = xxtea.decrypt(s, key,padding=False)
    print repr(dec)
    

## Orz

程序的主要逻辑是做了两段加密。  
第一段加密，首先根据flag中三个byte的和做种子，来生成一些随机数。之后，这些随机数与输入一起做一些数字运算：  
sum0 = flag[0] ^ rand[0]  
sum1 = flag[0] ^ rand[1] + flag[1] ^ rand[0]  
sum2 = flag[0] ^ rand[2] + flag[1] ^ rand[1] + flag[2] ^ rand[0]  
…  
这个过程在随机数固定的前提下是可以逐位推回去的，由于三个可打印字符的和只有几百种可能性，因此可以直接爆破。  
第二段是lfsr+des，其中des可以根据常量表识别，调试可以发现是标准des，lfsr跟signin类似，也很好逆回去。加密过程中有许多细节还是需要通过动态调试确认。  
最后两段逻辑连起来，爆破出一个可打印字符串即为flag：

    
    
    from libnum import *
    dest = [0]*64
    dest[0] = 0x4ECECA3B;
    dest[1] = 0x1DE25ED2;
    dest[2] = 0xDA7EBA7A;
    dest[3] = 0x44F2041D;
    dest[4] = 0x71270A83;
    dest[5] = 0x715B81E2;
    dest[6] = 0xCC2D1A85;
    dest[7] = 0x6B97F8E2;
    dest[8] = 0x4596FD5E;
    dest[9] = 0xC9405183;
    dest[10] = 0x67849B79;
    dest[11] = 0xEF406872;
    dest[12] = 0xDB7BE64E;
    dest[13] = 0x77CA5D7F;
    dest[14] = 0x6070B274;
    dest[15] = 0xC2D41ACA;
    dest[16] = 0x29662171;
    dest[17] = 0x3A3AA2EB;
    dest[18] = 0x54295545;
    dest[19] = 0x51A2A886;
    dest[20] = 0xB8591BC3;
    dest[21] = 0xE6483C3B;
    dest[22] = 0x8CFFBA61;
    dest[23] = 0x53D9BFBD;
    dest[24] = 0x5DACAA24;
    dest[25] = 0x44052042;
    dest[26] = 0x6F8736A6;
    dest[27] = 0x4AD433FC;
    dest[28] = 0x4DA7890F;
    dest[29] = 0x1186C3C6;
    dest[30] = 0x6BDC52CA;
    dest[31] = 0x92FE845E;
    dest[32] = 0xC7BBCDC0;
    dest[33] = 0xDE6CAAF1;
    dest[34] = 0x53A24F48;
    dest[35] = 0x78834993;
    dest[36] = 0x488B8BDA;
    dest[37] = 0xEEA0C8A;
    dest[38] = 0x1CC9883A;
    dest[39] = 0xCDD1C18E;
    dest[40] = 0xEE39C8CC;
    dest[41] = 0xBA7C009;
    dest[42] = 0x226A5717;
    dest[43] = 0x5DC4DC65;
    dest[44] = 0xEDE6EE3E;
    dest[45] = 0x98620CDC;
    dest[46] = 0xEDE770F4;
    dest[47] = 0xD228163E;
    dest[48] = 0x354BE5A8;
    dest[49] = 0x7ECFB5E9;
    dest[50] = 0x4D0D6FEA;
    dest[51] = 0xE4C117B9;
    dest[52] = 0x414C97B1;
    dest[53] = 0x2F630D6;
    dest[54] = 0xA9AB28BC;
    dest[55] = 0x7A42D719;
    dest[56] = 0x5436A531;
    dest[57] = 0x5AFEBE42;
    dest[58] = 0xB0E3691A;
    dest[59] = 0x3E1B42F0;
    dest[60] = 0xCA9380FC;
    dest[61] = 0x44BEA9CC;
    dest[62] = 0xF32B3091;
    dest[63] = 0x57A91678;
    
    def delfsr(n):
        ret = []
        odds = []
        x = n
        for i in range(64):
            x &= 0xffffffffffffffff
            ret.append(x)
    
            if x & 1 != 0:
                x ^= 0x3FD99AEBAD576BA5
                x = x/2 | 0x8000000000000000
                odds.append(1)
            else:
                x = x/2
                odds.append(0)
        ret.append(x & 0xffffffffffffffff)
        return ret, odds
    
    from pyDes import des
    xor_buf = [0x73,0x79,0x63,0x6c,0x6f,0x76,0x65,0x72]
    dest_enc = []
    for i in range(0, 64, 4):
        x = (dest[i+1] << 32) | dest[i] 
        keys, odds = delfsr(x)
        text = n2s((dest[i+3] << 32) | dest[i+2])[::-1]
        for j in range(64):
            kk = n2s(keys[j]).rjust(8, 'x00')
            kk=kk[::-1]
            text = des(kk).decrypt(text)
            if odds[j] == 1:
                text2 = ''
                for i in range(8):
                    text2 += chr(ord(text[i]) ^ xor_buf[i])
                text = text2
            else:
                pass
        r2 = s2n(text[::-1])
    
        dest_enc.append(keys[64]&0xffffffff)
        dest_enc.append(keys[64]>>32)
        dest_enc.append(r2&0xffffffff)
        dest_enc.append(r2>>32)
    
    for aa in range(95, 350):
        enc_lst = []
        seed = ((53*(aa))^0xffffffff)&0xfff
        for _ in range(32):
            seed = (0x1ED0675 * seed + 0x6C1)%254
            enc_lst.append(seed)
    
        flag=[]
        for i in range(32):
            tot = dest_enc[i]
            for j in range(i):
                tot -= flag[j]^enc_lst[i-j]
            flag.append(tot^enc_lst[0])
    
        if all (x in range(32,128) for x in flag):
            flag = ''.join(map(chr, flag))
            print flag
    

## easyre

通过查找字符串引用可以找到check函数sub_40B600，里面逻辑比较复杂，但是通过对输入下硬件断点，可以跟到几处对flag的加密，有aes加密和一些位运算操作，然后最后与一串常量作比较。  
如果跟着这段逻辑解完，最后会拿到一个fake flag。  
假如我们逆向比较仔细，应该能够发现一个很长很可疑的字符串。在运行时，程序会通过自校验crc值对其进行异或解密。尝试解密，可以发现是一个dll，而且其中有一个enc函数跟check函数长得非常像。  
通过查找引用还能找到一个函数sub_409FF0，里面跟check函数打印出了一样的字符串，但是这些字符串也同样被异或加密了，非常可疑。  
于是我们解出dll，发现enc函数的逻辑与check函数非常像，但运算顺序和加密方式都有不同，比如aes
key假逻辑是做了padding，而真逻辑是做了hex编码、异或密钥不同、和颠倒了三段位运算的顺序。  
于是对应修改一下脚本，即可得到真正的flag：

    
    
    from Crypto.Cipher import AES
    dest = [0]*32
    dest[0] = 0x8E
    dest[1] = 0x38;
    dest[2] = 0x51;
    dest[3] = 0x73;
    dest[4] = 0xA6
    dest[5] = 0x99
    dest[6] = 0x2A;
    dest[7] = 0xF0
    dest[8] = 0xDA
    dest[9] = 0xD5
    dest[10] = 0x6A;
    dest[11] = 0x91
    dest[12] = 0xE9
    dest[13] = 0x4E;
    dest[14] = 0x98
    dest[15] = 0xCE
    dest[16] = 0x2A;
    dest[17] = 0xB7
    dest[18] = 0x3D;
    dest[19] = 0x40;
    dest[20] = 0xF1
    dest[21] = 0xE5
    dest[22] = 0x1D;
    dest[23] = 0xAB
    dest[24] = 0xEF
    dest[25] = 0xEE
    dest[26] = 0xB0
    dest[27] = 0xD6
    dest[28] = 0x14;
    dest[29] = 0xB;
    dest[30] = 0x2A;
    dest[31] = 0x95
    
    aa3=[]
    
    def ror(x, n):
        return ((x>>n)|(x<<(8-n)))&0xff
    
    def enc_ef(x):
        return ror(x^0xef, 4)
    def enc_ad(n):
        x=n^0xad
        return (((x&0xaa)>>1) | ((x<<1)&0xaa))&0xff
    def enc_be(n):
        x=n^0xbe
        return (((x&0xcc)>>2) | ((x<<2)&0xcc))&0xff
    
    def dec_ef(x):
        return ror(x, 4)^0xef
    def dec_ad(x):
        n= (((x&0xaa)>>1) | ((x<<1)&0xaa))&0xff
        return n^0xad
    def dec_be(x):
        n= (((x&0xcc)>>2) | ((x<<2)&0xcc))&0xff
        return n^0xbe
    
    j = 0x55
    
    aa3 = [0] * 32
    for i in range(32):
        aa3[i] = dest[i]
    for i in range(32):
        aa3[i] = aa3[i] ^ j
    for i in range(7,14):
        aa3[i] = dec_ef(aa3[i])
    for i in range(14,21):
        aa3[i] = dec_be(aa3[i])
    for i in range(21,28):
        aa3[i] = dec_ad(aa3[i])
    
    enc = ''.join(map(chr,aa3))
    c = AES.new('SCTF2020'.encode('hex'))
    ss = c.decrypt(enc)
    print ss
    

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **dotsu** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/210037](/post/id/210037)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)

 **+1** __5赞

 __收藏

![](https://p0.ssl.qhimg.com/t010857340ce46bb672.jpg) dotsu

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

