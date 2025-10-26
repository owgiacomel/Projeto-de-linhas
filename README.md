# Projeto-de-linhas

Este repositório contém o plugin **Flight Line Connector** para o QGIS. O plugin automatiza a criação de linhas contínuas de voo e das zonas de não pulverização necessárias para drones de aplicação agrícola.

## Funcionalidades

- Conecta automaticamente as extremidades das linhas selecionadas (ou de todas as linhas da camada ativa) para formar o trajeto contínuo do drone.
- Gera um polígono de segurança 10 metros mais curto do que cada linha de ligação criada e com largura de 5 metros para cada lado.
- Armazena as linhas geradas na camada "Linhas de Ligação" e os polígonos na camada "Zonas de Não Pulverização" dentro do projeto QGIS.

## Como usar

1. Instale o plugin copiando a pasta `flight_line_connector` para o diretório de plugins do QGIS.
2. Abra um projeto com uma camada vetorial de linhas representando as faixas de pulverização.
3. Selecione as linhas que deseja conectar (ou deixe sem seleção para usar todas as linhas).
4. Clique no botão **Criar linhas contínuas e áreas de segurança** na barra de ferramentas do QGIS.
5. As novas camadas com as linhas de ligação e zonas de não pulverização serão adicionadas ao projeto.

## Requisitos

- QGIS 3.22 ou superior.

## Licença

Este projeto é distribuído sob a licença MIT.
