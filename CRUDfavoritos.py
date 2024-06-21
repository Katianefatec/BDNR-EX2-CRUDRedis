from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId

from CRUDusuario import read_usuario

uri = "mongodb+srv://admin:admin@fatec.izfgkb8.mongodb.net/?retryWrites=true&w=majority&appName=Fatec"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre

def adicionar_favorito(cpf_usuario, id_produto):
    global db
    produto = db.produto.find_one({"_id": id_produto})
    if not produto:
        print("Erro: Produto não encontrado.")
        return
    db.usuario.update_one({"cpf": cpf_usuario}, {"$push": {"favoritos": id_produto}})
    print("Produto adicionado aos favoritos do usuário com sucesso!")

def produto_existe(id_produto):
    global db
    return db.produto.find_one({"_id": id_produto}) is not None

def visualizar_favoritos(cpf_usuario):
    global db
    usuario = db.usuario.find_one({"cpf": cpf_usuario})
    if not usuario or "favoritos" not in usuario:
        print("O usuário não possui favoritos.")
        return
    
    favoritos_validos = [id_produto for id_produto in usuario["favoritos"] if produto_existe(id_produto)]
   
    db.usuario.update_one({"cpf": cpf_usuario}, {"$set": {"favoritos": favoritos_validos}})

    print("Favoritos do usuário:")
    for id_produto in favoritos_validos:  
        produto = db.produto.find_one({"_id": id_produto})
        if produto:
            print("Nome do Produto:", produto["nome"])
            print("Valor:", produto["valor"])
            nome_vendedor = produto.get("nome_vendedor")
            if nome_vendedor:
                vendedor = db.vendedor.find_one({"nome": nome_vendedor})
                if vendedor:
                    print("Vendedor:", vendedor["nome"])
                else:
                    print("Vendedor: Não encontrado")
            else:
                print("Nome do vendedor não disponível para o produto:", produto["nome"])
            print()
        else:
            print("Erro inesperado: Produto não encontrado para o favorito com ID:", id_produto)  


def excluir_favorito(cpf_usuario):
    global db
    usuario = db.usuario.find_one({"cpf": cpf_usuario})
    
    if not usuario or "favoritos" not in usuario or not usuario["favoritos"]:
        print("O usuário não possui favoritos.")
        return
    
    print("Favoritos:")
    for i, id_produto in enumerate(usuario["favoritos"], start=1):
        print(f"{i}. {id_produto}")

    while True:
        try:
            indice = int(input("Digite o número do favorito que deseja excluir (ou '0' para cancelar): "))
            if indice == 0:
                print("Operação cancelada.")
                return
            elif 1 <= indice <= len(usuario["favoritos"]):
                break
            else:
                print("Número de favorito inválido. Digite um número válido.")
        except ValueError:
            print("Entrada inválida. Digite um número válido.")

    id_produto_selecionado = usuario["favoritos"][indice - 1]
    db.usuario.update_one({"cpf": cpf_usuario}, {"$pull": {"favoritos": id_produto_selecionado}})
    print("Favorito removido com sucesso!")



def listar_produtos():
    global db
    print("Lista de produtos:")
    produtos = list(db.produto.find())
    for i, produto in enumerate(produtos, start=1):
        vendedor = db.vendedor.find_one({"cpf": produto.get("vendedor")})
        if vendedor:
            print(f"{i} - ID: {produto['_id']} | Produto: {produto['nome']} | Vendedor: {vendedor['nome']} | valor: {produto['valor']}")
        else:
            print(f"{i} - ID: {produto['_id']} | Produto: {produto['nome']} | Vendedor: Não disponível | valor: {produto['valor']}")

def adicionarnovo_favorito():
    global db
    while True:
        cpf_usuario = input("Digite seu CPF: ")
        if not db.usuario.find_one({"cpf": cpf_usuario}):
            print("Erro: CPF de usuário não encontrado.")
            break
        
        produtos = list(db.produto.find())
        listar_produtos()

        id_produto = input("Digite o número do produto que deseja adicionar aos favoritos (ou 'V' para voltar): ")
        if id_produto.upper() == 'V':
            return

        try:
            id_produto = int(id_produto)
            if id_produto < 1 or id_produto > len(produtos):
                raise ValueError
        except ValueError:
            print("Erro: Entrada inválida. Digite um número válido.")
            continue

        produto_selecionado = produtos[id_produto - 1]
        adicionar_favorito(cpf_usuario, produto_selecionado["_id"])

        adicionar_mais = input("Deseja adicionar mais produtos aos favoritos (S/N)? ").upper()
        if adicionar_mais != "S":
            break

