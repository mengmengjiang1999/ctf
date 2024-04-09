## 考点

* 考点 1 代换密码（quipquip的使用方式）
* 考点 2 base64换表解密

## 步骤

1. flag1：quipquip

打开attachment.zip之后看到4个文件：cipher.txt，encoded.txt，encryptMessage.py，main。

cipher.txt可以看出是代换密码，flag放在文末。放进quipquip里解密即可。

2. flag2：base64换表解密

main放进IDA里，看着感觉就像base64。不过仔细查看代码逻辑，发现base64的表是在运行的时候输入的。然后查看encryptMessage.py，可以看出这个表的字母部分和flag1的代换表是同一个代换方式。因此就可以得到新的base64表，然后再结合encoded.txt给出的编码后的结果，换表解码即可。

## 总结

好像没啥要总结的（逃