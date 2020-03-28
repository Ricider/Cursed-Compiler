global condCtr
condCtr=0
class block:
    def __init__(self,symbol,tokens,asm=""):
        self.symbol=symbol
        self.tokens=tokens
        self.operators=[] #2'nd level of ast
        self.operands=[] #3'rd level of ast
        self.asm=asm #for asm operators
    def astGen(self): #for this operation only
        for i in self.tokens:
            if i[1]=="symbol":
                self.operators.append(i[0])
            if i[1]=="constant":
                self.operands.append("$"+i[0])
            if i[1]=="variable": #all operators have 2 variables therefore we can know their location on stack without a symbol table
                if i[0]=="left": 
                    self.operands.append("16(%rsp)") 
                elif i[0]=="right":
                    self.operands.append("8(%rsp)")
    def asmGen(self):
        self.asm+=self.symbol+":\n" #asm function label
        self.asm+="movq "+self.operands[0]+", %rbx\n"
        self.asm+="movq %rbx, -8(%rsp)\n" #set accum to first operand
        for i in range(len(self.operators)):
            self.asm+="movq -8(%rsp), %rax\n" 
            self.asm+="movq %rax, -16(%rsp)\n" #accum passed as left arg
            self.asm+="movq "+self.operands[i+1]+", %rax\n"
            self.asm+="movq %rax, -24(%rsp)\n"
            self.asm+="subq $24, %rsp\n"
            self.asm+="call "+self.operators[i]+"\n"
            self.asm+="addq $24, %rsp\n"
            self.asm+="movq %rax, -8(%rsp)\n" #return value passed to accum
        self.asm+="movq -8(%rsp), %rax\n" #accum to return        
        self.asm+="ret\n"
            
symbols=["add","sub","is_condition", "of"]
keywords=["def"]
variables=["left","right"]

tokenTypes=[symbols,keywords,variables]
tokenTypeNames=["symbol","keyword","variable"]

source=open("input.txt","r")
sourceStr=source.read()

tokens=[]
asmBlocks=[block("add",None,
              "add:\n"+
              "movq 16(%rsp), %rbx\n"+
              "movq 8(%rsp), %rcx\n"+
              "addq %rcx, %rbx\n"+
              "movq %rbx, %rax\n"+
              "ret\n"
              ),
           block("sub",None,
              "sub:\n"+
              "movq 16(%rsp), %rbx\n"+
              "movq 8(%rsp), %rcx\n"+
              "subq %rcx, %rbx\n"+
              "movq %rbx, %rax\n"+
              "ret\n"
              ),
           block("is_condition",None,
              "is_condition:\n"+
              "movq -8(%rsp), %rbx\n"+
              "movq $1, %rax\n"+
              "comp %rbx, %rax\n"+
              "jg 32($rsp)"+
              "movq $0, 24($rsp)\n"+
              "ret\n"
              ),
           block("of",None,
              "of:\n"+
              "movq 16(%rsp), %rax\n"+
              "ret\n"
              )]

#token generation
wordList=sourceStr.split()
for i in wordList:
    isSymbol=True
    for v in range(len(tokenTypes)):
        if i.isnumeric():
            tokens.append((i,"constant"))
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
    asmBlocks.append(block(tokens[offset+1][0],tokens[offset+2:defPos[i+1]]))
    asmBlocks[-1].astGen()
    asmBlocks[-1].asmGen()
    
print (".global func\n")
for i in asmBlocks: print(i.asm)
