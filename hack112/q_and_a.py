import random 

from PySide2.QtCore import QObject, Slot

class QAndA(QObject):
    @Slot(result=list)
    def makeQandA(self):
        qAndA = {}
        q1 = "Forwards it's heavy backwards it's not. What is it?"
        a1 = "ton"
        qAndA[q1] = a1
        q2 = "what kind of animal is kimchee"
        a2 = "Axolotl"
        qAndA[q2] = a2
        q3 = "how many front toes does kimchee have"
        a3 = "4"
        qAndA[q3] = a3
        q4 = "does kimchi taste good"
        a4 = "yee"
        qAndA[q4] = a4
        q5 = "how long can a python get (on average)"
        a5 = "23 feet"
        qAndA[q5] = a5
        q6 = "what goes with eggs, sausage, tomato, and baked beans"
        a6 = "spam"
        qAndA[q6] = a6
        q7 = "whats the efficiency of merge sort"
        a7 = "o(nlog(n))"
        qAndA[q7] = a7
        q8 = "fill in the blank: apes ______ strong"
        a8 = "together"
        qAndA[q8] = a8

        q9 = "When was sliced bread invented"
        a9 = "1928"
        qAndA[q9] = a9
        q10 = "What is 42 in binary"
        a10 = "101010"
        qAndA[q10] = a10
        q11 = "Is boba a soup"
        a11 = "Yup"
        qAndA[q11] = a11
        q12 = "Does pineapple belong on pizza"
        a12 = "YES"
        qAndA[q12] = a12
        q13 = "What's the capital of Pennasylvania?"
        a13 = "Harrisburgh"
        qAndA[q13] = a13
        q14 = "When do you use a semicolon? \nA) after an if statement \nB) to connect 2 complete sentence or clauses without a conjunction \nC) whenever you feel like it \nD) never \nE) all of the above"
        a14 = "B"
        qAndA[q14] = a14
        q15 = "Assuming complete conversion between kinetic and thermal energy, and other ideal conditions and stuff, \nhow fast would you need to slap a chicken in order to cook it?"
        a15 = "1665.65 m/s"
        qAndA[q15] = a15


        

        currQ, currA = random.choice(list(qAndA.items()))
        return [currQ, currA]





