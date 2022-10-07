import hashlib

chunk_size = 1000 # 1 kb 

def pad_data(data : bytes):
    if len(data)%chunk_size!=0:
        data = data + b"\x00"*(len(data)%chunk_size)
    return data

def merkle_tree(data : bytes, hash= hashlib.sha1):
    tree = [[]]
    
    for i in range(0,len(data),chunk_size):
        tree[0].append(hash(data[i:i+chunk_size]).hexdigest())
    while len(tree[0]) > 1:
        temp = []
        for i in range(0,len(tree[0]),2):
            node1 = tree[0][i]
            node = node1
            if i+1!=len(tree[0]):
                node2 = tree[0][i+1] 
                node = node1+node2
                
            h = hash(node.encode()).hexdigest()
            temp.append(h)
        tree.insert(0,temp)         

    return tree

def proof_of_inclusion(data_chunk : bytes,tree : list,hash= hashlib.sha1):
    h = hash(data_chunk).hexdigest()
    pi = []
    for i in range(len(tree)-1,0,-1):
        in_tree = False
        for j in range(0,len(tree[i]),2):
            node1 = tree[i][j]
            
            if j+1 != len(tree[i]):
                node2 = tree[i][j+1]
                if h == node1:
                    pi.append(("R",node2))
                elif h == node2:
                    pi.append(("L",node1))
                else:
                    continue
                # am lazy to index lol
                h = hash((node1+node2).encode()).hexdigest()
                in_tree = True
                break  
            else:
                if h == node1:
                    h = hash((node1).encode()).hexdigest()
                    in_tree = True
                    break 
                else:
                    return [] 
        if (not in_tree) and (i == len(tree) - 1) :
            return []

    return pi
def verify_inclusion(data_chunk : bytes,pi : list, root_hash : str, hash=hashlib.sha1):
    h = hash(data_chunk).hexdigest()
    for i in pi:
        direc,h1 = i[0],i[1]
        if direc == "R":
            h = hash((h + h1).encode()).hexdigest()
        else:
            h = hash((h1+h).encode()).hexdigest()
    return h == root_hash 
f = open("unix_horro.txt","rb")

a = f.read()
f.close()
# pad to multiple of your chunk size
a = pad_data(a)
tree = merkle_tree(a)
root_hash = tree[0][0]
print("Root hash of your tree :", root_hash)
data_chunk = [a[i:i+chunk_size] for i in range(0,len(a),chunk_size)][3]
pi = proof_of_inclusion(data_chunk,tree)
print("Your proof of inclusion :" , pi)
print("Verification :",verify_inclusion(data_chunk,pi,root_hash))
