# 【木马分析】天眼实验室权威发布：XShell后门DNS Tunnel编码分析

阅读量 **197988**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2017-08-15 19:35:27

 **x**

##### 译文声明

本文是翻译文章，文章来源：安全客

译文仅供参考，具体内容表达以及含义原文为准。

XShellGhost通过DNS Tunnel把打点的数据传上去，分析了下编码算法，对数据进行了解密。

  

**编码分析**

****

DNS Tunnel的编码算法是先经过下图的算法1编码;如图：

待编码的数据单字节和一个每4次运算一次的DWORD常量的1,2,3,4字节进行单字节运算来编码，如下：

算法1编码后的数据如下：

然后把结果转换成可见的字符转换方法是通过每个字节的高位加‘j’低位加‘a’，把1个字节拆分成2个字节的可见字符，这样就浪费了一个字节：

解密算法是加密算法的逆运算，解密算法流程如下图：

解密的单条数据的HEX如下：

根据网上的一些公开的流量数据，

解密出的一些上传的数据：

解密代码如下：

    
    
    int DecodeSecond(int a1, unsigned char* a2, int a3, int a4, unsigned char* szOut)
    {
    	char v4; // cl@1
    	int v5; // esi@1
    	unsigned char* v6; // edi@2
    	byte v7[1024]= {0}; // eax@11
    	char v8; // dl@11
    	int v10; // [sp+4h] [bp-10h]@1
    	int v11; // [sp+8h] [bp-Ch]@1
    	int v12; // [sp+Ch] [bp-8h]@1
    	int v13; // [sp+10h] [bp-4h]@1
    	v4 = 0;
    	v5 = 0;
    	v10 = a1;
    	v11 = a1;
    	v12 = a1;
    	v13 = a1;
    	int i = 0;
    	if ( a3 > 0 )
    	{
    		v6 = a2 - a4;
    		do
    		{
    			if ( v5 & 3 )
    			{
    				switch ( v5 & 3 )
    				{
    				case 1:
    					v11 = 0xBFD7681A - 0x7DB1F70F * v11;
    					v4 = (*((byte *)&v11  + 2) ^ (*((byte *)&v11 + 1)
    						+ (*((byte *)&v11) ^ v4)))
    						- *((byte *)&v11 + 3);
    					v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
    					v7[i] = v8;
    					i++;
    					break;
    				case 2:
    					v12 = 0xE03A30FA - 0x3035D0D6 * v12;
    					v4 = (*((byte *)&v12  + 2) ^ (*((byte *)&v12 + 1)
    						+ (*((byte *)&v12) ^ v4)))
    						- *((byte *)&v12 + 3);
    					v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
    					v7[i] = v8;
    					i++;
    					break;
    				case 3:
    					v13 = 0xB1BF5581 - 0x11C208F * v13;
    					v4 = (*((byte *)&v13  + 2) ^ (*((byte *)&v13 + 1)
    						+ (*((byte *)&v13) ^ v4)))
    						- *((byte *)&v13 + 3);
    					v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
    					v7[i] = v8;
    					i++;
    					break;
    				}
    			}
    			else
    			{	
    			        v10 = 0x9F248E8A - 0x2F8FCE7E * v10;
    				v4 = (*((byte *)&v10 + 2) ^ (*((byte *)&v10 + 1)
    					+ (*((byte *)&v10 ) ^ v4)))
    					- *((byte *)&v10 + 3);
    				v8 = v4 ^ *(byte *)(v6 + v5++ + a4);
    				v7[i] = v8;
    				i++;
    			}
    		}
    		while ( v5 < a3 );
    		memcpy(szOut, v7, a3);
    	}
    	return 0;
    }		
    
    void DecodeFirst(unsigned char* szText)
    {
    	int iLength = strlen((char*)szText);
    	int iSubLength = iLength/2;
    	unsigned char* szXXX = new unsigned char[iSubLength+1];
    	memset(szXXX, 0, iSubLength+1);
    	for (int i=0; i<iSubLength; i++)
    	{
    		unsigned char One = szText[2*i] - 'a';
    		unsigned char Two = szText[2*i+1] -'j';
    		unsigned char Total = One+Two*16;
    		szXXX[i] = Total;
    	}
    	unsigned char* szOutData = new unsigned char[iSubLength+1];
    	memset(szOutData, 0, iSubLength+1);
    	DecodeSecond(0, szXXX, iSubLength, 0, szOutData);
    
    	printf(" --------------------Decode Data--------------------------------rn");
    	hexdump(szOutData, iSubLength); 
    	delete [] szOutData;
    	return;
    }
    
    void hexdump(void *pAddressIn, long  lSize)
    {
    	char szBuf[100];
    	long lIndent = 1;
    	long lOutLen, lIndex, lIndex2, lOutLen2;
    	long lRelPos;
    	struct { char *pData; unsigned long lSize; } buf;
    	unsigned char *pTmp,ucTmp;
    	unsigned char *pAddress = (unsigned char *)pAddressIn;
    	buf.pData   = (char *)pAddress;
    	buf.lSize   = lSize;
    	while (buf.lSize > 0)
    	{
    		pTmp     = (unsigned char *)buf.pData;
    		lOutLen  = (int)buf.lSize;
    		if (lOutLen > 16)
    			lOutLen = 16;
    		sprintf(szBuf, " |                            "
    			"                      "
    			"    %08lX", pTmp-pAddress);
    		lOutLen2 = lOutLen;
    		for(lIndex = 1+lIndent, lIndex2 = 53-15+lIndent, lRelPos = 0;
    			lOutLen2;
    			lOutLen2--, lIndex += 2, lIndex2++
    			)
    		{
    			ucTmp = *pTmp++;
    			sprintf(szBuf + lIndex, "%02X ", (unsigned short)ucTmp);
    			if(!isprint(ucTmp))  ucTmp = '.'; // nonprintable char
    			szBuf[lIndex2] = ucTmp;
    			if (!(++lRelPos & 3))     // extra blank after 4 bytes
    			{  lIndex++; szBuf[lIndex+2] = ' '; }
    		}
    		if (!(lRelPos & 3)) lIndex--;
    		szBuf[lIndex  ]   = '|';
    		szBuf[lIndex+1]   = ' ';
    		printf("%sn", szBuf);
    		buf.pData   += lOutLen;
    		buf.lSize   -= lOutLen;
    	}
    }

**  
**

**解密工具**

****

链接：<http://pan.baidu.com/s/1gfy4ImZ>

密码：vugv

  

**参考链接**

****

<http://bobao.360.cn/news/detail/4263.html>

本文翻译自安全客 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **奇安信威胁情报中心** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/86630](/post/id/86630)

安全客 - 有思想的安全新媒体

本文转载自: [安全客]()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [安全知识](/tag/安全知识)

 **+1** __0赞

 __收藏

![](https://p3.ssl.qhimg.com/t01dce0f9e833e11f13.png) 奇安信威胁情报中心

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

