import os
import pickle
from charm.toolbox.pairinggroup import PairingGroup, G1, ZR


def generate_and_save():

    group_name = 'SS512'
    group = PairingGroup(group_name)

    P = group.random(G1)
    U = group.random(G1)
    print('P:',P)
    print('U:',U)

    print("Generating and Saving")
    print(f"Group Name: {group_name}")
    print(f"Original P type: {type(P)}")
    print(f"Original U type: {type(U)}")

   
    params_to_save = {
        'group_name': group_name,
        'P': group.serialize(P),
        'U': group.serialize(U)
    }


    filename = 'crypto_params.pkl'
    with open(filename, 'wb') as f:
        pickle.dump(params_to_save, f)

    print(f"\nparameters successfully saved to: {filename}")
    print(params_to_save)


if __name__ == "__main__":
    generate_and_save()


