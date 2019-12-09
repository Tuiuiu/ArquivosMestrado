# Arquivos do repositorio:

## Arquivos:

$ teststart2.sh
	- Chama os comandos que inicializarao o arquivo de topologia programado

$ populate_tables.sh
	- Comando para invocar o runtime_cli e popular a tabela inicial

$ set_route_A.sh
	- Comando com as instrucoes que implementarao a Rota A

$ set_route_B.sh
	- Comando com as instrucoes que implementarao a Rota B

$ commandss1_test.txt
  commandss2_test.txt
  commandss3_test.txt
  commandss4_test.txt
  	- Sao os arquivos que descrevem os comandos a serem inicialmente inseridos
  	nas tabelas dos switches cujo nome esta presentes nos nomes desses 
  	arquivos

$ topoteste.py
	- Arquivo contendo a topologia utilizada nos testes

$ router.p4
	- Arquivo em P4 contendo o codigo com o programa P4 executado em cada um dos switches

$ router.json
	- Arquivo compilado do router, no formato JSON, para ser inserido no switch.

$ send.py
	- Programa executado no Host 5, que fara o papel de controlador, com o intuito de se comunicar com os outros monitores para	realizar as medicoes de latencia nas rotas da rede 

$ receive.py
	- Programa executado no Host 6, com o intuito de se comunicar com o Controlador para realizar as medicoes de latencia das rotas da rede 