# CardCraftAI Web 0.2 — candidato de staging

## Implementado

- Next.js com rotas próprias: início, catálogo, carta/edição, Atlas, análise, login/cadastro/recuperação, coleção, comunidade, Shop, planos e documentos legais.
- Catálogo público com o índice existente (4.425 nomes). Carta clicável consulta detalhes TCGdex, mantendo referência de edição, variante e fonte. Não é um catálogo exaustivo de edições nem autenticação física.
- Supabase SSR/PKCE: sessão em cookies, atualização via proxy, identidade e e-mail confirmado verificados no servidor. APIs privadas exigem aceite legal vigente e respondem sem cache. Não usa service role no navegador.
- Coleção com paginação, adição pelo catálogo, quantidades, estado de conservação, idioma, variante, notas, desejos, exclusão e comparação otimista dos campos antes de editar. RLS existente preservada.
- Comunidade com leitura das últimas 30 discussões e publicação autenticada. Comentários, reações e moderação avançada ainda usam a implementação anterior; não foram migrados nesta entrega.
- Shop de links comuns, categorias, busca, desejos e carrinho de links persistidos no navegador. Não cobra pelos produtos, não inventa estoque ou preços e não simula receita/conversões.
- Atlas aceita texto/colar, imagem JPEG/PNG/WebP (até 3 MB e 16 MP, normalizada com remoção de metadados) e PDF (até 3 MB/20 páginas, válido e sem senha). Só consultas diretas de nome/código com detalhe disponível são respondidas deterministicamente. Demais mensagens exigem Gemini configurado no servidor. Dados gerados nunca são gravados no catálogo como confirmados.
- Limite de cinco perguntas por conta já existente, com novo wrapper transacional de UUID para impedir reprocessamento do mesmo pedido e limite de dez reservas por minuto. IDs de pedidos são guardados sem conteúdo das mensagens. A sexta pergunta indica planos; pagamento não é oferecido enquanto indisponível.
- Arena e game ausentes da navegação.

## Alterações no TEST

A migração `20261003212738_atlas_web_request_guard.sql` foi aplicada somente no projeto `hwsaxufycqgmzrxjxsfb` (CardCraftAI-TEST). Cria tabela privada sem grants ao cliente, RLS, função privada com verificação de proprietário/e-mail confirmado e wrapper público SECURITY INVOKER com EXECUTE somente para authenticated. O Streamlit continua usando sua função original.

Na Vercel, `NEXT_PUBLIC_SUPABASE_URL` e `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` foram criadas somente para Preview/staging. Ambas são identificadores públicos, não credenciais administrativas. Nenhum segredo deve ser inserido no código.

## Validação executada

- Build Next.js e verificação TypeScript passaram.
- Quatro testes de corpo limitado (Content-Length e streaming/bytes), preservação de conteúdo e idioma passaram.
- Smoke HTTP: dez páginas, consulta pública, limite de 24 resultados, busca vazia, 404, bloqueio de APIs privadas sem sessão, cache privado e proteção de origem nas mutações.
- TEST PostgreSQL: perguntas 1 a 5 permitidas, sexta bloqueada, UUID repetido rejeitado sem nova reserva, leitura/atualização de coleção entre duas contas bloqueadas e RPC negada a anon. Contas/entradas sintéticas existiram apenas na transação revertida; nenhum dado de usuário foi alterado.
- Suíte Python anterior iniciada, mas interrompida pelo processo com código 135 (SIGBUS) durante AppTest de Streamlit neste ambiente. Não considerar a suíte completa aprovada; CI deve rodá-la.
- Inspeção visual automatizada bloqueada: agent-browser não conseguiu criar socket local (Operation not permitted); download do Chromium alternativo falhou. Sem alegação de aprovação visual.

## Bloqueios de lançamento / paridade

1. Definir `GEMINI_API_KEY` e `GEMINI_MODEL` no Preview, confirmar modelo aprovado e testar geração real, upload e respostas em vários idiomas. Sem configuração, API retorna indisponibilidade antes de reservar pergunta. Com provedor configurado, falha após reserva consome a tentativa de TEST; é necessário implementar finalização/estorno confiável no servidor antes de vender esse fluxo.
2. Autorizar o callback `https://project-ay3im-git-staging-francisnolasco47-8892.vercel.app/auth/callback` (incluindo fluxo recovery) no Supabase TEST e testar Google, confirmação e recuperação por e-mail em conta controlada. O conector Supabase atual não expõe alteração das configurações Auth. Não mudar o Site URL do app anterior sem necessidade.
3. Não há checkout PayPal ativo. Exige conta merchant/Sandbox, produto/plano, credenciais server-only, endpoint verificado, conciliação idempotente e testes de cancelamento/reembolso. A preparação Python existente foi preservada. Mercado Pago anterior não foi removido, mas não é exposto como compra nesta interface.
4. Preços/valor de coleção e indicadores comerciais de receita dependem de fontes, permissões e confirmação de conversões. O Shop novo ainda não envia eventos ao coletor antigo; não chamar listas locais de analytics. Cache compartilhado de cotações, busca vetorial/OCR híbrido, estatísticas de receita, histórico de análise e autonomia do assistente de desenvolvimento não foram migrados nesta entrega.
5. Interface em português; o catálogo conserva nomes/textos da fonte em inglês. Localização completa da UI não foi portada. Gemini recebe instrução de responder no idioma da última pergunta. Fotos não comprovam autenticidade.
6. A auditoria TEST ainda indica alertas anteriores: search_path mutável de touch_analysis_runs_updated_at, extensão pg_trgm em public, funções SECURITY DEFINER antigas com EXECUTE excessivo e proteção contra senhas vazadas desabilitada. A tabela privada nova intencionalmente não possui políticas nem grants de acesso direto (negação por padrão).
7. Rever apresentação dos documentos legais na nova hospedagem com o responsável; o texto vigente foi preservado, acrescido de aviso de hospedagem Vercel/checkout indisponível nesta interface.

Não promover para produção sem essas validações. Main e Supabase produção não foram alterados.
