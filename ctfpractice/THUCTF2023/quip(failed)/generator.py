
# origin='''
# At a certain season of our life we are accustomed to consider every spot as the possible site of a house.I have thus surveyed the country on every side within a dozen miles of where I live.In imagination I have bought all the farms in succession,for all were to be bought,and I knew their price.I walked over each farmer's premises,tasted his wild apples,discoursed on husbandry with him,took his farm at his price,at any price,mortgaging it to him in my mind;even put a higher price on it,—took everything but a deed of it,—took his word for his deed,for I dearly love to talk,—cultivated it,and him too to some extent,I trust,and withdrew when I had enjoyed it long enough,leaving him to carry it on.This experience entitled me to be regarded as a sort of real-estate broker by my friends.Wherever I sat,there I might live,and the landscape radiated from me accordingly.What is a house but a sedes,a seat?—better if a country seat.I discovered many a site for a house not likely to be soon improved,which some might have thought too far from the village,but to my eyes the village was too far from it.Well,there I might live,I said;and there I did live,for an hour,a summer and a winter life;saw how I could let the years run off,buffet the winter through,and see the spring come in.The future inhabitants of this region,wherever they may place their houses,may be sure that they have been anticipated.An afternoon sufficed to lay out the land into orchard,woodlot,and pasture,and to decide what fine oaks or pines  should be left to stand before the door,and whence each blasted tree could be seen to the best advantage;and then I let it lie,fallow perchance,for a man is rich in proportion to the number of things which he can afford to let alone. 
# '''

# origin='''
# Before the modern era, cryptography focused on message confidentiality (i.e., encryption)—conversion of messages from a comprehensible form into an incomprehensible one and back again at the other end, rendering it unreadable by interceptors or eavesdroppers without secret knowledge (namely the key needed for decryption of that message). Encryption attempted to ensure secrecy in communications, such as those of spies, military leaders, and diplomats. In recent decades, the field has expanded beyond confidentiality concerns to include techniques for message integrity checking, sender/receiver identity authentication, digital signatures, interactive proofs and secure computation, among others.
# '''

origin='''
The main classical cipher types are transposition ciphers, which rearrange the order of letters in a message, and substitution ciphers, which systematically replace letters or groups of letters with other letters or groups of letters. Simple versions of either have never offered much confidentiality from enterprising opponents. An early substitution cipher was the Caesar cipher, in which each letter in the plaintext was replaced by a letter some fixed number of positions further down the alphabet. Suetonius reports that Julius Caesar used it with a shift of three to communicate with his generals. Atbash is an example of an early Hebrew cipher. The earliest known use of cryptography is some carved ciphertext on stone in Egypt, but this may have been done for the amusement of literate observers rather than as a way of concealing information. flag{cryptography_is_interesting}.
'''

table=[chr(item) for item in range(ord("a"),ord("z")+1)]

from random import shuffle

shuffle(table)

print(table)

ans=""

for item in origin.lower():
    if ord(item)>=ord("a") and ord(item)<=ord("z"):
        ans+=table[ord(item)-ord("a")]
    else:
        ans+=item
        
print(ans)




