今天玩一个找茬游戏。但是我们不是用眼睛找，我们用代码找。

最近做的题基本都是用工具做题，这次来尝试一下用代码解题。

来看题目解压附件cry200.zip，得到两张图片（附件在c盘根目录下的解密200文件夹中）

![headImg.action?news=6aa01de0-1b7d-42f8-8efa-f6fe4a5e6852.png](https://image.3001.net/images/20210420/1618910736_607e9e1013f0fb0f5ba16.png!small)

![headImg.action?news=f2eb5343-fa78-4dfe-b113-dad2292028c7.png](https://image.3001.net/images/20210420/1618910736_607e9e10bd16d3072eabb.png!small)

我们一般就是比较两张图片的像素，用程序进行对比（这段代码在c盘根目录下的解密200文件夹中有）

    
    
    import java.io.BufferedReader;
    
    import java.io.File;
    
    import java.io.FileInputStream;
    
    import java.io.FileNotFoundException;
    
    import java.io.IOException;
    
    import java.io.InputStreamReader;
    
    import javax.imageio.ImageIO;
    
    import java.awt.image.BufferedImage;
    
    public class PicTest2 {
    
    public static void main(String[] args) throws IOException {
    
    int i,j;
    
    int rgb1[] = new int[3];
    
    int rgb2[] = new int[3];
    
    File file1 = new File("C:\1.png");// 实例化file对象，并设置读取图片路径
    
    File file2 = new File("C:\2.png");
    
    File file3 = new File("C:\3.png");
    
    BufferedImage bi1 = null; // 像素缓冲区开始为空
    
    BufferedImage bi2 = null;
    
    BufferedImage bi3 = null;
    
    bi1 = ImageIO.read(file1);
    
    bi2 = ImageIO.read(file2);
    
    bi3 = ImageIO.read(file3);
    
    int width = bi1.getWidth();
    
    int height = bi1.getHeight();
    
    for (i = 0; i < width; i++) {
    
    for (j = 0; j < height; j++) {
    
    int pixel1 = bi1.getRGB(i, j);
    
    rgb1[0] = (pixel1 & 0xff0000) >> 16;
    
    rgb1[1] = (pixel1 & 0xff00) >> 8;
    
    rgb1[2] = (pixel1 & 0xff);
    
    int pixel2 = bi2.getRGB(i, j);
    
    rgb2[0] = (pixel2 & 0xff0000) >> 16;
    
    rgb2[1] = (pixel2 & 0xff00) >> 8;
    
    rgb2[2] = (pixel2 & 0xff);
    
    bi3.setRGB(i, j, Integer.parseInt(Integer.toHexString(rgb1[0]^rgb2[0])+Integer.toHexString(rgb1[1]^rgb2[1])+Integer.toHexString(rgb1[2]^rgb2[2]),16));
    
    }
    
    }
    
    ImageIO.write(bi3, "PNG", file3); //写入文件
    
    }
    
    }

这里运行没有成功，看一下代码里面的地址。需要把1.png和2.png放到c盘根目录下(程序中已经指定为c盘根目录)把1.png复制到c盘根目录下一份，重命名为3.png打开eclipse，新建一个工程，运行代码（自己安装eclipse，安装程序在c盘根目录下的解密200文件夹中有）

然后打开3.png，如下图

![headImg.action?news=83b8d685-647a-438f-89fd-ad2d3f1eeed4.png](https://image.3001.net/images/20210420/1618910737_607e9e117c014de5a5c91.png!small)

隐隐约约可以看到图中有个二维码（这是真的很隐约）

那我们再加点代码让他看得更清楚些在ImageIO.write(bi3, "PNG", file3);
上面加入下面的代码（需要添加的这段代码在c盘根目录下的解密200文件夹中有）

    
    
    for(i = 0; i < width; i++) {
    
    for(j = 0; j < height; j++) {
    
    //System.out.println(bi3.getRGB(i, j));
    
    if(bi3.getRGB(i, j)==-16777216) bi3.setRGB(i, j, -1);
    
    }
    
    }

添加了代码之后，再运行

再次打开3.png，如下图

![headImg.action?news=bc821acf-36f1-488e-9e5b-9bda38753801.png](https://image.3001.net/images/20210420/1618910738_607e9e12113a34ffc28ee.png!small)

扫码即可得到flag。

这道题是真题，当年难倒了一大片人。题目有迷惑性，要用程序对比像素。用代码解游戏题虽然是一种思路，但是速度应该会慢一些。

本文实验地址：https://www.hetianlab.com/expc.do?

    
    
    ec=ECID9d6c0ca797abec2016111111233100001&pk_campaign=freebuf-wemedia

