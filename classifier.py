# 2017-May-3 17:16:11
# Author:Yuqian Shi
import time
from functools import wraps
from decimal import Decimal
accuracy = 5
zero = Decimal("0.00000000000000001")

# print time consumption for each function
def fun_timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print ("time running {0}: {1:.3f} seconds".format(function.__name__, t1-t0))
        return result
    return function_timer

@fun_timer
def read_file(path):
    l = []
    f = open(path,"r")
    for line in f:
        tmp = line.split(", ")
        # remove ID number
        tmp = tmp[0:2]+tmp[3:15]
        l.append(tmp)
    f.close()
    return l


@fun_timer
def types_rate(index_of_types,train_data):
    result = dict()
    for line in train_data:
        tmp = line[index_of_types]
        if tmp in result:
            result[tmp] += Decimal(1)
        else:
            result[tmp] = Decimal(0)
    total = Decimal(len(train_data))
    for t in result:
        result[t] = Decimal(result[t]/total)
        if result[t] == 0:
            result[t] = zero
    return result
    
@fun_timer
def attributes_rate(index_of_types,train_data,types):
    result = dict()
    for index in range(0,index_of_types):
        result[index]=dict()
    #do the counting
    for line in train_data:
        for index in range(0,index_of_types):
            if not line[index] in result[index]:
                result[index][line[index]] = dict()
                for t in types:
                    result[index][line[index]][t] = Decimal(0)
            else:
                result[index][line[index]][line[index_of_types]] += Decimal(1)

    #caculate rate
    total = Decimal(len(train_data))
    for index in result:
        for attribute in result[index]:
            for t in result[index][attribute]:
                result[index][attribute][t] = Decimal(result[index][attribute][t]/total)
                if result[index][attribute][t] == 0:
                    result[index][attribute][t] = zero
    return result
def predict(dic):
    tmp = Decimal("0")
    for key in dic:
        if tmp < dic[key]:
            tmp = dic[key]
            index = key
    return tmp,index

if __name__ == '__main__':
    train = read_file("adult.data")
    train_size = len(train)
    print ("training file loaded:",train_size)
    p_types = types_rate(13,train)
    types = []
    for t in p_types:
        types.append (t)
    #first caculate positive rate.
    p_atts = attributes_rate(13,train,types)
    print ("finished training, start testing")
    tp=Decimal(0)
    fp=Decimal(0)
    fn=Decimal(0)
    tn=Decimal(0)
    t_count = Decimal(0)
    test = read_file("adult.test")
    t_count = Decimal(len(test))
    for line in test:
        # p to record possibility in each type, in this case,noly two types
        p=dict()
        for t in p_types:
            p[t]= Decimal(1)
        for index in range(0,13):
            for t in p_types:
                # caculate possibility of this line is a type t under given attributes
                try:
                    p[t] *= p_atts[index][line[index]][t]
                # some value of attributes never show up in training, so consider as zero
                except:
                    p[t] *= zero
        p,key = predict(p)
        # classify into true negative/true positive/false negative/false positive
        if key=="<=50K\n" and line[13]=="<=50K.\n":
            tn += 1
        elif key=="<=50K\n" and line[13]==">50K.\n":
            fn += 1
        elif key==">50K\n" and line[13]==">50K.\n":
            tp += 1
        elif key==">50K\n" and line[13]=="<=50K.\n":
            fp += 1
    # print scores
    print ("accuracy:\t"  ,(tp+tn)/(tp+fn+tn+fp))
    print ("recall:\t\t"  ,(tp)/(tp+fn))
    print ("precision:\t" ,(tp)/(tp+fp))
    print ("f1 score:\t"  ,(2*tp)/(2*tp+fp+fn))
