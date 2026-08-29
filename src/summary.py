from collections import defaultdict

def build_summary(results):
    total=0.0; stores=defaultdict(float); n=0
    for r in results:
        amount=r.get('total_amount',{}).get('value')
        if isinstance(amount,(int,float)):
            total+=amount; n+=1
            store=r.get('store_name',{}).get('value') or 'Unknown'
            stores[store]+=amount
    return {'total_spend':round(total,2),'number_of_transactions':n,'spend_per_store':{k:round(v,2) for k,v in sorted(stores.items(),key=lambda kv:-kv[1])}}
