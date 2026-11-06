# Guia da rede neural (papel 2: IA e match)

Este guia explica o que a rede neural da Pérgamo faz, como ela funciona por dentro, como configurar e como explicar na apresentação.
Os números das tabelas foram medidos com `scikit-learn 1.8.0` e a semente 42; no seu computador podem variar um pouco.

## 1. O que a rede faz, em uma frase

Ela lê as respostas de um perfil (aluno ou professor) e diz **a probabilidade de cada tipo de perfil pedagógico**: Prático, Ouvinte, Visual, Leitor e Racional.

```
Entrada (respostas do formulário)        Saída (probabilidades, somam 100%)
estilos: prático, visual                 Prático   90%
ritmo: rápido                    --->    Visual     6%
estrutura: flexível                      Ouvinte    2%
social: individual                       Leitor     1%
                                         Racional   0,5%
                                         label = Prático (o maior)
```

Essas probabilidades são usadas depois em `ml/match.py`, que compara aluno e professor e calcula a nota de compatibilidade.

## 2. O caminho completo

```
respostas (dicionário)
   |  ml/features.py ......... transforma em 12 números (0 ou 1)
   v
rede neural 12 -> 16 -> 8 -> 5   (arquivo models/perfil_model.joblib)
   |  ml/classifier.py ....... classify(): devolve label e probabilidades
   v
ml/match.py ................. compara aluno x professor e gera a nota (%)
```

| Arquivo | Para que serve |
|---|---|
| `ml/features.py` | Converte o perfil em 12 números. Ordem das colunas: `FEATURE_NAMES`. |
| `ml/dataset.py` | Inventa perfis de treino (dados sintéticos) e salva `data/perfis_sinteticos.csv`. |
| `ml/train.py` | Treina a rede, mede a acurácia e salva `models/perfil_model.joblib` e `models/metricas.json`. |
| `ml/classifier.py` | `classify()`: usa a rede; se o modelo não existir, usa as regras. |
| `tests/test_ml.py` | Testes automáticos desta parte. |

## 3. Como a rede funciona (sem matemática pesada)

**Neurônio.** Recebe números, multiplica cada um por um peso, soma tudo e aplica uma função de ativação (aqui, ReLU: o que for negativo vira zero). O resultado é passado adiante.

**Camadas.** A rede tem 4 camadas: entrada (12 números), duas camadas escondidas (16 e 8 neurônios) e saída (5 neurônios, um por tipo). Cada neurônio de uma camada se liga a todos os da seguinte.

**Pesos.** São os números que a rede ajusta. Nesta rede há 389 (192 + 16 + 128 + 8 + 40 + 5, contando os pesos e os valores de ajuste de cada camada). Começam aleatórios e o treino os melhora.

**Saída.** A última camada usa uma função (softmax) que transforma os 5 resultados em probabilidades que somam 100%.

**Treino.** Repete milhares de vezes: a rede dá um palpite para um exemplo, compara com o tipo correto, calcula o erro e ajusta os pesos um pouquinho para errar menos. Cada rodada completa sobre os dados é uma iteração (`max_iter` é o limite delas).

**Treino e teste.** Os dados são divididos: 80% para treinar e 20% para testar. A rede nunca vê o teste durante o treino, então a acurácia no teste mostra se ela acerta exemplos novos, em vez de só decorar.

## 4. Passo a passo para configurar

Na pasta do projeto, com o ambiente ativado:

```
python -m pergamo.ml.classifier     # mostra qual motor está em uso (regras ou rede)
python -m pergamo.ml.dataset        # 1) gera data/perfis_sinteticos.csv
python -m pergamo.ml.train          # 2) treina e salva models/perfil_model.joblib
python -m pergamo.ml.classifier     # 3) agora deve dizer "rede neural"
pytest tests/test_ml.py             # 4) confere tudo
streamlit run app.py                # 5) o app já usa a rede
```

O `train` já gera o CSV sozinho, então o passo 1 é opcional. Depois de retreinar, **reinicie o app**, porque o modelo é carregado uma vez só.

Para compartilhar com o grupo, envie ao Git os arquivos `models/perfil_model.joblib`, `models/metricas.json` e `data/perfis_sinteticos.csv`. Assim ninguém precisa treinar de novo. Se alguém usar outra versão do scikit-learn, o modelo pode não carregar: o app cai para as regras sozinho, e basta rodar o `train` de novo.

## 5. Como cada parte funciona

**Dados sintéticos (`dataset.py`).** Não temos dados reais, então o script sorteia perfis (estilos, ritmo, estrutura, social e, em metade deles, um método de ensino). O tipo correto de cada perfil vem das regras de pontos em `classifier.pontuar_por_regras()`. Depois, uma parte dos rótulos (10%) é trocada por outro tipo ao acaso. Isso é o **ruído**: simula respostas inconsistentes do mundo real.

**Regras de pontos (exemplo).** Cada estilo escolhido vale 3 pontos para o seu tipo; método do professor vale 2; ritmo rápido soma 1 para Prático; debate soma 1 para Ouvinte; estrutura estruturada soma 1 para Leitor; individual soma 1 para Racional. O tipo com mais pontos vence (empate: o primeiro da lista). **Alterar essas regras muda o que a rede aprende.**

**Treino (`train.py`).** Cria um `MLPClassifier(hidden_layer_sizes=(16, 8))`, treina com 80% dos dados e mede no teste. Calcula quatro números:

| Métrica | O que significa |
|---|---|
| acurácia no treino | quanto acerta os exemplos que usou para aprender |
| acurácia no teste | quanto acerta exemplos novos (com o ruído) |
| acurácia sem ruído | quanto acerta o tipo correto, ignorando o ruído: mostra se aprendeu as regras |
| confiança média | a maior probabilidade que a rede costuma dar (quão "segura" ela é) |

**Uso (`classifier.py`).** `classify(perfil)` transforma o perfil em números, pede as probabilidades à rede (`predict_proba`) e devolve o tipo mais provável.

## 6. Experimentos para entender (rode e compare)

Use `--sem-salvar` para não sobrescrever o modelo do grupo:

```
python -m pergamo.ml.train --camadas 4 --sem-salvar
python -m pergamo.ml.train --ruido 0.3 --sem-salvar
python -m pergamo.ml.train --amostras 300 --sem-salvar
```

Resultados medidos (2.000 amostras e 10% de ruído, salvo quando indicado; `max_iter` 2000):

**Tamanho da rede**

| Camadas escondidas | Treino | Teste | Sem ruído | Confiança |
|---|---|---|---|---|
| (2) | 70,6% | 68,0% | 76,5% | 63,1% |
| (4) | 88,7% | 84,8% | 95,0% | 79,3% |
| (16, 8) (padrão) | 90,9% | 85,3% | 96,3% | 87,4% |
| (64, 32) | 92,4% | 84,0% | 94,8% | 90,9% |

Rede pequena demais não consegue aprender as regras (subajuste). Rede grande demais não melhora e começa a se ajustar demais ao treino (diferença maior entre treino e teste).

**Ruído nos rótulos**

| Ruído | Treino | Teste | Sem ruído | Confiança |
|---|---|---|---|---|
| 0% | 100% | 99,8% | 99,8% | 99,0% |
| 10% | 90,9% | 85,3% | 96,3% | 87,4% |
| 30% | 69,5% | 63,5% | 89,5% | 66,4% |

Com mais ruído, a acurácia medida cai e a rede fica menos "confiante", embora ainda aprenda as regras (coluna "sem ruído").

**Quantidade de dados**

| Amostras | Teste | Sem ruído |
|---|---|---|
| 300 | 66,7% | 73,3% |
| 2.000 | 85,3% | 96,3% |
| 10.000 | 89,5% | 100% |

Poucos dados deixam a rede instável. Com o padrão do projeto (5.000 amostras, 10% de ruído), o teste dá cerca de 89,8% e o "sem ruído" cerca de 99,5%.

**Iterações.** Com `max_iter` baixo (por exemplo 50), a rede para antes de aprender direito e o scikit-learn mostra um aviso de convergência. Com 2.000 ela termina sozinha, antes do limite.

**Por que não chega a 100% no teste?** Como 10% dos rótulos foram trocados de propósito, o melhor resultado possível no teste é perto de 90%. Se a rede chegou perto disso, ela já aprendeu tudo o que dava. Não persiga 100%.

## 7. Limites (e como apresentar com honestidade)

- A rede aprende **regras que nós mesmos escrevemos**. A acurácia mede o quanto ela imita essas regras, não se o match melhora o aprendizado de verdade.
- Os dados são fictícios. Uma versão real precisaria de dados de uso: avaliações das aulas e quantos alunos continuam com o professor.
- A rede costuma ser muito "confiante" (cerca de 88%), então a nota de match depende bastante de aluno e professor terem o **mesmo tipo**. Uma ideia de melhoria é suavizar as probabilidades ou combinar com as regras.
- No pôster, descreva como **simulação do algoritmo de match**. Resultado honesto para colocar: "a rede reproduziu as regras com cerca de 99,5% de fidelidade em perfis que não viu no treino".

## 8. Perguntas que podem aparecer na apresentação

**Por que usar rede neural se as regras já resolvem?** Porque o objetivo é simular como um algoritmo aprendido funcionaria. Com dados reais, as regras seriam desconhecidas e a rede aprenderia padrões a partir dos exemplos.

**De onde vêm os dados?** São sintéticos, gerados por um script com regras definidas pelo grupo e um pouco de ruído. Não usamos dados de pessoas reais.

**Como vocês sabem que funciona?** Separamos 20% dos dados para teste e a rede acertou cerca de 99,5% dos tipos corretos nesses exemplos novos. Isso comprova que ela aprendeu as regras, mas não valida o match com usuários reais.

**O que é a acurácia de 89,8%, se vocês dizem 99,5%?** A primeira é medida contra rótulos com 10% de ruído colocado de propósito (o máximo possível é perto de 90%); a segunda é medida contra os rótulos corretos.

**O que acontece se o modelo falhar?** O `classify()` volta automaticamente para as regras, então o app continua funcionando.

**O que a IA do match faz depois da classificação?** `match.py` compara as probabilidades do aluno e do professor (similaridade do cosseno), as matérias em comum e o encaixe de ritmo, estrutura e contexto.

## 9. Exercícios para fixar

1. Mude um peso em `pontuar_por_regras()` (por exemplo, dê 4 pontos ao estilo Visual), retreine e veja como os tipos mudam em `python -m pergamo.ml.classifier`.
2. Compare `--camadas 4` com `--camadas 64 32` e explique a diferença entre treino e teste.
3. Gere com `--ruido 0` e depois `--ruido 0.3` e explique a mudança na confiança média.
4. Abra `data/perfis_sinteticos.csv` e confira à mão 5 linhas: o tipo faz sentido pelas regras?

## 10. Glossário

- **Feature:** uma entrada numérica da rede (as 12 colunas).
- **Rótulo:** o tipo correto de um exemplo.
- **Peso:** número que a rede ajusta durante o treino.
- **Iteração (época):** uma rodada de aprendizado sobre os dados.
- **Acurácia:** porcentagem de acertos.
- **Subajuste:** rede simples demais, erra até no treino.
- **Sobreajuste:** rede que decora o treino e vai pior em dados novos.
- **Ruído:** erros propositais nos rótulos para simular dados reais.
- **Probabilidade (`predict_proba`):** quanto a rede acredita em cada tipo (soma 100%).
