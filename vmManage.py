# Parâmetros
pageSize = 512
tlbSize = 16
frames = 128 
physicalMemorySize = frames * pageSize

# Arquivos
address = 'addresses.txt'
backingStore = 'BACKING_STORE.bin'

# Estruturas de dados
pageTable = [-1] * 128  # -1 indica página não carregada
physicalMemory = []          # Cada item: (pageNumber)
tlb = []                     # Cada item: (pageNumber, frameNumber)

# Estatísticas
totalAccess = 0
pageFaults = 0
tlbHits = 0

#Variaveis

# FIFO 
def fifo(data, new, lim):
    if len(data) >= lim:
        data.pop(0)
    data.append(new)

# Lê BACKING_STORE.bin
def loadBackingStore(pageNumber):
    with open(backingStore, 'rb') as f:
        f.seek(pageNumber * pageSize)
        return f.read(pageSize)

# Traduz endereço virtual
def translateAddress(virtualAddress):
    global totalAccess, pageFaults, tlbHits

    totalAccess += 1 #Contabiliza o numero de acessos a memoria

    virtualPageNumber = virtualAddress // pageSize
    offset = virtualAddress % pageSize

    print(f"\nAcesso #{totalAccess}")
    print(f"Endereço virtual: {virtualAddress}")
    print(f"Número da página: {virtualPageNumber}   Deslocamento: {offset}")

    #Verificar TLB
    for pageNumber, frameNumber in tlb:
        if pageNumber == virtualPageNumber:
            tlbHits += 1
            print(f"# TLB HIT (quadro {frameNumber})")
            physicalAddress = (frameNumber * pageSize) + offset

            print(f"# Endereço físico: {physicalAddress}")
            return

    print("# TLB MISS")

    # Verificar Tabela de Páginas
    frame = pageTable[virtualPageNumber]
    if frame == -1:
        print("# PAGE FAULT")
        pageFaults += 1

        # FIFO --> Primeiro a entrar e o primeiro a sair
        if len(physicalMemory) >= frames:
            removedPage = physicalMemory.pop(0)
            removed = pageTable[removedPage]
            pageTable[removedPage] = -1
            print(f"# Substituindo página {removedPage} do frame {removed}")

        # Carrega nova página
        conteudo = loadBackingStore(virtualPageNumber)
        #print(f"Memoria: {physicalMemory} ")
        frame = len(physicalMemory)
        physicalMemory.append((virtualPageNumber, conteudo))
        pageTable[virtualPageNumber] = frame
        print(f"# Página {virtualPageNumber} carregada no frame {frame}")
    else:
        print(f"# Página {virtualPageNumber} já está na memória (frame {frame})")

    # Atualizar TLB (FIFO)
    fifo(tlb, (virtualPageNumber, frame), tlbSize)

    # Gerar endereço físico 
    print(f"Frame: {frame}   Pagesize: {pageSize}    Offset: {offset}")
    physicalAddress = (frame * pageSize) + offset

    print(f"# Endereço físico: {physicalAddress}")


def main():

    # Executar simulação
    with open(address, 'r') as f:
        for linha in f:
            virtualAddress = int(linha.strip())
            translateAddress(virtualAddress)

    # Estatísticas finais
    print("\n===== ESTATÍSTICAS FINAIS =====")
    print(f"Total de endereços traduzidos: {totalAccess}")
    print(f"Total de page faults: {pageFaults}")
    print(f"Taxa de page faults: {pageFaults / totalAccess * 100:.2f}%")
    print(f"Total de TLB hits: {tlbHits}")
    print(f"Taxa de acertos da TLB: {tlbHits / totalAccess * 100:.2f}%")

if __name__ == "__main__":
    main()
