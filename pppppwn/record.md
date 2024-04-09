checksec --file=./warmup_csaw_2016
https://www.51cto.com/article/740130.html



file warmup_csaw_2016


使用sudo sh -c "echo 0 > /proc/sys/kernel/randomize_va_space"即可关闭ASLR
cat /proc/sys/kernel/randomize_va_space


systemctl start docker