from build.builder_layer import BuilderLayer
from utils.import_aws_credentials import AWS_SERVICES
from dotenv import load_dotenv


REGION_NAME = 'sa-east-1'

# -----------------------------------------------------------------
# Importando as credenciais AWS
load_dotenv()

AWS_SERVICES(region_name=REGION_NAME)
# -----------------------------------------------------------------

# -----------------------------------------------------------------
# ARQUIVO DE CONFIGURAÇÃO
# Altere as variáveis abaixo para configurar sua Layer.
# -----------------------------------------------------------------
def start_controller():
    """
    Função que inicia o controlador de criação de Layer.
    """
    print("Iniciando o controlador de criação de Layer...")

    # Nome que a sua Layer terá na AWS.
    # Dica: use um padrão, como 'meu-projeto-layer-dependencias'
    LAYER_NAME = "acelerador-lambda-layer"

    # A versão exata do runtime Python que seu Lambda utiliza.
    # (Exemplos: "3.9", "3.10", "3.11", "3.12")
    PYTHON_VERSION = "3.13"

    # O nome do seu arquivo de dependências.
    REQUIREMENTS_FILE = "requirements.txt"

    # 1. Instancia o controlador com as configurações definidas acima.
    layer_builder = BuilderLayer(
        layer_name=LAYER_NAME,
        python_version=PYTHON_VERSION,
        req_file=REQUIREMENTS_FILE,
        region_name=REGION_NAME
    )

    # 2. Executa o processo de build e publicação.
    layer_builder.run()


# -----------------------------------------------------------------
# LÓGICA DE EXECUÇÃO
# Não é necessário alterar nada abaixo desta linha.
# -----------------------------------------------------------------

if __name__ == "__main__":

    builder = LambdaLayerBuilder(python_version="3.13")
    builder.run()
    # start_controller()
 
