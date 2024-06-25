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
    total_usuarios_mongo = 0
    usuarios_cadastrados = []
    contador = 0

    if cpf:
        # Lógica para buscar por CPF específico (sem alterações)
        usuario_redis = get_data(cpf)
        if usuario_redis:
            print(usuario_redis)
        else:
            usuario_mongo = db.usuario.find_one({"cpf": cpf})
            if usuario_mongo:
                print(usuario_mongo)
                set_data(cpf, usuario_mongo)  # Armazenar no Redis após buscar do MongoDB
            else:
                print("Usuário não encontrado.")

    else:
        # Usuários do Redis
        print("\nUsuários no Redis:")
        usuarios_redis = []
        for chave in conR.scan_iter():
            valor_redis = conR.get(chave)
            try:
                usuario_redis = json.loads(valor_redis.decode('utf-8'))
                if 'cpf' in usuario_redis:
                    usuarios_redis.append(usuario_redis)
                    print(f"- {usuario_redis['nome']} {usuario_redis['sobrenome']} (CPF: {usuario_redis['cpf']})")
                    contador += 1  # Incrementa o contador aqui
            except (json.JSONDecodeError, AttributeError):
                print(f"- Erro ao carregar dados com a chave {chave.decode('utf-8')}: Valor inválido no Redis")

        # Usuários do MongoDB
        print("\nUsuários no MongoDB:")
        usuarios_mongo = list(db.usuario.find())
        total_usuarios_mongo = len(usuarios_mongo)
        for usuario in usuarios_mongo:
            print(f"- {usuario['nome']} {usuario['sobrenome']} (CPF: {usuario['cpf']})")
            usuarios_cadastrados.append(usuario)
            contador += 1  # Incrementa o contador aqui

        # Usuários apenas no Redis (correção da lógica)
        usuarios_apenas_redis = [u for u in usuarios_redis if not any(u['cpf'] == m['cpf'] for m in usuarios_mongo)]
        for usuario in usuarios_apenas_redis:  # Incrementa o contador para usuários apenas no Redis
            contador += 1

        # Combinar e exibir usuários cadastrados
        print("\nUsuários cadastrados:")
        for i, usuario in enumerate(usuarios_cadastrados, start=1):
            print(f"{i} - {usuario['nome']} {usuario['sobrenome']} (CPF: {usuario['cpf']})")

        # Perguntar sobre usuários que estão apenas no Redis
        for usuario in usuarios_apenas_redis:
            while True:
                acao = input(f"\nO usuário {usuario['nome']} {usuario['sobrenome']} (CPF: {usuario['cpf']}) está apenas no Redis. Deseja adicionar ao MongoDB (A) ou excluir do Redis (E)? ").strip().upper()
                if acao == 'A':
                    if not db.usuario.find_one({"_id": usuario['_id']}):
                        usuario['_id'] = ObjectId(usuario['_id'])
                        db.usuario.insert_one(usuario)
                        print("Usuário adicionado ao MongoDB com sucesso!")
                    else:
                        print("Usuário já existe no MongoDB.")
                    break
                elif acao == 'E':
                    delete_data(usuario['cpf'])
                    print("Usuário excluído do Redis com sucesso!")
                    break
                else:
                    print("Opção inválida. Digite A ou E.")

        # Escolher usuário para ver detalhes (somente se houver usuários no Redis ou no MongoDB)
        if usuarios_redis or usuarios_mongo:
            while True:
                try:
                    escolha = int(input("\nDigite o número do usuário para ver detalhes (ou 0 para cancelar): "))
                    if escolha == 0:
                        break

                    # Correção na verificação da escolha
                    if 1 <= escolha <= contador:  # Compara com o contador total
                        if escolha <= total_usuarios_mongo:
                            usuario_escolhido = usuarios_mongo[escolha - 1]
                        else:
                            usuario_escolhido = usuarios_redis[escolha - total_usuarios_mongo - 1]
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
        print("\nUsuários no MongoDB:")
        for usuario in usuarios_mongo:
            print(f"- {usuario['nome']} {usuario['sobrenome']} (CPF: {usuario['cpf']})")
    else:
        print("\nNenhum usuário encontrado no MongoDB.")

    print("\nUsuários no Redis:")
    usuarios_redis = []
    for chave in conR.scan_iter():
        valor_redis = conR.get(chave)
        try:
            usuario_redis = json.loads(valor_redis.decode('utf-8'))
            if 'cpf' in usuario_redis:
                usuarios_redis.append(usuario_redis)
                print(f"- {usuario_redis['nome']} {usuario_redis['sobrenome']} (CPF: {usuario_redis['cpf']})")
        except (json.JSONDecodeError, AttributeError):
            pass

    if not usuarios_redis and not usuarios_mongo:
        print("Nenhum usuário encontrado no Redis.")
        return

    # Lista unificada e numerada para escolha do usuário (sem duplicatas)
    print("\nUsuários para atualizar/excluir:")
    todos_usuarios = []
    cpfs_adicionados = set()  # Conjunto para armazenar CPFs já adicionados
    for usuario in usuarios_mongo + usuarios_redis:
        if usuario['cpf'] not in cpfs_adicionados:
            todos_usuarios.append(usuario)
            cpfs_adicionados.add(usuario['cpf'])
            print(f"{len(todos_usuarios)} - {usuario['nome']} {usuario['sobrenome']} (CPF: {usuario['cpf']})")

    # Escolher usuário para atualizar/excluir
    while True:
        try:
            escolha = int(input("\nDigite o número do usuário para atualizar/excluir (ou 0 para cancelar): "))
            if escolha == 0:
                return

            if 1 <= escolha <= len(todos_usuarios):
                usuario_escolhido = todos_usuarios[escolha - 1]
                usuario_no_mongo = usuario_escolhido in usuarios_mongo
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


    
