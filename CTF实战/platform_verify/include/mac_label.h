#ifndef MAC_LABEL_H
#define MAC_LABEL_H

enum dtype_mac_label
{
	TYPE(MAC_LABEL)=0x1110,
};

enum subtype_mac_label
{
	SUBTYPE(MAC_LABEL,LABEL)=0x01,
	SUBTYPE(MAC_LABEL,SUBJECT),
	SUBTYPE(MAC_LABEL,OBJECT),
	SUBTYPE(MAC_LABEL,ADDR)
};
enum flag_sec_class
{
	RESEARCH=0x01,
	PRODUCE=0x02,
	TEST=0x04,	
	PUBLIC=0x10	
};

typedef struct mac_label_label
{
	unsigned short sec_class;
	unsigned char sec_label;
   	unsigned char inte_label;
}__attribute__((packed)) RECORD(MAC_LABEL,LABEL); 

typedef struct mac_label_subject
{
	char *user_name;
    	int user_id;
    	RECORD(MAC_LABEL,LABEL) label;  // score of the user label 
    	RECORD(MAC_LABEL,LABEL) exec_label; // user's real label(judge by platform verify result)
}__attribute__((packed)) RECORD(MAC_LABEL,SUBJECT);

typedef struct mac_label_object
{
	char *file_name;
	unsigned char object_uuid[32];
   	 RECORD(MAC_LABEL,LABEL) label;
}__attribute__((packed)) RECORD(MAC_LABEL,OBJECT);
typedef struct mac_label_addr{
	BYTE node_uuid[DIGEST_SIZE];
	char proc_name[DIGEST_SIZE];
	char * user_name;
}__attribute__((packed)) RECORD(MAC_LABEL,ADDR);

#endif
