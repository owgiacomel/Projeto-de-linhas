# Projeto-de-linhas

Este repositório contém o plugin **Flight Line Connector** para o QGIS. O plugin automatiza a criação de linhas contínuas de voo e das zonas de não pulverização necessárias para drones de aplicação agrícola.

## Funcionalidades

- Conecta automaticamente as extremidades das linhas selecionadas (ou de todas as linhas da camada ativa) para formar o trajeto contínuo do drone.
- Gera um polígono de segurança 10 metros mais curto do que cada linha de ligação criada e com largura de 5 metros para cada lado.
- Armazena as linhas geradas na camada "Linhas de Ligação" e os polígonos na camada "Zonas de Não Pulverização" dentro do projeto QGIS.

## Instalação

1. Clone ou baixe este repositório.
2. Gere o pacote ZIP do plugin executando `python scripts/package_plugin.py`. O arquivo `dist/flight_line_connector.zip` será criado e possui a estrutura correta para o QGIS.
   - Alternativamente, copie apenas a pasta `flight_line_connector` (sem o diretório superior) para o diretório de plugins do QGIS.
3. No QGIS, utilize a opção **Instalar a partir de ZIP** e selecione o arquivo `dist/flight_line_connector.zip` gerado no passo anterior.
4. Ative o plugin através do Gerenciador de Plugins.

> **Importante:** o QGIS não consegue carregar um plugin quando o nome da pasta contém hífens (por exemplo, `Projeto-de-linhas-main`). Certifique-se de instalar utilizando o arquivo ZIP gerado ou renomeie a pasta para `flight_line_connector` antes de copiar para o diretório de plugins.

## Como usar

1. Abra um projeto com uma camada vetorial de linhas representando as faixas de pulverização.
2. Selecione as linhas que deseja conectar (ou deixe sem seleção para usar todas as linhas).
3. Clique no botão **Criar linhas contínuas e áreas de segurança** na barra de ferramentas do QGIS.
4. As novas camadas com as linhas de ligação e zonas de não pulverização serão adicionadas ao projeto.

## Requisitos

- QGIS 3.22 ou superior.

## Licença

Este projeto é distribuído sob a licença MIT.
