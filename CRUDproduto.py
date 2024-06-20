from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://admin:admin@fatec.izfgkb8.mongodb.net/?retryWrites=true&w=majority&appName=Fatec"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre

def delete_produto(nome):
    #Delete
    global db
    mycol = db.produto
    myquery = {"nome": nome}
    mydoc = mycol.delete_one(myquery)
    print("Deletado o produto",mydoc)

def create_produto():
    #Insert
    global db
    mycol = db.produto
    print("\nInserindo um novo produto")
    nome = input("Nome: ")
    valor= input("Valor: ")

    
    mydoc = { "nome": nome, "valor": valor}
    x = mycol.insert_one(mydoc)
    print("Documento inserido com ID ",x.inserted_id)

def read_produto(nome):
    #Read
    global db
    mycol = db.produto
    print("Produtos existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
        for x in mydoc:
            print(x["nome"],x["valor"])
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)
        for x in mydoc:
            print(x)

def update_produto(nome):
    #Read
    global db
    mycol = db.produto
    myquery = {"nome": nome}
    mydoc = mycol.find_one(myquery)
    print("Dados do produto: ",mydoc)
    nome = input("Mudar nome:")
    if len(nome):
        mydoc["nome"] = nome

    valor = input("Mudar valor:")
    if len(valor):
        mydoc["valor"] = valor
    
    newvalues = { "$set": mydoc }
    mycol.update_one(myquery, newvalues)