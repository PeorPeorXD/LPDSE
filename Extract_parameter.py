
import pickle
from traceback import print_tb

from charm.toolbox.pairinggroup import PairingGroup

filename = '/home/yanhaolong/PycharmProjects/PythonProject/Our/crypto_params.pkl'
with open(filename, 'rb') as f:
    loaded_params = pickle.load(f)

group_name = loaded_params['group_name']
group = PairingGroup(group_name)

def get_generator():

    P_loaded = group.deserialize(loaded_params['P'])
    return P_loaded

def get_initial_state():

    U_loaded = group.deserialize(loaded_params['U'])
    return U_loaded


