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
                print("Erro ao criar usuário. Por favor, tente novamente.")
                return
            print("Usuário cadastrado com sucesso.")
        else:
            print("Não é possível continuar com a compra sem um usuário cadastrado.")
            return
    endereco = db.endereco.find_one({"usuario_id": cpf_usuario})
    if not endereco:
        print("Endereço não encontrado. Por favor, cadastre um endereço para continuar.")
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
    print("\nSelecione o endereço de entrega:")
    for i, endereco in enumerate(enderecos, start=1):
        print(f"{i} - {endereco['rua']}, {endereco['num']}, {endereco['bairro']}, {endereco['cidade']}, {endereco['estado']}, CEP: {endereco['cep']}")

    while True:
        endereco_selecionado = input("Digite o número do endereço selecionado: ")
        try:
            endereco_selecionado = int(endereco_selecionado)
            if 1 <= endereco_selecionado <= len(enderecos):
                endereco_entrega = enderecos[endereco_selecionado - 1]
                print("Endereço selecionado para entrega:")
                print(f"{endereco_entrega['rua']}, {endereco_entrega['num']}, {endereco_entrega['bairro']}, {endereco_entrega['cidade']}, {endereco_entrega['estado']}, CEP: {endereco_entrega['cep']}")

                compra = {
                    "cpf_usuario": cpf_usuario,
                    "produtos": carrinho,
                    "endereco_entrega": endereco_entrega,
                    "valor_total": total
                }
                db.compra.insert_one(compra)

                # Adiciona a compra ao usuário
                if 'compras' not in usuario:
                    usuario['compras'] = [compra]
                else:
                    usuario['compras'].append(compra)
                db.usuario.update_one({"cpf": cpf_usuario}, {"$set": {"compras": usuario['compras']}})

                print("Compra concluída com sucesso!")
                return carrinho
            else:
                print("Número de endereço inválido.")
        except ValueError:
            print("Entrada inválida. Digite um número válido.")

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