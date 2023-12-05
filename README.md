# Análise de Rede - Dashboard
## Visão Geral
Este é um dashboard baseado na web para analisar dados de comunicação de rede em cenários industriais. O dashboard permite que os usuários carreguem arquivos CSV contendo informações de pacotes de rede e fornece insights sobre detalhes dos pacotes, distribuição de protocolos e métricas estatísticas.

## Instalação
### Pré-requisitos:
- Python 3.9
- pip (instalador de pacotes do Python)
- Configurar Ambiente Virtual

## Configurar Ambiente Virtual
```python
# Clonar o repositório
git clone https://github.com/joaoaxerb/analise_redes.git

# Navegar até o diretório do projeto
cd dashboard

# Criar um ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# No Windows
venv\Scripts\activate

# No Unix ou MacOS
source venv/bin/activate
```
## Instalar Dependências
```python
# Instalar pacotes necessários
pip install -r requirements.txt
```
## Uso
### Executar o Dashboard
```python
# Certifique-se de que o ambiente virtual está ativado
# No Windows
venv\Scripts\activate

# No Unix ou MacOS
source venv/bin/activate

# Executar o aplicativo
python3 dashboard_8.py
```
### Upload de Dados
1. Acesse http://127.0.0.1:8050/ em seu navegador.
2. Utilize as seções de upload de arquivo para selecionar arquivos CSV para os Cenários 1 e 2.
3. Escolha o cenário a ser analisado no menu suspenso.

### Abas
- Visão Geral dos Pacotes: Fornece uma visão geral das estatísticas e visualizações de pacotes.
- Detalhes dos Pacotes: Exibe uma tabela com informações detalhadas sobre os pacotes capturados.
- Métricas Estatísticas: Apresenta métricas estatísticas e distribuições para o comprimento dos pacotes e o intervalo entre chegadas.

## Contribuições
Sinta-se à vontade para contribuir para o desenvolvimento deste dashboard, enviando problemas ou solicitações de pull.
