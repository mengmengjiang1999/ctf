#ifndef KEY_MANAGE_HACK_H
#define KEY_MANAGE_HACK_H
 
 
int key_manage_hack_init (void * sub_proc, void * para);
int key_manage_hack_start (void * sub_proc, void * para);

struct init_para
{
	int first_cheat;  
	int next_cheat;	
}__attribute__((packed));
#endif
