import supabase
import json

from flask import current_app


def get_supabase():
    supabase_url = current_app.config["SUPABASE_URL"]
    supabase_api_key = current_app.config["SUPABASE_API_KEY"]
    return supabase.Client(supabase_url, supabase_api_key)


def get_session_list():
    supabase_client = get_supabase()
    data = supabase_client.table("SessionList").select("*").execute()
    return data.data


def update_code_train(listWordTrain):
    supabase_client = get_supabase()
    data = supabase_client.table("WordVector").select("*").execute()
    listWordTrainDB = data.data
    
    code_product_dict = {item["codeProduct"]: item for item in listWordTrainDB}

    for item in listWordTrain:
        code_product = item["codeProduct"]
        vector = item["vector"]

        if code_product in code_product_dict:
            code_product_dict[code_product]["vector"] = vector
        else:
            new_id = (
                max(item["id"] for item in listWordTrainDB) + 1
                if listWordTrainDB
                else 1
            )
            item["id"] = new_id
            listWordTrainDB.append(item)
    
    response = supabase_client.table("WordVector").upsert(listWordTrainDB).execute()
    
    if not response.data:
        return False
    
    return True

def get_popular_product():
    supabase_client = get_supabase()
    response = supabase_client.table("Product").select("*").order("view", desc=True).limit(20).execute()
    return response

def find_word_vector_code(listCode):
    supabase_client = get_supabase()
    checked = True
    for code in listCode:
        result = supabase_client.table("WordVector").select('*').eq("codeProduct", code).execute()
        if len(result.data) > 0:
            checked = False
            break

    return checked

def get_suggest_product(listCode):
    supabase_client = get_supabase()
    response = []
    for code in listCode:
        result = supabase_client.table("Product").select('*').eq("code", code).eq("deleted", 0).execute()
        if len(result.data) > 0:
            response.append(result.data)
    
    return response

def get_brand_product(code):
    supabase_client = get_supabase()
    result = supabase_client.table("Product").select('*').eq("code", code).execute()
    print(result.data)
    productBrandId = result.data[0]['productBrandId']
    response = supabase_client.table("Product").select('*').eq("productBrandId", productBrandId).eq("deleted", 0).limit(20).execute()

    return response.data

def update_session_list(listCode):
    supabase_client = get_supabase()

    listCodeOld = listCode[:-1]
    listCodeStrOld = json.dumps(listCodeOld) 
    result = supabase_client.table("SessionList").select('*').contains("listCodeProduct", listCodeStrOld).order('id', desc=True).execute()

    listCodeStrNew = json.dumps(listCode)
    listCodeJsonNew = json.loads(listCodeStrNew)

    if len(result.data):
        supabase_client.table("SessionList").update({"listCodeProduct": listCodeJsonNew}).eq("id", result.data[0]['id']).execute()
    else:
        data = supabase_client.table("SessionList").select("*").execute()
        listSessionListDB = data.data
        new_id = (
            max(item["id"] for item in listSessionListDB) + 1
            if listSessionListDB
                else 1
        )
        supabase_client.table("SessionList").upsert({"id": new_id, "listCodeProduct": listCodeJsonNew}).execute()

def get_code_train():
    supabase_client = get_supabase()
    response = supabase_client.table("WordVector").select("*").execute()
    return response.data

