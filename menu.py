import CRUDusuario
import CRUDvendedor
import CRUDproduto
import CRUDcompras
import CRUDfavoritos

key = 0
sub = 0
while (key != 'S'):
    print("1-CRUD Usuário")
    print("2-CRUD Vendedor")
    print("3-CRUD Produto")
    print("4-CRUD Compras")
    print("5-CRUD Favoritos")
    key = input("Digite a opção desejada? (S para sair) ").upper()

    if (key == '1'):
        print("Menu do Usuário")
        print("1-Criar Usuário")
        print("2-Listar Usuário")
        print("3-Atualizar Usuário")
        print("4-Excluir Usuário")
        sub = input("Digite a opção desejada? (V para voltar) ")
        if (sub == '1'):
            print("Criar usuario")
            CRUDusuario.create_usuario()
            
        elif (sub == '2'):
            nome = input("Listar usuários, deseja algum nome especifico? ")
            CRUDusuario.read_usuario(nome)
        
        elif (sub == '3'):
            nome = input("Digite o usuário a ser atualizado: ")
            CRUDusuario.update_usuario(nome)

        elif (sub == '4'):
            print("delete usuario")
            nome = input("Digite o usuário a ser deletado: ")
            sobrenome = input("Sobrenome a ser deletado: ")
            CRUDusuario.delete_usuario(nome, sobrenome)
            
    elif (key == '2'):
        print("Menu do Vendedor")     
        print("1-Criar Vendedor")
        print("2-Listar Vendedor")
        print("3-Atualizar Vendedor")
        print("4-Excluir Vendedor")
        sub = input("Digite a opção desejada? (V para voltar) ")
        if (sub == '1'):
            print("Criar vendedor")
            CRUDvendedor.create_vendedor()
            
        elif (sub == '2'):
            nome = input("Listar vendedores, deseja algum nome especifico? ")
            CRUDvendedor.read_vendedor(nome)
        
        elif (sub == '3'):            
            CRUDvendedor.update_vendedor()

        elif (sub == '4'):
            print("Excluir vendedor")
            nome = input("Nome a ser deletado: ")           
            CRUDvendedor.delete_vendedor(nome)  
         
    elif (key == '3'):
        print("Menu do Produto")  
        print("1-Criar Produto")
        print("2-Listar Produto")
        print("3-Atualizar Produto")
        print("4-Excluir Produto")
        sub = input("Digite a opção desejada? (V para voltar) ")
        if (sub == '1'):
            print("Criar produto")
            CRUDproduto.create_produto()
            
        elif (sub == '2'):
            nome = input("Listar produto, deseja algum produto especifico? ")
            CRUDproduto.read_produto(nome)
        
        elif (sub == '3'):            
            CRUDproduto.update_produto()

        elif (sub == '4'):                             
            CRUDproduto.delete_produto()     

    elif key == '4':
        print("Compras") 
        print("1 - Realizar compra")
        print("2 - Ver compras realizadas")        
        sub = input("Digite a opção desejada? (V para voltar) ")

        if sub == '1':
            cpf_usuario = input("Digite seu CPF: ")
            carrinho_usuario = CRUDcompras.realizar_compra(cpf_usuario)
              
        elif sub == '2':
            cpf_usuario = input("Digite seu CPF: ")
            CRUDcompras.ver_compras_realizadas(cpf_usuario)
        else:
            print("Opção inválida. Por favor, digite uma opção válida.")

    elif (key == '5'):
            print("Favoritos") 
            print("1 - Adicionar favoritos")
            print("2 - Visualizar favoritos")
            print("3 - Deletar favoritos")
            sub = input("Digite a opção desejada? (V para voltar) ")

            if (sub == '1'):
                CRUDfavoritos.adicionarnovo_favorito()

            elif (sub == '2'):
                cpf_usuario = input("Digite seu CPF: ")
                CRUDfavoritos.visualizar_favoritos(cpf_usuario)

            elif (sub == '3'):
                cpf_usuario = input("Digite seu CPF: ")                
                CRUDfavoritos.excluir_favorito(cpf_usuario)

            else:
                print("Opção inválida. Por favor, digite uma opção válida.")
 
        

print("Obrigada!")