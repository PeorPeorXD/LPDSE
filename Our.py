import hashlib
from charm.toolbox.pairinggroup import PairingGroup, G1, ZR
from charm.toolbox.bitstring import Bytes, getBytes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import time
import csv
import sys

import Extract_parameter as ep
from server import DatabaseServer

from concurrent.futures import ThreadPoolExecutor, as_completed

CS = DatabaseServer()
TABLE_NAME = 'Test'

lambda_val = 256
group = ep.group
G1 = G1
ZR = ZR
q = group.order()
P = ep.get_generator() #the generator of G1
U = ep.get_initial_state() #the initial state
nonce = b'\x82Ql3*%\xa7u\xa2x\xd0\x84\xa0xeE' #the sub secret encryption key


#G_1 -> {0,1}^(lambda)
def F_1( x) :
    hash_bytes = hashlib.sha256(x).digest()
    output_bytes = Bytes(hash_bytes)
    return output_bytes

#G_1 * {0,1}^(lambda) -> {0,1}^(lambda) , y is a keyword
def F_2( x, y:Bytes) :
    x_y = x.__add__(y)
    hash_bytes = hashlib.sha256(x_y).digest()
    output_bytes = Bytes(hash_bytes)
    return output_bytes

def F_3( st_key_bytes, key_bytes, w,) :
    x_y_z = (st_key_bytes.__add__(key_bytes)).__add__(w)
    hash_bytes = hashlib.sha256(x_y_z).digest()
    output_bytes = Bytes(hash_bytes)
    return output_bytes

#{0,1}^(lambda) * {0,1}^(lambda) -> {0,1}^(lambda)
def H_1(x:Bytes) :
    hash_bytes = hashlib.sha256(x).digest()
    output_bytes = Bytes(hash_bytes)
    return output_bytes

#{0,1}^(lambda) * {0,1}^(lambda) * {0,1}^(lambda) -> {0,1}^(lambda)
def H_2(x:Bytes, y:Bytes, z:Bytes) :
    x_y_z = (x.__add__(y)).__add__(z)
    hash_bytes = hashlib.sha256(x_y_z).digest()
    output_bytes = Bytes(hash_bytes)
    return output_bytes

#{0,1}^(lambda) * G1-> {0,1}^(lambda)
def H_3(x:Bytes) :
    hash_bytes = hashlib.sha256(x).digest()
    output_bytes = Bytes(hash_bytes)
    return output_bytes

#{0,1}^(lambda) * {0,1}^(lambda) * G1 -> {0,1}^(lambda)
def H_4(x:Bytes, y:Bytes) :
    x_y = x.__add__(y)
    hash_bytes = hashlib.sha256(x_y).digest()
    output_bytes = Bytes(hash_bytes)
    return output_bytes

#G1 * G1 -> {0,1}^(lambda)
def H_5(x:group, y:group) :
    x_bytes = group.serialize(x)
    y_bytes = group.serialize(y)
    x_y = x_bytes.__add__(y_bytes)
    hash_bytes = hashlib.sha256(x_y).digest()
    output_bytes = Bytes(hash_bytes)
    return output_bytes

def AES_encryption(key:Bytes,m:Bytes) :
    aes_key = hashlib.sha256(key).digest()
    cipher = Cipher(algorithms.AES(aes_key), modes.CTR(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(m) + encryptor.finalize()
    return ciphertext

def AES_decryption(key:Bytes,ciphertext:Bytes) :
    aes_key = hashlib.sha256(key).digest()
    decryptor_cipher = Cipher(algorithms.AES(aes_key), modes.CTR(nonce),backend=default_backend())
    decryptor = decryptor_cipher.decryptor()
    decrypted_text = decryptor.update(ciphertext) + decryptor.finalize()
    return decrypted_text

#transstr to specific length bytes
def trans_to_specific_length_bytes(input: Bytes) :
    target_length = lambda_val // 8
    if len(input) > target_length :
        res = input[:target_length]
    else :
        res = bytes(input).rjust(target_length, b'\0')
    return Bytes(res)

def get_keywords(IN) :
    W = set()
    for row in IN :
        W.add(row[1])
    return W

def get_indexes(IN,w) :
    indexes = []
    c = 0
    for row in IN :
        if row[1] == w :
            indexes.append([row[0],row[2]])
            c= c + 1
    return c,indexes

def get_EDB_size(EDB) :
    s = 0
    for row in EDB :
        s += len(row[0])
        s += len(row[1])
    return s/(1024 ** 2)

def KeyGen() :
    sk = group.random(ZR)
    pk = sk * P
    return sk,pk

def Update_in_DO(pk_DU,sk_DO,v_p,W,Ind) :
    EDB = []
    if v_p is None:
        v_p = U
    r = group.random(ZR)
    key = pk_DU * sk_DO
    key_bytes = group.serialize(key)
    st_key = r * key
    st_key_bytes = group.serialize(st_key)
    st_vl = F_1(st_key_bytes)
    L_st_vl = H_1(st_vl)
    E_st_vl = F_1(group.serialize(v_p * sk_DO)).__xor__(H_3(st_vl))
    EDB.append((L_st_vl,E_st_vl))
    v_p = v_p
    v_c = r * pk_DO
    for w in W :
        c = Ind[w][0]
        indexes = Ind[w][1]
        t_w = F_2(key_bytes, Bytes(w))  #need trans w to a specific Bytes
        j = 0
        L_st_vl_tw = H_2(st_vl, t_w, Bytes(j.to_bytes(lambda_val // 8,'big')))
        E_IN_w = Bytes(c.to_bytes(lambda_val // 8,'big')).__xor__(H_4(st_vl,t_w))
        EDB.append((L_st_vl_tw,E_IN_w))
        j= j+1
        k_vl_w = F_3(st_key_bytes,key_bytes,w)
        for ind in indexes :
            L_ind = H_2(st_vl,t_w, Bytes(j.to_bytes(lambda_val // 8,'big')))
            E_ind = AES_encryption(k_vl_w,trans_to_specific_length_bytes(Bytes(ind[0]+ind[1])))
            EDB.append((L_ind,E_ind))
            j=j+1
    return EDB,v_c, v_p

def Update_in_CS(EDB,v_c) :
    CS.create_table(TABLE_NAME)
    CS.batch_insert(TABLE_NAME,EDB)

def Trapdoor(v_c,sk_DU,pk_DO,w) :
    key = sk_DU * pk_DO
    key_bytes = group.serialize(key)
    st_vl = F_1(group.serialize(v_c * sk_DU))
    t_w = F_2(key_bytes, w)
    return st_vl,t_w

def Search_in_CS(st_vl,t_w) :
    res = []
    L_st_vl = H_1(st_vl)
    E_st_vl = CS.query_by_col1(TABLE_NAME, L_st_vl)
    while E_st_vl is not None:
        E_st_vl = Bytes(E_st_vl)
        L_stvl_tw = H_2(st_vl, t_w, Bytes((0).to_bytes(lambda_val // 8, 'big')))
        E_IN = Bytes(CS.query_by_col1(TABLE_NAME, L_stvl_tw))
        IN_bytes = E_IN.__xor__(H_4(st_vl, t_w))
        IN_int = int.from_bytes(IN_bytes, 'big')
        for j in range(1, IN_int + 1):
            j_bytes = Bytes(j.to_bytes(lambda_val // 8, 'big'))
            L_ind = H_2(st_vl, t_w, j_bytes)
            E_ind = CS.query_by_col1(TABLE_NAME, L_ind)
            res.append(E_ind)
        st_vl_p = E_st_vl.__xor__(H_3(st_vl))
        L_st_vl = H_1(st_vl_p)
        E_st_vl = CS.query_by_col1(TABLE_NAME, L_st_vl)
    return res

def Decryption(res, sk_DU) :
    ind_add = set()
    ind_del = set()
    for row in res :
        ind = row[0].__xor__(H_5(row[1] * sk_DU, row[1]))
        if ind[lambda_val//8-3:lambda_val] == b'add' :
            ind_add.add(ind[:lambda_val//8 - 3])
        else :
            ind_del.add(ind[:lambda_val//8 - 3])
    for ind in ind_del :
        ind_add.discard(ind)
    return ind_add


if __name__ == '__main__':
    sk_DU,pk_DU = KeyGen()
    sk_DO,pk_DO = KeyGen()

# Update time test
    reader = csv.reader(open('chose your dataset path'))
    IN = []
    for row in reader :
        IN.append([row[0].encode('utf-8'),row[1].encode('utf-8'),row[2].encode('utf-8')])
    W = get_keywords(IN)
    Ind = {}
    for w in W :
        Ind[w] = get_indexes(IN,w)
    start_time = time.time()
    EDB,v_c, v_p = Update_in_DO(pk_DU,sk_DO,U,W,Ind)
    # Update_in_CS(EDB, v_c)
    end_time = time.time()
    print('Update time cost:', end_time-start_time)
    print(f'Ciphertext size{get_EDB_size(EDB)}MB')


# Search time test
#     reader = csv.reader(open('chose your dataset path'))
#     IN = []
#     for row in reader :
#         IN.append([row[0].encode('utf-8'),row[1].encode('utf-8'),row[2].encode('utf-8')])
#     W = get_keywords(IN)
#     Ind = {}
#     for w in W :
#         Ind[w] = get_indexes(IN,w)
#     EDB, v_c, v_p = Update_in_DO(pk_DU, sk_DO, U, W,Ind)
#     Update_in_CS(EDB, v_c)
#     start_time_TD = time.time()
#     st_vl, t_w = Trapdoor(v_c,sk_DU,pk_DO,b'Internet of Things')
#     end_time_TD = time.time()
#     print((end_time_TD-start_time_TD)*1000) #ms
#     start_time = time.time()
#     res = Search_in_CS(st_vl,t_w)
#     end_time = time.time()
#     print('Our search time cost:', end_time - start_time)
#     print('res size:', get_EDB_size(res))

    # start_time = time.time()
    # r = group.random(ZR)
    # key = pk_DU * sk_DO
    # key_bytes = group.serialize(key)
    # st_key = r * key
    # st_key_bytes = group.serialize(st_key)
    # st_vl = F_1(st_key_bytes)
    # t_w = F_2(key_bytes, Bytes(b'Internet of Things'))
    # end_time = time.time()
    # print((end_time-start_time)*1000) #ms


    CS.delete_table(TABLE_NAME)
    CS.close()
