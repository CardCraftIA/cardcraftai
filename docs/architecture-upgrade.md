# CardCraftAI · evolução incremental da arquitetura

## Entregue nesta revisão

- A interface pública de componentes em `web/` oferece início responsivo, navegação para o app existente e busca de nomes em um índice local versionado do TCGdex. O endpoint `/api/catalog` devolve no máximo 24 nomes e não expõe credenciais, preços ou dados privados.
- A análise por foto cria uma cópia temporária com orientação, tamanho e contraste ajustados. Havendo OpenCV no ambiente, um contorno retangular inequívoco é corrigido por perspectiva; sem ele, o fluxo permanece funcional com Pillow. Havendo Tesseract e `pytesseract`, possíveis números de coleção são enviados à IA como pistas não verificadas. OCR nunca confirma identidade, variante nem autenticidade.
- A correção de idioma do cabeçalho do jogo 3D cobre os quatro idiomas que o app oferece.

## Contratos preservados

- O app Streamlit continua a operar Atlas, contas, pagamentos, coleção e Shop durante a migração. Arena e game foram suspensos em 2026-09-28: não aparecem na navegação e suas antigas URLs exibem um aviso. A nova interface não recebe tokens de sessão nem executa análise paga; seus links apontam ao ambiente existente indicado por `NEXT_PUBLIC_LEGACY_APP_URL`.
- Créditos são reservados no banco por `reserve_credit` antes da chamada de IA e concluídos ou estornados por RPC. No Supabase TEST, a atualização condicionada do saldo e o índice único de `usage_logs.request_id` foram verificados em 2026-09-28. As alterações desta revisão não mudam o esquema do banco.
- Preços mantêm as fontes externas, o cache de consulta de uma hora e a classificação de idade já presentes em `app.py`. Não foi introduzido Redis sem medidas de tráfego e sem quota/licença de API dos fornecedores. Nenhum preço é inferido pela IA.
- Atlas só considera confirmados os dados lidos do catálogo; observações da foto e OCR permanecem preliminares. A avaliação física de autenticidade exige inspeção especializada.

## Execução

Na raiz, `PYTHONPATH=<diretório de dependências> python scripts/run_tests.py` roda a suíte sem acesso externo. Em `web/`, `npm ci && npm run build` prepara o índice local e gera o site. O deploy Next.js deve ter acesso à raiz do repositório no build para copiar `data/catalog_name_index_tcgdex_en.json`. Configure `NEXT_PUBLIC_LEGACY_APP_URL` com o URL público do ambiente correspondente. Não publique a nova interface como substituta do Streamlit até configurar hospedagem, domínio e fluxo de autenticação comum.

Para habilitar correção de perspectiva, instale versões aprovadas de `opencv-python-headless` e `numpy` no ambiente de inferência. OCR local também requer `pytesseract` e o binário Tesseract com os idiomas necessários. Ambas as integrações são opcionais e não bloqueiam o app. Monitore latência, taxa de recortes rejeitados e correções humanas antes de ampliar seu uso.

## Próxima etapa para produto público completo

1. Medir p50/p95 das consultas, memória por sessão, erros de OCR, taxa de acerto por set/variante e custo por análise.
2. Migrar autenticação e ações privadas para uma API com checagem de usuário no servidor, reaproveitando o ledger transacional existente. Testar concorrência, reenvio e falha após inferência.
3. Migrar Atlas, coleção e checkout por rotas, com testes de paridade, antes de desativar telas do Streamlit.
4. Avaliar cache compartilhado de cotações apenas com acesso licenciado à fonte e volume medido; guardar origem, moeda, condição, variante e instante da coleta.
