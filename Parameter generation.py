import os
import pickle
from charm.toolbox.pairinggroup import PairingGroup, G1, ZR


def generate_and_save():
    """
    生成密码学参数并将其序列化后保存到文件中。
    """
    # 1. 选择一个配对曲线并初始化 PairingGroup
    group_name = 'SS512'
    group = PairingGroup(group_name)

    # 2. 在 G1 和 ZR 群中生成随机元素
    # P 是 G1 群的一个生成元或随机元素
    # U 是一个initial state （G1 中的元素）
    P = group.random(G1)
    U = group.random(G1)
    print('P:',P)
    print('U:',U)
    # 打印原始对象信息以供比对
    print("--- 正在生成和保存 ---")
    print(f"Group Name: {group_name}")
    print(f"Original P type: {type(P)}")
    print(f"Original U type: {type(U)}")

    # 3. 准备要保存的数据
    # 注意：我们不直接保存 group 对象，而是保存它的名称
    # 我们使用 group.serialize() 来序列化群元素
    params_to_save = {
        'group_name': group_name,
        'P': group.serialize(P),
        'U': group.serialize(U)
    }

    # 4. 使用 pickle 将字典保存到文件
    # 使用 'wb' 模式（写入二进制）是因为序列化的结果是字节串
    filename = 'crypto_params.pkl'
    with open(filename, 'wb') as f:
        pickle.dump(params_to_save, f)

    print(f"\n参数已成功保存到文件: {filename}")
    print("保存的数据结构:")
    print(params_to_save)


if __name__ == "__main__":
    generate_and_save()


