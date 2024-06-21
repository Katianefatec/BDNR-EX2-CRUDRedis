from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId

uri = "mongodb+srv://admin:admin@fatec.izfgkb8.mongodb.net/?retryWrites=true&w=majority&appName=Fatec"

client = MongoClient(uri, server_api=ServerApi('1'))
db = client.mercadolivre

def delete_produto():
    mycol_vendedor = db.vendedor
    mycol_produto = db.produto

    print("Vendedores disponíveis:")
    vendedores = list(mycol_vendedor.find())
    for indice, vendedor in enumerate(vendedores, start=1):
        print(f"{indice}: {vendedor['nome']} {vendedor.get('sobrenome', '')}")
   
    escolha_vendedor = input("Escolha o vendedor pelo número (ou digite 'abortar' para cancelar): ")
    if escolha_vendedor.lower() == 'abortar':
        print("Operação cancelada.")
        return
    escolha_vendedor = int(escolha_vendedor) - 1
    vendedor_id = vendedores[escolha_vendedor]['_id']
  
    produtos = list(mycol_produto.find({"vendedor_id": vendedor_id}))
    if not produtos:
        print("Este vendedor não possui produtos cadastrados.")
        return
    print("Produtos deste vendedor:")
    for indice, produto in enumerate(produtos, start=1):
        print(f"{indice}: {produto['nome']} - Valor: {produto['valor']}")

    escolha_produto = input("Escolha o produto pelo número para deletar (ou digite 'abortar' para cancelar): ")
    if escolha_produto.lower() == 'abortar':
        print("Operação cancelada.")
        return
    escolha_produto = int(escolha_produto) - 1
    produto_escolhido = produtos[escolha_produto]
   
    produto_id_str = str(produto_escolhido['_id'])

    mycol_produto.delete_one({"_id": produto_escolhido['_id']})

    db.vendedor.update_one(
    {"_id": vendedor_id},
    {"$pull": {"produtos": {"_id": ObjectId(produto_id_str)}}}
)
    print(f"Deletado o produto {produto_escolhido['nome']}.")
def create_produto():
    mycol = db.produto
    mycol_vendedor = db.vendedor

    print("\nInserindo um novo produto")   
    
    nome = input("Nome: ")
    if nome.lower() == 'abortar':
        print("Operação cancelada.")
        return
    valor = input("Valor: ")
    if valor.lower() == 'abortar':
        print("Operação cancelada.")
        return

    print("Vendedores disponíveis:")
    vendedores = list(mycol_vendedor.find())
    for indice, vendedor in enumerate(vendedores, start=1):
        print(f"{indice}: {vendedor['nome']} {vendedor.get('sobrenome', '')}")

    escolha = input("Escolha o vendedor pelo número (ou digite 'abortar' para cancelar): ")
    if escolha.lower() == 'abortar':
        print("Operação cancelada.")
        return
    try:
        escolha_numerica = int(escolha) - 1  
        if escolha_numerica < 0 or escolha_numerica >= len(vendedores):
            raise ValueError("Número fora do intervalo")
        vendedor_id = vendedores[escolha_numerica]['_id']
        nome_vendedor = vendedores[escolha_numerica]['nome']  
    except (ValueError, IndexError):
        print("Escolha inválida.")
        return

    mydoc = {"nome": nome, "valor": valor, "vendedor_id": vendedor_id,  "nome_vendedor": nome_vendedor}
    x = mycol.insert_one(mydoc)
    print("Produto inserido com ID ", x.inserted_id)

    produto_inserido = mycol.find_one({"_id": x.inserted_id})
    
    mycol_vendedor.update_one(
        {"_id": vendedor_id},
        {"$push": {"produtos": produto_inserido}},
        upsert=True
    )
    print("Vendedor atualizado com o novo produto.")

def update_produto():
    mycol = db.produto
    mycol_vendedor = db.vendedor
    
    print("Vendedores disponíveis:")
    vendedores = list(mycol_vendedor.find())
    for indice, vendedor in enumerate(vendedores, start=1):
        print(f"{indice}: {vendedor['nome']} {vendedor.get('sobrenome', '')}")

    escolha_vendedor = input("Escolha o vendedor pelo número (ou digite 'abortar' para cancelar): ")
    if escolha_vendedor.lower() == 'abortar':
        print("Operação cancelada.")
        return
    escolha_vendedor = int(escolha_vendedor) - 1
    vendedor_id = vendedores[escolha_vendedor]['_id']
   
    produtos = list(mycol.find({"vendedor_id": vendedor_id}))
    print("Produtos deste vendedor:")
    for indice, produto in enumerate(produtos, start=1):
        print(f"{indice}: {produto['nome']} - Valor: {produto['valor']}")
    
    escolha_produto = input("Escolha o produto pelo número (ou digite 'abortar' para cancelar): ")
    if escolha_produto.lower() == 'abortar':
        print("Operação cancelada.")
        return
    escolha_produto = int(escolha_produto) - 1
    produto_escolhido = produtos[escolha_produto]
    
    novo_nome = input("Novo nome (deixe em branco para não alterar ou digite 'abortar' para cancelar): ")
    if novo_nome.lower() == 'abortar':
        print("Operação cancelada.")
        return
    novo_valor = input("Novo valor (deixe em branco para não alterar ou digite 'abortar' para cancelar): ")
    if novo_valor.lower() == 'abortar':
        print("Operação cancelada.")
        return
    update_fields = {}
    if novo_nome:
        update_fields["nome"] = novo_nome
    if novo_valor:
        update_fields["valor"] = novo_valor

    if update_fields:
        mycol.update_one({"_id": produto_escolhido['_id']}, {"$set": update_fields})
               
        produto_atualizado = mycol.find_one({"_id": produto_escolhido['_id']})
               
        db.vendedor.update_one(
            {"_id": vendedor_id, "produtos._id": produto_escolhido['_id']},
            {"$set": {"produtos.$": produto_atualizado}}
        )
        print("Produto atualizado com sucesso.")
    else:
        print("Nenhuma atualização realizada.")

def read_produto(nome):
    global db
    mycol = db.produto
    mycol_vendedor = db.vendedor  

    print("Produtos existentes: ")
    if not len(nome):
        mydoc = mycol.find().sort("nome")
    else:
        myquery = {"nome": nome}
        mydoc = mycol.find(myquery)

    for produto in mydoc:
        
        vendedor_id = produto.get("vendedor_id")
        vendedor = mycol_vendedor.find_one({"_id": vendedor_id})
        nome_vendedor = vendedor["nome"] if vendedor else "Vendedor não encontrado"
        
        
        print(f"Nome: {produto['nome']}, Valor: {produto['valor']}, Vendedor: {nome_vendedor}")
    

