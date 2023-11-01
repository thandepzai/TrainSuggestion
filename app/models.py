import supabase

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


def get_code_train():
    supabase_client = get_supabase()
    response = supabase_client.table("WordVector").select("*").execute()
    return response.data
