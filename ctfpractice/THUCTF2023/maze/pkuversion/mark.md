1. ./main是二进制文件，由puzzle.cpp生成。这个文件里隐藏了flag1和flag2，flag1可以直接逆向得到。flag2需要逆向出输入才能得到。

g++ puzzle.cpp -o main

2. 二进制文件改成压缩包

zip attachment.zip ./main

3. 压缩包逆序一下，并将逆序之后的文件隐写进图片里面

python3 reversezip.py 

最终得到的是finalimage.png