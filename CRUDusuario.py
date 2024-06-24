import json
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from CRUDredis import set_data, get_data, delete_data, conR, converter_objectid_para_string
from bson import ObjectId

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
    usuario = db.usuario.find_one({"nome": nome, "sobrenome": sobrenome})
    if usuario:
        delete_data(usuario["cpf"])
        print("Dados do usuário deletados no Redis com sucesso!")

def input_with_cancel(prompt, cancel_keyword="CANCELAR", cancel_on_n_for_specific_prompt=False):
    resposta = input(f"{prompt} (digite {cancel_keyword} para abortar): ")
    if resposta.upper() == cancel_keyword:
        print("Operação cancelada.")
        return None
    if cancel_on_n_for_specific_prompt and resposta.upper() == 'N':
        return resposta
    return resposta

def create_usuario():
    print("\nInserindo um novo usuário")
    nome = input_with_cancel("Nome")
    if nome is None: return

    sobrenome = input_with_cancel("Sobrenome")
    if sobrenome is None: return
    
    cpf = input_with_cancel("CPF")
    if cpf is None or cpf.strip() == "":  
        print("CPF é obrigatório.")
        return

    if db.usuario.find_one({"cpf": cpf}):
        print("Já existe um usuário cadastrado com este CPF.")
        return
    
    end = []
    while True:
        rua = input_with_cancel("Rua", cancel_on_n_for_specific_prompt=True)
        if rua is None: break  

        num = input_with_cancel("Num", cancel_on_n_for_specific_prompt=True)
        if num is None: break

        bairro = input_with_cancel("Bairro", cancel_on_n_for_specific_prompt=True)
        if bairro is None: break

        cidade = input_with_cancel("Cidade", cancel_on_n_for_specific_prompt=True)
        if cidade is None: break

        estado = input_with_cancel("Estado", cancel_on_n_for_specific_prompt=True)
        if estado is None: break

        cep = input_with_cancel("CEP", cancel_on_n_for_specific_prompt=True)
        if cep is None: break

        endereco = {"rua": rua, "num": num, "bairro": bairro, "cidade": cidade, "estado": estado, "cep": cep}
        end.append(endereco)

        continuar = input("Deseja cadastrar um novo endereço (S/N)? ").strip().upper()
        if continuar != 'S': break
    

    mydoc = {"nome": nome, "sobrenome": sobrenome, "cpf": cpf, "end": end}
    x = db.usuario.insert_one(mydoc)
    print("Usuário inserido com ID ", x.inserted_id)
    usuario = db.usuario.find_one({"_id": x.inserted_id})

    # Converter _id para string antes de armazenar no Redis
    usuario_convertido = converter_objectid_para_string(usuario)
    set_data(usuario_convertido['cpf'], usuario_convertido)

    return mydoc["cpf"]
    

def read_usuario(cpf=None):  
    global db
    
    if cpf:  
        usuario_redis = get_data(cpf)
        if usuario_redis:
            print(usuario_redis)
    else:
        # Usuários do Redis
        print("\nUsuários no Redis:")
        for chave in conR.scan_iter():  # Iterar pelas chaves do Redis
            valor_redis = conR.get(chave)
            try:
                usuario_redis = json.loads(valor_redis.decode('utf-8'))
                print(f"- {usuario_redis.get('nome', 'N/A')} {usuario_redis.get('sobrenome', 'N/A')} (CPF: {chave.decode('utf-8')})")
            except (json.JSONDecodeError, AttributeError):
                print(f"- Erro ao carregar dados do usuário com CPF {chave.decode('utf-8')}: Valor inválido no Redis")


        
        usuarios_mongo = list(db.usuario.find())
        total_usuarios = len(usuarios_mongo)
        if total_usuarios > 0:
            print("\nUsuários no MongoDB:")
            for index, usuario in enumerate(usuarios_mongo):
                print(f"{index + 1} - {usuario['nome']} {usuario['sobrenome']} (CPF: {usuario['cpf']})")
        else:
            print("\nNenhum usuário encontrado no MongoDB.")
            print("Usuários encontrados no Redis: ", len(conR.scan_iter()))

        if total_usuarios > 0:
            print("\nUsuários cadastrados:")
            for index, usuario in enumerate(usuarios_mongo):
                print(f"{index + 1} - {usuario['nome']} {usuario['sobrenome']}")

            while True:
                try:
                    escolha = int(input("\nDigite o número do usuário para ver detalhes (ou 0 para cancelar): "))
                    if escolha == 0:
                        break

                    if 1 <= escolha <= total_usuarios:
                        usuario_escolhido = usuarios_mongo[escolha - 1]  
                        print("\nDetalhes do usuário:")
                        print(usuario_escolhido)
                        break
                    else:
                        print("Escolha inválida. Tente novamente.")
                except ValueError:
                    print("Digite um número válido.")
        else:
            print("Nenhum usuário encontrado.")

def update_usuario():
    global db
    usuarios_mongo = list(db.usuario.find())
    total_usuarios_mongo = len(usuarios_mongo)

    if total_usuarios_mongo > 0:
        print("\nUsuários cadastrados no MongoDB:")
        for index, usuario in enumerate(usuarios_mongo):
            print(f"{index + 1} - {usuario['nome']} {usuario['sobrenome']}")
    else:
        print("\nNenhum usuário encontrado no MongoDB.")

    # Listar usuários do Redis se não houver no MongoDB ou se o usuário não for encontrado
    print("\nUsuários cadastrados no Redis:")
    usuarios_redis = []
    for index, chave in enumerate(conR.scan_iter()):  # Adicionamos enumerate aqui
        valor_redis = conR.get(chave)
        try:
            usuario_redis = json.loads(valor_redis.decode('utf-8'))
            usuarios_redis.append(usuario_redis)
            print(f"{index + 1} - {usuario_redis.get('nome', 'N/A')} {usuario_redis.get('sobrenome', 'N/A')} (CPF: {chave.decode('utf-8')})")
        except (json.JSONDecodeError, AttributeError):
            print(f"- Erro ao carregar dados do usuário com CPF {chave.decode('utf-8')}: Valor inválido no Redis")

    total_usuarios_redis = len(usuarios_redis)
    if total_usuarios_redis == 0 and total_usuarios_mongo == 0:
        print("Nenhum usuário encontrado no Redis.")
        return

    # Escolher usuário para atualizar/excluir (MongoDB ou Redis)
    while True:
        try:
            escolha = int(input("\nDigite o número do usuário para atualizar/excluir (ou 0 para cancelar): "))
            if escolha == 0:
                return

            if 1 <= escolha <= total_usuarios_mongo:
                usuario_escolhido = usuarios_mongo[escolha - 1]
                usuario_no_mongo = True  # Flag para indicar que o usuário está no MongoDB
            elif 1 <= escolha <= total_usuarios_mongo + total_usuarios_redis:
                usuario_escolhido = usuarios_redis[escolha - total_usuarios_mongo - 1]
                usuario_no_mongo = False  # Flag para indicar que o usuário está no Redis
            else:
                print("Escolha inválida. Tente novamente.")
                continue

            print("\nDados do usuário:", usuario_escolhido)

            nome = input("Mudar Nome (deixe em branco para manter): ")
            if nome:
                usuario_escolhido["nome"] = nome

            sobrenome = input("Mudar Sobrenome (deixe em branco para manter): ")
            if sobrenome:
                usuario_escolhido["sobrenome"] = sobrenome

            cpf = input("Mudar CPF (deixe em branco para manter): ")
            if cpf:
                if db.usuario.find_one({"cpf": cpf}):
                    print("CPF já cadastrado. Tente novamente.")
                    continue
                usuario_escolhido["cpf"] = cpf

            # Obter o CPF antigo antes de atualizar
            cpf_antigo = usuario_escolhido["cpf"]

            # Atualiza/insere o usuário no MongoDB
            if usuario_no_mongo:
                db.usuario.update_one({"_id": usuario_escolhido["_id"]}, {"$set": usuario_escolhido})
            else:
                # Se o usuário não existir no MongoDB, insere os dados
                usuario_escolhido['_id'] = ObjectId(usuario_escolhido['_id'])
                db.usuario.insert_one(usuario_escolhido)

            # Atualiza o usuário no Redis
            delete_data(cpf_antigo)  # Remove a chave antiga (com o CPF antigo)
            usuario_convertido = converter_objectid_para_string(usuario_escolhido)
            set_data(usuario_escolhido['cpf'], usuario_convertido)  # Adiciona/atualiza a chave no Redis com o CPF

            print("Usuário atualizado com sucesso!")
            break

        except ValueError:
            print("Digite um número válido.")


    
