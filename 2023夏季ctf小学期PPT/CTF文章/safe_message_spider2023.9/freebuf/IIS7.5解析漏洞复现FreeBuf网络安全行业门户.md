IIS7.5 cgi解析漏洞复现

## 实验环境

Windows Server 2008 R2

我们先搭建IIS，在安装的时候，勾选上CGI，我这里安装过了

![1612081695_60166a1f13cddd6610cb6.png!small](https://image.3001.net/images/20210131/1612081695_60166a1f13cddd6610cb6.png!small)

需要下载phpstudy for IIS

下载地址：<https://www.xp.cn/phpstudy/phpStudy4iis.zip>

![1612081715_60166a335a1317e027525.png!small](https://image.3001.net/images/20210131/1612081715_60166a335a1317e027525.png!small)

我们新建一个test网站

![1612081743_60166a4f4c6acf1bb052a.png!small](https://image.3001.net/images/20210131/1612081743_60166a4f4c6acf1bb052a.png!small)

点击处理程序映射

![1612081749_60166a55c6e761ed388bf.png!small](https://image.3001.net/images/20210131/1612081749_60166a55c6e761ed388bf.png!small)

添加模块映射

![1612081763_60166a634ef3876996f8b.png!small](https://image.3001.net/images/20210131/1612081763_60166a634ef3876996f8b.png!small)

![1612081770_60166a6a2d2744d566d7f.png!small](https://image.3001.net/images/20210131/1612081770_60166a6a2d2744d566d7f.png!small)![1612081779_60166a73af77bac926fd1.png!small](https://image.3001.net/images/20210131/1612081779_60166a73af77bac926fd1.png!small)

把php的一句话放在网站根目录下，并以.jpg后缀结尾

![1612081819_60166a9b2aa5d00be13cf.png!small](https://image.3001.net/images/20210131/1612081819_60166a9b2aa5d00be13cf.png!small)

![1612081826_60166aa22822c5068f38c.png!small](https://image.3001.net/images/20210131/1612081826_60166aa22822c5068f38c.png!small)

访问这个11.jpg

![1612081832_60166aa8e2c573de0ac06.png!small](https://image.3001.net/images/20210131/1612081832_60166aa8e2c573de0ac06.png!small)

并不能被解析

在后面加上/.php,这次解析成功了

![1612081841_60166ab14caa3f99215f8.png!small](https://image.3001.net/images/20210131/1612081841_60166ab14caa3f99215f8.png!small)

用蚁剑连接

![1612081849_60166ab92682cf904e2ca.png!small](https://image.3001.net/images/20210131/1612081849_60166ab92682cf904e2ca.png!small)

