from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://admin:admin@fatec.izfgkb8.mongodb.net/?retryWrites=true&w=majority&appName=Fatec"


client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre
mycol = db.vendedor

def delete_vendedor(nome):
    
    global db   
    myquery = {"nome": nome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o vendedor",mydoc)

def input_with_cancel(prompt, cancel_keyword="CANCELAR"):
    resposta = input(f"{prompt} (digite {cancel_keyword} para abortar): ")
    if resposta.upper() == cancel_keyword:
        print("Criação de vendedor cancelada.")
        return None
    return resposta

def create_vendedor():
    print("\nInserindo um novo vendedor")
    nome = input_with_cancel("Nome")
    if nome is None: return

    sobrenome = input_with_cancel("Sobrenome")
    if sobrenome is None: return
    
    cpf = input_with_cancel("CPF")
    if cpf is None or cpf.strip() == "":  
        print("CPF é obrigatório.")
        return        
    
    if mycol.find_one({"cpf": cpf}):
        print("Já existe um vendedor cadastrado com este CPF.")
        return
    
    cnpj = input_with_cancel("CNPJ")
    if cnpj is None: return
    
    if mycol.find_one({"cnpj": cnpj}):
        print("Já existe um vendedor cadastrado com este CNPJ.")
        return
            
    end = []
    while True:
        rua = input_with_cancel("Rua")
        if rua is None: break  

        num = input_with_cancel("Num")
        if num is None: break

        bairro = input_with_cancel("Bairro")
        if bairro is None: break

        cidade = input_with_cancel("Cidade")
        if cidade is None: break

        estado = input_with_cancel("Estado")
        if estado is None: break

        cep = input_with_cancel("CEP")
        if cep is None: break

        endereco = {"rua": rua, "num": num, "bairro": bairro, "cidade": cidade, "estado": estado, "cep": cep}
        end.append(endereco)

        continuar = input("Deseja cadastrar um novo endereço (S/N)? ").strip().upper()
        if continuar != 'S': break
    

    mydoc = {"nome": nome, "sobrenome": sobrenome, "cnpj": cnpj, "cpf": cpf, "end": end}
    x = mycol.insert_one(mydoc)
    print("Vendedor inserido com ID ", x.inserted_id)
    return mydoc["cpf"]

def read_vendedor(nome):
    global db
    mycol = db.vendedor
    print("Vendedores existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:            
            produtos = x.get("produtos", "Nenhum produto cadastrado")
            print(x["nome"], x.get("cnpj", "CNPJ não cadastrado"), produtos)
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            produtos = x.get("produtos", "Nenhum produto cadastrado")
            print(x["nome"], x.get("cnpj", "CNPJ não cadastrado"), produtos)

def update_vendedor(nome):
    global db
    mycol = db.vendedor
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    if not mydoc:
        print("Vendedor não encontrado.")
        return
    print("Dados do usuário: ", mydoc)

    novo_nome = input("Mudar Nome (deixe em branco para manter): ")
    if novo_nome:
        mydoc["nome"] = novo_nome

    novo_sobrenome = input("Mudar Sobrenome (deixe em branco para manter): ")
    if novo_sobrenome:
        mydoc["sobrenome"] = novo_sobrenome

    novo_cnpj = input("Mudar CNPJ (deixe em branco para manter): ")
    if novo_cnpj:
        mydoc["cnpj"] = novo_cnpj

    novo_cpf = input("Mudar CPF (deixe em branco para manter): ")
    if novo_cpf:        
        if mycol.find_one({"cpf": novo_cpf, "_id": {"$ne": mydoc["_id"]}}):
            print("Já existe um vendedor cadastrado com este CPF.")
            return
        else:
            mydoc["cpf"] = novo_cpf

    newvalues = {"$set": mydoc}
    mycol.update_one(myquery, newvalues)
    print("Vendedor atualizado com sucesso.")