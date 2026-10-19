![1619342597_6085350577e83c63ad5c8.png!small](https://image.3001.net/images/20210425/1619342597_6085350577e83c63ad5c8.png!small)

1.打开网址后，发现是一个上传页面

![1619342602_6085350abe56214024af6.png!small](https://image.3001.net/images/20210425/1619342602_6085350abe56214024af6.png!small)

2.直接上传后缀名为php的文件，发现无法上传

![1619342610_6085351207c6673556d32.png!small](https://image.3001.net/images/20210425/1619342610_6085351207c6673556d32.png!small)

![1619342615_60853517c8a8e66d6cb52.png!small](https://image.3001.net/images/20210425/1619342615_60853517c8a8e66d6cb52.png!small)

3.采用BurpSuite进行抓包，将上传的后缀为php的文件的后缀改为php5，即可绕过

![1619342625_60853521326c062711d8f.png!small](https://image.3001.net/images/20210425/1619342625_60853521326c062711d8f.png!small)

4.使用菜刀进行连接，在var/www/html的目录中，发现带有KEY的文件，打开即可看到key

![1619342643_6085353343e625610ee76.png!small](https://image.3001.net/images/20210425/1619342643_6085353343e625610ee76.png!small)![1619342648_608535387eb25ac96158c.png!small](https://image.3001.net/images/20210425/1619342648_608535387eb25ac96158c.png!small)![1619342653_6085353d94b2658191c88.png!small](https://image.3001.net/images/20210425/1619342653_6085353d94b2658191c88.png!small)

5.打开另一个网址，同时也是一个上传页面，但是设置了上传名单，仅允许以.gif .jpg .png为后缀文件通过上传

![1619342670_6085354e41d68018f41f4.png!small](https://image.3001.net/images/20210425/1619342670_6085354e41d68018f41f4.png!small)

6.我们写一个txt一句话木马，将其后缀改为jpg

![1619342675_6085355358d6ebe4ffeb1.png!small](https://image.3001.net/images/20210425/1619342675_6085355358d6ebe4ffeb1.png!small)

7.在上传的时候，采用BurpSiuit抓包，并对文件后缀进行修改，显示上传成功

![1619342680_60853558e6cd867386c20.png!small](https://image.3001.net/images/20210425/1619342680_60853558e6cd867386c20.png!small)

![1619342685_6085355d95537e45bd9e4.png!small](https://image.3001.net/images/20210425/1619342685_6085355d95537e45bd9e4.png!small)

![1619342696_60853568e6eeb9d2a27e1.png!small](https://image.3001.net/images/20210425/1619342696_60853568e6eeb9d2a27e1.png!small)

8.使用蚁剑进行连接 ，在var/www/html中发现key

![1619342710_60853576e01e7bc1aab45.png!small](https://image.3001.net/images/20210425/1619342710_60853576e01e7bc1aab45.png!small)

