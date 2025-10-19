import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.calculator import Calculator
import pytest

# Tests para la calculadora
class TestCalculator:

    # Configuración antes de cada test
    def setup_method(self):
        self.calc = Calculator()

    # Test suma básica
    def test_sumar(self):
        assert self.calc.sumar(2, 3) == 5
        assert self.calc.sumar(-1, 1) == 0

    # Test resta básica
    def test_restar(self):
        assert self.calc.restar(5, 3) == 2
        assert self.calc.restar(0, 5) == -5

    # Test división normal
    def test_dividir(self):
        assert self.calc.dividir(10, 2) == 5
        assert self.calc.dividir(9, 3) == 3

    # Test división por cero - debe lanzar excepción
    def test_dividir_por_cero(self):
        with pytest.raises(ValueError, match="No se puede dividir por cero"):
            self.calc.dividir(10, 0)

    # Test multiplicación
    def test_multiplicar(self):
        assert self.calc.multiplicar(3, 4) == 12
        assert self.calc.multiplicar(-2, 5) == -10

    # Test potencia con exponente positivo
    def test_potencia_positiva(self):
        assert self.calc.potencia(2, 3) == 8
        assert self.calc.potencia(5, 2) == 25
