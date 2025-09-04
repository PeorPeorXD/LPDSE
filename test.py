import os
import pickle
import Our
from charm.toolbox.pairinggroup import PairingGroup, G1, ZR
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


def update_test(pk_DU,sk_DO,pk_DO) :
    CS = DatabaseServer()
    TABLE_NAME = 'Test'
    print('Start update test')
    reader = csv.reader(open('/home/yanhaolong/PycharmProjects/PythonProject/keywords_500_extended30000.csv'))
    IN = []
    for row in reader :
        IN.append([row[0].encode('utf-8'),row[1].encode('utf-8'),row[2].encode('utf-8')])
    W = Our.get_keywords(IN)
    Ind = {}
    for w in W :
        Ind[w] = Our.get_indexes(IN,w)
    start_time = time.time()
    EDB,v_c, v_p = Our.Update_in_DO(pk_DU,sk_DO,pk_DO,Our.U,W,Ind)
    # Update_in_CS(EDB, v_c)
    end_time = time.time()
    print('Update time cost:', end_time-start_time)
    print(f'{Our.get_EDB_size(EDB)}MB')
    CS.delete_table('Test')
    CS.close()

def search_test(sk_DU,pk_DU,sk_DO,pk_DO) :
    CS = DatabaseServer()
    TABLE_NAME = 'Test'
    print('Start search test')
    reader = csv.reader(open('/home/yanhaolong/PycharmProjects/PythonProject/IN_IOT_10000.csv'))
    IN = []
    for row in reader :
        IN.append([row[0].encode('utf-8'),row[1].encode('utf-8'),row[2].encode('utf-8')])
    W = Our.get_keywords(IN)
    Ind = {}
    for w in W :
        Ind[w] = Our.get_indexes(IN,w)
    EDB, v_c, v_p = Our.Update_in_DO(pk_DU, sk_DO, pk_DO, Our.U, W, Ind)
    Our.Update_in_CS(EDB, v_c,CS,TABLE_NAME)
    #start_time_TD = time.time()
    st_vl, t_w = Our.Trapdoor(v_c,sk_DU,pk_DO,b'Internet of Things')
    #end_time_TD = time.time()
    #print((end_time_TD-start_time_TD)*1000) #ms
    start_time = time.time()
    res = Our.Search_in_CS(st_vl,t_w)
    end_time = time.time()
    print('Our search time cost:', end_time - start_time)
    CS.delete_table('Test')
    CS.close()

def state_generation_test():
    start_time = time.time()
    r = Our.group.random(ZR)
    key = pk_DU * sk_DO
    key_bytes = Our.group.serialize(key)
    st_key = r * key
    st_key_bytes = Our.group.serialize(st_key)
    st_vl = Our.F_1(st_key_bytes)
    t_w = Our.F_2(key_bytes, Bytes(b'Internet of Things'))
    end_time = time.time()
    print((end_time-start_time)*1000) #ms





if __name__ == "__main__":
    sk_DU, pk_DU = Our.KeyGen()
    sk_DO, pk_DO = Our.KeyGen()
    CS = DatabaseServer()
    TABLE_NAME = 'Test'
    CS.delete_table('Test')
    CS.close()
    update_test(pk_DU,sk_DO,pk_DO)
    search_test(sk_DU,pk_DU,sk_DO,pk_DO)
    state_generation_test()
