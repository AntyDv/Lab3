class Calculator:
 #Suma dos números
 def sumar(self, a, b):
  return a + b
 #Resta dos números
 def restar(self, a, b):
  return a - b
 #Divide dos número
 def dividir(self, a, b):
  if b == 0:
   raise ValueError("No se puede dividir por cero")
  return a / b
 #Multiplica dos números
 def multiplicar (self, a, b):
  return a * b
 #Calcula la potencia
 def potencia(self, base, exponente):
  if exponente < 0:
   return 1 / (base ** abs (exponente))
  return base ** exponente