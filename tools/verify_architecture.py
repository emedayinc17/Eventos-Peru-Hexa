#!/usr/bin/env python3
"""
Script de verificación de arquitectura hexagonal
Verifica que todos los servicios cumplan con la estructura esperada
Created by emeday 2025
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file_exists(path: Path) -> bool:
    """Verifica si un archivo existe"""
    return path.exists() and path.is_file()

def check_dir_exists(path: Path) -> bool:
    """Verifica si un directorio existe"""
    return path.exists() and path.is_dir()

def verify_service_structure(service_path: Path, service_name: str) -> Dict[str, List[Tuple[str, bool]]]:
    """Verifica la estructura de un servicio"""
    results = {
        "required_files": [],
        "required_dirs": [],
        "domain_layer": [],
        "application_layer": [],
        "infrastructure_layer": [],
        "entrypoints_layer": []
    }
    
    # Archivos requeridos en la raíz del servicio
    required_files = [
        ".env",
        "requirements.txt",
        "run.ps1",
        "run.bat"
    ]
    
    for file in required_files:
        file_path = service_path / file
        exists = check_file_exists(file_path)
        results["required_files"].append((file, exists))
    
    # Directorios requeridos
    required_dirs = [
        "app",
        "app/domain",
        "app/application",
        "app/infrastructure",
        "app/entrypoints",
        "app/entrypoints/fastapi"
    ]
    
    for dir_name in required_dirs:
        dir_path = service_path / dir_name
        exists = check_dir_exists(dir_path)
        results["required_dirs"].append((dir_name, exists))
    
    # Capa de Dominio
    domain_files = [
        "app/domain/__init__.py",
        "app/domain/models.py"
    ]
    
    for file in domain_files:
        file_path = service_path / file
        exists = check_file_exists(file_path)
        results["domain_layer"].append((file, exists))
    
    # Capa de Aplicación
    application_files = [
        "app/application/__init__.py",
        "app/application/use_cases.py"
    ]
    
    for file in application_files:
        file_path = service_path / file
        exists = check_file_exists(file_path)
        results["application_layer"].append((file, exists))
    
    # Capa de Infraestructura
    infrastructure_files = [
        "app/infrastructure/__init__.py",
        "app/infrastructure/db/__init__.py"
    ]
    
    for file in infrastructure_files:
        file_path = service_path / file
        exists = check_file_exists(file_path)
        results["infrastructure_layer"].append((file, exists))
    
    # Capa de Entrypoints
    entrypoints_files = [
        "app/entrypoints/__init__.py",
        "app/entrypoints/fastapi/__init__.py",
        "app/entrypoints/fastapi/main.py",
        "app/entrypoints/fastapi/router.py"
    ]
    
    for file in entrypoints_files:
        file_path = service_path / file
        exists = check_file_exists(file_path)
        results["entrypoints_layer"].append((file, exists))
    
    return results

def print_results(service_name: str, results: Dict[str, List[Tuple[str, bool]]]) -> int:
    """Imprime los resultados de verificación"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}🔍 Verificando: {service_name.upper()}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    errors = 0
    
    for category, items in results.items():
        category_title = category.replace("_", " ").title()
        print(f"{YELLOW}📁 {category_title}:{RESET}")
        
        for item_name, exists in items:
            if exists:
                print(f"  {GREEN}✓{RESET} {item_name}")
            else:
                print(f"  {RED}✗{RESET} {item_name} {RED}(FALTANTE){RESET}")
                errors += 1
        
        print()
    
    return errors

def verify_shared_lib(base_path: Path) -> int:
    """Verifica la librería compartida"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}🔍 Verificando: SHARED LIBRARY{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    shared_path = base_path / "libs" / "shared" / "ev_shared"
    
    required_files = [
        "__init__.py",
        "config.py",
        "db.py",
        "logger.py",
        "http_debug.py"
    ]
    
    errors = 0
    
    print(f"{YELLOW}📦 Archivos Core:{RESET}")
    for file in required_files:
        file_path = shared_path / file
        if check_file_exists(file_path):
            print(f"  {GREEN}✓{RESET} {file}")
        else:
            print(f"  {RED}✗{RESET} {file} {RED}(FALTANTE){RESET}")
            errors += 1
    
    print(f"\n{YELLOW}🔐 Módulo Security:{RESET}")
    security_files = ["security/__init__.py", "security/passwords.py", "security/jwt.py"]
    for file in security_files:
        file_path = shared_path / file
        if check_file_exists(file_path):
            print(f"  {GREEN}✓{RESET} {file}")
        else:
            print(f"  {RED}✗{RESET} {file} {RED}(FALTANTE){RESET}")
            errors += 1
    
    print()
    return errors

def main():
    """Función principal"""
    base_path = Path(__file__).parent
    services_path = base_path / "services"
    
    if not services_path.exists():
        print(f"{RED}Error: No se encontró el directorio 'services'{RESET}")
        sys.exit(1)
    
    print(f"{GREEN}{'='*80}{RESET}")
    print(f"{GREEN}🏗️  VERIFICACIÓN DE ARQUITECTURA HEXAGONAL{RESET}")
    print(f"{GREEN}{'='*80}{RESET}")
    
    # Verificar librería compartida
    shared_errors = verify_shared_lib(base_path)
    
    # Servicios a verificar
    services = [
        "iam-service",
        "catalogo-service",
        "proveedores-service",
        "contratacion-service"
    ]
    
    total_errors = shared_errors
    service_results = {}
    
    # Verificar cada servicio
    for service in services:
        service_path = services_path / service
        if not service_path.exists():
            print(f"{RED}⚠️  Servicio no encontrado: {service}{RESET}")
            continue
        
        results = verify_service_structure(service_path, service)
        errors = print_results(service, results)
        total_errors += errors
        service_results[service] = errors
    
    # Resumen final
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}📊 RESUMEN FINAL{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    
    if total_errors == 0:
        print(f"{GREEN}✅ TODOS LOS SERVICIOS ESTÁN CORRECTAMENTE ESTRUCTURADOS{RESET}")
        print(f"{GREEN}🎉 Arquitectura Hexagonal: VÁLIDA{RESET}\n")
    else:
        print(f"{RED}❌ Se encontraron {total_errors} errores en total{RESET}\n")
        
        print(f"{YELLOW}Errores por servicio:{RESET}")
        print(f"  Shared Library: {shared_errors} errores")
        for service, errors in service_results.items():
            status = f"{GREEN}✓{RESET}" if errors == 0 else f"{RED}✗{RESET}"
            print(f"  {status} {service}: {errors} errores")
        
        print(f"\n{YELLOW}💡 Revisa el archivo CORRECCIONES_HEXAGONAL.md para más detalles{RESET}\n")
        sys.exit(1)
    
    print(f"{GREEN}{'='*80}{RESET}\n")

if __name__ == "__main__":
    main()
