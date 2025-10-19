import subprocess
import time
import json
import re
from datetime import datetime
from pathlib import Path

"""Ejecuta tests y recopila métricas de Coverage y Build Time"""
class MetricsRunner:

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.metrics = {
            'timestamp': datetime.now().isoformat(),
            'build_time': {},
            'coverage': {},
            'test_results': {}
        }

    #Ejecuta tests midiendo tiempo y capturando coverage
    def run_tests_with_metrics(self):

        print("\n" + "=" * 70)
        print(" EJECUTANDO TESTS CON MÉTRICAS DE BUILD TIME Y COVERAGE")
        print("=" * 70 + "\n")

        # Medir tiempo total
        start_time = time.time()

        # Ejecutar pytest con coverage
        print("Ejecutando tests con coverage...\n")
        test_start = time.time()

        result = subprocess.run(
            [
                'pytest',
                'tests/',  # Tu carpeta de tests
                '--cov=src',
                '--cov-report=term-missing',  # Mostrar líneas faltantes
                '--cov-report=json',
                '--cov-report=html',
                '-v',
                '--durations=10',
                '--tb=short'  # Traceback corto
            ],
            capture_output=True,
            text=True,
            cwd=self.project_root
        )

        test_end = time.time()
        test_duration = test_end - test_start

        # Mostrar salida
        output = result.stdout + result.stderr
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        # Extraer métricas
        self.extract_coverage_metrics()
        self.extract_test_metrics(output, test_duration)

        # Tiempo total
        end_time = time.time()
        total_duration = end_time - start_time

        self.metrics['build_time']['total_seconds'] = round(total_duration, 3)
        self.metrics['build_time']['test_execution_seconds'] = round(test_duration, 3)

        # Mostrar resultados
        self.print_results()

        # Guardar métricas
        self.save_metrics()

        return result.returncode == 0

    def extract_coverage_metrics(self):
        """Extrae métricas de coverage del archivo JSON"""
        coverage_file = self.project_root / 'coverage.json'
        try:
            with open(coverage_file, 'r') as f:
                cov_data = json.load(f)

            totals = cov_data.get('totals', {})

            self.metrics['coverage'] = {
                'percent_covered': round(totals.get('percent_covered', 0), 2),
                'lines_covered': totals.get('covered_lines', 0),
                'lines_total': totals.get('num_statements', 0),
                'lines_missing': totals.get('missing_lines', 0),
                'branches_covered': totals.get('covered_branches', 0),
                'branches_total': totals.get('num_branches', 0)
            }

            # Branch coverage
            if self.metrics['coverage']['branches_total'] > 0:
                branch_percent = (
                        self.metrics['coverage']['branches_covered'] /
                        self.metrics['coverage']['branches_total'] * 100
                )
                self.metrics['coverage']['branch_coverage_percent'] = round(branch_percent, 2)

        except FileNotFoundError:
            print("Archivo coverage.json no encontrado")
            self.metrics['coverage'] = {'error': 'No coverage data available'}

    def extract_test_metrics(self, output, duration):
        """Extrae métricas de los tests ejecutados"""
        passed_match = re.search(r'(\d+) passed', output)
        failed_match = re.search(r'(\d+) failed', output)

        self.metrics['test_results'] = {
            'total_tests': 0,
            'passed': int(passed_match.group(1)) if passed_match else 0,
            'failed': int(failed_match.group(1)) if failed_match else 0,
            'duration_seconds': round(duration, 3),
            'status': 'PASSED' if not failed_match else 'FAILED'
        }

        self.metrics['test_results']['total_tests'] = (
                self.metrics['test_results']['passed'] +
                self.metrics['test_results']['failed']
        )

        if self.metrics['test_results']['total_tests'] > 0:
            avg_time = duration / self.metrics['test_results']['total_tests']
            self.metrics['test_results']['avg_test_seconds'] = round(avg_time, 3)

    def print_results(self):
        """Imprime resultados formateados"""
        print("\n" + "=" * 70)
        print(" RESUMEN DE MÉTRICAS")
        print("=" * 70)

        # Build Time
        print("\n️  BUILD TIME:")
        print(f"  ├─ Ejecución de tests: {self.metrics['build_time']['test_execution_seconds']}s")
        print(f"  └─ Tiempo total:       {self.metrics['build_time']['total_seconds']}s")

        total = self.metrics['build_time']['total_seconds']
        if total < 10:
            status = " EXCELENTE (< 10s)"
        elif total < 60:
            status = " BUENO (< 1 min)"
        else:
            status = "  PUEDE MEJORAR (> 1 min)"
        print(f"  └─ Estado: {status}")

        # Coverage
        print("\n CODE COVERAGE:")
        cov = self.metrics['coverage']
        if 'error' not in cov:
            print(f"  ├─ Líneas cubiertas:    {cov['lines_covered']}/{cov['lines_total']} ({cov['percent_covered']}%)")
            print(f"  └─ Líneas faltantes:    {cov['lines_missing']}")

            if 'branch_coverage_percent' in cov:
                print(
                    f"  └─ Ramas cubiertas:     {cov['branches_covered']}/{cov['branches_total']} ({cov['branch_coverage_percent']}%)")

            percent = cov['percent_covered']
            if percent >= 90:
                status = " EXCELENTE (≥ 90%)"
            elif percent >= 80:
                status = " BUENO (≥ 80%)"
            elif percent >= 60:
                status = " ACEPTABLE (≥ 60%)"
            else:
                status = "  BAJO (< 60%)"
            print(f"  └─ Estado: {status}")

        # Test Results
        print("\n RESULTADOS DE TESTS:")
        tests = self.metrics['test_results']
        print(f"  ├─ Total de tests:      {tests['total_tests']}")
        print(f"  ├─ Pasados:             {tests['passed']} ")
        if tests['failed'] > 0:
            print(f"  ├─ Fallados:            {tests['failed']} ")
        print(f"  ├─ Tiempo por test:     {tests.get('avg_test_seconds', 0)}s")
        print(f"  └─ Estado:              {tests['status']}")

        print("\n" + "=" * 70)
        print(" Reportes generados:")
        print("  ├─ htmlcov/index.html  (Reporte visual)")
        print("  ├─ coverage.json       (Datos JSON)")
        print("  └─ metrics.json        (Métricas completas)")
        print("=" * 70 + "\n")

    def save_metrics(self, filename='metrics.json'):
        """Guarda métricas en archivo JSON"""
        metrics_file = self.project_root / filename
        with open(metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f" Métricas guardadas en {filename}")

#Función principal
def main():
    runner = MetricsRunner()
    success = runner.run_tests_with_metrics()

    print("\n TIP: Para ver el reporte visual ejecuta:")
    print("   start htmlcov/index.html   # Windows")

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())