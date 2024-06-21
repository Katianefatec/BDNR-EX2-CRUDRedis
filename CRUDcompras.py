from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from CRUDusuario import create_usuario

uri = "mongodb+srv://admin:admin@fatec.izfgkb8.mongodb.net/?retryWrites=true&w=majority&appName=Fatec"

client = MongoClient(uri, server_api=ServerApi('1'))
global db
db = client.mercadolivre

def adicionar_compra_usuario(cpf_usuario, compra):
    db.usuario.update_one(
        {"cpf": cpf_usuario}, 
        {"$push": {"compras": compra}}
    )

def cadastrar_endereco(cpf_usuario):
    print("Cadastro de novo endereço.")
    rua = input("Rua: ")
    numero = input("Número: ")
    bairro = input("Bairro: ")
    cidade = input("Cidade: ")
    estado = input("Estado: ")
    cep = input("CEP: ")

    novo_endereco = {
        "rua": rua,
        "num": numero,
        "bairro": bairro,
        "cidade": cidade,
        "estado": estado,
        "cep": cep
    }

    db.usuario.update_one({"cpf": cpf_usuario}, {"$push": {"end": novo_endereco}})

    print("Endereço cadastrado com sucesso.")
    return novo_endereco


def realizar_compra(cpf_usuario):
    global db
    usuario = db.usuario.find_one({"cpf": cpf_usuario})
    if not usuario:
        print("Usuário não encontrado. Deseja realizar o cadastro? (S/N)")
        resposta = input().upper()
        if resposta == 'S':
            cpf_usuario = create_usuario()              
            usuario = db.usuario.find_one({"cpf": cpf_usuario})            
            if not usuario:
                print("Erro: Usuário não encontrado após o cadastro.")
                return
            print("Usuário cadastrado com sucesso.")
        else:
            print("Não é possível continuar com a compra sem um usuário cadastrado.")
            return
    carrinho = []

    print("Lista de produtos disponíveis:")
    produtos = list(db.produto.find())
    for i, produto in enumerate(produtos, start=1):
        vendedor = db.vendedor.find_one({"cpf": produto.get("vendedor")})
        if vendedor:
            print(f"{i} - ID: {produto['_id']} | Produto: {produto['nome']} | Vendedor: {vendedor['nome']} | valor: {produto['valor']}")
        else:
            print(f"{i} - ID: {produto['_id']} | Produto: {produto['nome']} | Vendedor: Não disponível | valor: {produto['valor']}")

    while True:
        id_produto = input("\nDigite o número do produto que deseja adicionar ao carrinho (ou 'C' para concluir): ")
        if id_produto.upper() == 'C':
            break

        try:
            id_produto = int(id_produto)
            if id_produto < 1 or id_produto > len(produtos):
                raise ValueError
            produto = produtos[id_produto - 1]
            carrinho.append(produto)
            print(f"Produto '{produto['nome']}' adicionado ao carrinho.")
        except ValueError:
            print("Erro: Produto inválido. Digite um número válido.")

    if not carrinho:
        print("Carrinho vazio. Operação cancelada.")
        return

    total = sum(float(produto["valor"]) for produto in carrinho)
    print(f"\nValor total do carrinho: R${total:.2f}")

    confirmar = input("\nDeseja confirmar a compra (S/N)? ").upper()
    if confirmar != "S":
        print("Compra cancelada.")
        return carrinho

    enderecos = usuario.get("end", [])
    if not enderecos:
        print("Nenhum endereço cadastrado. Deseja cadastrar um novo endereço? (S/N)")
        resposta = input().upper()
        if resposta == 'S':
            endereco_entrega = cadastrar_endereco(cpf_usuario)  
            enderecos = [endereco_entrega]
        else:
            print("Não é possível continuar com a compra sem um endereço de entrega.")
            return

    print("\nSelecione o endereço de entrega:")
    for i, endereco in enumerate(enderecos, start=1):
        print(f"{i} - {endereco['rua']}, {endereco['num']}, {endereco['bairro']}, {endereco['cidade']}, {endereco['estado']}, CEP: {endereco['cep']}")

    while True:
        endereco_selecionado = input("Digite o número do endereço selecionado (ou 'N' para cadastrar um novo): ")
        if endereco_selecionado.upper() == 'N':
            endereco_entrega = cadastrar_endereco(cpf_usuario)
            break
        try:
            endereco_selecionado = int(endereco_selecionado)
            if 1 <= endereco_selecionado <= len(enderecos):
                endereco_entrega = enderecos[endereco_selecionado - 1]
                break
            else:
                print("Número de endereço inválido.")
        except ValueError:
            print("Entrada inválida. Digite um número válido ou 'N' para cadastrar um novo endereço.")

   
    print("\nConfirmação da Compra:")
    for produto in carrinho:
        print(f"Produto: {produto['nome']} - Valor: R${produto['valor']}")
    print(f"Valor total do carrinho: R${total:.2f}")
    print("Endereço de entrega selecionado:")
    print(f"{endereco_entrega['rua']}, {endereco_entrega['num']}, {endereco_entrega['bairro']}, {endereco_entrega['cidade']}, {endereco_entrega['estado']}, CEP: {endereco_entrega['cep']}")
    
    confirmar_compra = input("\nConfirmar compra? (S/N): ").upper()
    if confirmar_compra != "S":
        print("Compra cancelada.")
        return

    else:
        print("Compra realizada com sucesso.")
        for produto in carrinho:
            if 'vendedor_id' in produto:  
                vendedor_id = produto['vendedor_id']
                vendedor = db.vendedor.find_one({"_id": vendedor_id})

                if vendedor:
                    venda = {
                        "id_produto": produto['_id'],
                        "nome_produto": produto['nome'],
                        "valor_venda": produto['valor'],
                        "cpf_comprador": cpf_usuario,
                        "cpf_vendedor": vendedor['cpf']
                    }
                    
                    db.vendedor.update_one(
                        {"_id": vendedor_id},
                        {"$push": {"vendas": venda}}
                    )

                    
                    db.produto.delete_one({"_id": produto['_id']})
    

    produtos_compra = [{
    "nome": produto['nome'],
    "valor": produto['valor']
    } for produto in carrinho]
    
    compra = {
        "cpf_usuario": cpf_usuario,
        "produtos": produtos_compra,
        "endereco_entrega": endereco_entrega,
        "valor_total": total
    }
    
    db.compra.insert_one(compra)
    
    if 'compras' not in usuario:
        usuario['compras'] = [compra]
    else:
        usuario['compras'].append(compra)
    db.usuario.update_one({"cpf": cpf_usuario}, {"$set": {"compras": usuario['compras']}})

    
    carrinho.clear()
    return carrinho

def ver_compras_realizadas(cpf_usuario):
    global db
    print("Compras realizadas pelo usuário:")
    
    compras_realizadas = db.compra.find({"cpf_usuario": cpf_usuario})
    
    count = 0

    for compra in compras_realizadas:
        count += 1
        print(f"ID da Compra: {compra['_id']}")
        print("Produtos:")
        for produto in compra['produtos']:
            print(f"   Nome do Produto: {produto['nome']} | valor: {produto['valor']}")
        print(f"Endereço de Entrega: {compra['endereco_entrega']}")
        print("----")
    
    if count == 0:
        print("Nenhuma compra encontrada para este usuário.")