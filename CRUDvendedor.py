from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://admin:admin@fatec.izfgkb8.mongodb.net/?retryWrites=true&w=majority&appName=Fatec"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre

def delete_vendedor(nome):
    #Delete
    global db
    mycol = db.vendedor
    myquery = {"nome": nome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o vendedor",mydoc)

def create_vendedor():
    #Insert
    global db
    mycol = db.vendedor
    print("\nInserindo um novo usuário")
    nome = input("Nome: ")
    sobrenome = input("Sobrenome: ")
    cnpj = input("CNPJ: ")
    key = 1
    end = []
    while (key != 'N'):
        rua = input("Rua: ")
        num = input("Num: ")
        bairro = input("Bairro: ")
        cidade = input("Cidade: ")
        estado = input("Estado: ")
        cep = input("CEP: ")
        endereco = {        #isso nao eh json, isso é chave-valor, eh um obj
            "rua":rua,
            "num": num,
            "bairro": bairro,
            "cidade": cidade,
            "estado": estado,
            "cep": cep
        }
        end.append(endereco) #estou inserindo na lista
        key = input("Deseja cadastrar um novo endereço (S/N)? ")
    mydoc = { "nome": nome, "sobrenome": sobrenome, "cnpj": cnpj, "end": end }
    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ",x.inserted_id)

def read_vendedor(nome):
    #Read
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
    #Read
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