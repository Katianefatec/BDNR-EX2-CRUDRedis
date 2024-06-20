from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://admin:admin@fatec.izfgkb8.mongodb.net/?retryWrites=true&w=majority&appName=Fatec"


client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre

def delete_usuario(nome, sobrenome):
    
    global db
    mycol = db.usuario
    myquery = {"nome": nome, "sobrenome":sobrenome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o usuário ",mydoc)

def input_with_cancel(prompt, cancel_keyword="CANCELAR"):
    resposta = input(f"{prompt} (digite {cancel_keyword} para abortar): ")
    if resposta.upper() == cancel_keyword:
        print("Criação de usuário cancelada.")
        return None
    return resposta

def create_usuario():
    global db
    mycol = db.usuario
    print("\nInserindo um novo usuário")
    nome = input_with_cancel("Nome")
    if nome is None: return

    sobrenome = input_with_cancel("Sobrenome")
    if sobrenome is None: return
    
    cpf = input_with_cancel("CPF")
    if cpf is None: return

    if mycol.find_one({"cpf": cpf}):
        print("Já existe um usuário cadastrado com este CPF.")
        return
    
    end = []
    while True:
        rua = input_with_cancel("Rua")
        if rua is None: return

        num = input_with_cancel("Num")
        if num is None: return

        bairro = input_with_cancel("Bairro")
        if bairro is None: return

        cidade = input_with_cancel("Cidade")
        if cidade is None: return

        estado = input_with_cancel("Estado")
        if estado is None: return

        cep = input_with_cancel("CEP")
        if cep is None: return

        endereco = {
            "rua": rua,
            "num": num,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "cep": cep
        }
        end.append(endereco)

        key = input_with_cancel("Deseja cadastrar um novo endereço (S/N)?", "N")
        if key is None or key.upper() == 'N': break

    mydoc = {"nome": nome, "sobrenome": sobrenome, "cpf": cpf, "end": end}
    x = mycol.insert_one(mydoc)
    print("Usuário inserido com ID ", x.inserted_id)

def read_usuario(nome):
    
    global db
    mycol = db.usuario
    print("Usuários existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:
            print(x["nome"],x["cpf"])
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)

def update_usuario(nome):
   
    global db
    mycol = db.usuario
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    print("Dados do usuário: ",mydoc)
    nome = input("Mudar Nome:")
    if len(nome):
        mydoc["nome"] = nome

    sobrenome = input("Mudar Sobrenome:")
    if len(sobrenome):
        mydoc["sobrenome"] = sobrenome

    cpf = input("Mudar CPF:")
    if len(cpf):
        mydoc["cpf"] = cpf

    newvalues = { "$set": mydoc }
    mycol.update_one(myquery, newvalues)