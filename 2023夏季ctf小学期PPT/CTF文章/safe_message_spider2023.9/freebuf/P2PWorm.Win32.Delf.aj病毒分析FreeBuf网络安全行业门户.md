## 1.样本概况

### 1.1样本信息

病毒名称

|

P2P-Worm.Win32.Delf.aj  
  
---|---  
  
病毒类型

|

蠕虫病毒  
  
MD5

|

0c6b7ccfc0069bf2bae75eae4a006a73  
  
SHA-1

|

d72b4885ae3d8903e9aeafad9cdf23cd4fd2dd79  
  
SHA-256

|

95f5936234787ec09e3c89d237c438776588080e70d0679c89f8ebc19a5b58ce  
  
导入表MD5

|

ec76897ebac5cc7223f5be81d6f630e3  
  
BagarBubba

|

感染标识  
  
---|---  
  
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000042616761724275626261

|

特征码(尾部偏移-40h)  
  
  

### 1.2测试环境及工具

测试环境

|

虚拟机Windows 10 64位  
  
---|---  
  
测试工具

|

火绒剑、PEiD、xdbg、IDA、stud_PE  
  
  

### 1.3样本行为概述

这是个感染蠕虫病毒，样本运行后的行为:

遍历目录,寻找后缀为exe,scr,com,pif,cmd,bat的文件并进行感染操作。

![1687937062_649be02683d5d97bb83c8.png!small?1687937064164](https://image.3001.net/images/20230628/1687937062_649be02683d5d97bb83c8.png!small?1687937064164)

  

## 2 恶意代码分析

该函数位置为0x403174，主要功能为将宿主文件以及其大小保存在病毒文件后面，将宿主删除并将病毒重命名为宿主名称。

![1687937105_649be05145b4f0f7c7d0a.png!small?1687937107009](https://image.3001.net/images/20230628/1687937105_649be05145b4f0f7c7d0a.png!small?1687937107009)

![1687937119_649be05fc701cee99b5a0.png!small?1687937121227](https://image.3001.net/images/20230628/1687937119_649be05fc701cee99b5a0.png!small?1687937121227)

  

下图为被感染文件的尾部，排除感染标志以外的部分是一个大小为280个字节的结构体，0x00947C57为指向一个结构体的偏移，该结构体中保存着宿主文件的大小及其路径。BagarBubba为病毒的感染标识。

![1687937145_649be0794761c1ff81831.png!small?1687937146706](https://image.3001.net/images/20230628/1687937145_649be0794761c1ff81831.png!small?1687937146706)

  

  

该结构体大小为280个字节，其中保存着宿主的大小及其路径，其中0030C1F0为宿主文件的大小

##

![1687937234_649be0d2a715b5eae1d2b.png!small?1687937236117](https://image.3001.net/images/20230628/1687937234_649be0d2a715b5eae1d2b.png!small?1687937236117)

  

## 3文件恢复

### 3.1思路

  1. 判断文件尾部是否有BagarBubba感染标识以及固定位置的crc32是否相同
  2. 判断文件尾部宿主PE文件偏移所指的位置获取宿主文件大小以及计算出宿主所在位置。
  3. 从宿主偏移位置开始读取宿主PE文件内容并保存。

### 3.2参考代码

    
    
    long func_long_clear(unsigned char* puchar_src_buf, uint32_t u32_src_size, unsigned char* puchar_dst_buf, uint32_t* pu32_dst_size)
    {
    	long long_ret = 0, long_last_ret = 0;
    
    	if (puchar_src_buf == NULL || puchar_dst_buf == NULL || pu32_dst_size == NULL)
    	{
    		long_last_ret = -1;
    		long_ret = -1;			//	parameter error
    	}
    
    
    	int32_t i32_struct_size = 280;
    	int32_t	i32_infect_flag_off = -10;
    	int32_t i32_end_struct_off = (int32_t)(u32_src_size + i32_infect_flag_off - i32_struct_size);
    	int32_t i32_bge_struct_off = 0;
    	int32_t	i32_orig_file_size = -13;
    	int32_t i32_orig_file_off = 0;
    
    	uint32_t i32_struct_flag = *(uint32_t*)(puchar_src_buf + i32_end_struct_off);
    
    	unsigned char auchar_infect_flag[10] = { 0 };
    	uint32_t	u32_orig_file_off = 0;
    	uint32_t	u32_orig_file_size = 0;
    	if (i32_struct_flag != STRUCT_FLAG)
    	{
    		long_last_ret = -1;
    	}
    
    	if (long_last_ret == 0)
    	{
    		i32_bge_struct_off = *(int32_t*)(puchar_src_buf + i32_end_struct_off + 8);
    	}
    
    	if (i32_bge_struct_off == 0)
    	{
    		long_last_ret = -1;
    	}
    	i32_struct_flag = *(int32_t*)(puchar_src_buf + i32_bge_struct_off);
    
    	if (i32_struct_flag != STRUCT_FLAG)
    	{
    		long_last_ret = -1;
    	}
    
    	if (long_last_ret == 0)
    	{
    		u32_orig_file_size = *(uint32_t*)(puchar_src_buf + i32_bge_struct_off+8);
    	}
    	if (u32_orig_file_size == 0)
    	{
    		long_last_ret = -1;
    	}
    
    	if (long_last_ret == 0)
    	{
    		u32_orig_file_off = (uint32_t)( i32_bge_struct_off + i32_struct_size);
    	}
    	
    	if (long_last_ret == 0)
    	{
    		memcpy(auchar_infect_flag, puchar_src_buf + u32_src_size + i32_infect_flag_off, 10);
    		//u32_orig_file_off = *(uint32_t*)(puchar_src_buf + u32_src_size + i32_orig_file_off);
    		//u32_orig_file_size = *(uint32_t*)(puchar_src_buf + u32_src_size + i32_orig_file_size);
    
    		if (u32_orig_file_off > u32_src_size || u32_orig_file_size > u32_src_size || u32_orig_file_off + u32_orig_file_size > u32_src_size )
    		{
    			long_last_ret = -1;
    			long_ret = -5;
    		}
    	}
    
    	if (long_last_ret == 0)
    	{
    		memcpy(puchar_dst_buf, puchar_src_buf + u32_orig_file_off, u32_orig_file_size);
    		memcpy(puchar_dst_buf + u32_orig_file_size, auchar_infect_flag, 10);
    		*pu32_dst_size = u32_orig_file_size + 10;
    
    		long_ret = 1;
    	}
    
    
    	return long_ret;
    }

