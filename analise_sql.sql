#Pergunta 1
SELECT COUNT(*) 
FROM `datario.administracao_servicos_publicos.chamado_1746` 
WHERE DATE(data_inicio) = "2023-04-01";

#Pergunta 2
SELECT tipo, SUM(reclamacoes) AS total_reclamacoes
FROM `datario.administracao_servicos_publicos.chamado_1746`
WHERE DATE(data_inicio) = "2023-04-01"
GROUP BY tipo
ORDER BY total_reclamacoes DESC
LIMIT 1;

#Pergunta 3
SELECT bairro.nome, COUNT(id_chamado) AS num_chamados
FROM `datario.administracao_servicos_publicos.chamado_1746` AS chamados JOIN `datario.dados_mestres.bairro` AS bairro
ON chamados.id_bairro = bairro.id_bairro
WHERE DATE(data_inicio) = "2023-04-01"
GROUP BY bairro.nome
ORDER BY num_chamados DESC
LIMIT 3;

#Pergunta 4
SELECT bairro.subprefeitura, COUNT(id_chamado) AS num_chamados
FROM `datario.administracao_servicos_publicos.chamado_1746` AS chamados JOIN `datario.dados_mestres.bairro` AS bairro
ON chamados.id_bairro = bairro.id_bairro
WHERE DATE(chamados.data_inicio) = '2023-04-01'
GROUP BY bairro.subprefeitura
ORDER BY num_chamados DESC
LIMIT 1;

#Pergunta 5
SELECT *
FROM `datario.administracao_servicos_publicos.chamado_1746` AS chamados
WHERE DATE(chamados.data_inicio) = '2023-04-01' AND chamados.id_bairro IS NULL;

SELECT *
FROM `datario.dados_mestres.bairro` AS bairro
WHERE bairro.subprefeitura IS NULL;

#Pergunta 6
SELECT COUNT(*)
FROM `datario.administracao_servicos_publicos.chamado_1746`
WHERE subtipo = 'Perturbação do sossego' AND DATE(data_inicio) >= '2022-01-01' AND DATE(data_inicio) <= '2023-12-31';

#Pergunta 7
SELECT chamado.*
FROM `datario.administracao_servicos_publicos.chamado_1746` AS chamado, `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` AS eventos
WHERE chamado.subtipo = 'Perturbação do sossego' AND DATE(chamado.data_inicio) >= eventos.data_inicial AND DATE(chamado.data_inicio) <= eventos.data_final;

#Pergunta 8
SELECT eventos.evento, COUNT(*)
FROM `datario.administracao_servicos_publicos.chamado_1746` AS chamado, `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` AS eventos
WHERE chamado.subtipo = 'Perturbação do sossego' AND DATE(chamado.data_inicio) >= eventos.data_inicial AND DATE(chamado.data_inicio) <= eventos.data_final
GROUP BY eventos.evento;

#Pergunta 9
WITH num_chamados_por_dia AS (
  SELECT DATE(chamado.data_inicio), eventos.evento, COUNT(*) as num_chamados
  FROM `datario.administracao_servicos_publicos.chamado_1746` AS chamado, `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` AS eventos
  WHERE chamado.subtipo = 'Perturbação do sossego' AND DATE(chamado.data_inicio) >= eventos.data_inicial AND DATE(chamado.data_inicio) <= eventos.data_final
  GROUP BY DATE(chamado.data_inicio), eventos.evento
)
SELECT num_chamados_por_dia.evento, AVG(num_chamados_por_dia.num_chamados) AS media_de_chamados_por_dia
FROM num_chamados_por_dia
GROUP BY num_chamados_por_dia.evento
ORDER BY media_de_chamados_por_dia DESC
LIMIT 1;

#Pergunta 10
WITH num_chamados_por_dia_2_anos AS (
  SELECT DATE(chamado.data_inicio), COUNT(*) as num_chamados
  FROM `datario.administracao_servicos_publicos.chamado_1746` AS chamado
  WHERE chamado.subtipo = 'Perturbação do sossego' AND DATE(chamado.data_inicio) >= '2022-01-01' AND DATE(chamado.data_inicio) <= '2023-12-31'
  GROUP BY DATE(chamado.data_inicio)
)
SELECT AVG(num_chamados)
FROM num_chamados_por_dia_2_anos;

WITH num_chamados_por_dia AS (
  SELECT DATE(chamado.data_inicio) as data, eventos.evento, COUNT(*) as num_chamados
  FROM `datario.administracao_servicos_publicos.chamado_1746` AS chamado, `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos` AS eventos
  WHERE chamado.subtipo = 'Perturbação do sossego' AND DATE(chamado.data_inicio) >= eventos.data_inicial AND DATE(chamado.data_inicio) <= eventos.data_final
  GROUP BY DATE(chamado.data_inicio), eventos.evento
)
SELECT AVG(num_chamados_por_dia.num_chamados)
FROM num_chamados_por_dia;