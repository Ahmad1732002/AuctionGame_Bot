import random
#from client_runner import play
from uuid import uuid4

def analyze_list(info,left_to_win, curr_rnd, items):
     #dictionary that stores each painting as a key and the round when in which the third painting of the same artist will be on the list
    artist_reps={}
    painter_repitition=0
    for i,painter in enumerate(info["items"]):
        painter_repitition=0
        #check the first 12 elements as it is enough to find the first painting that is repeated three times
        for j in range(curr_rnd,curr_rnd+11):
            if(i>=j):
                if(info["items"][i]==info["items"][j] and (painter not in artist_reps) and (painter in items)):
                    painter_repitition+=1
                    #left_to_win refers to how many paintings do i still need to win the game
                    if(painter_repitition==left_to_win):
                        painter_repitition=0
                        artist_reps[painter]=j+1
    #rearrange the dictionary and store it as a tuple in a list then sort it based on which painter has three repeated paintings first
    # the dictionary will have this format: (picasso:8,da_vinci:7)
    # the sorted new_list will have this format: {(7,da_vinci),(8,picasso)}
    lst=[(v,k) for k,v in artist_reps.items()]
    new_list= sorted(lst)
    return new_list

#function to return two lists, one for the paintings that i have only 1 from, and one for the paintings that i possess two from
def myPaintingsCnt(info):
    singlePaintingsList=[]
    twosPaintingsList=[]
    for x,y in info["self"]["item_count"].items():
        if(y==1):
            singlePaintingsList.append(x)
        elif(y==2):
            twosPaintingsList.append(x)
    return singlePaintingsList,twosPaintingsList

def avgBudget_Others(info, playersNum):
    sum=0
    for x in range(playersNum):
        sum+=info["others"][x]["budget"]
    avg=sum//playersNum
    return avg

def block_player(info, painting, original_bid):
     bid=original_bid
     for x in range (len(info["others"])):
        if(info["others"][x]["item_count"][painting]==2):
            new_bid = info["others"][x]["budget"]+1
            if new_bid <= info['self']['budget']:
                bid=max(bid, new_bid)
                
     return bid

# for concurrent runs, dont use global state
def compute_bid_state(info, prev_state=None):
    if prev_state is None:
        prev_state = 0
    next_state = prev_state + 1
    
    #I will create a list of the four painters based on their priority, for the painting with the lowest priority I bid only 3
    min_bid=2
    bid=min_bid
    round=info["cur_round"]
    numOfPlayers=len(info["others"])
    

    #First step: We should analyze the list and decide the priorities of each painting based on the list
    initial_priority=analyze_list(info,3,round,info["item_types"]) 
   
    #give initial priorities based on values stored in new_list
    #assign the first painting that is repeated three times to be of highest priority
    #the highest priority will be a set that might be updated after each round
    highest_priority=initial_priority[0][1]
    
    painting=info["items"][round]
    
    mySinglePaintingsList,myDoublePaintingsList=myPaintingsCnt(info) 
    #assign highest priority to the paintings that I already possess one piece of
    if(len(mySinglePaintingsList)>=1):
        updated_priority=analyze_list(info,2,round,mySinglePaintingsList)
        print(updated_priority)
        #we need to check whether the priority list is empty to avoid errors
        if(len(updated_priority)!=0):
            highest_priority=updated_priority[0][1]
    
    
    #assign bids based on priority
    if((painting==highest_priority) and (len(myDoublePaintingsList)==0)):
        #if i still have no paintings I bid small amount for first painting to have money left for other paintings
        if(len(mySinglePaintingsList)==0):
            
            #if there is only one player, my first bid will be 1/3 of the total money he owns plus 1 to get slight advantage
            if(numOfPlayers==1):
                otherPlayerBudget=info["others"][0]["budget"]
                bid=((otherPlayerBudget)//3) + 1
            else:
            #when playing against many people my first bid will be based on their average
                bid=(avgBudget_Others(info, numOfPlayers)//3) + 1
                new_bid=0
            #when people possess my priority painting then my bid will be based on their remaining budget 
                for x in range(numOfPlayers):   
                    if(info["others"][x]["item_count"][painting]>=1):
                        bid2=((info["others"][x]["budget"])//2)
                        if(bid2>=new_bid):
                            new_bid=bid2
                            bid2=0
                            
                if new_bid:
                    bid = new_bid
            #in these calculations i might get a small value of bid but to stay safe the lowest i want to get is 20
            if (bid<20): 
                bid=20
                
        else:
            bid=0.4*info['self']['budget']
    
    #if one other player has two paintings of the same type, 
    
    if(len(info["others"])<=2 or (block_player(info,painting,bid)<=(info['self']['budget']//2))):
        bid=block_player(info, painting, bid)
    

    #We will spend all of the money left on a painting if we already purchased two of the same painting
    if(info['self']['item_count'][painting]==2):
        bid=info['self']['budget']
    

    print(f"bidding ${bid} for a", info["items"][round])

    return bid, None


# memorize state between rounds
store = None


def compute_bid(info):
    global store
    if info["cur_round"] == 0:
        # first round, we init the store
        store = {}
        store["mysecret"] = 3
    # update store
    store["mysecret"] += 1
    return round(info["self"]["budget"] * random.random())


if __name__ == "__main__":
    my_name = "matt-" + uuid4().hex[:6]
    server = "tcp://localhost:50018"
    print(my_name)
    play(my_name, server, compute_bid)