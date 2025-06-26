# controller/builder_layer.py

import os
import shutil
import subprocess
import sys

class BuilderLayer:
    """
    Uma classe para orquestrar a construção, empacotamento e publicação 
    de uma AWS Lambda Layer a partir de um arquivo requirements.txt.
    """
    def __init__(self, layer_name, python_version, req_file, region_name='sa-east-1'):
        """
        Inicializa o builder com as configurações necessárias.

        Args:
            layer_name (str): Nome da Layer que será criada na AWS.
            python_version (str): Versão do Python que a Layer irá suportar (ex: "3.9", "3.10").
            req_file (str): Caminho para o arquivo requirements.txt contendo as dependências.
        """
        self.layer_name = layer_name
        self.python_version = python_version
        self.requirements_file = req_file
        self.region_name = region_name
        
        # Atributos internos do processo de build
        self.build_dir = "build"
        self.output_zip = f"{layer_name}.zip"

    def run(self):
        """
        Executa todas as etapas do processo de build e publicação da Layer.
        """
        # A limpeza inicial agora é a primeira etapa dentro do 'run'
        # para garantir um ambiente limpo antes de começar.
        self._cleanup(initial=True)
        try:
            print(f"🚀 Iniciando a criação da Layer '{self.layer_name}'...")
            self._create_structure()
            self._install_dependencies()
            self._package_layer()
            self._publish_to_aws()
            print("\n----------------------------------------------------")
            print(f"✅ Processo finalizado! Layer '{self.layer_name}' publicada com sucesso.")
            print("----------------------------------------------------")
        
        finally:
            # Garante que a limpeza final dos arquivos de build sempre ocorra
            print("\n--- Limpando arquivos temporários ---")
            self._cleanup(initial=False)

    def _cleanup(self, initial=True):
        """
        Remove a pasta de build e/ou o .zip.

        Args:
            initial (bool): Se True, remove tanto a pasta de build quanto o arquivo zip.
                            Se False, remove apenas a pasta de build.
        """
        if os.path.exists(self.build_dir):
            shutil.rmtree(self.build_dir)
            if initial:
                print(f"Pasta de build antiga '{self.build_dir}' removida.")
        
        if os.path.exists(self.output_zip):
            if initial:
                os.remove(self.output_zip)
                print(f"Arquivo zip antigo '{self.output_zip}' removido.")

    def _create_structure(self):
        """
        Cria a estrutura de pastas correta para a Layer (build/python).
        """
        print("\n--- Etapa 1: Criando estrutura de pastas ---")
        self.layer_path = os.path.join(self.build_dir, "python")
        os.makedirs(self.layer_path)
        print(f"Diretório de trabalho criado em: '{self.layer_path}'")

    def _install_dependencies(self):
        """
        Instala as dependências usando pip.
        """
        print(f"\n--- Etapa 2: Instalando dependências de '{self.requirements_file}' ---")
        pip_command = [
            sys.executable, "-m", "pip", "install",
            "--platform", "manylinux2014_x86_64",
            "--implementation", "cp",
            f"--python-version", self.python_version,
            "--only-binary=:all:",
            "--requirement", self.requirements_file,
            "--target", self.layer_path
        ]
        self._run_command(pip_command, "Falha ao instalar dependências com o pip.")

    def _package_layer(self):
        """
        Empacota o conteúdo da pasta de build em um arquivo .zip.
        """
        print(f"\n--- Etapa 3: Empacotando a Layer em '{self.output_zip}' ---")
        shutil.make_archive(self.output_zip.replace('.zip', ''), 'zip', self.build_dir)
        print("Empacotamento concluído.")

    def _publish_to_aws(self):
        """
        Publica a Layer na AWS usando o AWS CLI.
        """
        print("\n--- Etapa 4: Publicando a Layer na AWS ---")
        aws_command = [
            "aws", "lambda", "publish-layer-version",
            "--layer-name", self.layer_name,
            "--description", f"Dependências de {self.requirements_file}",
            "--zip-file", f"fileb://{self.output_zip}",
            "--compatible-runtimes", f"python{self.python_version}",
            "--region", f"{self.region_name}"
        ]
        self._run_command(aws_command, "Falha ao publicar a Layer na AWS.")

    @staticmethod
    def _run_command(command, error_message):
        """
        Método estático para executar um comando no terminal, com tratamento
        de erro de codificação para ambientes Windows.
        """
        print(f"Executando: {' '.join(command)}")
        try:
            # Alteração principal: Não forçamos mais a decodificação.
            # Capturamos a saída como bytes e decodificamos depois com 'errors=replace'.
            result = subprocess.run(command, check=True, capture_output=True)
            
            # Opcional: imprimir a saída para debug
            if result.stdout:
               print(result.stdout.decode(errors='replace'))

        except FileNotFoundError:
            print(f"Erro: O comando '{command[0]}' não foi encontrado. Verifique se ele está instalado e no PATH do sistema.")
            sys.exit(1)
        
        except subprocess.CalledProcessError as e:
            # Decodifica a saída de erro substituindo caracteres problemáticos
            stderr_output = e.stderr.decode(errors='replace').strip()
            print(f"ERRO: {error_message}")
            print(f"Saída do erro:\n{stderr_output}")
            sys.exit(1)
