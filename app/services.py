import jwt
import ast
import base64
import numpy as np
from flask import current_app, jsonify
from gensim.models import Word2Vec

from .models import *


def decode_token(self):
    tokenKey = current_app.config["TOKEN_KEY"]
    try:
        payload = jwt.decode(self, tokenKey, algorithms=["HS256"])
        roles = payload.get("roles", [])
        if "admin" in roles or "product" in roles:
            return True
        return False
    except Exception as e:
        print(e)
        return False


def trainWord2Vec(data):
    token = data.get("token")
    checkRole = decode_token(token)

    if checkRole:
        purchases_train = []
        sessionList = get_session_list()
        for i in sessionList:
            purchases_train.append(i.get("listCodeProduct"))

        model = Word2Vec(window = 10, sg = 1, hs = 0,
                        negative = 10, # for negative sampling
                        alpha=0.03, min_alpha=0.0007,
                        seed = 14)

        model.build_vocab(purchases_train, progress_per=200)

        model.train(purchases_train, total_examples = model.corpus_count,
                    epochs=10, report_delay=1)
        
        listWordTrain = []
        for word in model.wv.index_to_key:
            vector = model.wv[word]
            
            # Chuyển đổi vector thành chuỗi Base64
            vector_base64 = base64.b64encode(vector.tobytes()).decode("utf-8")
            listWordTrain.append({"codeProduct": word, "vector": vector_base64})

        checkUpdate = update_code_train(listWordTrain)

        if checkUpdate:
            return jsonify({"ok": True, "msg": "Train DB thành công"}), 200

        return jsonify({"ok": False, "msg": "Train DB thất bại có lỗi"}), 400

    return jsonify({"ok": False, "msg": "Không đủ quyền hoặc hết phiên vui lòng đăng nhập lại"}), 403


def getListCodeProductView(data):
    sessionProducts = data.get("product-view")

    checked = find_word_vector_code(sessionProducts)
    if checked:
        popularProduct = get_popular_product()
        data = popularProduct.data
        return jsonify({"ok":True, "data": data, "msg": "Success"}), 200

    word_vectors = get_code_train()

    # Chuyển sang dạng nhị phân rồi sang  NumPy
    words = [entry.get("codeProduct") for entry in word_vectors]
    vectors = [
        np.frombuffer(base64.b64decode(entry.get("vector")), dtype=np.float32)
        for entry in word_vectors
    ]
    vectors = [np.frombuffer(vector, dtype=np.float32) for vector in vectors]
    
    #Xet model
    model = Word2Vec(
        sentences=words,
        window=10,
        sg=1,
        hs=0,
        negative=10,
        alpha=0.03,
        min_alpha=0.0007,
        seed=14,
    )

    model.wv[words] = vectors
    model.init_sims(replace=True)

    # Liệt kê san phẩm gợi ý
    def similar_products(v, n=21):
        ms = model.wv.most_similar([v], topn=n + 1)

        new_ms = []
        for j in ms:
            print(j)
            new_ms.append(j[0])

        return new_ms

    # Tính vector trung bình
    def aggregate_vectors(products):
        product_vec = []
        for i in products:
            try:
                product_vec.append(model.wv.get_vector(i))
            except KeyError:
                continue
        # Tính giá trị trung bình
        return np.mean(product_vec, axis=0)

    listSuggest = similar_products(aggregate_vectors(sessionProducts))
    
    response = get_suggest_product(listSuggest)

    return jsonify({"ok": True, "data": response, "msg": "Success"}), 200


def getListCodeProductSimilar(data):
    viewProducts = data.get("product-view")
    getCode = data.get("product-code")
    codeProducts =getCode[0]
    
    #Cap nhat session
    if len(viewProducts) >=5:
        update_session_list(viewProducts)
    
    word_vectors = get_code_train()
    #Check san pham da duoc train chua
    found = True
    for item in word_vectors:
        if item['codeProduct'] == codeProducts:
            found = False
            break

    #Chua train lay cung hang
    if found:
        listBrandProduct = get_brand_product(codeProducts)
        return jsonify({"ok": True, "data": listBrandProduct, "msg": "Success"}), 200

    # Chuyển sang dạng nhị phân rồi sang  NumPy
    words = [entry.get("codeProduct") for entry in word_vectors]
    vectors = [
        np.frombuffer(base64.b64decode(entry.get("vector")), dtype=np.float32)
        for entry in word_vectors
    ]
    vectors = [np.frombuffer(vector, dtype=np.float32) for vector in vectors]
    
    #Xet model
    model = Word2Vec(
        sentences=words,
        window=10,
        sg=1,
        hs=0,
        negative=10,
        alpha=0.03,
        min_alpha=0.0007,
        seed=14,
    )

    model.wv[words] = vectors
    model.init_sims(replace=True)

    # Liệt kê san phẩm gợi ý
    def similar_products(v, n=21):
        ms = model.wv.most_similar([v], topn=n + 1)

        new_ms = []
        for j in ms:
            print(j)
            new_ms.append(j[0])

        return new_ms


    listSuggest = similar_products(model.wv.get_vector(codeProducts))
    response = get_suggest_product(listSuggest)

    return jsonify({"ok": True, "data": response, "msg": "Success"}), 200
