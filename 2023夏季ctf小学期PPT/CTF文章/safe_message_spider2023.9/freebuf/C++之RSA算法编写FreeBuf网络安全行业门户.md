## 简介

### 密钥生成

选取两互异大素数：

p和q 计算 N=p×q 和&(N)=(p－1) ·(q－1)

选一整数e:1< e<&(N), gcd(&(N), e)=1 在模&(N)下，计算e的乘法逆元d: e · d = 1 mod (N) 公钥pk=(N,
e)，私钥sk=d。

### 加解密

公钥pk=(N, e)，私钥sk=d:

加密E(pk, M)：给定一个整数 M<N,计算

C = E(pk, M)= Me mod N

解密D(sk, C):

M = D(sk, C) = Cd mod N

### 实际举例

一：Bob计算(pkB, skB)

取 p=7, q=17, N=p×q=119

&(N)= (p-1) × (q-1) = 6 X 16= 96

取 e=5, 计算d=77

公钥：pkB = (e, N)=(5, 119)

私钥：skB= 77

Alice 知道 pkB = (e, N)=(5, 119)

Bob 知道 (pkB, skB)

二：Alice 使用 pkB = (e, N)=(5, 119) 加密

明文 m=19；

计算密文 c= me mod N

= 195 mod 119

= 66

三：Bob收到 密文66 后

利用自己的公私钥对pkB = (e, N)=(5, 119), skB= 77计算 明文m = 6677 mod 119 = 19

## 源码

> #include<iostream>
>
> using namespace std;
>
> int cgyjia(int a, int b,int c)
>
> {
>
> int r=1;
>
> while(b!=0){
>
> r=r*a;
>
> r=r%c;
>
> b--;}
>
> return r;
>
> }
>
> cgyjie(int a, int b,int c)
>
> {
>
> int r=1;
>
> while(b!=0){
>
> r=r*a;
>
> r=r%c;
>
> b--;}
>
> return r;
>
> }
>
> int main()
>
> {
>
> int p,q,n,n1,t,e;
>
> cout<<"请输入p和q:";
>
> cin>>p>>q;
>
> n=p*q;
>
> t=(p-1)*(q-1);
>
> cout<<"n的值为"<<n<<"，t的值为"<<t<<endl;
>
> cout<<"请输入e的值"<<endl;
>
> cin>>e;
>
> while(e<1||e>t||t%e!=1)
>
> {
>
> cout<<"e 的值不符合要求，请重新输入：";
>
> cin>>e;
>
> }
>
> int d=1;
>
> while(((e*d)%t)!=1) d++;
>
> cout<<"d的值为:"<<d<<endl;
>
> while(d<0)
>
> {
>
> cout<<"e 的值不符合要求，请重新输入：";
>
> cin>>e;
>
> d=1;
>
> while(((e*d)%t)!=1) d++;
>
> }
>
> cout<<"加密起码输1，解密请输入2"<<endl;
>
> cin>>n1;
>
> if(n1==1)
>
> {
>
> int m,ja;
>
> cout<<"请输入M"<<endl;
>
> cin>>m;
>
> ja=cgyjia(m,e,n);
>
> cout<<"加密后的密文为："<<ja<<endl;
>
> }
>
> else
>
> {
>
> int c,je;
>
> cout<<"请输入C"<<endl;
>
> cin>>c;
>
> je=cgyjie(c,d,n);
>
> cout<<"解密后的明文为："<<je<<endl;
>
> }
>
> return 0;
>
> }

## 运行截图

### 加密

###
![](https://image.3001.net/images/20210512/1620828704_609be220a52f49401e640.png!small)解密

![](https://image.3001.net/images/20210512/1620828741_609be2454093a57864c20.png!small)

