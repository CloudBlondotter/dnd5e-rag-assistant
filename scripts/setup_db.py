#!/usr/bin/env python3
# -------------------------------------------------------------------------#
# SETUP_DB - Script de inicialización y gestión de la base de datos vectorial
# -------------------------------------------------------------------------#

"""
Script de utilidad para gestionar la base de datos vectorial de D&D 5E

Funcionalidades:
• Inicializar nueva base de datos
• Actualizar base de datos existente  
• Resetear completamente la base de datos
• Mostrar estadísticas de la base de datos
• Añadir documentos específicos
"""

import argparse
import sys
import os
from pathlib import Path

# Añadir el directorio src al path para importar módulos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    # ✅ CORRECCIÓN 1: Cambiar vector_final por vector_pipeline
    from vector_pipeline import (
        init_or_update,
        reset_database,
        get_database_stats,
        process_markdown_files,
        load_existing_database
    )  # ✅ CORRECCIÓN 2: Añadir paréntesis de cierre
    
    # ✅ CORRECCIÓN 3: Importar de config.py las rutas correctas
    from config import DATA_DIR, DB_DIR, PROJECT_ROOT
    
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de que estás ejecutando desde el directorio raíz del proyecto")
    sys.exit(1)

# -------------------------------------------------------------------------#
# FUNCIONES DE GESTIÓN DE BASE DE DATOS
# -------------------------------------------------------------------------#

def initialize_database(force: bool = False):
    """
    Inicializa o actualiza la base de datos vectorial.
    
    Args:
        force: Si True, resetea la base de datos antes de inicializar
    """
    print("🐉 Inicializando base de datos de D&D 5E...")
    print(f"📁 Directorio de datos: {DATA_DIR}")
    print(f"🗄️  Directorio de BD: {DB_DIR}")
    print("-" * 60)
    
    if force and DB_DIR.exists():
        print("⚠️  Modo forzado activado - reseteando base de datos...")
        if reset_database():
            print("✅ Base de datos reseteada correctamente")
        else:
            print("❌ Error reseteando la base de datos")
            return False
    
    try:
        vector_store = init_or_update()
        if vector_store:
            print("\n✅ ¡Base de datos inicializada correctamente!")
            show_stats()
            return True
        else:
            print("\n❌ Error durante la inicialización")
            return False
            
    except FileNotFoundError:
        print(f"\n❌ Error: No se encontró el directorio de datos: {DATA_DIR}")
        print("💡 Asegúrate de tener archivos Markdown en la carpeta data/markdown/")
        return False
        
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        return False

def show_stats():
    """Muestra estadísticas de la base de datos."""
    print("\n📊 Estadísticas de la Base de Datos")
    print("=" * 40)
    
    stats = get_database_stats()
    
    if stats["status"] == "no_database":
        print("📭 No existe base de datos")
        
    elif stats["status"] == "error":
        print(f"❌ Error obteniendo estadísticas: {stats['error']}")
        
    elif stats["status"] == "active":
        print(f"📄 Documentos indexados: {stats['document_count']:,}")
        print(f"📁 Archivos procesados: {stats['processed_files']}")
        print(f"🕐 Última actualización: {stats['last_update']}")
        print(f"💾 Ubicación: {DB_DIR}")
        
        # Información adicional del directorio
        if DB_DIR.exists():
            total_size = sum(f.stat().st_size for f in DB_DIR.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            print(f"📦 Tamaño en disco: {size_mb:.2f} MB")

def reset_database_interactive():
    """Resetea la base de datos con confirmación interactiva."""
    print("⚠️  ADVERTENCIA: Esta acción eliminará completamente la base de datos")
    print("🗄️  Ubicación:", DB_DIR)
    
    if not DB_DIR.exists():
        print("📭 No existe base de datos para resetear")
        return
        
    # Mostrar stats antes del reset
    stats = get_database_stats()
    if stats["status"] == "active":
        print(f"📊 Se perderán {stats['document_count']} documentos indexados")
    
    # Confirmación
    confirm = input("\n❓ ¿Estás seguro? Escribe 'RESET' para confirmar: ")
    
    if confirm.strip().upper() == "RESET":
        print("\n🗑️  Reseteando base de datos...")
        if reset_database():
            print("✅ Base de datos reseteada correctamente")
        else:
            print("❌ Error durante el reseteo")
    else:
        print("🚫 Operación cancelada")

def check_prerequisites():
    """Verifica que el entorno esté correctamente configurado."""
    print("🔍 Verificando prerrequisitos...")
    
    issues = []
    
    # Verificar directorio de datos
    if not DATA_DIR.exists():
        issues.append(f"❌ Directorio de datos no existe: {DATA_DIR}")
    elif not any(DATA_DIR.rglob("*.md")):
        issues.append(f"⚠️  No se encontraron archivos .md en: {DATA_DIR}")
    else:
        md_files = list(DATA_DIR.rglob("*.md"))
        print(f"✅ Encontrados {len(md_files)} archivos Markdown")
    
    # Verificar directorios de almacenamiento
    storage_dir = PROJECT_ROOT / "storage"
    if not storage_dir.exists():
        print(f"📁 Creando directorio storage: {storage_dir}")
        storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Verificar dependencias (importaciones ya verificadas arriba)
    print("✅ Dependencias Python disponibles")
    
    if issues:
        print("\n⚠️  Problemas encontrados:")
        for issue in issues:
            print(f"  {issue}")
        return False
    
    print("✅ Todos los prerrequisitos están OK")
    return True

def add_specific_files(file_paths: list):
    """
    Añade archivos específicos a la base de datos.
    
    Args:
        file_paths: Lista de rutas de archivos a procesar
    """
    print(f"📥 Añadiendo {len(file_paths)} archivos específicos...")
    
    # Verificar que los archivos existen
    valid_files = []
    for file_path in file_paths:
        path = Path(file_path)
        if path.exists() and path.suffix.lower() in ['.md', '.markdown']:
            valid_files.append(str(path))
        else:
            print(f"⚠️  Archivo no válido o no encontrado: {file_path}")
    
    if not valid_files:
        print("❌ No hay archivos válidos para procesar")
        return False
    
    try:
        # Procesar archivos
        documents = process_markdown_files(valid_files)
        
        if not documents:
            print("❌ No se generaron documentos")
            return False
        
        # Cargar base de datos existente o crear nueva
        if DB_DIR.exists():
            vector_store = load_existing_database()
            vector_store.add_documents(documents)
            print(f"✅ Añadidos {len(documents)} chunks a la base de datos existente")
        else:
            from vector_pipeline import create_vector_database
            vector_store = create_vector_database(documents)
            print(f"✅ Creada nueva base de datos con {len(documents)} chunks")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando archivos: {e}")
        return False

# -------------------------------------------------------------------------#
# INTERFAZ DE LÍNEA DE COMANDOS
# -------------------------------------------------------------------------#

def create_parser():
    """Crea el parser de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="🐉 Gestor de Base de Datos Vectorial para D&D 5E",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python setup_db.py init                    # Inicializar/actualizar BD
  python setup_db.py init --force            # Resetear e inicializar BD
  python setup_db.py stats                   # Mostrar estadísticas
  python setup_db.py reset                   # Resetear BD (interactivo)
  python setup_db.py check                   # Verificar prerrequisitos
  python setup_db.py add file1.md file2.md   # Añadir archivos específicos
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando init
    init_parser = subparsers.add_parser('init', help='Inicializar o actualizar la base de datos')
    init_parser.add_argument('--force', action='store_true', 
                           help='Fuerza el reseteo antes de inicializar')
    
    # Comando stats
    subparsers.add_parser('stats', help='Mostrar estadísticas de la base de datos')
    
    # Comando reset
    subparsers.add_parser('reset', help='Resetear completamente la base de datos')
    
    # Comando check
    subparsers.add_parser('check', help='Verificar prerrequisitos del sistema')
    
    # Comando add
    add_parser = subparsers.add_parser('add', help='Añadir archivos específicos')
    add_parser.add_argument('files', nargs='+', help='Rutas de archivos a añadir')
    
    return parser

def main():
    """Función principal del script."""
    print("🐉 Gestor de Base de Datos D&D 5E")
    print("=" * 50)
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Si no se proporciona comando, mostrar ayuda
    if not args.command:
        parser.print_help()
        return
    
    # Ejecutar comando correspondiente
    if args.command == 'check':
        check_prerequisites()
        
    elif args.command == 'init':
        if check_prerequisites():
            initialize_database(force=args.force)
        else:
            print("\n❌ No se puede inicializar: faltan prerrequisitos")
            sys.exit(1)
            
    elif args.command == 'stats':
        show_stats()
        
    elif args.command == 'reset':
        reset_database_interactive()
        
    elif args.command == 'add':
        if check_prerequisites():
            add_specific_files(args.files)
        else:
            print("\n❌ No se pueden añadir archivos: fallan prerrequisitos")
            sys.exit(1)

if __name__ == "__main__":
    main()
