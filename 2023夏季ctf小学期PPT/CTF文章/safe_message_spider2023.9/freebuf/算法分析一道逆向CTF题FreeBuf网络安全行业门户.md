### 1.下载查壳，跑一遍

![](https://image.3001.net/images/20220421/1650533254_626123861e68da45827df.png!small)

![](https://image.3001.net/images/20220421/1650533254_626123867477102cd8824.png!small)

#### 提示输入，随便输入后结束程序

### 2.使用IDA静态分析，拖进去直接F5伪代码分析

![](https://image.3001.net/images/20220421/1650533254_62612386c63be71bdace2.png!small)

v7 = strcmp(byte_40336C, aXircjR2twsv3pt);

if ( v7 )

v7 = v7 < 0 ? -1 : 1;

if ( !v7 )

{

sub_401020("right\n", Arglist[0]);

system("pause");

}

####
从伪代码中可以看到关键字符"right\n"，那这里可以直接看出这个sub_401020指定就是输入正确后的提示函数，但是要执行sub_401020函数则需要v7是一个非零的数，那么我们就跟踪v7,可以从整个main函数中看到，对v7变量做出更改的只有一下两个地方

v7 = strcmp(byte_40336C, aXircjR2twsv3pt);

if ( v7 )

v7 = v7 < 0 ? -1 : 1;

####
第一个地方v7是byte_40336C变量与aXircjR2twsv3pt变量strcmp的返回值，第二个地方v7无论怎么样都是非零数，所以第二个地方的v7就不影响提示输入正确的函数sub_401020("right\n",
Arglist[0])，那只有第一个地方的了，化简后的对比代码如下

v7 = strcmp(byte_40336C, aXircjR2twsv3pt);

if ( !v7 )

{

sub_401020("right\n", Arglist[0]);

system("pause");

}

####
也就是说，只要byte_40336C与aXircjR2twsv3pt相等就行了，相等v7就等于0，!v7就为真，那就执行提示输入正确的函数，到这里根据以往的经验就可以有90%的信心确定这个byte_40336C就是最后一次flag的密文，我们只需推到出这个byte_40336C就应该可以解决题目了

#### 那好，接下来找出aXircjR2twsv3pt的具体值，双击aXircjR2twsv3pt进入查看具体值

![](https://image.3001.net/images/20220421/1650533255_626123873d0f8c8f1a786.png!small)

#### shift+e把aXircjR2twsv3pt提取出来先放好，继续查看aXircjR2twsv3pt与byte_40336C存在的逻辑

for ( i = 0; i < 0x18; ++i )

byte_40336C[i] = (byte_40336C[i] + 1) ^ 6;

####
我们刚才得到最后的byte_40336C正确的满足条件就是等于aXircjR2twsv3pt，那在上面的代码中就只存在一个未知数：每次循环前的byte_40336C，那我们先用刚才提取出的aXircjR2twsv3pt写脚本推导出每次循环前的byte_40336C，代码如下：

#include

#include

int main()

{

unsigned char aXircjR2twsv3pt[] =

{

0x78, 0x49, 0x72, 0x43, 0x6A, 0x7E, 0x3C, 0x72, 0x7C, 0x32,

0x74, 0x57, 0x73, 0x76, 0x33, 0x50, 0x74, 0x49, 0x7F, 0x7A,

0x6E, 0x64, 0x6B, 0x61, 0x00, 0x00, 0x00, 0x00

};

char get[24];

for (size_t i = 0; i < 0x18; i++)

{

get[i] = (aXircjR2twsv3pt[i] ^ 6) - 1;

}

for (size_t i =0; i < 0x17; i++)

{

printf("%c", get[i]);

}

system("pause");

}

![](https://image.3001.net/images/20220421/1650533255_626123879e2c2e505587d.png!small)

####
到这里以后，我们继续阅读main函数代码逻辑，发现在这个for循环之前只有一个地方操作了这个byte_40336C变量，但是即使再怎么操作byte_40336C变量的最后操作都是for循环结构内，所以再for以前的代码毫无意义了，那此时我们得到最后的条件就是上面输出的“}NsDkw9sy3qPto4UqNx{galf”字符了，所以只能通过这个字符串来查找关键信息最快，咱们不如把“}NsDkw9sy3qPto4UqNx{galf”倒序看一下，是不是有flag{...}这味？那我们把for循环输出从最后一位开始倒序

![](https://image.3001.net/images/20220421/1650533255_62612387efa7c06901250.png!small)

#### 脚本如下：

#include

#include

int main()

{

char aXircjR2twsv3pt[] =

{

0x78, 0x49, 0x72, 0x43, 0x6A, 0x7E, 0x3C, 0x72, 0x7C, 0x32,

0x74, 0x57, 0x73, 0x76, 0x33, 0x50, 0x74, 0x49, 0x7F, 0x7A,

0x6E, 0x64, 0x6B, 0x61, 0x00, 0x00, 0x00, 0x00

};

char get[24];

for (size_t i = 0; i < 0x18; i++)

{

get[i] = (aXircjR2twsv3pt[i] ^ 6) - 1;

}

for (size_t i = 0x17; i >=0; i--)

{

printf("%c", get[i]);

}

system("pause");

}

![](https://image.3001.net/images/20220421/1650533256_626123884bd1bf6ae3134.png!small)

  

