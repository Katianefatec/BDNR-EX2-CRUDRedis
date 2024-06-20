from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://admin:admin@fatec.izfgkb8.mongodb.net/?retryWrites=true&w=majority&appName=Fatec"


client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre

def delete_vendedor(nome):
    
    global db
    mycol = db.vendedor
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
    global db
    mycol = db.vendedor
    print("\nInserindo um novo vendedor")

    nome = input_with_cancel("Nome")
    if nome is None: return

    sobrenome = input_with_cancel("Sobrenome")
    if sobrenome is None: return

    cnpj = input_with_cancel("CNPJ")
    if cnpj is None: return

    cpf = input_with_cancel("CPF")
    if cpf is None: return

    if mycol.find_one({"cpf": cpf}):
        print("Já existe um vendedor cadastrado com este CPF.")
        return
    if mycol.find_one({"cnpj": cnpj}):
        print("Já existe um vendedor cadastrado com este CNPJ.")
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

    mydoc = {"nome": nome, "sobrenome": sobrenome, "cnpj": cnpj, "cpf": cpf, "end": end}
    x = mycol.insert_one(mydoc)
    print("Vendedor inserido com ID ", x.inserted_id)

def read_vendedor(nome):
   
    global db
    mycol = db.vendedor
    print("Vendedores existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:
            print(x["nome"],x["cnpj"])
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)

def update_vendedor(nome):
    
    global db
    mycol = db.vendedor
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    print("Dados do usuário: ",mydoc)
    nome = input("Mudar Nome:")
    if len(nome):
        mydoc["nome"] = nome

    sobrenome = input("Mudar Sobrenome:")
    if len(sobrenome):
        mydoc["sobrenome"] = sobrenome

    cnpj = input("Mudar CNPJ:")
    if len(cnpj):
        mydoc["cnpj"] = cnpj

    newvalues = { "$set": mydoc }
    mycol.update_one(myquery, newvalues)