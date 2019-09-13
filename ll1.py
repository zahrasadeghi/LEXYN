import six
class PredictiveParser(object):
    def is_terminal(self, sym):
        if not sym or sym[0].isupper():
            return False
        return True

    def is_nonterminal(self, sym):
        if not sym or not sym[0].isupper():
            return False
        return True

    def __init__(self, start, grammar):
        self.start = start
        self.grammar = grammar
        self.terminals = set()
        self.nonterminals = set()
        self.null_dict = self.gen_nullable()
        self.first_dict = self.gen_first()
        self.follow_dict = self.gen_follow()
        self.table = self.gen_table()

    def match(self, seq):
        seq.append('$')
        si = 0
        stack = ['$', self.start]
        top = self.start
        print("--- parsing table ---")
        print("STACK    STRING    ACTION")
        while top != '$':
            if top == seq[si]:
                si = si + 1
                stack.pop()
                print("".join(stack), " | ", "".join(seq[si:]), " | ")
            elif (self.is_terminal(top)):
                return False
            else:
                try:
                    prod = self.table[top, seq[si]]
                    stack.pop()
                    if prod != [""]:
                        stack.extend(reversed(prod))
                        print("".join(stack), " | ", "".join(seq[si:]), " | ", top +" -> "+ "".join(prod))
                except KeyError:
                    return False
            top = stack[-1]
        return True

    def verbose_match(self, seq, display_stack=False):
        seq.append('$')
        si = 0
        stack = ['$', self.start]
        top = self.start
        while top != '$':
            if display_stack:
                print
                "Stack:", stack
            if top == seq[si]:
                si = si + 1
                print
                "** Action: match `{0}`".format(top)
                stack.pop()
            elif (self.is_terminal(top)):
                return False
            else:
                try:
                    prod = self.table[top, seq[si]]
                    stack.pop()
                    if prod == [""]:
                        print
                        "** Action:derive {0} on '{1}'; to: lamda".format(top, seq[si])
                    else:
                        print
                        "** Action: derive {0} on '{1}' to: {2}".format(top, seq[si], " ".join(prod))
                        stack.extend(reversed(prod))
                except KeyError:
                    print
                    "ERROR: Not able to find derivation of {0} on `{1}`".format(top, seq[si])
                    return False
            top = stack[-1]
        return True

    def gen_table(self):
        table = {}
        for head, prods in six.iteritems(self.grammar):
            for prod in prods:
                first_set = self.first(prod)
                for terminal in first_set - set([""]):
                    table[head, terminal] = prod
                if "" in first_set:
                    for terminal in self.follow_dict[head]:
                        table[head, terminal] = prod
                    if '$' in self.follow_dict[head]:
                        table[head, '$'] = prod
        return table

    def print_table(self):
        print("   " + ' | '.join(self.terminals.union(set(['$']))))
        print("-----------------")
        for nonterminal in self.nonterminals:
            tempString = nonterminal + " | "
            for terminal in self.terminals.union(set(['$'])):
                try:
                    if len(self.table[(nonterminal, terminal)]) > 0:
                            tempString += str(' '.join(self.table[(nonterminal, terminal)])) + " | "
                    else:
                        tempString += "- | "
                except KeyError:
                    pass
            print(tempString)

    def gen_nullable(self):
        null_dict = {"": True}
        for head, prods in six.iteritems(self.grammar):
            null_dict[head] = False
            self.nonterminals.add(head)
            for prod in prods:
                for symbol in prod:
                    if self.is_terminal(symbol):
                        null_dict[symbol] = False
                        self.terminals.add(symbol)
                    elif not symbol:
                        null_dict[head] = True
        while True:
            changes = 0
            for head, prods in six.iteritems(self.grammar):
                for prod in prods:
                    all_nullable = True
                    for symbol in prod:
                        if not null_dict[symbol]:
                            all_nullable = False
                            break
                    if all_nullable and not (head in null_dict and null_dict[head]):
                        null_dict[head] = True
                        changes = changes + 1
            if changes == 0:
                return null_dict

    def nullable(self, symbols):
        if not symbols:
            return True
        elif not self.null_dict[symbols[0]]:
            return False
        return self.nullable(symbols[1:])

    def gen_first(self):
        first_dict = {}
        for head, prods in six.iteritems(self.grammar):
            first_dict[head] = set()
            for prod in prods:
                for symbol in prod:
                    if self.is_terminal(symbol):
                        first_dict[symbol] = set([symbol])
        while True:
            changes = first_dict.copy()
            for head, prods in six.iteritems(self.grammar):
                for prod in prods:
                    if not prod[0]:
                        first_dict[head] = first_dict[head].union(set([""]))
                    else:
                        first_dict[head] = first_dict[head].union(first_dict[prod[0]])
                    for i in range(1, len(prod)):
                        if self.nullable(prod[:i]):
                            if not prod[0]:
                                first_dict[head] = first_dict[head].union(set([""]))
                            else:
                                first_dict[head] = first_dict[head].union(first_dict[prod[0]])
            if changes == first_dict:
                return first_dict

    def first(self, symbols):
        if not symbols:
            return set()
        if "" in symbols:
            return set([""])
        if not self.null_dict[symbols[0]]:
            return self.first_dict[symbols[0]]
        return self.first_dict[symbols[0]].union(self.first(symbols[1:]))

    def gen_follow(self):
        follow_dict = {}
        for head in self.grammar:
            if head == self.start:
                follow_dict[self.start] = set(["$"])
            else:
                follow_dict[head] = set()
        while True:
            changes = follow_dict.copy()
            for head, prods in six.iteritems(self.grammar):
                for prod in prods:

                    for i in range(len(prod) - 1):
                        if self.is_nonterminal(prod[i]):
                            follow_dict[prod[i]] = follow_dict[prod[i]].union(self.first(prod[i + 1:]) - set([""]))

                    for i in reversed(range(len(prod))):
                        if self.is_nonterminal(prod[i]) and self.nullable(prod[i + 1:]):
                            follow_dict[prod[i]] = follow_dict[prod[i]].union(follow_dict[head])

            if changes == follow_dict:
                return follow_dict


def makeParser(text):
    rules = text.split("\n")
    rules = rules[2:]
    first = rules[0].split(" -> ")
    dict_rules = {}
    for line in rules:
        line = line.split(" -> ")

        if line[0] in dict_rules.keys():
            dict_rules[line[0]].append(line[1].split(" "))
        else:
            dict_rules[line[0]] = [line[1].split(" ")]
    parser = PredictiveParser(first[0], dict_rules)
    return parser


def ll1(inputFile, inputString):
    text = open(str(inputFile)).read()

    print("****** LL(1) ******\n")
    parser = makeParser(text)
    if parser.match(inputString):
        print("\n"+str("".join(inputString)) + " : ACCEPT")
    else:
        print(str("".join(inputString)) + " : REJECT")
    print("\n--- LL(1) table ---")
    parser.print_table()