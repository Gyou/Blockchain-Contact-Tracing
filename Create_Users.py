import pickle
from Crypto.PublicKey import RSA
import threading
import numpy as np
def save_variable(v, filename):
    f = open(filename, 'wb')
    pickle.dump(v, f)
    f.close()
    return filename


def load_variavle(filename):
    f = open(filename, 'rb')
    r = pickle.load(f)
    f.close()
    return r



class User:
    def __init__(self, id, credit, balance, mean_cont, var_cont, mean_wit,var_wit):
        self.pub_key = 0
        self.pri_key = 0
        self.credit = credit  # reputation
        self.balance = balance  # pecuniary reward
        # device ID
        self.dev_id = id
        #  mean of length of contact list, it will be set 4 for frequent users, and be set 1 for ordinary users
        self.u_c = mean_cont
        self.d_c = var_cont
        self.u_w = mean_wit
        self.d_w = var_wit
        self.mined_count = 0.0000001

        #  contact record, a local copy of this user's contactors, contact[0] is a list [, , , ], records all other users contacted, the witnes info is stored in wit_rec
        self.old_len = 0  # this is to help indicate is there any new contacts are recorded
        self.cont_rec = []
        self.wit_rec = []

        # to be verified (signed) transaction record. each element is [a,b,c,d] , a is the index of unverified_TX_pool, indicating which transaction, b is the index of which record in the TX_body, c = 0/1, indicating the record is in contact_list or witness_list, d indicating which one in the list
        self.TX_to_be_verified = []

        self.TX_to_be_stored = []

        # generated transaction and corresponding secret message in used in that transaction
        self.tran_msg = {}

    # generate privatekey and private key.
    def gen_keys(self):
        keyPair = RSA.generate(1024)
        self.pri_key = keyPair
        self.pub_key = keyPair.publickey()
        #Reg_Dic[self.dev_id] = self.pub_key

low_user = []
mid_user = []
high_user = []

def gen_low_user():
    for i in range(0,10):
        u = User(id=i, credit=100, balance=100, mean_cont=0,var_cont=2,mean_wit=0,var_wit=1)
        u.gen_keys()
        low_user.append(u)

    #filename = save_variable(low_user, 'low_user.txt')

def gen_mid_user():
    for i in range(0,10):
        u = User(id=i, credit=100, balance=100, mean_cont=2,var_cont=4,mean_wit=2,var_wit=2)
        u.gen_keys()
        low_user.append(u)

    #filename = save_variable(mid_user, 'mid_user.txt')


def gen_high_user():
    for i in range(0,10):
        u = User(id=i, credit=100, balance=100, mean_cont=5,var_cont=2,mean_wit=7,var_wit=2)
        u.gen_keys()
        low_user.append(u)

    #filename = save_variable(high_user, 'high_user.txt')

if __name__ == '__main__':

    threads = []

    threads.append(threading.Thread(target=gen_low_user))
    threads.append(threading.Thread(target=gen_mid_user))
    threads.append(threading.Thread(target=gen_high_user))
    for t in threads:
        print(t)
        t.start()
        t.join()

    np.savez('users.npz', l_u=low_user, m_u=mid_user,h_u = high_user)

    Users = np.load('users.npz')
    # low_user = load_variavle('low_user.txt')
    # print('low user', low_user)
    # mid_user = load_variavle('mid_user.txt')
    # print('mid user', mid_user)
    # high_user = load_variavle('high_user.txt')
    # print('high user', high_user)
    print(Users['l_u'])