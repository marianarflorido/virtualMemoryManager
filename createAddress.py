import random

# Nome do arquivo de saída
arquivo_saida = 'addresses.txt'

# Quantidade de endereços virtuais
quantidade = 300

# Tamanho máximo de endereço virtual (16 bits: 0 a 65535)
limite_superior = 2**16 - 1

# Gerar os endereços aleatórios
enderecos = [str(random.randint(0, limite_superior)) for _ in range(quantidade)]

# Salvar no arquivo, um por linha
with open(arquivo_saida, 'w') as f:
    f.write('\n'.join(enderecos))

print(f"{quantidade} endereços foram salvos em '{arquivo_saida}'.")
