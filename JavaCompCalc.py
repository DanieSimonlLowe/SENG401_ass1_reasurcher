import re

import radon.visitors
from radon.visitors import ComplexityVisitor

def javacyc(code):
    complexity = 0
    main_index = code.find("public static void main")
    if main_index != -1:
        complexity += 1

    ifs = [m.start() for m in re.finditer(" if ", code)]
    ifs += [m.start() for m in re.finditer(" if\n", code)]
    ifs += [m.start() for m in re.finditer("\nif ", code)]
    ifs += [m.start() for m in re.finditer(" if\(", code)]
    ifs += [m.start() for m in re.finditer("\nif\(", code)]
    complexity += len(ifs)

    cases = [m.start() for m in re.finditer(" case ", code)]
    complexity += len(cases)

    whiles = [m.start() for m in re.finditer(" while ", code)]
    whiles += [m.start() for m in re.finditer(" while\n", code)]
    whiles += [m.start() for m in re.finditer("\nwhile ", code)]
    whiles += [m.start() for m in re.finditer(" while\(", code)]
    whiles += [m.start() for m in re.finditer("\nwhile\(", code)]
    complexity += len(whiles)

    fors = [m.start() for m in re.finditer(" for ", code)]
    fors += [m.start() for m in re.finditer(" for\n", code)]
    fors += [m.start() for m in re.finditer("\nfor ", code)]
    fors += [m.start() for m in re.finditer(" for\(", code)]
    fors += [m.start() for m in re.finditer("\nfor\(", code)]
    complexity += len(fors)

    print(complexity)
    return complexity

code = """public static void main(String[] args) {
    if (20 > 18) {
      System.out.println("20 is greater than 18"); // obviously
    }  
  }
"""
javacyc(code)