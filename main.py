import lexer
import ll1
import slr1
import lr1
from lalr.parser import  LALR1Parser


def lexHandler():
    inputFile = input("Please Enter File name :")
    lexer.lexer(inputFile)
    print("done!\ncheck lexer_result.txt!")


def ll1Handler():
    inputFile = input("Please Enter File name :")
    inputString = list(input("String : "))
    ll1.ll1(inputFile, inputString)


def slr1Handler():
    slr1.main()


def lalr1Handler():
    inputFile = input("Please Enter File name :")
    LALR1Parser(inputFile)


def lr1Handler():
    inputFile = input("Please Enter File name :")
    lr1.main(inputFile)


print(" *** LEXYN *** ")
print("Hello, Please select what you want:")
print("1. Lexical Analysis\n2. Syntax Analysis")


while True:
    num = input()
    if num == "1":
        lexHandler()
        break
    elif num == "2":
        print("Type of syntsx analysis\n1. LL(1)\n2. LR(1)\n3. LALR(1)\n4. SLR(1)")
        num = 0
        while True:
            num = input()
            if num == "1":
                ll1Handler()
                break
            elif num == "2":
                lr1Handler()
                break
            elif num == "3":
                lalr1Handler()
                break
            elif num == "4":
                slr1Handler()
                break
            else:
                print("Please select again")
        break
    else:
        print("Please select again")
