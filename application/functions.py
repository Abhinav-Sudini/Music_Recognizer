from django.db import connection

def execute_sql(query):
    out = []
    with connection.cursor() as cursor:
        cursor.execute(query)
        out=dictfetchall(cursor)
    return out

def execute_raw_sql(query):
    out = []
    with connection.cursor() as cursor:
        cursor.execute(query)
        out=cursor.fetchall()
    return out

def make_dict(hashes):
    out_dic = {}
    for hsh,off in hashes:
        if hsh not in out_dic:
            out_dic[hsh] = []
        
        out_dic[hsh].append(off)
    
    return out_dic

def SmallestDifference(A, B):
    a = 0
    b = 0
    m = len(A)
    n = len(B)
    result = 10000000
    while (a < m and b < n):
     
        if ( B[b] - A[a]< result and A[a] <= B[b]):
            result =  B[b]-A[a] 
 
        # Move Smaller Value
        if (A[a] < B[b]):
            a += 1
 
        else:
            b += 1
    # return final sma result
    return result 

def dictfetchall(cursor):
    """
    Return all rows from a cursor as a dict.
    Assume the column names are unique.
    """
    if cursor.description == None:
        return []
    
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]