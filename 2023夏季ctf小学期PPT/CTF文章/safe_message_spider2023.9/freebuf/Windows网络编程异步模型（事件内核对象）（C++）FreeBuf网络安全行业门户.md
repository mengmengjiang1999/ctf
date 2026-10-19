## 一、 **概述**

异步模型（事件内核对象）：

第一个参数：socket对象

第二个参数：WSABUF结构体数组

typedef struct __WSABUF {

u_long len;

char FAR *buf;

} WSABUF, FAR * LPWSABUF;

buf指向一个缓冲区的位置，len是缓冲区的大小

第三个参数：WSABUF结构体数量

第四个参数：接收到多少byte就返回，选择null就是非阻塞模式

第五个参数：指向flag的指针

第六个参数： WSAOVERLAPPED 结构体指针

typedef struct _WSAOVERLAPPED {

DWORD Internal;

DWORD InternalHigh;

DWORD Offset;

DWORD OffsetHigh;

WSAEVENT hEvent;

} WSAOVERLAPPED, *LPWSAOVERLAPPED;

第七个参数：完成例程指针

当I/O操作完成后WSAOVERLAPPED中的结构体保存的事件内核对象处于有信号状态，等待的线程将会只有一个线程，拿到进一步处理接收到缓冲区的I/O的权力。

![1684918718_646dd1be667883da0b551.png!small?1684918719891](https://image.3001.net/images/20230524/1684918718_646dd1be667883da0b551.png!small?1684918719891)

第一个参数：socket对象

第二个参数：WSAOVERLAPPED 结构体指针

第三个参数：实际发出或者收到的byte

第四个参数：

第五个参数：flags指针

![1684918736_646dd1d0e5dbda7dabba7.png!small?1684918738348](https://image.3001.net/images/20230524/1684918736_646dd1d0e5dbda7dabba7.png!small?1684918738348)

## 二、 **服务器代码**

#include<winsock2.h>

#include<Windows.h>

#include<stdio.h>

#pragma comment(lib,"ws2_32.lib")

#define READ 0x1

#define WRITE 0x2

#define ACCEPT 0x3

#define MAXBUFFER 0x1000

typedef struct MYSOCKET

{

SOCKET m_C;

SOCKADDR m_CC;

UINT state;//SOCKET状态

WSAOVERLAPPED S_OV;//异步IO结构体

WSABUF Rece_Buff;

char Buffer1[MAXBUFFER];

WSABUF Send_Buff;

char Buffer2[MAXBUFFER];

DWORD Flags;

}MYSOCKET, * PMySOCKET;

MYSOCKET MySocket[6] = { 0 };//创建全局结构体数组

WSAEVENT pEvent[6] = { 0 };//创建事件内核对象数组

CRITICAL_SECTION MySection;//声明关键区-操作全局变量MySocket[5]

VOID CreateE() {

for (size_t i = 0; i < 6; i++)

{

pEvent[i] = CreateEvent(NULL,FALSE,0,NULL);

MySocket[i].Rece_Buff.buf = MySocket[i].Buffer1;

MySocket[i].Send_Buff.buf = MySocket[i].Buffer2;

MySocket[i].Flags = 0;

}

}

DWORD GetSocket()//用于获取结构体数组中空闲的socket，按照顺序遍历

{

EnterCriticalSection(&MySection);

for (size_t i = 0; i < 5; i++)

{

if (MySocket[i].m_C == 0)

{

MySocket[i].m_C == 1;//main函数中MySocket[index].m_C =
m_S1;给Socket赋值。防止此线程调用完此函数返回后下一个线程进入关键区后还没执行MySocket[index].m_C = m_S1；

LeaveCriticalSection(&MySection);

return i;

}

}

LeaveCriticalSection(&MySection);

return -1;

}

VOID FreeSocket(int index)

{

EnterCriticalSection(&MySection);

closesocket(MySocket[index].m_C);

ZeroMemory(&MySocket[index], sizeof(MYSOCKET));

MySocket[index].Rece_Buff.buf = MySocket[index].Buffer1;

MySocket[index].Send_Buff.buf = MySocket[index].Buffer2;

LeaveCriticalSection(&MySection);

printf("Sock%d closed ", index);

}

DWORD Is_Over(WSABUF mybuf)

{

for (size_t i = 0; i < mybuf.len; i++)

{

if (mybuf.buf[i] == 'e')

{

return TRUE;

}

else if (mybuf.buf[i] == 0)

return FALSE;

}

return FALSE;

}

VOID ProcessData(WSABUF* pRecv_Buf,WSABUF* pSend_Buf) {

printf("Start process data...\n");

ZeroMemory(pSend_Buf->buf, MAXBUFFER);

CopyMemory(pSend_Buf->buf, pRecv_Buf->buf, pRecv_Buf->len -2);//减去命令结束符和字符串结束符

printf("Finish process data...\n");

}

DWORD WINAPI Rec_SOCKET(LPVOID lpParameter) {

int index = 0;

DWORD re = 0;

DWORD Flag;

while (1)

{

index = WSAWaitForMultipleEvents(6, pEvent, FALSE, WSA_INFINITE, FALSE);

//WSAResetEvent(pEvent[index]); 不需要手动设置Event状态。

if ((index == WSA_WAIT_FAILED) || (index == WSA_WAIT_TIMEOUT))

{

continue;

}

if (MySocket[index].state & READ)

{

WSAGetOverlappedResult(MySocket[index].m_C,&MySocket[index].S_OV, &re, FALSE,
&Flag);

if (re == 0)

{

FreeSocket(index);

continue;

}

if (Is_Over(MySocket[index].Rece_Buff))

{

//合并数据

//（1）MySocket[index].Rece_Buff.buf是每次接收数据的起始位置；

//（2）MySocket[index].Buffer1是最初接收数据的起始位置

MySocket[index].Rece_Buff.len = (MySocket[index].Rece_Buff.buf -MySocket[index].Buffer1) + re;//得到总数居长度

MySocket[index].Rece_Buff.buf = MySocket[index].Buffer1;//所有数据接受完成吧指针的起始位置复位；

//处理数据

ProcessData(&MySocket[index].Rece_Buff, &MySocket[index].Send_Buff);

MySocket[index].state = WRITE;

ZeroMemory(&MySocket[index].S_OV, sizeof(WSAOVERLAPPED));

MySocket[index].S_OV.hEvent = pEvent[index];

int re1 = WSASend(MySocket[index].m_C, &MySocket[index].Send_Buff, 1, NULL,
MySocket[index].Flags, &MySocket[index].S_OV, NULL);

if (re1 ==SOCKET_ERROR)

{

if (re1 != WSA_IO_PENDING) {

FreeSocket(index);

}

}

else if (re1 == 0)

{

printf("Send OK\n");

}

else//没有接收到完整的命令，继续接受

{

MySocket[index].Rece_Buff.buf = MySocket[index].Rece_Buff.buf +
re;//更新接收数据指针位置

MySocket[index].Rece_Buff.len = MAXBUFFER - (MySocket[index].Rece_Buff.buf -MySocket[index].Buffer1);//计算剩余大小

ZeroMemory(&MySocket[index].S_OV, sizeof(WSAOVERLAPPED));

MySocket[index].S_OV.hEvent = pEvent[index];

int re1 = WSASend(MySocket[index].m_C, &MySocket[index].Send_Buff, 1, NULL,
MySocket[index].Flags, &MySocket[index].S_OV, NULL);

if (re1 ==SOCKET_ERROR)

{

if (re1 != WSA_IO_PENDING) {

FreeSocket(index);

}

}

else if (re1 == 0)

{

printf("This Send OK\n");

}

}

}

else if (MySocket[index].state & WRITE)//接受完一次完整指令后，重新进行接收操作

{

ZeroMemory(MySocket[index].Buffer1, MAXBUFFER);

MySocket[index].state = READ;

MySocket[index].Rece_Buff.len = MAXBUFFER;

ZeroMemory(&MySocket[index].S_OV, sizeof(WSAOVERLAPPED));

MySocket[index].S_OV.hEvent = pEvent[index];

int re = WSARecv(MySocket[index].m_C, &MySocket[index].Rece_Buff, 1, NULL,
&MySocket[index].Flags, &MySocket[index].S_OV, NULL);

if (re != WSA_IO_PENDING)

{

FreeSocket(index);

}

else if (re ==0)

{

printf("Recv OK\n");

}

}

}

return 0;

}

}

int main()

{

WSADATA wsdata;

int wsa = WSAStartup(MAKEWORD(2, 2), &wsdata);

InitializeCriticalSection(&MySection);

CreateE();//线程开始前先创建对应Socket的事件内核对象

CreateThread(NULL, 0, Rec_SOCKET, NULL, 0, NULL);

SOCKET m_S = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);

sockaddr_in Sock_in = {0};

Sock_in.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");

Sock_in.sin_family = AF_INET;

Sock_in.sin_port = htons(0x1234);

int s=sizeof(Sock_in);

int re=bind(m_S, (sockaddr*)&Sock_in, s);

listen(m_S,10);

MySocket[5].m_C = m_S;

while (1)

{

int m_len = sizeof(SOCKADDR_IN);

SOCKET m_S1=accept(m_S, (SOCKADDR*)&Sock_in, &m_len);

int index = GetSocket();

  

if (index!=-1)

{

if (m_S1 ==INVALID_SOCKET)

{

FreeSocket(index);

}

else

{

MySocket[index].m_C = m_S1;

ZeroMemory(MySocket[index].Buffer1, MAXBUFFER);

MySocket[index].state = READ;

MySocket[index].Rece_Buff.len = MAXBUFFER;

ZeroMemory(&MySocket[index].S_OV, sizeof(WSAOVERLAPPED));

MySocket[index].S_OV.hEvent = pEvent[index];

int re = WSARecv(MySocket[index].m_C, &MySocket[index].Rece_Buff, 1, NULL,
&MySocket[index].Flags, &MySocket[index].S_OV, NULL);

re = WSAGetLastError();

if (re == 0)

{

printf("Recv OK\n");

}

else if (re != WSA_IO_PENDING)

{

FreeSocket(index);

}

}

}

else

{

closesocket(m_S1);//没有空闲的Socket

}

}

DeleteCriticalSection(&MySection);

WSACleanup();

return 0;

}

