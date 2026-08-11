# GymTrack

Este site fornece uma plataforma para que os usuários organizem e registrem seus treinos, permitindo visualizar os exercícios realizados em tabelas e acompanhar o desenvolvimento pessoal ao longo do tempo por meio de dashboards.

# Estrutura

O projeto foi executado com o uso das seguintes ferramentas:

`Python`: linguagem principal
`Streamlit`: construção da interface web
`SQLite`: banco de dados
`Plotly`: criação de gráficos interativos para os dashboards
`Pandas`: manipulação e análise de dados

A interface da aplicação foi desenvolvida utilizando Streamlit, que permite a sua criação diretamente em Python. 

# Funcionalidade

O site possui seções de cadastro e login, feitos com email e senha. Os usuários logados conseguem visualizar uma seção para cadastro de treinos, permitindo a organização dos exercícios conforme as listas de treinamentos que estão realizando. Os usuários podem visualizar os treinos cadastrados, alterá-los e apagá-los, se desejarem. Caso haja algum exercício que os usuários conheçam que não esteja registrado na plataforma, essa seção permite o registro de novos exercícios, porém apenas o administrador tem o poder de excluir exercícios criados. Também há uma seção para o lançamento dos treinos realizados no dia, permitindo a definição do número de séries, repetições, o peso e, em caso de exercício aeróbico, a velocidade. Por fim, a seção de dashboard permite a visualização de gráficos que representam a evolução do usuário ao longo do tempo em termos de peso utilizado (por exercício), quantidade de treinos por mês, velocidade e tempo de treinameno. 

# Execução (Desenvolvimento)

```bash
git clone https://github.com/Ivanictor/GymTrack.git
cd GymTrack
streamlit run app.py
```

