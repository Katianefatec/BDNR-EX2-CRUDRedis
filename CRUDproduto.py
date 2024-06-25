from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from CRUDredis import set_data, get_data, delete_data, conR, converter_objectid_para_string
from bson import ObjectId
import json

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

def read_produto(nome=""):
    global db
    mycol = db.produto
    mycol_vendedor = db.vendedor
    
    print("Produtos no MongoDB:")
    produtos_mongo = list(mycol.find({"nome": nome if nome else {"$regex": ""}}).sort("nome"))
    for produto in produtos_mongo:
        vendedor_id = produto.get("vendedor_id")
        if isinstance(vendedor_id, str):  # Verifica se vendedor_id é string (do Redis)
            vendedor_id = ObjectId(vendedor_id)  # Converte para ObjectId
        vendedor = mycol_vendedor.find_one({"_id": vendedor_id})
        nome_vendedor = vendedor["nome"] if vendedor else "Vendedor não encontrado"
        print(f"- {produto['nome']} (Valor: {produto['valor']}, Vendedor: {nome_vendedor})")

        # Adiciona o produto ao Redis se ele não estiver lá
        produto_redis = get_data(str(produto["_id"]))
        if not produto_redis:
            produto['_id'] = str(produto['_id'])  # Converte o ObjectId para string
            produto["vendedor_id"] = str(vendedor_id)  # Converte o vendedor_id para string
            set_data(str(produto["_id"]), produto)

    print("\nProdutos no Redis:")
    produtos_redis = []
    for chave in conR.scan_iter():
        valor_redis = conR.get(chave)
        try:
            produto_redis = json.loads(valor_redis.decode('utf-8'))
            if '_id' in produto_redis and 'valor' in produto_redis:
                produtos_redis.append(produto_redis)
                # Buscar vendedor no MongoDB (convertendo vendedor_id para ObjectId)
                vendedor_id = ObjectId(produto_redis.get("vendedor_id"))
                vendedor = mycol_vendedor.find_one({"_id": vendedor_id}) if vendedor_id else None
                nome_vendedor = vendedor["nome"] if vendedor else "Vendedor não encontrado"
                print(f"- {produto_redis['nome']} (Valor: {produto_redis['valor']}, Vendedor: {nome_vendedor})")
        except (json.JSONDecodeError, AttributeError):
            pass

    # Produtos apenas no Redis
    produtos_apenas_redis = [p for p in produtos_redis if not any(p['_id'] == str(m['_id']) for m in produtos_mongo)]

    # Lista unificada e numerada para escolha do produto (sem duplicatas)
    print("\nTodos os produtos:")
    todos_produtos = {}   # Movido para fora do bloco condicional
    ids_adicionados = set() # Movido para fora do bloco condicional
    for produto in produtos_mongo + produtos_redis:  # Combina as listas atualizadas
        if produto['_id'] not in ids_adicionados:
            todos_produtos[produto['_id']] = produto
            ids_adicionados.add(produto['_id'])
            vendedor_id = produto.get("vendedor_id")
            if isinstance(vendedor_id, str):
                vendedor_id = ObjectId(vendedor_id)
            vendedor = mycol_vendedor.find_one({"_id": vendedor_id}) if vendedor_id else None
            nome_vendedor = vendedor["nome"] if vendedor else "Vendedor não encontrado"
            print(f"{len(todos_produtos)} - {produto['nome']} (Valor: {produto['valor']}, Vendedor: {nome_vendedor})")

    if produtos_apenas_redis:
        print("\nProdutos apenas no Redis:")
        for produto in produtos_apenas_redis:
            vendedor_id = produto.get("vendedor_id")
            vendedor = mycol_vendedor.find_one({"_id": ObjectId(vendedor_id)}) if vendedor_id else None
            nome_vendedor = vendedor["nome"] if vendedor else "Vendedor não encontrado"
            print(f"- {produto['nome']} (Valor: {produto['valor']}, Vendedor: {nome_vendedor})")

            # Opções para o usuário
            while True:
                acao = input(f"\nO produto {produto['nome']} (ID: {produto['_id']}) está apenas no Redis. Deseja adicionar ao MongoDB (A) ou excluir do Redis (E)? ").strip().upper()
                if acao == 'A':
                    if not mycol.find_one({"_id": ObjectId(produto['_id'])}):
                        produto['_id'] = ObjectId(produto['_id'])
                        mycol.insert_one(produto)
                        print("Produto adicionado ao MongoDB com sucesso!")

                        # Atualiza a lista todos_produtos e remove do Redis
                        todos_produtos[produto['_id']] = produto
                        

                    else:
                        print("Produto já existe no MongoDB.")
                    break
                elif acao == 'E':
                    delete_data(str(produto['_id']))  # Converte o ObjectId para string aqui
                    print("Produto excluído do Redis com sucesso!")
                    break
                else:
                    print("Opção inválida. Digite A ou E.")

   
    








