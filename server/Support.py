import random

def randomFromList (l):
    if len (l) == 0:
        return None
    
    listSize = len (l)
    ra = random.randint(0, listSize - 1)        
    return l[ra] 
    
