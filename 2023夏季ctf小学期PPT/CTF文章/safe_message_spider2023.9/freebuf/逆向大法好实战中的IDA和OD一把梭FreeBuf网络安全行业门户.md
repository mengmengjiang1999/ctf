0X01

一直对D盾检测账号克隆的功能感到好奇，终于跟着老师傅的教程手把手学会了怎么用IDA，OD配合去逆向分析。

D盾有一项功能是账号克隆：

![0XRhlYFgnxI](http://si1.go2yd.com/get-image/0XRhlYFgnxI)

​

通过StudyPe查看，使用了NetUserEnum相关的函数

![0XRhloqVFJY](http://si1.go2yd.com/get-image/0XRhloqVFJY)

​

通过查看msdn的例子：

https://docs.microsoft.com/zh-cn/windows/desktop/api/lmaccess/nf-lmaccess-netuserenum

大致可以知道这些函数是怎么使用。

0x02

OD调试

按ctrl+g输入NetUserEnum

![0XRhlnf6DBY](http://si1.go2yd.com/get-image/0XRhlnf6DBY)

​

按F2下断点

![0XRhloYDtWi](http://si1.go2yd.com/get-image/0XRhloYDtWi)

​

按F9运行,点击D盾克隆账号检测

![0XRhlmkqh7Y](http://si1.go2yd.com/get-image/0XRhlmkqh7Y)

​

Od命中断点，记录下返回地址

![0XRhll0P1F2](http://si1.go2yd.com/get-image/0XRhll0P1F2)

​

0x03

IDA配合

Ok，上ida,按g键，输入地址：0051158B

![0XRhll8CiVE](http://si1.go2yd.com/get-image/0XRhll8CiVE)

​

往上翻，查看函数头（地址为5114A4）：

![0XRhlkwXnE0](http://si1.go2yd.com/get-image/0XRhlkwXnE0)

​

分析sub_5114A4函数。

![0XRhli7njpA](http://si1.go2yd.com/get-image/0XRhli7njpA)

​

//32 此结构在系统有异常的情况下NetUserEnum 将失败返回2221状态值

typedefstruct _USER_INFO_3 {

LPWSTR usri3_name; 0

LPWSTR usri3_password; 4

DWORD usri3_password_age; 8

DWORD usri3_priv; C

LPWSTR usri3_home_dir; 10

LPWSTR usri3_comment; 14

DWORD usri3_flags; 18

LPWSTR usri3_script_path; 1C

DWORD usri3_auth_flags; 20

LPWSTR usri3_full_name; 24

LPWSTR usri3_usr_comment; 28

LPWSTR usri3_parms; 2C

LPWSTR usri3_workstations; 30

DWORD usri3_last_logon; 34

DWORD usri3_last_logoff; 38

DWORD usri3_acct_expires; 3C

DWORD usri3_max_storage; 40

DWORD usri3_units_per_week; 44

PBYTE usri3_logon_hours; 48

DWORD usri3_bad_pw_count; 4C

DWORD usri3_num_logons; 50

LPWSTR usri3_logon_server; 54

DWORD usri3_country_code; 58

DWORD usri3_code_page; 5C

DWORD usri3_user_id; 60

DWORD usri3_primary_group_id; 64

LPWSTR usri3_profile; 68

LPWSTR usri3_home_dir_drive; 6C

DWORD usri3_password_expired; 70

}USER_INFO_3, *PUSER_INFO_3, *LPUSER_INFO_3;

![0XRhlk3bz4C](http://si1.go2yd.com/get-image/0XRhlk3bz4C)

​

权限问题

![0XRhlhx6yLQ](http://si1.go2yd.com/get-image/0XRhlhx6yLQ)

​

![0XRhlhbSaem](http://si1.go2yd.com/get-image/0XRhlhbSaem)

​

![0XRhliUBZvU](http://si1.go2yd.com/get-image/0XRhliUBZvU)

​

读取F值。

![0XRhlesv7Mu](http://si1.go2yd.com/get-image/0XRhlesv7Mu)

​

![0XRhlekMcBE](http://si1.go2yd.com/get-image/0XRhlekMcBE)

​

F值二进制流30h偏移是 关联的 user_id

![0XRhlfKDryi](http://si1.go2yd.com/get-image/0XRhlfKDryi)

​

![0XRhlfH8voG](http://si1.go2yd.com/get-image/0XRhlfH8voG)

​

Bin搜索了一下 f值的含义：

http://www.beginningtoseethelight.org/ntsecurity/index.htm

![0XRhlawGHjs](http://si1.go2yd.com/get-image/0XRhlawGHjs)

​

关键字符串：

![0XRhlbNzCC0](http://si1.go2yd.com/get-image/0XRhlbNzCC0)

​

![0XRhlcY5CIy](http://si1.go2yd.com/get-image/0XRhlcY5CIy)

​

0x04

这样一来，检测逻辑就清楚了：

![0XRhlbva7aS](http://si1.go2yd.com/get-image/0XRhlbva7aS)

​

0x05

逆向大法好，通过OD和IDA的配合调试分析，学习了D盾判断账号克隆功能实现的逻辑，当然，最关键的是在掌握了逆向的思维和方法。

相关操作推荐

逆向破解—CrackMe系 ：在破解过程中学习逆向知识。点击

http://www.hetianlab.com/cour.do?w=1&c=C172.19.104.182016031814360300001

开始操作学习！

![0XRhlbNnRR2](http://si1.go2yd.com/get-image/0XRhlbNnRR2)

​

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关，本文为合天原创，如需转载，请注明出处！

  

