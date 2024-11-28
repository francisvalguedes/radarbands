#!/bin/bash

# Instala o virtualenv, caso não esteja instalado
pip install virtualenv
# Cria um novo ambiente virtual chamado 'env'
virtualenv env
# Ativa o ambiente virtual
source env/bin/activate
# Atualiza o pip para a versão mais recente
pip install --upgrade pip
# Instala as dependências do arquivo requirements.txt
pip install -r requirements.txt