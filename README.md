Painel DW-BR
============

[![Deploy to dev VM](https://github.com/andrespp/dash-br/actions/workflows/deploy_dev.yml/badge.svg)](https://github.com/andrespp/dash-br/actions/workflows/deploy_dev.yml)

## Introdução

Ferramenta de visualização do [DW-BR](https://github.com/andrespp/dw-br/).

## Implantação e Utilização

### Clone do Repositório

```bash
$ git clone https://github.com/andrespp/dash-br.git
```

### Configurar os parâmetros de conexões

Para configurar os parâmetros da aplicação,  as variáveis do arquivo
`config.ini` devem ser definidas.

### Instalação de Requisitos

* Instalação do gerenciador de pacotes [Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)

* Criação do ambiente de execução da aplicação

```bash
$ conda env create -f environment.yml
```

### Execução da Aplicação
```bash
$ conda activate dash-dwbr
$ python index.py
```

## Referências
