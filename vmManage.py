# Parâmetros
pageSize = 256 # 2^8 -->8 bits de deslocamento 
tlbSize = 16
# Valor do frameCount pequeno para forçar politica FIFO
frameCount = 16 # quantidade de frames na memoria fisica
pageCount = 256 # 2^(16-8) --> 16 são os bits de endereco e 8 são do deslocamento

# Arquivos 
backingStoreFile = "BACKING_STORE.bin"
addressesFile = "addresses.txt"

# Memória física --> lista de quadros 
physicalMemory = [None] * frameCount
# Tabela de páginas (indice --> número da página  valor --> número do quadro)
pageTable = [-1] * pageCount
# TLB -- (numeroPagina, numeroQuadro)
tlb = []
# FIFO
frameQueue = []

# Estatísticas
totalAddresses = 0
pageFaults = 0
tlbHits = 0


def fifo(data, newItem, limit):
    if len(data) >= limit:
        data.pop(0)
    data.append(newItem)

def loadFromBackingStore(pageNumber):
   
    print(f"# Carregando página {pageNumber} do '{backingStoreFile}'.")
    try:
        with open(backingStoreFile, "rb") as f:
            f.seek(pageNumber * pageSize)
            return f.read(pageSize)
    except IOError:
        print(f"ERRO: Não foi possível ler o arquivo '{backingStoreFile}'.")
        exit()

def translateAddress(logicalAddress):
   
    global totalAddresses, pageFaults, tlbHits

    totalAddresses += 1
    pageNumber = logicalAddress // pageSize
    offset = logicalAddress % pageSize

    print(f"\n--- Traduzindo Endereço Lógico: {logicalAddress} ---")
    print(f"Número da Página: {pageNumber}   Deslocamento: {offset}")

    # Verificar a TLB
    frameNumber = -1 #marca que não foi encontrado
    for tlbPage, tlbFrame in tlb:
        if tlbPage == pageNumber:
            frameNumber = tlbFrame # se encontrado atualiza
            tlbHits += 1
            print(f"# TLB Hit --> Página {pageNumber} está no quadro {frameNumber}.")
            break
    
    if frameNumber == -1: #se não encontrado tlb miss

        print("# TLB Miss")
        
        # Verificar a tabela de páginas
        frameNumber = pageTable[pageNumber]

        if frameNumber == -1:
            print("# FALHA DE PÁGINA")
            
            pageFaults += 1
            pageContent = loadFromBackingStore(pageNumber) #Recebe conteudo de backing store

            # FIFO -- se a memória estiver cheia
            if len(frameQueue) >= frameCount:
                victimFrame = frameQueue.pop(0)
                # Encontra a página que estava usando o quadro do alvo
                oldPage = pageTable.index(victimFrame)
                pageTable[oldPage] = -1 # Invalida a entrada da página antiga
                print(f"# Memória cheia. Substituindo página {oldPage} no quadro {victimFrame}.")
                frameNumber = victimFrame
            else:
                # Usa o próximo quadro livre
                frameNumber = len(frameQueue)

            # Carrega a nova página na memória física e atualiza as estruturas
            physicalMemory[frameNumber] = pageContent
            pageTable[pageNumber] = frameNumber
            frameQueue.append(frameNumber)
            print(f"# Página {pageNumber} carregada no quadro {frameNumber}.")
        else:
            print(f"# SUCESSO --> Página {pageNumber} está no quadro {frameNumber}.")

        # Atualiza a TLB 
        fifo(tlb, (pageNumber, frameNumber), tlbSize)
        print(f"# Entrada [Página: {pageNumber}, Quadro: {frameNumber}] atualizada na TLB.")

    physicalAddress = (frameNumber * pageSize) + offset

    # O valor é lido como um inteiro
    byteValue = int(physicalMemory[frameNumber][offset])

    print("\n--- RESULTADO DA TRADUÇÃO ---")
    print(f"Endereço Lógico: {logicalAddress}")
    print(f"Endereço Físico: {physicalAddress}")
    print(f"Valor do Byte: {byteValue}")
    print("-----------------------------\n")

def main():
    
    try:
        with open(addressesFile, 'r') as f:
            addresses = [int(line.strip()) for line in f if line.strip()]
        print(f"INFO: {len(addresses)} endereços lógicos carregados de '{addressesFile}'.")
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{addressesFile}' não encontrado.")
        return
    except ValueError:
        print(f"ERRO: Arquivo '{addressesFile}' contém dados inválidos.")
        return

    for address in addresses:
        translateAddress(address)

    # Exibe estatísticas finais
    print("\n========== ESTATÍSTICAS ==========")
    if totalAddresses > 0:
        pageFaultRate = (pageFaults / totalAddresses) * 100
        tlbHitRate = (tlbHits / totalAddresses) * 100
        print(f"Total de endereços traduzidos: {totalAddresses}")
        print(f"Total de falhas de páginas: {pageFaults} ({pageFaultRate:.2f}%)")
        print(f"Total de acertos na TLB: {tlbHits} ({tlbHitRate:.2f}%)")
    else:
        print("Nenhum endereço foi traduzido.")

if __name__ == "__main__":
    main()