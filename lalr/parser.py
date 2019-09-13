from lalr.lexer import GenericLexer, LexToken as LT, LexToken
from lalr.compiler import *

import six
import copy

grammar = []
new_grammar = []
terminals = []
non_terminals = []
I_n = {}
shift_list = []
reduction_list = []
action_list = []
rule_dict = {}
follow_dict = {}
SR = []
RR = []


def Conflict():
    global SR, RR, shift_list, reduction_list
    conflict = False
    # SR conflict if shift and Reduce occurs for same condition
    for S in shift_list:
        for R in reduction_list:
            if S[:2] == R[:2]:
                SR.append([S, R])
                conflict = True

    # RR conflict if 2 Reduce occurs for same condition
    for R1 in reduction_list:
        for R2 in reduction_list:
            if R1 == R2:
                continue

            if R1[:2] == R2[:2]:
                RR.append(R1)
                conflict = True

    return conflict


def read_grammar(inputFile):
    global grammar, terminals, non_terminals, rule_dict

    file_name = inputFile

    # open given file
    try:
        grammar_file = open(file_name, "r")
    except:
        # grammar_file = open("slr1_test.txt", "r")
        print("Cannot Find File Named", file_name)
        exit(0)

    # add garmmar
    c = 0
    for each_grammar in grammar_file:
        if c == 0 or c == 1:
            c +=1
            continue
        c += 1
        each_grammar = each_grammar.replace(" ", "")
        grammar.append(each_grammar.strip())

        # find terminals
        if each_grammar[0] not in non_terminals:
            non_terminals.append(each_grammar[0])

    # find non terminals
    for each_grammar in grammar:
        for token in each_grammar.strip().replace(" ", "").replace("->", ""):
            if token not in non_terminals and token not in terminals:
                terminals.append(token)

    # generate dictionary of rules
    for l in range(1, len(grammar) + 1):
        rule_dict[l] = grammar[l - 1]
    # return slr1_test.txt
    # print terminals


def augmented_grammar(inputFile):
    global grammar, new_grammar
    read_grammar(inputFile)

    # if non augmented slr1_test.txt is given, augment it
    if "'" not in grammar[0]:
        grammar.insert(0, grammar[0][0] + "'" + "->" + grammar[0][0])

    # just add . infornt of each rule
    new_grammar = []
    for each_grammar in grammar:
        idx = each_grammar.index(">")
        # print each_grammar.split()
        each_grammar = each_grammar[:idx + 1] + "." + each_grammar[idx + 1:]
        new_grammar.append(each_grammar)
    # print new_grammar


def compute_I0(inputFile):
    global new_grammar, non_terminals, I_n
    augmented_grammar(inputFile)

    grammar2add = []

    # add first rule to I(0)
    grammar2add.append(new_grammar[0])
    i = 0

    # check for terminals in new_grammar[0]
    for each in grammar2add:
        current_pos = each.index(".")
        current_variable = each[current_pos + 1]
        # print current_variable

        if current_variable in non_terminals:
            for each_grammar in new_grammar:
                if each_grammar[0] == current_variable and each_grammar not in grammar2add:
                    grammar2add.append(each_grammar)

        I_n[i] = grammar2add
    # print grammar2add


def GOTO(inputFile):
    global grammar, non_terminals, terminals, I_n, shift_list
    compute_I0(inputFile)

    variables = non_terminals + terminals
    # variables = ["E", "T", "F", "(", ")", "+", "*", "i"]

    # I_n[0]
    i = 0
    current_state = 0
    done = False

    while (not done):
        for each_variable in variables:
            grammar2add = []
            # print each_variable, "------------------"
            try:
                for each_rule in I_n[current_state]:
                    if each_rule[-1] == ".":
                        continue
                    dot_idx = each_rule.index(".")

                    if each_rule[dot_idx + 1] == each_variable:

                        rule = copy.deepcopy(each_rule)
                        rule = rule.replace(".", "")
                        rule = rule[:dot_idx + 1] + "." + rule[dot_idx + 1:]
                        # rule[dot_idx] = rule[dot_idx+1]
                        # rule[dot_idx+1] = "."
                        # print rule
                        grammar2add.append(rule)

                        for rule in grammar2add:
                            dot_idx = rule.index(".")
                            if rule[-1] == ".":
                                pass
                            else:
                                current_variable = rule[dot_idx + 1]

                                if current_variable in non_terminals:
                                    for each_grammar in new_grammar:
                                        if each_grammar[0] == current_variable and each_grammar[1] != "'" and each_grammar not in grammar2add:
                                            grammar2add.append(each_grammar)

                                        # grammar2add.append([current_state, current_variable])
                                        # rule[dot_idx] = rule[dot_idx+1]
                                        # rule[dot_idx+1] = "."
                                        # grammar2add.append(rule)
            except:
                done = True
                break

            if grammar2add:

                # for value in I_n.viewvalues():
                # for item in I_n.iteritems():
                # 	if grammar2add == item[1]:
                # 		I_n[i] = item[0]
                # 		break

                if grammar2add not in I_n.values():
                    i += 1
                    I_n[i] = grammar2add

                # if isinstance(I_n[i], int):
                # 	shift_list.append([x, each_variable, I_n[i]])
                # else:
                # if grammar2add in I_n.values():
                for k, v in six.iteritems(I_n):
                    if grammar2add == v:
                        idx = k

                shift_list.append([current_state, each_variable, idx])
            # print grammar2add, "AFFFFFFFFF", idx

        current_state += 1


def follow(var):
    global rule_dict, follow_dict, terminals

    value = []
    if var == rule_dict[1][0]:
        value.append("$")

    for rule in rule_dict.values():

        lhs, rhs = rule.split("->")

        if var == rule[-1]:
            for each in follow(rule[0]):
                if each not in value:
                    value.append(each)

        if var in rhs:
            idx = rhs.index(var)

            try:
                if rhs[idx + 1] in non_terminals and rhs[idx + 1] != var:
                    for each in follow(rhs[idx + 1]):
                        value.append(each)
                    # print "AAAA", var
                else:
                    value.append(rhs[idx + 1])
                # print "BBB", var
            except:
                # print "Error at", var
                pass

    # if var == "S":
    # 	value = ["$"]
    # elif var == "L":
    # 	value = ["=", "$"]
    # elif var == "R":
    # 	value = ["=", "$"]

    return value


def reduction():
    global I_n, rule_dict, reduction_list

    reduction_list.append([1, "$", "Accept"])

    for item in six.iteritems(I_n):
        try:
            for each_production in item[1]:
                lhs, rhs = each_production.split(".")

                for rule in rule_dict.iteritems():

                    if lhs == rule[1]:
                        # print lhs
                        f = follow(lhs[0])
                        # print "FOOOOOO", lhs[0], f

                        for each_var in f:
                            reduction_list.append([item[0], each_var, "R" + str(rule[0])])

        except:
            # print item
            pass


def test(string):
    global action_list, shift_list, reduction_list
    done = False
    stack = []
    stack.append(0)

    print("\n\nSTACK\t\tSTRING\t\tACTION")
    while not done:
        Reduce = False
        Shift = False
        # Check for reduction
        for r in reduction_list:
            # Reduce
            if r[0] == int(stack[-1]) and r[1] == string[0]:
                Reduce = True
                print(''.join(str(p) for p in stack), "\t\t", string, "\t\t", "Reduce", r[2])

                if r[2] == 'Accept':
                    return 1
                # print "---ACCEPTED---"
                # done = True
                # break
                var = rule_dict[int(r[2][1])]
                lhs, rhs = var.split("->")

                for x in range(len(rhs)):
                    stack.pop()
                    stack.pop()

                var = lhs
                stack.append(var)

                for a in action_list:
                    # print stack
                    if a[0] == int(stack[-2]) and a[1] == stack[-1]:
                        stack.append(str(a[2]))
                        break
                    # print "String", string
                    # print "RRR", stack

                    # else:
                    # 	Reduce = False

        # Check for shift
        for g in shift_list:
            # Shift
            if g[0] == int(stack[-1]) and g[1] == string[0]:
                Shift = True
                print(''.join(str(p) for p in stack), "\t\t", string, "\t\t", "Shift", "S" + str(g[2]))
                stack.append(string[0])
                stack.append(str(g[2]))
                string = string[1:]
            # print "String", string
            # print "RRR", stack

        if not Reduce and not Shift:
            print(''.join(str(p) for p in stack), "\t\t", string)
            # print "---NOT ACCEPTED---"
            return 0
        # done = True
        # break


def main(inputFile):
    global I_n, shift_list, reduction_list, action_list, SR, RR

    GOTO(inputFile)
    reduction()

    action_list.extend(shift_list)
    action_list.extend(reduction_list)

    string = input("\n\nEnter String:: ")

    try:
        if string[-1] != "$":
            string = string + "$"
    except:
        print("InputError")
        exit(0)

    print("\nTest String:", string)

    result = test(string)

    if result == 1:
        print("---ACCEPTED---")
    elif result == 0:
        print("---NOT ACCEPTED---")

    return 0



class LALR1Parser:
    def __init__(self, fileName):
        self.lexicalRules = None
        self.inputFile = None
        self.rules = []
        self.semanticRules = []
        self.codeHandler = None
        self.precedence = []
        self.assoc = {}

        self.languageParser = None

        self.loadYaccParser(fileName)
        self.stringHandler(fileName)


    def loadYaccParser(self, fileName):

        def createRule(symbol, productions):
            symbol = symbol.value.split()[0]

            for p in productions:
                self.rules.append((symbol, tuple([i.value for i in p[0]])))
                codeId = int(p[1].value[1:-1])
                self.semanticRules.append(self.codeHandler.getCode()[codeId][1:-1])

        def createMacro(macro, ops):
            macro = macro.value
            ops = [o.value for o in ops]
            if macro == '%priority':
                for op1 in range(len(ops)):
                    for op2 in range(op1 + 1, len(ops)):
                        self.precedence.append((ops[op1], ops[op2]))
            elif macro == '%right' or macro == '%left':
                m = macro[1:]
                for op in ops:
                    self.assoc[op] = m
            else:
                print('Invalid macro ', macro)

        def listAppend(l, it):
            l.append(it)
            return l

        def pack(a, b):
            return (a, b)

        semantic = [
            CHILD(0),
            None, None,
            [createRule, CHILD(0), CHILD(1)], [createMacro, CHILD(0), CHILD(1)],
            [listAppend, CHILD(0), CHILD(1)],
            [listAppend, CHILD(0), CHILD(1)], [],
            [pack, CHILD(0), CHILD(1)],
            CHILD(0), None,
            [listAppend, CHILD(0), CHILD(1)], [CHILD(0)]
        ]
        g = readGrammar(fileName, semantic=semantic)
        self.yaccParser = LALRParser(g, "S")

    def stringHandler(self, inputFile):
        main(inputFile)



