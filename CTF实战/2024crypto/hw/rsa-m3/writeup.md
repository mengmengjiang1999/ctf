# rsa-m3

$$
c1 = pow(m, e, n) \\
c2 = pow(m+1, e, n)

$$

又因为$e=3$

因此有

$$
c1=m^3\mod n\\
c2=(m^3+3m^2+3m+1)\mod n
$$

因此有

$$
c2-c1-1=(3m^2+3m)\mod n \\ =3(m^2+m)\mod n \\
c2+c1=(2m^3+3m^2+3m+1)\mod n \\ =(2m+1)(m^2+m+1)\mod n 
$$

因此可以得到$2m+1$的值，进而求出$m$


flag：
flag{rsa_spreads_encryption_magic}