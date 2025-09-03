import os
import pickle
from charm.toolbox.pairinggroup import PairingGroup, G1, ZR


def load_and_use():
    """
    从文件中加载密码学参数并使用它们。
    """
    filename = 'crypto_params.pkl'

    # 检查文件是否存在
    if not os.path.exists(filename):
        print(f"错误: 参数文件 '{filename}' 不存在。")
        print("请先运行 'generate_and_save_params.py' 来生成文件。")
        return

    # 1. 使用 'rb' 模式（读取二进制）从文件中加载数据
    with open(filename, 'rb') as f:
        loaded_params = pickle.load(f)

    print("--- 正在加载和使用 ---")
    print("从文件加载的序列化数据:")
    print(loaded_params)

    # 2. 重新构建密码学环境
    # 首先，使用保存的 group name 重新初始化 PairingGroup
    group_name = loaded_params['group_name']
    group = PairingGroup(group_name)

    # 3. 使用 group 对象反序列化群元素
    # 这是关键步骤，必须用对应的 group 对象来反序列化
    P_loaded = group.deserialize(loaded_params['P'])
    U_loaded = group.deserialize(loaded_params['U'])

    print("\n参数已成功加载并反序列化！")
    print(f"Re-created g type: {type(P_loaded)}")
    print(f"Re-created a type: {type(U_loaded)}")

    # 4. 验证加载的参数是否可用
    # 例如，我们可以用加载的 g 和 a 来进行一次计算
    try:
        print('P:', P_loaded)
        print('U:', U_loaded)
        # 验证h确实是G1的元素
        assert group.ismember(P_loaded), "计算结果 h 不在 G1 群中！"
        assert group.ismember(U_loaded), "计算结果 h 不在 G1 群中！"
        print("类型验证通过，h 确实是 G1 的成员。")
    except Exception as e:
        print(f"\n验证失败！加载的参数无法使用: {e}")


if __name__ == "__main__":
    load_and_use()
    #P: [359629342177373923026949629650954095453381884975825337873381987273757947361828896253353720636351389907139879810096158202342651266525298691210499153752386,
    #    2942300549389005214566004753369687610799096590201725532507454848455596977401820156886853709946154478344047732496582536686855027549508548959932031308934980]
    #U: [6519694733633508567166758613220991749737150813751856830061016242685035666904478623524317186227955879782227879516409360855432438127543519351781277113253903,
    #    4868312991768617781092205994614587326894298636185112206698819196272166389866691895974537345672467451023030349906132959596997023704483030105815437341992614]