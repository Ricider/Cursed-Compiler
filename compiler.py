global blocks

def getBlock(symbol):
    for i in blocks:
        if i.symbol==symbol: return i

class block:
    def __init__(self, symbol="", repeatCount="",returnTech="",tokens=[],asm=""):
        self.symbol=symbol
        self.repeatCount=repeatCount
        self.returnTech=returnTech
        self.tokens=tokens
        if asm=="": asm=self.asmGen()
        else: self.asm=asm
        
    def toString(self):
        return self.symbol+" "+str(self.repeatCount)+" "+self.returnTech+" "+str(self.tokens)

    def asmGen(self): #code generation for block
        if self.symbol=="main": self.asm="movq (%rsp), %r12\n"
        else: self.asm=""
        rspOffset=0
        for i in self.tokens:
            if i[1]=="constant":
                self.asm+=("movq $"+str(i[0])+",(%rsp)\n")
                self.asm+=("subq $8 , %rsp\n")
                rspOffset+=8
            if i[1]=="variable":
                argOffset=16 if i[0]=="left" else 8 #left arg or right arg
                self.asm+=("movq "+str(rspOffset+argOffset)+"(%rsp), %rbx\n") #rbx is temporary to move element from args to postfix stack
                self.asm+=("movq %rbx,(%rsp)\n")
                self.asm+=("subq $8 , %rsp\n")
                rspOffset+=8
            if i[1]=="symbol":
                blok=getBlock(i[0])
                self.asm+=blok.asm
                rspOffset-=8

#tokens
symbols=["+","-"]
keywords=["def","repeat"]
variables=["left","right"]
returnTech=["accum","last","print"]

tokenTypes=[symbols,keywords,variables,returnTech]
tokenTypeNames=["symbol","keyword","variable","returnTech"]

source=open("input.txt","r")
sourceStr=source.read()

tokens=[]
blocks=[block("+",1,"last",None, 
              "movq 8(%rsp), %r10\n"+
              "movq 16(%rsp), %r11\n"+
              "addq %r10, %r11\n"+
              "movq %r11, 16(%rsp)\n"+
              "addq $8, %rsp\n"),
        block("-",1,"last",None, 
              "movq 8(%rsp), %r10\n"+
              "movq 16(%rsp), %r11\n"+
              "subq %r10, %r11\n"+
              "movq %r11, 16(%rsp)\n"+
              "addq $8, %rsp\n")]

#token generation
wordList=sourceStr.split()
for i in wordList:
    isSymbol=True
    for v in range(len(tokenTypes)):
        if i.isnumeric():
            tokens.append((int(i),"constant"))
            isSymbol=False
            break
        if i in tokenTypes[v]: 
            tokens.append((i,tokenTypeNames[v]))
            isSymbol=False
            break
    if isSymbol: 
        symbols.append(i)
        tokens.append((i,"symbol"))
        
#definition blocks indexes
defPos=[]
for i in range(len(tokens)):
    if tokens[i][0]=="def": defPos.append(i)
defPos.append(-1)

#definition blocks
for i in range(len(defPos)-1):
    offset=defPos[i]
    blocks.append(block(tokens[offset+1][0],
                        tokens[offset+3][0],
                        tokens[offset+4][0],
                        tokens[offset+5:defPos[i+1]]))

print(".global func")
print("func:")
print(blocks[3].asm)
print("movq 8(%rsp), %rax")
print("movq %r12, (%rsp)")
print("ret")