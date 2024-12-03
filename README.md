# Velocidade, Aceleração e Bandas

## Descrição  
Este projeto é uma aplicação desenvolvida em **Streamlit** para realizar cálculos de velocidade, aceleração e bandas passantes de trajetórias nominais cartesianas em referenciais locais ENU (East-North-Up). Ele permite carregar arquivos CSV com coordenadas, realizar cálculos com base em parâmetros configurados pelo usuário, e exibir resultados de forma interativa com gráficos e tabelas.

---

## Funcionalidades  
- Conversão de coordenadas entre sistemas ENU diferentes.  
- Cálculo de velocidades e acelerações em referenciais cartesianos e polares.  
- Determinação de bandas de aquisição e regime com base em parâmetros de erro configuráveis.  
- Visualização de gráficos interativos para análise.

---

## Pré-requisitos  

### Windows  
1. Instale o Python (>= 3.8) através do [site oficial do Python](https://www.python.org/).  
2. Certifique-se de que o **pip** está instalado. Você pode verificar usando:  
   ```bash  
   python -m ensurepip  
   python -m pip install --upgrade pip  
   ```  

### Linux (Debian/Ubuntu)  
1. Atualize os pacotes do sistema e instale o Python caso não tenha instalado:  
   ```bash  
   sudo apt update && sudo apt upgrade -y  
   sudo apt install python3 python3-pip -y  
   ```  

2. Atualize o pip:  
   ```bash  
   python3 -m pip install --upgrade pip  
   ```  

---

## Instalação  

1. Clone este repositório:  
   ```bash  
   git clone https://github.com/francisvalguedes/radarbands.git  
   cd radarbands  
   ```  

2. Crie e ative um ambiente virtual:  
   - No Windows:  
     ```bash  
     python -m venv venv  
     env\Scripts\activate
     pip install --upgrade pip
     ```  
   - No Linux:  
     ```bash  
     pip install virtualenv
     virtualenv env     
     source env/bin/activate 
     pip install --upgrade pip 
     ```  


3. Instale as dependências do projeto:  
   ```bash  
   pip install -r requirements.txt  
   ```  

---

## Execução  

1. Navegue até o diretório do projeto (se ainda não estiver).  
2. Execute o aplicativo:  
   ```bash  
   streamlit run source/main.py  
   ```  
3. Abra o navegador no endereço fornecido pelo terminal (geralmente `http://localhost:8501`).  
4. Em caso de instalação em servidor linux opcionalmente pode ser agendada a inicialização do Crontab com a execução do arquivo run.sh que cria também um log de eventos do aplicativo:
   ```bash
   ./run.sh
   ```

---

## Estrutura do Projeto  
```
.
├── source/  
│   ├── main.py  
│   ├── pages/  
│   │   └── Velocidade, Aceleração e Bandas.py  
├── lib/  
│   ├── constants.py  
│   └── pgFunctions.py  
├── data/  
│   └── confLocalWGS84.csv  
├── requirements.txt  
└── README.md  
```  

---

## Bibliotecas Utilizadas  
- **Streamlit**: Interface interativa.  
- **Pandas**: Manipulação de dados.  
- **Numpy**: Cálculos matemáticos e array.  
- **Plotly**: Visualização de dados interativa.  
- **Pymap3d**: Conversões de coordenadas geodésicas e ENU.  

---

## Licença  
Licenciado sob a **MIT License**. Consulte o arquivo LICENSE para mais detalhes.

---

## Autor  
Iniciado por: **Francisval Guedes Soares**  
Ano: 2024  
