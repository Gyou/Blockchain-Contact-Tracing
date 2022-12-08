# this python file simulates the DPoS benchmark for this paper


# the benchmark here is only to see how decentralized will the system be if we use ordinary DPoS consensus algorithm
import threading
import os, time
import math, random
import uuid
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA384
import binascii
import numpy as np
import matplotlib.pyplot as plt
import quantecon as qe
from multiprocessing import Process
import multiprocessing

# generate frequency
gen_freq = 1  # every 5 minutes
User_num = 300
# this dictionary stores all ( publickey, deviceID) pair
Reg_Dic = [0 for i in range(User_num)]
gen_tran_mon_reward = 1
sign_tran_mon_reward = 1
mine_block_mon_reward = 5  # this varies for different user
failure_mon_punish = 5

record_point = 5000

#  Transactions will be generated for every 1 minute
class Transaction:
    # randomly generate transaction id
    def __init__(self):
        self.TX_id = uuid.uuid4().hex
        self.generator = 0
        self.TX_body = []
        self.gen_time = 0
        self.verify_time = 0
        self.stored_in_block_time = 0


class Block:
    # here we ignore the hash value and the linkage of each block
    def __init__(self):
        self.BK_id = uuid.uuid4().hex
        self.Miner_pub_key = 0
        self.BK_body = []  # a collection of transactions
        self.gen_time = 0


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
        #keyPair = RSA.generate(1024)
        self.pri_key = self.dev_id
        self.pub_key = self.dev_id
        Reg_Dic[self.dev_id] = self.pub_key

    # add

    #  generate transactions
    def gen_tran(self):
        #print(len(self.cont_rec), self.old_len)
        cur_len = len(self.cont_rec)
        while(True):
            #print(self.cont_rec)
            if (len(self.cont_rec) >= (self.old_len + gen_freq)):
                #print('user',self.dev_id,'is generating transaction',len(self.tran_msg),len(self.cont_rec), self.old_len,'\n')
                new_Tran = Transaction()
                #  read contact info and witness info
                contact_list = []  # every element is a public key
                witness_list = []  # every element is a public key
                flag = 0
                for i in range(self.old_len, self.old_len + gen_freq):
                    #print('start generating',self.dev_id)
                    # one record in a TX body is one record of contact at timestamp i+1

                    # first eliminate potential duplicated record
                    self.cont_rec[i] = list(set(self.cont_rec[i]))
                    self.wit_rec[i] = list(set(self.wit_rec[i]))

                    if len(self.cont_rec[i]) == 0:
                        #print("not contact for this timestamp", i+1)
                        continue

                    flag = 1 # we actually have contact here
                    # format the contact list in TX_body
                    formated_cont_list = []

                    for dev_id in self.cont_rec[i]:
                        # encrypt the secret message with public key
                        #print('encrypting one')
                        pubkey = dev_id
                        # encryptor = PKCS1_OAEP.new(pubkey)
                        # encrypted = encryptor.encrypt(msg)
                        formated_cont_list.append([pubkey])
                        # assume all user will honestly sign, assign rewards to them
                        Users[dev_id].balance += sign_tran_mon_reward

                    formated_wit_list = []
                    for dev_id in self.wit_rec[i]:
                        pubkey = dev_id
                        # encryptor = PKCS1_OAEP.new(pubkey)
                        # encrypted = encryptor.encrypt(msg)
                        formated_wit_list.append([pubkey])
                        # assume all user will honestly sign, assign rewards to them
                        Users[dev_id].balance += sign_tran_mon_reward

                    new_Tran.TX_body.append([formated_cont_list, formated_wit_list, i + 1])

                # in this version we directly put the generated transaction into verified transaction, we ignore the verification process to speed up simulation
                if flag ==1:
                    new_Tran.generator = self.pub_key
                    s = 'a'
                    # msg = uuid.uuid4().bytes  # a secret message
                    msg = bytes(s, encoding="utf8")
                    self.tran_msg[new_Tran.TX_id] = msg
                    verified_TX_pool.append(new_Tran)

                    # assign rewards to the tx generator
                    self.balance += gen_tran_mon_reward

                    print('tx appended\n')
                self.old_len = self.old_len + gen_freq

    #
    def get_notified_signature(self, tx_index, rec_index, if_wit, list_index):
        if [tx_index, rec_index, if_wit, list_index] not in self.TX_to_be_verified:
            self.TX_to_be_verified.append([tx_index, rec_index, if_wit, list_index])

    def get_notified_populate_TX(self, tx_index, full_signed_indicator):
        if [tx_index, full_signed_indicator] not in self.TX_to_be_stored:
            self.TX_to_be_stored.append([tx_index, full_signed_indicator])


#  this function is to simulate the people contacting
def gen_contact():
    timestamp = 1
    while (True):

        # for every user create contact list and witness list
        for user in Users:
            user.cont_rec.append([])
            user.wit_rec.append([])

        # traverse  every user and generate contact info
        print('=======================timestamp==========',timestamp,)
        for i in range(0, len(Users)):
            user = Users[i]
            if user.u_c == 0:
                if timestamp % 12 != 0:
                    continue
            elif user.u_c == 2:
                if timestamp % 4 != 0:
                    continue
            elif user.u_c == 5:
                if timestamp % 1 != 0:
                    continue
            # do uniform sampling to decide how many contacts in this minute
            len_contact = int(random.gauss(user.u_c, user.d_c))
            # print('len_contact',len_contact,'user',i)
            # if len_contact <0, then this timestamp there will be no transaction for this user
            if len_contact <= 0:
                # the contact list and the witness list will be set as empty set [] for this timestamp
                # Users[i].cont_rec.append([])
                # Users[i].wit_rec.append([])

                continue

            contact_list = []
            u_type = Users[i].u_c
            available_cont_wit_list = []
            # deep copy
            for k in User_type[u_type]:
                available_cont_wit_list.append(k)
            contact_list = []
            # print('user',i,'generating contact\n')
            for j in range(0, len_contact):
                # randomly choose one in the same type as a contact
                if len(available_cont_wit_list) > 1:
                    ind = random.randint(0, len(available_cont_wit_list) - 1)
                elif len(available_cont_wit_list) == 1:
                    ind = 0
                else:
                    break
                dev_id = available_cont_wit_list[ind]
                # to avoid contact with itself
                # print(Users[dev_id].u_c,Users[i].u_c)
                while (dev_id == i or (dev_id in contact_list) or (Users[dev_id].u_c != Users[i].u_c)):
                    del (available_cont_wit_list[ind])  # delete the one that does not fit in
                    if len(available_cont_wit_list) > 1:
                        ind = random.randint(0, len(available_cont_wit_list) - 1)
                    elif len(available_cont_wit_list) == 1:
                        ind = 0
                    else:
                        break
                    dev_id = available_cont_wit_list[ind]
                # one instance of contact is generated as follows
                # print('one contact record: user ',i,' contacted with user ', dev_id, ' at time ',timestamp)
                # record this contact info into both users local copy.
                # timestamp start at 1, but the index starts at 0
                contact_list.append(dev_id)
                # del(available_cont_wit_list[ind])

            # print('gen contact finished',contact_list)
            user.cont_rec[timestamp - 1].extend(contact_list)

            for id in contact_list:
                # print('contact list',contact_list)
                # print('target user contact list',id,Users[id].cont_rec )

                Users[id].cont_rec[timestamp - 1].append(i)
            # print('user', i, 'generating witness\n')

            # let's make the witness list simple, the number of witness is the distribution with mean: user.u+2
            len_witness = int(random.gauss(user.u_w, user.d_w))
            if len_witness <= 0:
                continue

            wit_list = []
            for j in range(0, len_witness):
                # randomly choose one as a witness, the witness must not in the contact list
                if len(available_cont_wit_list) > 1:
                    ind = random.randint(0, len(available_cont_wit_list) - 1)
                elif len(available_cont_wit_list) == 1:
                    ind = 0
                else:
                    break
                dev_id = available_cont_wit_list[ind]
                while (dev_id == i or (dev_id in user.cont_rec[timestamp - 1]) or (dev_id in wit_list) or (
                        Users[dev_id].u_c != Users[i].u_c)):
                    del (available_cont_wit_list[ind])
                    # print(dev_id,i)
                    # print(user.cont_rec[timestamp - 1])
                    # print(wit_list)
                    # print(Users[dev_id].u_c,Users[i].u_c)
                    if len(available_cont_wit_list) > 1:
                        ind = random.randint(0, len(available_cont_wit_list) - 1)
                    elif len(available_cont_wit_list) == 1:
                        ind = 0
                    else:
                        break
                    # ind = random.randint(0, len(available_cont_wit_list) - 1)
                    dev_id = available_cont_wit_list[ind]

                    # print("new rand",dev_id)
                wit_list.append(dev_id)
                #del(available_cont_wit_list[ind])
                # record this witness info
            # print('gen witness finished', wit_list)
            user.wit_rec[timestamp-1].extend(wit_list)

            for id in wit_list:
                # print('contact list',contact_list)
                # print('target user contact list',id,Users[id].cont_rec )
                Users[id].wit_rec[timestamp-1].append(i)

            #print('user', i, 'contact', Users[i].cont_rec[timestamp - 1],)
            #print('user',i,'len contrec',len(user.cont_rec), 'len wit rec',len(user.wit_rec))

        timestamp += 1
        time.sleep(5)# wait for user generating transactions and mining blocks
        if timestamp>1440:
            print('gen finished')
            break


# full user list, to simplify the implementation, the index of Users, is also the dev_id of the corresponding user.
Users = []

# candidate miners
Candidate_Miners = []

Old_Candidate_index = []

# shared transaction pool
unverified_TX_pool = []

verified_TX_pool = []

# Blockchain Simulation (user list to simulate chained structure)
Blockchain_Storage = []




# do reputation-corrected DPoS.
def vote_for_new_Candidate_Miners():
    vote_record = [[] for i in range(len(Users))]  # use this to record who was voted by whom

    user_balance = []
    user_credit = []
    user_mined_count = []
    for user in Users:
        user_balance.append(user.balance)
        user_credit.append(user.credit)
        user_mined_count.append(user.mined_count)

    #prepare for balance_based vote
    ban_ratio_list = []
    for i in range(len(user_balance)):
        ban_ratio_list.append(user_balance[i] / np.sum(user_balance))

    cum_ban_ratio_list = ban_ratio_list
    for i in range(1, len(ban_ratio_list)):
        cum_ban_ratio_list[i] = cum_ban_ratio_list[i] + cum_ban_ratio_list[i - 1]

    # prepare for credit based vote
    crdt_ratio_list = []
    for i in range(len(user_credit)):
        crdt_ratio_list.append(user_credit[i] / np.sum(user_credit))

    cum_crdt_ratio_list = crdt_ratio_list
    for i in range(1, len(crdt_ratio_list)):
        cum_crdt_ratio_list[i] = cum_crdt_ratio_list[i] + cum_crdt_ratio_list[i - 1]

    for user in Users:
        # try random vote, every user have the same possibility to be voted
        voted_user_index = random_vote()
        # balance or credit ratio based vote
        #voted_user_index = ratio_based_vote(cum_ban_ratio_list)
        vote_record[voted_user_index].append(user.dev_id)

    # total score
    total_score = [0 for i in range(len(Users))]

    # after all voting, calculate the total score of each user
    # the total score here will be sum of voters' balance
    for i in range(len(vote_record)):
        for user_index in vote_record[i]:
            total_score[i] += Users[user_index].balance #/ np.sum(user_balance)

        # correct the score according to the users credit
        #total_score[i] = total_score[i] * (Users[i].credit / np.sum(user_credit)) *(1 - Users[i].mined_count / np.sum(user_mined_count))
    #print('score list before ranking', total_score)

    # select top N/5 user
    selected_index = top_user_selection(math.ceil(len(Users) / 5), total_score)

    # add these users into candidate miner list
    for ind in selected_index:
        Candidate_Miners.append(Users[ind])


def random_vote():
    user_index = random.randint(0, len(Users) - 1)
    return user_index

# the more balance you have, the more like you are voted
def ratio_based_vote(cum_ratio_list):

    # get a random number
    rand = random.uniform(0,1)
    for i in range(len(cum_ratio_list)):
        if rand<=cum_ratio_list[i]:
            return i # this is the index been choosen

    print('no one chosen')

# select top k users from the the score list
def top_user_selection(k, scored_list):
    global Old_Candidate_index
    ranked_index_list = [i for i in range(len(scored_list))]

    # do rank the scored_list, meanwhile rank the index_list, so that we can know the original index of each score
    for i in range(1, len(scored_list)):

        key = scored_list[i]
        key1 = ranked_index_list[i]

        j = i - 1
        while j >= 0 and key > scored_list[j]:
            scored_list[j + 1] = scored_list[j]
            ranked_index_list[j + 1] = ranked_index_list[j]
            j -= 1
        scored_list[j + 1] = key
        ranked_index_list[j + 1] = key1

    #print('score list', scored_list)

    # return_index_list = []
    # i=0
    #
    # while(i<k and j<len(ranked_index_list)):
    #     if ranked_index_list[j] not in Old_Candidate_index:
    #         return_index_list.append(ranked_index_list[j])
    #         i+=1
    #
    #     j+=1

    #print('old',Old_Candidate_index)
    #print('new',return_index_list)
    #Old_Candidate_index = return_index_list

    #return return_index_list
    return ranked_index_list[0:k]


 # do the mining job


def blockchain_mining():
    global verified_TX_pool
    while (True):
        if len(verified_TX_pool) == 0:
            continue
        if len(Candidate_Miners) == 0:
            vote_for_new_Candidate_Miners()

        chosen_one = random.randint(0, len(Candidate_Miners) - 1)
        miner = Candidate_Miners[chosen_one]  # miner is also a user
        # every miner have 0.1% change of failure to mine
        while(random.uniform(0,1)<=0.001):
            miner.balance -= failure_mon_punish
            del(Candidate_Miners[chosen_one])
            if(len(Candidate_Miners)==0):
                print('All Candidate Miners Failed! Generating New cadidate Miners')
                vote_for_new_Candidate_Miners()
            chosen_one = random.randint(0, len(Candidate_Miners) - 1)
            miner = Candidate_Miners[chosen_one]  # miner is also a user

        # generate a block
        new_Block = Block()
        new_Block.Miner_pub_key = miner.pub_key
        new_Block.BK_body = verified_TX_pool  # put all transactions in the verified pool into blockchain
        verified_TX_pool = []  # clear all transactions in the verified pool
        Blockchain_Storage.append(new_Block)
        print('mined block')

        # if there is 2000 blocks, draw a pic
        if len(Blockchain_Storage) == record_point:
            draw_decentralized_figure(Users, Blockchain_Storage)

        # assign rewards:
        #miner.credit += mine_block_cred_reward

        #calculate how many transactions the system have been generated
        total_tran = 0
        for user in Users:
            total_tran += len(user.tran_msg)

        # the more transactions the user generating, the less pecuniary reward will be given to him.
        miner.balance += mine_block_mon_reward
        miner.mined_count += 1

        del(Candidate_Miners[chosen_one])




def gini(arr):
    count = arr.size
    coefficient = 2 / count
    indexes = np.arange(1, count + 1)
    weighted_sum = (indexes * arr).sum()
    total = arr.sum()
    constant = (count + 1) / count
    return coefficient * weighted_sum / total - constant

def lorenz(arr):
    # this divides the prefix sum by the total sum
    # this ensures all the values are between 0 and 1.0
    scaled_prefix_sum = arr.cumsum() / arr.sum()
    # this prepends the 0 value (because 0% of all people have 0% of all wealth)
    return np.insert(scaled_prefix_sum, 0, 0)

def draw_decentralized_figure(Users,Blockchain_Storage):
        if len(Blockchain_Storage)%20 !=0:
            return
        credit = []
        balance = []
        mining_count = []

        for user in Users:
            credit.append(user.credit-99.999)
            balance.append(user.balance-99.999)
            mining_count.append(user.mined_count)

        #credit.sort()
        #balance.sort()
        #mining_count.sort()

        credit = np.array(credit)
        balance = np.array(balance)
        mining_count = np.array(mining_count)

        #print(credit)
        #print(balance)
        #print(mining_count)

        array_list = [credit,balance,mining_count]
        name_list = ['user credit', 'user balance', 'mined blocks count']
        gini_list = [round(qe.gini_coefficient(credit),2),round(qe.gini_coefficient(balance),2), round(qe.gini_coefficient(mining_count),2)]

        fo = open("Gini_record4.txt", "a")
        fo.write(str(gini_list[0])+" "+str(gini_list[1])+" "+str(gini_list[2])+" "+str(len(Blockchain_Storage))+"\n")
        fo.close()

        # show the gini index!
        # print("gini of credit ", gini_list[0])
        # print("gini of balance ", gini_list[1])
        # print("gini of mining count ", gini_list[2])
        colors = ['orange', 'limegreen', 'blueviolet']
        fig, ax = plt.subplots()
        for i in range(len(name_list)):
            f_vals, l_vals = qe.lorenz_curve(array_list[i])
            ax.plot(f_vals*100, l_vals*100, label=name_list[i] + ', gini = ' + str(gini_list[i]),color = colors[i])
        ax.plot(f_vals*100, f_vals*100, label='equality, gini = 0')
        ax.legend()

        plt.title('Baseline, Total user '+str(len(Users))+', Mined '+ str(len(Blockchain_Storage)) + ' Blocks')
        plt.xlabel("Cumulative % of users")
        plt.ylabel("Cumulative % of  corresponding value")
        if len(Blockchain_Storage) in [1000,3000, record_point]:
            plt.savefig("new"+str(User_num)+'diff_user_50_ban_reward_non_restricted_BenchMark_'+str(len(Blockchain_Storage) )+'.pdf')
        plt.show()

        Gini_Change = [[],[],[]]
        Gini_Change_X_Stick = []
        with open('Gini_record4.txt','r') as f:
            r = f.readline()
            while(r):
                line = r.split(" ")
                #print(line)
                credit_gini = float(line[0])
                balance_gini = float(line[1])
                mining_count_gini = float(line[2])
                block_height = int(line[3])
                #print(block_height)
                Gini_Change[0].append(credit_gini)
                Gini_Change[1].append(balance_gini)
                Gini_Change[2].append(mining_count_gini)
                Gini_Change_X_Stick.append(block_height)
                r = f.readline()

        draw_gini_curve(Gini_Change,Gini_Change_X_Stick,Blockchain_Storage,Users)




# draw the Gini Change to see if it will converge
def draw_gini_curve(Gini_Change,Gini_Change_X_Stick,Blockchain_Storage,Users):
    plt.figure()
    x = Gini_Change_X_Stick
    #
    y = Gini_Change
    colors = ['orange','limegreen','blueviolet']
    legends = ['-','-','-','-*','-o','-o','-s','-s']

    for index in range(len(y)):
        #sample_y = y[index]
        sample_y = y[index]
        plt.plot(x,sample_y,legends[index],color = colors[index])

    ax = plt.gca()
    #plt.xticks([ 5,10,15,20,25,30,35])
    # xticks = ['' for i in range(len(x))]
    # # only show 6 labels on x axis
    # if len(x)>4:
    #     for i in range(6):
    #         ind = int(len(x)/5*i)
    #         xticks[ind] = x[ind]
    #plt.xticks(np.arange(0, np.max(x), int(np.max(x)/5)))
    #ax.set_xticklabels(['Eu-email','Contact','Facebok','Coauthor','Prosper','Digg','Slashdot'])
    plt.yticks(np.arange(0, 1, 0.1))
    plt.legend(['Credit','Balance','Mining Count'])
    plt.xlabel('Height of Blockchain')
    plt.ylabel('Gini Index')
    plt.title('Baseline, Total user ' + str(len(Users)) + ', Gini Index with Height of block')
    if len(Blockchain_Storage) in [1000,3000, record_point]:
        plt.savefig("new"+str(User_num)+'diff_user_50_ban_reward_non_restricted_BenchMark_Gini_'+str(len(Blockchain_Storage) )+'.pdf')
    plt.show()

def plot_lorenz_curve(array_list,name_list,gini_list):
    fig, ax = plt.subplots()
    for i in range(len(name_list)):
        print('==11')
        print('arraylist[i]',array_list[i])
        f_vals, l_vals = qe.lorenz_curve(array_list[i])
        print('add one plot')
        ax.plot(f_vals, l_vals, label=name_list[i]+'gini = '+ str(gini_list[i]))
    ax.plot(f_vals, f_vals, label='equality')
    ax.legend()

    plt.show()

User_type = [[] for i in range(6)]

if __name__ == '__main__':
    #  create users
    #Users = [User(id=i, credit=100, balance=1, mean=4) for i in range(User_num)]
    for i in range(100):
        u = User(id=i, credit=100, balance=100, mean_cont=0, var_cont=1, mean_wit=0, var_wit=2)
        u.gen_keys()
        Users.append(u)
        User_type[0].append(i)
    for i in range(100, 200):
        u = User(id=i, credit=100, balance=100, mean_cont=2, var_cont=4, mean_wit=2, var_wit=2)
        u.gen_keys()
        Users.append(u)
        User_type[2].append(i)
    for i in range(200, 300):
        u = User(id=i, credit=100, balance=100, mean_cont=5, var_cont=2, mean_wit=7, var_wit=2)
        u.gen_keys()
        Users.append(u)
        User_type[5].append(i)

    # print(Reg_Dic.index(Users[0].pub_key))
    #print(Users)

    print('users are created')
    #gen_contact()
    #draw_decentralized_figure()

    threads = []

    if os.path.exists('Gini_record4.txt'):
        os.remove("Gini_record4.txt")

    for i in range(len(Users)):
        threads.append(threading.Thread(target=Users[i].gen_tran))

    threads.append(threading.Thread(target=gen_contact))
    #threads.append(threading.Thread(target=user_activity))
    threads.append(threading.Thread(target=blockchain_mining))



    for t in threads:
        print(t)
        t.start()


    while(True):
        if (len(Blockchain_Storage) != 0 and len(Blockchain_Storage) % 50 == 0):
            t = Process(target=draw_decentralized_figure, args=(Users, Blockchain_Storage))
            t.start()
            t.join()

    print('After all threads created, you may wait about 5 minutes until they start')
    #draw_decentralized_figure()
